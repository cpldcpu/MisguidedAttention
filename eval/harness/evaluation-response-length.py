import json
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Set
from collections import defaultdict

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Analyze LLM output and thinking lengths from JSON files")
    parser.add_argument("path", help="Path to the directory containing output_queries*.json files")
    parser.add_argument("-o", "--output", default="response_length_analysis.png", 
                        help="Output figure filename (default: response_length_analysis.png)")
    parser.add_argument("--all-prompts", action="store_true", 
                        help="Use all prompts instead of only those available for all LLMs")
    return parser.parse_args()

def find_json_files(path: str) -> List[str]:
    """Find all JSON files starting with 'output_queries' in the given directory"""
    json_files = []
    for file in os.listdir(path):
        if file.startswith("output_queries") and file.endswith(".json"):
            json_files.append(os.path.join(path, file))
    return json_files

def analyze_json_files(json_files: List[str]) -> Tuple[Dict[str, Dict[str, List[int]]], Dict[str, Set[str]]]:
    """Analyze all JSON files and track prompts by LLM"""
    all_results = {}
    prompts_by_llm = defaultdict(set)
    
    for file in json_files:
        print(f"Analyzing {file}...")
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for result in data.get("results", []):
            llm_name = result.get("llm", "unknown")
            prompt_id = result.get("prompt_id", "unknown")
            output = result.get("output", [""])
            thinking = result.get("thinking", [""])
            
            # Track which prompts each LLM has responded to
            prompts_by_llm[llm_name].add(prompt_id)
            
            # Initialize data structures if needed
            if llm_name not in all_results:
                all_results[llm_name] = {"output_lengths": [], "thinking_lengths": [], "prompt_ids": []}
            
            # Handle None values and ensure we have lists of strings
            if output is None:
                output = [""]
            output = ["" if item is None else item for item in output]
            
            if thinking is None:
                thinking = [""]
            thinking = ["" if item is None else item for item in thinking]
            
            # Calculate lengths
            output_length = sum(len(o) for o in output)
            thinking_length = sum(len(t) for t in thinking)
            
            # Store results with prompt_id
            all_results[llm_name]["output_lengths"].append(output_length)
            all_results[llm_name]["thinking_lengths"].append(thinking_length)
            all_results[llm_name]["prompt_ids"].append(prompt_id)
    
    return all_results, prompts_by_llm

def find_common_prompts(prompts_by_llm: Dict[str, Set[str]]) -> Set[str]:
    """Find prompts that are available for all LLMs"""
    if not prompts_by_llm:
        return set()
    
    # Start with all prompts from the first LLM
    common_prompts = next(iter(prompts_by_llm.values()))
    
    # Find intersection with all other LLMs
    for prompt_set in prompts_by_llm.values():
        common_prompts &= prompt_set
    
    return common_prompts

def filter_results_by_common_prompts(all_results: Dict[str, Dict[str, List]], 
                                    common_prompts: Set[str]) -> Dict[str, Dict[str, List[int]]]:
    """Filter results to only include common prompts"""
    filtered_results = {}
    
    for llm_name, data in all_results.items():
        filtered_results[llm_name] = {
            "output_lengths": [],
            "thinking_lengths": []
        }
        
        for i, prompt_id in enumerate(data["prompt_ids"]):
            if prompt_id in common_prompts:
                filtered_results[llm_name]["output_lengths"].append(data["output_lengths"][i])
                filtered_results[llm_name]["thinking_lengths"].append(data["thinking_lengths"][i])
    
    return filtered_results

def calculate_statistics(results: Dict[str, Dict[str, List[int]]]) -> Dict[str, Dict[str, float]]:
    """Calculate averages and medians from filtered results"""
    stats = {}
    for llm_name, data in results.items():
        output_lengths = data["output_lengths"]
        thinking_lengths = data["thinking_lengths"]
        
        # Calculate averages
        avg_output = sum(output_lengths) / len(output_lengths) if output_lengths else 0
        avg_thinking = sum(thinking_lengths) / len(thinking_lengths) if thinking_lengths else 0
        
        # Calculate medians
        median_output = sorted(output_lengths)[len(output_lengths)//2] if output_lengths else 0
        median_thinking = sorted(thinking_lengths)[len(thinking_lengths)//2] if thinking_lengths else 0
        
        # Check if this is a "thinking" LLM (has non-zero thinking traces)
        is_thinking_llm = avg_thinking > 0
        
        stats[llm_name] = {
            "avg_output_length": avg_output,
            "avg_thinking_length": avg_thinking,
            "median_output_length": median_output,
            "median_thinking_length": median_thinking,
            "is_thinking_llm": is_thinking_llm,
            "sample_count": len(output_lengths)
        }
    
    return stats

def create_visualization(results: Dict[str, Dict[str, float]], output_file: str):
    """Create bar charts for output and thinking lengths (average and median)"""
    # Create figure with four subplots (2x2)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 14))
    
    # Process data for average output lengths
    output_avg_data = [(llm, data["avg_output_length"], data["is_thinking_llm"]) 
                   for llm, data in results.items()]
    output_avg_data.sort(key=lambda x: x[1])  # Sort by output length
    
    # Process data for median output lengths
    output_med_data = [(llm, data["median_output_length"], data["is_thinking_llm"]) 
                   for llm, data in results.items()]
    output_med_data.sort(key=lambda x: x[1])  # Sort by output length
    
    # Plot average output lengths
    llm_names = [item[0] for item in output_avg_data]
    output_lengths = [item[1] for item in output_avg_data]
    is_thinking = [item[2] for item in output_avg_data]
    colors = ['#1f77b4' if thinking else '#ff7f0e' for thinking in is_thinking]
    
    bars1 = ax1.bar(range(len(llm_names)), output_lengths, color=colors)
    ax1.set_title("Average Output Length by LLM")
    ax1.set_ylabel("Length (characters)")
    ax1.set_xticks(range(len(llm_names)))
    ax1.set_xticklabels(llm_names, rotation=45, ha="right")
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=8)
    
    # Plot median output lengths
    llm_names = [item[0] for item in output_med_data]
    output_lengths = [item[1] for item in output_med_data]
    is_thinking = [item[2] for item in output_med_data]
    colors = ['#1f77b4' if thinking else '#ff7f0e' for thinking in is_thinking]
    
    bars2 = ax2.bar(range(len(llm_names)), output_lengths, color=colors)
    ax2.set_title("Median Output Length by LLM")
    ax2.set_ylabel("Length (characters)")
    ax2.set_xticks(range(len(llm_names)))
    ax2.set_xticklabels(llm_names, rotation=45, ha="right")
    
    # Add value labels on bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=8)
    
    # Plot average thinking lengths - use the same order as output avg chart for consistency
    thinking_lengths = [data["avg_thinking_length"] if data["is_thinking_llm"] else 0 
                    for llm, data in sorted(results.items(), key=lambda x: x[1]["avg_output_length"])]
    
    # Use the same LLM names order as output chart
    bars3 = ax3.bar(range(len(llm_names)), thinking_lengths, 
                   color=['#1f77b4' if length > 0 else 'none' for length in thinking_lengths])
    ax3.set_title("Average Thinking Length by LLM")
    ax3.set_ylabel("Length (characters)")
    ax3.set_xticks(range(len(llm_names)))
    ax3.set_xticklabels(llm_names, rotation=45, ha="right")
    
    # Add value labels only for bars with thinking data
    for i, (bar, length) in enumerate(zip(bars3, thinking_lengths)):
        if length > 0:
            ax3.text(bar.get_x() + bar.get_width()/2., length,
                    f'{int(length)}',
                    ha='center', va='bottom', fontsize=8)
    
    # Plot median thinking lengths - use the same order as output med chart for consistency
    thinking_lengths = [data["median_thinking_length"] if data["is_thinking_llm"] else 0 
                    for llm, data in sorted(results.items(), key=lambda x: x[1]["median_output_length"])]
    
    # Use the same LLM names order as output chart
    bars4 = ax4.bar(range(len(llm_names)), thinking_lengths,
                   color=['#1f77b4' if length > 0 else 'none' for length in thinking_lengths])
    ax4.set_title("Median Thinking Length by LLM")
    ax4.set_ylabel("Length (characters)")
    ax4.set_xticks(range(len(llm_names)))
    ax4.set_xticklabels(llm_names, rotation=45, ha="right")
    
    # Add value labels only for bars with thinking data
    for i, (bar, length) in enumerate(zip(bars4, thinking_lengths)):
        if length > 0:
            ax4.text(bar.get_x() + bar.get_width()/2., length,
                    f'{int(length)}',
                    ha='center', va='bottom', fontsize=8)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#1f77b4', label='Thinking LLMs'),
        Patch(facecolor='#ff7f0e', label='Normal LLMs')
    ]
    ax1.legend(handles=legend_elements, loc='upper right')
    ax2.legend(handles=legend_elements, loc='upper right')
    
    # Add grid lines for better readability
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    ax3.grid(axis='y', linestyle='--', alpha=0.7)
    ax4.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Visualization saved to {output_file}")

def main():
    args = parse_arguments()
    
    # Find all JSON files
    json_files = find_json_files(args.path)
    if not json_files:
        print(f"No JSON files starting with 'output_queries' found in {args.path}")
        return
    
    print(f"Found {len(json_files)} JSON files to analyze")
    
    # Analyze all files at once to track prompts by LLM
    all_results, prompts_by_llm = analyze_json_files(json_files)
    
    # Find common prompts across all LLMs
    common_prompts = find_common_prompts(prompts_by_llm)
    
    if not args.all_prompts:
        print(f"\nFound {len(common_prompts)} prompts common to all LLMs")
        # Filter results to only include common prompts
        filtered_results = filter_results_by_common_prompts(all_results, common_prompts)
        # Calculate statistics from filtered results
        stats = calculate_statistics(filtered_results)
    else:
        print("\nUsing all available prompts for each LLM")
        # Use all results but still calculate statistics
        stats = calculate_statistics(all_results)
    
    # Create visualization
    create_visualization(stats, args.output)
    
    # Print summary to console
    print("\nAnalysis Summary:")
    print("=" * 110)
    print(f"{'LLM Name':<30} {'Avg Output':<10} {'Med Output':<10} {'Avg Thinking':<10} {'Med Thinking':<10} {'Samples':<10}")
    print("-" * 110)
    for llm, data in sorted(stats.items(), key=lambda x: x[1]["avg_output_length"], reverse=True):
        print(f"{llm:<30} {data['avg_output_length']:<10.0f} {data['median_output_length']:<10.0f} "
              f"{data['avg_thinking_length']:<10.0f} {data['median_thinking_length']:<10.0f} {data['sample_count']:<10}")

if __name__ == "__main__":
    main()
