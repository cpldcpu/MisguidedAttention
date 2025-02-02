import json
import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def create_plots(summary_data, output_file, limit):
    prompt_ids = list(summary_data.keys())
    if limit > 0:
        prompt_ids = prompt_ids[:limit]
    
    # A4 size in inches (landscape)
    a4_width_inch = 11.69
    a4_height_inch = 8.27
    
    with PdfPages(output_file) as pdf:
        for prompt_id in prompt_ids:
            fig, ax = plt.subplots(figsize=(a4_width_inch, a4_height_inch))
            plot_prompt(ax, summary_data[prompt_id], prompt_id)
            plt.tight_layout()
            pdf.savefig(fig, orientation='landscape')
            plt.close(fig)

def plot_prompt(ax, prompt_data, prompt_id):
    llms = sorted(prompt_data.keys())
    
    # Get all unique criteria across all LLMs
    all_criteria = set()
    for llm in llms:
        all_criteria.update(prompt_data[llm]['criteria_stats'].keys())
    all_criteria = sorted(all_criteria)
    
    total_bars = len(all_criteria)
    bar_width = 0.8 / total_bars
    
    ax2 = ax.twinx()  # Create a secondary y-axis
    
    # Create color map for criteria (using a blue-green palette)
    color_map = plt.cm.viridis
    criteria_colors = [color_map(0.3 + 0.7 * i / max(1, len(all_criteria) - 1)) for i in range(len(all_criteria))]

    legend_handles = []
    legend_labels = []
    max_n = 0
    
    for llm_index, llm in enumerate(llms):
        criteria_stats = prompt_data[llm]['criteria_stats']
        
        for j, criterion in enumerate(all_criteria):
            x = llm_index + (j - total_bars/2 + 0.5) * bar_width
            value = criteria_stats.get(criterion, 0)
            bar = ax.bar(x, value, width=bar_width, color=criteria_colors[j])
            if llm_index == 0:  # Add to legend only once
                legend_handles.append(bar)
                legend_labels.append(criterion)
        
        # Plot average total score
        ax2.scatter(llm_index, prompt_data[llm]['average_total_score'], color='black', zorder=3)
        max_n = max(max_n, prompt_data[llm]['num_evaluations'])

    ax.set_title(f"{prompt_id}\n[n={max_n}]", fontsize=16, fontweight='bold')
    ax.set_xticks(range(len(llms)))
    ax.set_xticklabels(llms, rotation=45, ha='right', fontsize=14)
    ax.set_ylabel('Criteria Success Rate', fontsize=14)
    ax.tick_params(axis='y', labelsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_ylim(0, 1.1)  # Set y-axis limits from 0 to 1.1 to show full range
    
    ax2.set_ylabel('Total Score (0-1)', fontsize=14)
    ax2.tick_params(axis='y', labelsize=12)
    ax2.set_ylim(0, 1.1)

    # Add legend
    ax.legend(legend_handles, legend_labels,  
              loc='upper left', fontsize=12, title_fontsize=14, ncol=1)

    # Adjust layout
    plt.subplots_adjust(bottom=0.2, top=0.9, left=0.1, right=0.9)

def main():
    parser = argparse.ArgumentParser(description="Create evaluation plots from summary data")
    parser.add_argument("--summary", default="evaluation_summary.json", help="Path to the summary JSON file")
    parser.add_argument("--output", default="summary.pdf", help="Path to the output PDF file")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of prompt_ids to process")

    args = parser.parse_args()

    summary_data = load_json(args.summary)
    create_plots(summary_data, args.output, args.limit)
    print(f"Plots saved to {args.output}")

if __name__ == "__main__":
    main()
