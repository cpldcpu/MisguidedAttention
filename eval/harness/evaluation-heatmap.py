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


def process_summaries(summaries, valid_llms=None, add_solved=False):
    data = []
    max_scores = {}  # Track maximum score per prompt_id
    
    for summary in summaries:
        for prompt_id, prompt_data in summary.items():
            for llm, llm_data in prompt_data.items():
                if valid_llms is None or llm in valid_llms:
                    score = llm_data['average_total_score']
                    data.append({
                        'prompt_id': prompt_id,
                        'llm': llm,
                        'average_score': score
                    })
                    
                    # Update maximum score for this prompt
                    if prompt_id not in max_scores or score > max_scores[prompt_id]:
                        max_scores[prompt_id] = score
                else:
                    print(f"Ignoring LLM '{llm}' for prompt ID '{prompt_id}'")
    
    # Add "solved prompts" entry if requested
    if add_solved:
        for prompt_id, max_score in max_scores.items():
            data.append({
                'prompt_id': prompt_id,
                'llm': "solved prompts",
                'average_score': max_score
            })
    
    return pd.DataFrame(data)

def save_llm_scores(llm_scores, output_file):
    with open(output_file, 'w') as f:
        for llm, score in llm_scores.items():
            f.write(f"{llm}\t{score:.3f}\n")
    print(f"LLM scores have been saved to '{output_file}'")

def create_heatmap(data, value_col, output_file, cmap, vmin, vmax, title='Misguided Attention Eval (long)'):
    # Group by llm and prompt_id, then aggregate using mean
    grouped_data = data.groupby(['llm', 'prompt_id'])[value_col].mean().reset_index()
    
    pivot_table = grouped_data.pivot(index='llm', columns='prompt_id', values=value_col)

    # Sort LLM names case-insensitively
    pivot_table = pivot_table.reindex(sorted(pivot_table.index, key=lambda s: s.casefold()))

    # Calculate row averages
    row_averages = pivot_table.mean(axis=1)
    
    # Sort pivot table rows by average score in descending order
    pivot_table = pivot_table.loc[row_averages.sort_values(ascending=False).index]
    
    # Recalculate row averages after sorting
    row_averages = pivot_table.mean(axis=1)
    
    column_averages = pivot_table.mean(axis=0)

    plt.figure(figsize=(14, 14))

   
    ax = sns.heatmap(pivot_table, cmap=cmap, 
                     annot=len(pivot_table.columns) < 30, fmt='.2f', 
                     cbar=False,
                     linewidths=1.0, linecolor='white',
                     vmin=vmin, vmax=vmax)

    plt.title(title, fontsize=20)
    plt.xlabel('', fontsize=16)
    plt.ylabel('', fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=14)

    for idx, average in enumerate(row_averages):
        plt.text(pivot_table.shape[1] + 0.2, idx + 0.5, f'{average:.2f}', 
                ha='left', va='center', fontsize=16)

    plt.text(pivot_table.shape[1] + 0.5, -0.3, '⌀', 
            ha='left', va='center', fontsize=20, fontweight='bold')
        
    # Add footer
    plt.figtext(0.99, 0.01, 'github.com/cpldcpu/MisguidedAttention', 
                ha='right', va='bottom', color='darkgray', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Heatmap has been generated and saved as '{output_file}'")
    return row_averages

def main(folder_path, valid_llms_file=None, title='Misguided Attention Eval (long)', add_solved=False):
    summaries = load_evaluation_summaries(folder_path)
    valid_llms = load_valid_llms(valid_llms_file) if valid_llms_file else None
    data = process_summaries(summaries, valid_llms, add_solved)
   
    # Generate heatmap for average score only
    row_averages = create_heatmap(data, 'average_score', 'heatmap_average_score.png', 
                                 'YlGnBu', 0, 1, title)
    save_llm_scores(row_averages, 'average_scores.txt')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate heatmaps from evaluation summaries.")
    parser.add_argument('folder_path', type=str, help='Path to the folder containing evaluation summary JSON files')
    parser.add_argument('--valid_llms', type=str, help='Path to JSON file containing valid LLMs. Usually this is query_config.json')
    parser.add_argument('--title', type=str, default='Misguided Attention Eval (long)', 
                       help='Title of the plot')
    parser.add_argument('--solved', action='store_true', 
                       help='Add a "solved prompts" entry showing maximum score across all LLMs')
    args = parser.parse_args()
    
    main(args.folder_path, args.valid_llms, args.title, args.solved)


