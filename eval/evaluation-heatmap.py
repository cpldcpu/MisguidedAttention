import json
import os
import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def load_evaluation_summaries(folder_path):
    summaries = []
    for filename in os.listdir(folder_path):
        if filename.startswith("evaluation_summary") and filename.endswith(".json"):
            with open(os.path.join(folder_path, filename), 'r') as file:
                summaries.append(json.load(file))
    return summaries

def process_summaries(summaries):
    data = []
    for summary in summaries:
        for prompt_id, prompt_data in summary.items():
            for llm, llm_data in prompt_data.items():
                average_score = llm_data['average_score']
                expected_behavior_avg = np.mean(list(llm_data['expected_behavior_stats'].values()) or [0])
                common_mistakes_avg = np.mean(list(llm_data['common_mistakes_stats'].values()) or [0])
                behavior_score = expected_behavior_avg - common_mistakes_avg
                data.append({
                    'prompt_id': prompt_id,
                    'llm': llm,
                    'average_score': average_score,
                    'behavior_score': behavior_score,
                    'expected_behavior_score': expected_behavior_avg
                })
    return pd.DataFrame(data)

def create_heatmap(data, value_col, output_file, cmap, vmin, vmax):
    # Group by llm and prompt_id, then aggregate using mean
    grouped_data = data.groupby(['llm', 'prompt_id'])[value_col].mean().reset_index()
    
    pivot_table = grouped_data.pivot(index='llm', columns='prompt_id', values=value_col)
    
    plt.figure(figsize=(14, 8))
    ax = sns.heatmap(pivot_table, cmap=cmap, annot=True, fmt='.1f', 
                     cbar_kws={'label': value_col.replace('_', ' ').title()},
                     vmin=vmin, vmax=vmax)
    
    plt.title(f'{value_col.replace("_", " ").title()} Heatmap', fontsize=20)
    plt.xlabel('Prompt ID', fontsize=16)
    plt.ylabel('LLM', fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=12)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Heatmap has been generated and saved as '{output_file}'")

def main(folder_path):
    summaries = load_evaluation_summaries(folder_path)
    data = process_summaries(summaries)
    
    # Custom colormap for average_score (red to blue)
    avg_score_cmap = LinearSegmentedColormap.from_list("custom", ["white", "blue"])
    
    # Custom colormap for expected_behavior_score (red to blue)
    expected_behavior_cmap = LinearSegmentedColormap.from_list("custom", ["red", "blue"])
    
    create_heatmap(data, 'average_score', 'average_score_heatmap.png', 'YlGnBu', 1, 5)
    create_heatmap(data, 'behavior_score', 'behavior_score_heatmap.png', 'YlGnBu', -1, 1)
    create_heatmap(data, 'expected_behavior_score', 'expected_behavior_heatmap.png', 'YlGnBu', 0, 1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate heatmaps from evaluation summaries.")
    parser.add_argument('folder_path', type=str, help='Path to the folder containing evaluation summary JSON files')
    args = parser.parse_args()
    
    main(args.folder_path)