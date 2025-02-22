import json
import argparse
import matplotlib.pyplot as plt
import numpy as np

def determine_llm_category(llm_name):
    implant_keywords = ['implant', 'implanted']
    if any(keyword in llm_name.lower() for keyword in implant_keywords):
        return 'Brain Implant', '#d62728'  # red
    return 'Directly Prompted', '#1f77b4'  # blue

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
    
    # Create figure
    plt.figure(figsize=(8, 6))
    bars = plt.bar(range(len(scores)), values, color=colors)
    
    # Customize plot
    plt.ylabel('Average Score (%)')
    plt.title(title)
    plt.xticks(range(len(scores)), names, rotation=45, ha='right', fontsize=8)
    plt.ylim(0, 100)
    
    # Add horizontal gridlines
    plt.grid(axis='y', linestyle='--', color='lightgray', alpha=0.7)
    plt.gca().set_axisbelow(True)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        rotation = 90 if len(scores) > 12 else 0
        plt.text(bar.get_x() + bar.get_width()/2., 
                height + (1 if rotation == 90 else 0),
                f'{height:.1f}%',
                ha='center',
                va='bottom',
                rotation=rotation,
                fontsize=8)
    
    # Add legend with just two categories
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
