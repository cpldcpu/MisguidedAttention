#!/usr/bin/env python3
import json
import os
import argparse
import glob
from collections import defaultdict
import re

def load_json(file_path):
    """Load data from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_evaluation_summaries(folder_path):
    """Find all JSON files starting with 'evaluation_summary' in the given folder and its subfolders."""
    summaries = []
    # Use glob to recursively find all files matching the pattern
    pattern = os.path.join(folder_path, '**', 'evaluation_summary*.json')
    for file_path in glob.glob(pattern, recursive=True):
        print(f"Found summary file: {file_path}")
        try:
            data = load_json(file_path)
            summaries.append(data)
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
    return summaries

def find_detailed_evaluations(folder_path):
    """Find all JSON files starting with 'detailed_evaluations' in the given folder and its subfolders."""
    evaluations = []
    # Use glob to recursively find all files matching the pattern
    pattern = os.path.join(folder_path, '**', 'detailed_evaluations*.json')
    for file_path in glob.glob(pattern, recursive=True):
        print(f"Found detailed evaluations file: {file_path}")
        try:
            data = load_json(file_path)
            evaluations.append(data)
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
    return evaluations

def load_model_configs():
    """Load model configuration data from query_config* files in the current folder."""
    model_info = {}
    model_type_map = {}
    
    # Find all query_config* files in the current directory
    config_files = glob.glob("query_config*.json")
    
    for config_file in config_files:
        # Extract model type from filename (e.g., "flagship" from "query_config_flagship.json")
        match = re.search(r"query_config_?([a-zA-Z0-9]+)?\.json", config_file)
        model_type = match.group(1) if match and match.group(1) else "general"
        
        try:
            config_data = load_json(config_file)
            for llm in config_data.get("llms", []):
                name = llm.get("name")
                if name:
                    # Extract lab (provider) from model field if possible
                    model_field = llm.get("model", "")
                    lab = "unknown"
                    if "/" in model_field:
                        lab = model_field.split("/")[0]
                    elif "-" in model_field:
                        lab = model_field.split("-")[0]
                    
                    # Store model info
                    model_info[name] = {
                        "model_type": model_type,
                        "lab": lab
                    }
                    
                    # Add max_tokens if available
                    if "max_tokens" in llm and llm["max_tokens"]:
                        model_info[name]["max_tokens"] = llm["max_tokens"]
        except Exception as e:
            print(f"Error processing config file {config_file}: {str(e)}")
    
    return model_info

def compile_data(summaries):
    """Compile all summary data into a single structure, without model information."""
    all_data = defaultdict(dict)
    
    for summary in summaries:
        for task_id, task_data in summary.items():
            for model_name, model_data in task_data.items():
                # Extract only the relevant data for this model and task
                score_data = {
                    "average_total_score": model_data.get("average_total_score", 0),
                    "num_evaluations": model_data.get("num_evaluations", 0),
                    # "criteria_stats": model_data.get("criteria_stats", {})
                }
                
                # Add to the compiled data
                if task_id not in all_data:
                    all_data[task_id] = {}
                all_data[task_id][model_name] = score_data
    
    return all_data

def compile_responses(evaluations):
    """Compile all detailed evaluation data into a single structure."""
    all_responses = defaultdict(dict)
    
    for evaluation in evaluations:
        for task_id, task_data in evaluation.items():
            for model_name, model_responses in task_data.items():
                # Skip if no responses exist
                if not model_responses:
                    continue
                
                # Make sure the task and model exist in our structure
                if task_id not in all_responses:
                    all_responses[task_id] = {}
                
                # Copy the list of response objects for this model and task
                all_responses[task_id][model_name] = model_responses
    
    return all_responses

def save_as_js(data, output_path, var_name="allData"):
    """Save the compiled data as a JavaScript file."""
    js_content = f"// {output_path}\nconst {var_name} = " + json.dumps(data, indent=2) + ";\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Data saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Collect and compile evaluation summary and detailed data")
    parser.add_argument("folder_path", help="Path to the folder to search for evaluation files")
    parser.add_argument("--output-data", default="data.js", help="Output JavaScript file path for summary data (default: data.js)")
    parser.add_argument("--output-responses", default="responses.js", help="Output JavaScript file path for detailed responses (default: responses.js)")
    parser.add_argument("--output-models", default="models.js", help="Output JavaScript file path for model information (default: models.js)")
    
    args = parser.parse_args()
    
    print(f"Searching for evaluation files in {args.folder_path}...")
    
    # Load model configuration information
    print("Loading model configuration data from query_config* files...")
    model_info = load_model_configs()
    print(f"Found configuration data for {len(model_info)} models")
    
    # Save model information to a separate file
    print(f"Saving model information to {args.output_models}...")
    save_as_js(model_info, args.output_models, "modelInfo")
    
    # Process summary data
    summaries = find_evaluation_summaries(args.folder_path)
    print(f"Found {len(summaries)} summary files")
    
    if summaries:
        print("Compiling summary data...")
        compiled_data = compile_data(summaries)
        print(f"Saving compiled data to {args.output_data}...")
        save_as_js(compiled_data, args.output_data, "allData")
    else:
        print("No evaluation summary files found.")
    
    # Process detailed evaluation data
    evaluations = find_detailed_evaluations(args.folder_path)
    print(f"Found {len(evaluations)} detailed evaluation files")
    
    if evaluations:
        print("Compiling response data...")
        compiled_responses = compile_responses(evaluations)
        print(f"Saving compiled responses to {args.output_responses}...")
        save_as_js(compiled_responses, args.output_responses, "allResponses")
    else:
        print("No detailed evaluation files found.")
    
    print("Done!")

if __name__ == "__main__":
    main()