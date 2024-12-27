import argparse
import json
import os
import glob

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def extract_llm_results(directory, llm_name):
    # Find all output_*.json files in the directory
    json_files = glob.glob(os.path.join(directory, "output_*.json"))
    
    # Combined results dictionary
    combined_results = {"results": []}
    
    # Process each file
    for file_path in json_files:
        try:
            data = load_json(file_path)
            # Extract entries where llm matches llm_name
            matching_results = [r for r in data.get("results", []) if r.get("llm") == llm_name]
            combined_results["results"].extend(matching_results)
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue
    
    return combined_results

def extract_llm_evaluations(directory, llm_name):
    # Find all detailed_evaluations_*.json files in the directory
    json_files = glob.glob(os.path.join(directory, "detailed_evaluations_*.json"))
    
    # Combined results dictionary
    combined_results = {}
    
    # Process each file
    for file_path in json_files:
        try:
            data = load_json(file_path)
            # For each problem type in the file
            for problem_type, evaluations in data.items():
                if llm_name in evaluations:
                    if problem_type not in combined_results:
                        combined_results[problem_type] = {}
                    combined_results[problem_type] = evaluations[llm_name]
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue
    
    return combined_results

def extract_llm_summaries(directory, llm_name):
    # Find all evaluation_summary_*.json files in the directory
    json_files = glob.glob(os.path.join(directory, "evaluation_summary_*.json"))
    
    # Combined results dictionary
    combined_results = {}
    
    # Process each file
    for file_path in json_files:
        try:
            data = load_json(file_path)
            # For each problem type in the file
            for problem_type, evaluations in data.items():
                if llm_name in evaluations:
                    # Only create entry if LLM data exists
                    if problem_type not in combined_results:
                        combined_results[problem_type] = {}
                    combined_results[problem_type] = {llm_name: evaluations[llm_name]}
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue
    
    return combined_results

def main():
    parser = argparse.ArgumentParser(description="Extract results for specific LLM from output files")
    parser.add_argument("--llm", required=True, help="Name of the LLM to extract")
    parser.add_argument("--dir", required=True, help="Directory containing output files")
    
    args = parser.parse_args()
    
    # Set output filenames
    queries_output = f"output_queries_{args.llm}.json"
    evaluations_output = f"detailed_evaluations_{args.llm}.json"
    summaries_output = f"evaluation_summary_{args.llm}.json"
    
    # Extract results for each file type
    queries_results = extract_llm_results(args.dir, args.llm)
    evaluation_results = extract_llm_evaluations(args.dir, args.llm)
    summary_results = extract_llm_summaries(args.dir, args.llm)
    
    # Save to output files
    save_json(queries_results, queries_output)
    save_json(evaluation_results, evaluations_output)
    save_json(summary_results, summaries_output)
    
    print(f"Extracted {len(queries_results['results'])} query results for {args.llm}")
    print(f"Extracted evaluations for {len(evaluation_results)} problems")
    print(f"Extracted summaries for {len(summary_results)} problems")
    print(f"Results saved to:")
    print(f"  - {queries_output}")
    print(f"  - {evaluations_output}")
    print(f"  - {summaries_output}")

if __name__ == "__main__":
    main()
