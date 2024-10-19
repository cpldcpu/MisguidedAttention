import json
import requests
import argparse
from collections import defaultdict
from tqdm import tqdm
import os

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

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
        # OPENROUTER_API_KEY = os.environ.get("Path")
        if not OPENROUTER_API_KEY:
            # print("Using OPENAI_API_KEY instead of OPENROUTER_API_KEY")
            OPENROUTER_API_KEY = os.environ.get("OPENAI_API_KEY")
            if not OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY and OPENAI_API_KEY environment variable not set")

        response = requests.post(
            # "http://localhost:1234/v1/chat/completions",
            "https://openrouter.ai/api/v1/chat/completions",

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "",  # Replace with your site URL
                "X-Title": "MA_Eval"  # Replace with your app name
            },
            json={
                "model": "meta-llama/llama-3.1-70b-instruct",
                # "model": "anthropic/claude-3.5-sonnet",  # careful, if model keyword missing, openrouter defaults to 4o
                "messages": messages,
                "temperature": 0.0,
                "max_tokens": 1000
            }
        )

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            # content = '{' + content.partition('{')[2]  
            content = '{' + content.partition('{')[2].rpartition('}')[0] + '}' # llama 3.1 tends to attach text before and after the JSON response
            try:
                json_response = json.loads(content)
                return json_response
            except json.JSONDecodeError:
                print(f"depth:{depth}\n{content}")
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": "The response was not in valid JSON format. Please provide a valid JSON response."})
                return recursive_loop(messages, depth + 1)
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    return recursive_loop(messages, 0)

def generate_evaluation_prompt(output, prompt, expected_behavior, common_mistakes):
    return f"""
You are a critical judge the evaluates the output of another LLM. Evaluate the following output based on the given prompt, expected behavior, and common mistakes. Do only judge the outcome, not the discussion itself.

Provide your evaluation in JSON format.

Prompt: {prompt}

Output: {output}

Expected Behavior:
{json.dumps(expected_behavior)}

Common Mistakes:
{json.dumps(common_mistakes)}

Analyze the output and determine if it meets each expected behavior and if it falls into any of the common mistakes. For each item, provide a boolean value (true or false) and a brief comment explaining your evaluation.

Please return your evaluation in the following JSON format:
{{
  "expected_behavior": [
    {{
      "behavior": "string",
      "met": boolean,
      "comment": "string"
    }}
  ],
  "common_mistakes": [
    {{
      "mistake": "string",
      "made": boolean,
      "comment": "string"
    }}
  ],
  "overall_score": number,
  "overall_comment": "string"
}}

The overall_score should be on a scale of 1 to 5, where 1 is completely incorrect and 5 is perfectly correct.

Evaluation:
"""

def evaluate_output(output, prompt, expected_behavior, common_mistakes):
    evaluation_prompt = generate_evaluation_prompt(output, prompt, expected_behavior, common_mistakes)
    sys_prompt = "You are an AI assistant tasked with evaluating the output of language models based on specific criteria. You must return your evaluation in JSON format."
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

    for entry in tqdm(output_queries['results'], desc="Evaluating outputs"):
        prompt_id = entry['prompt_id']
        if prompt_id not in prompt_ids:
            continue

        llm = entry['llm']
        outputs = entry['output']

        prompt_data = prompt_dict[prompt_id]
        expected_behavior = prompt_data['expected_behavior']
        common_mistakes = prompt_data['common_mistakes']

        for output in outputs:
            if args.debug:
                print(f"Evaluating prompt_id: {prompt_id}, LLM: {llm}")
                print(f"Output: {output[:100] if output else 'None'}...")  # Print first 100 characters of output or 'None'

            if output is not None:
                evaluation = evaluate_output(output, prompt_data['prompt'], expected_behavior, common_mistakes)
                if evaluation:
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
            scores = [eval['overall_score'] for eval in valid_evaluations]
            num_valid_responses = len(scores)
            
            summary[prompt_id][llm] = {
                'average_score': sum(scores) / num_valid_responses if num_valid_responses > 0 else 0,
                'num_evaluations': num_valid_responses,
                'expected_behavior_stats': defaultdict(float),
                'common_mistakes_stats': defaultdict(float)
            }
            
            for eval in valid_evaluations:
                for behavior in eval['expected_behavior']:
                    if behavior['met']:
                        summary[prompt_id][llm]['expected_behavior_stats'][behavior['behavior']] += 1
                
                for mistake in eval['common_mistakes']:
                    if mistake['made']:
                        summary[prompt_id][llm]['common_mistakes_stats'][mistake['mistake']] += 1
            
            # Calculate probabilities
            for behavior in summary[prompt_id][llm]['expected_behavior_stats']:
                summary[prompt_id][llm]['expected_behavior_stats'][behavior] /= num_valid_responses
            
            for mistake in summary[prompt_id][llm]['common_mistakes_stats']:
                summary[prompt_id][llm]['common_mistakes_stats'][mistake] /= num_valid_responses

    # Output results
    save_json(dict(results), 'detailed_evaluations.json')
    save_json(dict(summary), 'evaluation_summary.json')

    print("Evaluation complete. Results saved to detailed_evaluations.json and evaluation_summary.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate LLM outputs for Misguided Attention prompts")
    parser.add_argument("--dataset", default="misguided_attention.json", help="Path to the dataset JSON file")
    parser.add_argument("--output_queries", default="output_queries.json", help="Path to the output queries JSON file")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of prompt_ids to process (0 for no limit)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()
    main(args)
