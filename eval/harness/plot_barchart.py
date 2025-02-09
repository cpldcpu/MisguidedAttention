import json
import argparse
import matplotlib.pyplot as plt
import numpy as np

def load_config_llms(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return {llm['name'] for llm in config['llms']}

def determine_llm_category(llm_name):
    # Load all configuration files
    small_llms = load_config_llms('query_config_small.json')
    midrange_llms = load_config_llms('query_config_midrange.json')
    flagship_llms = load_config_llms('query_config_flagship.json')
    reasoning_llms = load_config_llms('query_config_reasoning.json')
    
    if llm_name in small_llms:
        return 'Small', '#1f77b4'  # blue
    elif llm_name in midrange_llms:
        return 'Midrange', '#2ca02c'  # green
    elif llm_name in flagship_llms:
        return 'Flagship', '#d62728'  # red
    elif llm_name in reasoning_llms:
        return 'Reasoning', '#9467bd'  # purple
    else:
        return 'Unknown', '#7f7f7f'  # gray

def load_and_sort_scores(scores_file):
    scores = {}
    with open(scores_file, 'r') as f:
        for line in f:
            name, score = line.strip().split('\t')
            scores[name] = float(score)
    
    # Sort by score
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

def create_barchart(scores_file, output_file, title='Misguided Attention Eval (long)'):
    # Load and sort scores
    scores = load_and_sort_scores(scores_file)
    
    # Prepare plot data
    names = list(scores.keys())
    values = np.array(list(scores.values())) * 100  # Convert to percentages
    
    # Get categories and colors
    categories = [determine_llm_category(name) for name in names]
    colors = [cat[1] for cat in categories]
    
    # Debug: print category assignments
    # for name, cat in zip(names, categories):
        # print(f"{name}: {cat[0]} ({cat[1]})")
    
    # Create figure
    plt.figure(figsize=(8, 6))
    bars = plt.bar(range(len(scores)), values, color=colors)
    
    # Customize plot
    plt.ylabel('Average Score (%)')
    plt.title(title)
    plt.xticks(range(len(scores)), names, rotation=45, ha='right', fontsize=8)  # smaller font size
    plt.ylim(0, 100)
    
    # Add horizontal gridlines
    plt.grid(axis='y', linestyle='--', color='lightgray', alpha=0.7)
    plt.gca().set_axisbelow(True)  # Put gridlines behind bars
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        # Determine rotation based on number of bars
        rotation = 90 if len(scores) > 12 else 0
        # Add text with smaller font size and adjusted position
        plt.text(bar.get_x() + bar.get_width()/2., 
                height + (1 if rotation == 90 else 0),  # Add small offset when rotated
                f'{height:.1f}%',
                ha='center',  # Always center horizontally
                va='bottom',  # Always align to bottom
                rotation=rotation,
                fontsize=8)
    
    # Add legend - fixed to ensure correct color matching
    unique_pairs = sorted(set((cat[0], cat[1]) for cat in categories))
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, label=cat)
                      for cat, color in unique_pairs]
    plt.legend(handles=legend_elements, loc='upper right')
    
    # Add footer
    plt.figtext(0.99, 0.01, 'github.com/cpldcpu/MisguidedAttention', 
                ha='right', va='bottom', color='darkgray', fontsize=8)
    
    # Save plot
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Bar chart has been generated and saved as '{output_file}'")

def main():
    parser = argparse.ArgumentParser(description="Generate bar chart from evaluation scores.")
    parser.add_argument('scores_file', type=str, help='Path to the scores text file')
    parser.add_argument('--output', type=str, default='barchart_average.png', help='Output file name')
    parser.add_argument('--title', type=str, default='Misguided Attention Eval (long)', 
                       help='Title of the plot')
    args = parser.parse_args()
    
    create_barchart(args.scores_file, args.output, args.title)

if __name__ == "__main__":
    main()
