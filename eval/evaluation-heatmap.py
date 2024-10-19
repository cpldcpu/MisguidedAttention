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

def load_valid_llms(file_path):
    if file_path is None:
        return None
    with open(file_path, 'r') as f:
        config = json.load(f)
    return [llm['name'] for llm in config['llms']]


def process_summaries(summaries, valid_llms=None):
    data = []
    for summary in summaries:
        for prompt_id, prompt_data in summary.items():
            for llm, llm_data in prompt_data.items():
                if valid_llms is None or llm in valid_llms:
                    average_score = llm_data['average_score']
                    expected_behavior_avg = np.mean(list(llm_data['expected_behavior_stats'].values()) or [0])
                    common_mistakes_avg = np.mean(list(llm_data['common_mistakes_stats'].values()) or [0])
                    behavior_score = expected_behavior_avg - common_mistakes_avg
                    data.append({
                        'prompt_id': prompt_id,
                        'llm': llm,
                        'average_rating': average_score,
                        'expected_minus_mistakes_score': behavior_score,
                        'expected_behavior_score': expected_behavior_avg,
                        'common_mistakes_score': - common_mistakes_avg
                    })
                else:
                    print(f"Ignoring LLM '{llm}' for prompt ID '{prompt_id}'")
    return pd.DataFrame(data)


def create_heatmap(data, value_col, output_file, cmap, vmin, vmax):
    # Group by llm and prompt_id, then aggregate using mean
    grouped_data = data.groupby(['llm', 'prompt_id'])[value_col].mean().reset_index()
    
    pivot_table = grouped_data.pivot(index='llm', columns='prompt_id', values=value_col)

    # Calculate row averages
    row_averages = pivot_table.mean(axis=1)

    plt.figure(figsize=(14, 8))
    # ax = sns.heatmap(pivot_table, cmap=cmap, annot=True, fmt='.1f', 
    #                  cbar_kws={'label': value_col.replace('_', ' ').title()},
    #                  vmin=vmin, vmax=vmax)

    ax = sns.heatmap(pivot_table, cmap=cmap, annot=True, fmt='.1f', 
                     cbar=False,
                     linewidths=1.0, linecolor='white',
                     vmin=vmin, vmax=vmax)

    for t in ax.texts:
        t.set_size(12)

    plt.title(f'{value_col.replace("_", " ").title()} Heatmap', fontsize=20)
    plt.xlabel('', fontsize=16)
    plt.ylabel('', fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=14)

    for idx, average in enumerate(row_averages):
        plt.text(pivot_table.shape[1] + 0.2, idx + 0.5, f'{average:.2f}', 
                ha='left', va='center', fontsize=16)

    plt.text(pivot_table.shape[1] + 0.5, -0.3, '⌀', 
            ha='left', va='center', fontsize=20, fontweight='bold')
        
    # cbar = ax.collections[0].colorbar
    # cbar.ax.tick_params(labelsize=12)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Heatmap has been generated and saved as '{output_file}'")

def main(folder_path, valid_llms_file=None):
    summaries = load_evaluation_summaries(folder_path)
    valid_llms = load_valid_llms(valid_llms_file) if valid_llms_file else None
    data = process_summaries(summaries, valid_llms)
   
    create_heatmap(data, 'average_rating', 'heatmap_average_rating.png', 'YlGnBu', 1, 5)
    create_heatmap(data, 'expected_minus_mistakes_score', 'heatmap_behavior_sum.png', 'YlGnBu', -1, 1)
    create_heatmap(data, 'expected_behavior_score', 'heatmap_expected_behavior.png', 'YlGnBu', 0, 1)
    create_heatmap(data, 'common_mistakes_score', 'heatmap_common_mistakes.png', 'YlGnBu', -1, 0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate heatmaps from evaluation summaries.")
    parser.add_argument('folder_path', type=str, help='Path to the folder containing evaluation summary JSON files')
    parser.add_argument('--valid_llms', type=str, help='Path to JSON file containing valid LLMs. Usually this is query_config.json')
    args = parser.parse_args()
    
    main(args.folder_path, args.valid_llms)    


