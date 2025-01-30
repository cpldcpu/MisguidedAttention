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


def process_summaries(summaries, valid_llms=None, all_columns=False):
    data = []
    prompt_ids_by_llm = {}
    
    # First pass: collect data and track prompt_ids per LLM
    for summary in summaries:
        for prompt_id, prompt_data in summary.items():
            for llm, llm_data in prompt_data.items():
                if valid_llms is None or llm in valid_llms:
                    data.append({
                        'prompt_id': prompt_id,
                        'llm': llm,
                        'average_score': llm_data['average_total_score']
                    })
                    if llm not in prompt_ids_by_llm:
                        prompt_ids_by_llm[llm] = set()
                    prompt_ids_by_llm[llm].add(prompt_id)
                else:
                    print(f"Ignoring LLM '{llm}' for prompt ID '{prompt_id}'")
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    if not all_columns:
        # Find prompt_ids that are common to all LLMs
        common_prompt_ids = set.intersection(*prompt_ids_by_llm.values()) if prompt_ids_by_llm else set()
        if not common_prompt_ids:
            raise ValueError("No common prompt IDs found across all LLMs!")
        # Filter data to include only common prompt_ids
        df = df[df['prompt_id'].isin(common_prompt_ids)]
        
    return df

def save_llm_scores(llm_scores, output_file):
    with open(output_file, 'w') as f:
        for llm, score in llm_scores.items():
            f.write(f"{llm}\t{score:.2f}\n")
    print(f"LLM scores have been saved to '{output_file}'")

def create_heatmap(data, value_col, output_file, cmap, vmin, vmax):
    # Group by llm and prompt_id, then aggregate using mean
    grouped_data = data.groupby(['llm', 'prompt_id'])[value_col].mean().reset_index()
    
    pivot_table = grouped_data.pivot(index='llm', columns='prompt_id', values=value_col)

    # Sort LLM names case-insensitively
    pivot_table = pivot_table.reindex(sorted(pivot_table.index, key=lambda s: s.casefold()))

    # Calculate row averages (excluding NaN values)
    row_averages = pivot_table.mean(axis=1, skipna=True)
    column_averages = pivot_table.mean(axis=0, skipna=True)

    plt.figure(figsize=(14, 9))
    
    # Create mask for NaN values
    mask = pivot_table.isna()

    ax = sns.heatmap(pivot_table, cmap=cmap, 
                     annot=len(pivot_table.columns) < 30, fmt='.2f', 
                     cbar=False,
                     linewidths=1.0, linecolor='white',
                     vmin=vmin, vmax=vmax,
                     mask=mask)  # Apply mask to hide NaN values

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
        
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Heatmap has been generated and saved as '{output_file}'")
    return row_averages

def main(folder_path, valid_llms_file=None, all_columns=False):
    summaries = load_evaluation_summaries(folder_path)
    valid_llms = load_valid_llms(valid_llms_file) if valid_llms_file else None
    data = process_summaries(summaries, valid_llms, all_columns)
   
    # Generate heatmap for average score only
    row_averages = create_heatmap(data, 'average_score', 'heatmap_average_score.png', 'YlGnBu', 0, 1)
    save_llm_scores(row_averages, 'average_scores.txt')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate heatmaps from evaluation summaries.")
    parser.add_argument('folder_path', type=str, help='Path to the folder containing evaluation summary JSON files')
    parser.add_argument('--valid_llms', type=str, help='Path to JSON file containing valid LLMs. Usually this is query_config.json')
    parser.add_argument('--all_columns', action='store_true', help='Include all columns even if not present in all results')
    args = parser.parse_args()
    
    main(args.folder_path, args.valid_llms, args.all_columns)


