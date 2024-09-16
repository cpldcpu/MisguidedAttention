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
    
    # Get all unique behaviors and mistakes across all LLMs
    all_behaviors = set()
    all_mistakes = set()
    for llm in llms:
        all_behaviors.update(prompt_data[llm]['expected_behavior_stats'].keys())
        all_mistakes.update(prompt_data[llm]['common_mistakes_stats'].keys())
    all_behaviors = sorted(all_behaviors)
    all_mistakes = sorted(all_mistakes, reverse=True)
    
    total_bars = max(len(all_behaviors), len(all_mistakes))
    bar_width = 0.8 / total_bars
    
    ax2 = ax.twinx()  # Create a secondary y-axis
    
    # Create color maps for behaviors (green) and mistakes (red)
    green_cmap = plt.cm.Greens
    red_cmap = plt.cm.Reds
    behavior_colors = [green_cmap(0.3 + 0.7 * i / (len(all_behaviors) - 1)) for i in range(len(all_behaviors))]
    mistake_colors = [red_cmap(0.3 + 0.7 * i / (len(all_mistakes) - 1)) for i in range(len(all_mistakes))]
    
    legend_handles = []
    legend_labels = []
    max_n = 0
    
    for llm_index, llm in enumerate(llms):
        expected_behaviors = prompt_data[llm]['expected_behavior_stats']
        common_mistakes = prompt_data[llm]['common_mistakes_stats']
        
        for j in range(total_bars):
            x = llm_index + (j - total_bars/2 + 0.5) * bar_width
            
            if j < len(all_behaviors):
                behavior = all_behaviors[j]
                value = expected_behaviors.get(behavior, 0)
                bar = ax.bar(x, value, width=bar_width, color=behavior_colors[j])
                if llm_index == 0:  # Add to legend only once
                    legend_handles.append(bar)
                    legend_labels.append(behavior)
            
            if j < len(all_mistakes):
                mistake = all_mistakes[j]
                value = common_mistakes.get(mistake, 0)
                bar = ax.bar(x, -value, width=bar_width, color=mistake_colors[j])
                # if llm_index == 0 and j >= len(all_behaviors):  # Add to legend only once and if not already added
                if llm_index == 0:  # Add to legend only once and if not already added
                    legend_handles.append(bar)
                    legend_labels.append(mistake)
        
        ax2.scatter(llm_index, prompt_data[llm]['average_score'], color='black', zorder=3)
        max_n = max(max_n, prompt_data[llm]['num_evaluations'])

    ax.set_title(prompt_id, fontsize=16, fontweight='bold')
    ax.set_xticks(range(len(llms)))
    ax.set_xticklabels(llms, rotation=45, ha='right', fontsize=14)
    ax.set_ylabel(f'Positive/negative behavior Score [n={max_n}]', fontsize=14)
    ax.tick_params(axis='y', labelsize=12)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax.set_ylim(-1.3, 1.3)  # Adjusted to show both positive and negative values
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    ax2.set_ylabel('Quality Eval (1-5)', fontsize=14)
    ax2.tick_params(axis='y', labelsize=12)
    ax2.set_ylim(0, 6)

    # Add legend to top-left corner
    # legend_labels = all_behaviors + all_mistakes
    ax.legend(legend_handles, legend_labels,  
              loc='upper left', fontsize=12, title_fontsize=14, ncol=1)

    # Adjust layout to prevent x-axis label overlap
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
