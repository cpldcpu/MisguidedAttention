import json
import requests
import argparse
from collections import defaultdict
from tqdm import tqdm
import os
import warnings
import time

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def make_api_call(messages, api_key, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "",  
                    "X-Title": "MA_Eval"  
                },
                json={
                    "model": "meta-llama/llama-3.3-70b-instruct",
                    "messages": messages,
                    "temperature": 0.0,
                    "max_tokens": 1000
                }
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1 and (
                isinstance(e, requests.exceptions.HTTPError) and 
                e.response is not None and 
                e.response.status_code == 429
            ):
                print(f"Rate limit error, retrying in 2 seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
                continue
            raise
    return None

def run_inference(prompt, sys_prompt, max_depth=5):
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": prompt}
    ]
    
    def recursive_loop(messages, depth):
        if depth >= max_depth:
            print(f"Maximum recursion depth reached ({max_depth}). Stopping recursion.")
            return None
            
        OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")    
        if not OPENROUTER_API_KEY:
            OPENROUTER_API_KEY = os.environ.get("OPENAI_API_KEY")
            if not OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY and OPENAI_API_KEY environment variable not set")

        try:
            response_json = make_api_call(messages, OPENROUTER_API_KEY)
            if not response_json:
                print("Failed after all retry attempts")
                return None

            if 'choices' not in response_json or not response_json['choices']:
                print(f"Invalid API response format: {response_json}")
                return None

            content = response_json['choices'][0]['message']['content']
            content = '{' + content.partition('{')[2].rpartition('}')[0] + '}'

            try:
                json_response = json.loads(content)
                return json_response
            except json.JSONDecodeError:
                print(f"depth:{depth}\n{content}")
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": "The response was not in valid JSON format. Please provide a valid JSON response."})
                return recursive_loop(messages, depth + 1)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    return recursive_loop(messages, 0)

def detect_format_version(data):
    """Detect if the dataset is in v2 format or old format"""
    if any('criteria' in prompt for prompt in data['prompts']):
        return 'v2'
    return 'old'

def convert_old_to_v2(prompt_data):
    """Convert old format to v2 format"""
    warnings.warn("Using old format dataset. Converting to v2 format.")
    return {
        'prompt_id': prompt_data['prompt_id'],
        'criteria': prompt_data['expected_behavior'],
        'weight': [1.0] * len(prompt_data['expected_behavior'])
    }

def generate_evaluation_prompt(output, prompt, criteria, weights):
    return f"""
You are a critical judge that evaluates the output of another LLM. 
Evaluate the following output based on the given prompt and criteria.
Respond only with true or false for each criterion.

Prompt: {prompt}

Output: {output}

Criteria:
{json.dumps(list(zip(criteria, weights)))}

Please return your evaluation in the following JSON format:
{{
  "criteria_results": [
    {{
      "criterion": "string",
      "met": boolean
    }}
  ],
  "feedback": "string"
}}
"""

def calculate_score(evaluation, weights):
    """Calculate weighted score and clip to [0,1]"""
    if not evaluation or 'criteria_results' not in evaluation:
        return 0.0
    
    total_score = sum(
        weight * (1.0 if result['met'] else 0.0)
        for result, weight in zip(evaluation['criteria_results'], weights)
    )
    
    return max(0.0, min(1.0, total_score))

def get_final_answer_QwQ(output):
    final_answer_marker = "**Final Answer"
    idx = output.rfind(final_answer_marker)
    if idx != -1:
        return output[idx:].strip()
    else:
        return output

def evaluate_output(output, prompt, criteria, weights):
    evaluation_prompt = generate_evaluation_prompt(output, prompt, criteria, weights)
    sys_prompt = "You are an AI assistant that evaluates outputs based on specific criteria. Return only true/false values for each criterion."
    return run_inference(evaluation_prompt, sys_prompt)

def main(args):
    output_queries = load_json(args.output_queries)
    dataset = load_json(args.dataset)

    prompt_dict = {prompt['prompt_id']: prompt for prompt in dataset['prompts']}
    results = defaultdict(lambda: defaultdict(list))

    # Filter prompt_ids if limit is set
    if args.limit > 0:
        prompt_ids = list(prompt_dict.keys())[:args.limit]
    else:
        prompt_ids = list(prompt_dict.keys())

    format_version = detect_format_version(dataset)
    
    for entry in tqdm(output_queries['results'], desc="Evaluating outputs"):
        prompt_id = entry['prompt_id']
        if prompt_id not in prompt_ids:
            continue

        llm = entry['llm']
        outputs = entry['output']

        prompt_data = prompt_dict[prompt_id]
        if format_version == 'old':
            prompt_data = convert_old_to_v2(prompt_data)
        
        criteria = prompt_data['criteria']
        weights = prompt_data['weight']

        for output in outputs:
            if args.debug:
                print(f"Evaluating prompt_id: {prompt_id}, LLM: {llm}")
                print(f"Output: {output[:100] if output else 'None'}...")  # Print first 100 characters of output or 'None'

            if output is not None:
                if args.QwQ:
                    output = get_final_answer_QwQ(output)
                
                evaluation = evaluate_output(output, prompt_data['prompt'], criteria, weights)
                if evaluation:
                    score = calculate_score(evaluation, weights)
                    evaluation['total_score'] = score
                    evaluation['original_question'] = prompt_data['prompt']
                    evaluation['original_response'] = output
                    results[prompt_id][llm].append(evaluation)

                if args.debug:
                    print(f"Evaluation: {json.dumps(evaluation, indent=2)}")
                    print("-" * 50)
            else:
                if args.debug:
                    print("Skipping evaluation for None output")
                    print("-" * 50)

    # Summarize statistics
    summary = defaultdict(lambda: defaultdict(dict))
    for prompt_id, llm_results in results.items():
        for llm, evaluations in llm_results.items():
            valid_evaluations = [eval for eval in evaluations if eval]
            num_valid_responses = len(valid_evaluations)
            
            if num_valid_responses == 0:
                continue

            criteria_stats = defaultdict(float)
            total_scores = []

            for eval in valid_evaluations:
                total_scores.append(eval['total_score'])
                for result in eval['criteria_results']:
                    criteria_stats[result['criterion']] += 1.0 if result['met'] else 0.0

            summary[prompt_id][llm] = {
                'average_total_score': sum(total_scores) / num_valid_responses,
                'num_evaluations': num_valid_responses,
                'criteria_stats': {
                    criterion: count / num_valid_responses 
                    for criterion, count in criteria_stats.items()
                }
            }

    # Output results
    save_json(dict(results), 'detailed_evaluations.json')
    save_json(dict(summary), 'evaluation_summary.json')

    print("Evaluation complete. Results saved to detailed_evaluations.json and evaluation_summary.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate LLM outputs for Misguided Attention prompts")
    parser.add_argument("--dataset", default="misguided_attention_v4_long.json", help="Path to the dataset JSON file")
    parser.add_argument("--output_queries", default="output_queries.json", help="Path to the output queries JSON file")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of prompt_ids to process (0 for no limit)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--QwQ", action="store_true", help="Activate final answer extraction")

    args = parser.parse_args()
    main(args)
