import argparse
import json
import requests
import os
import time
from tqdm import tqdm
from datetime import datetime

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_existing_results():
    if os.path.exists('output_queries.json'):
        with open('output_queries.json', 'r') as f:
            existing_data = json.load(f)
            # Create a dict for faster lookup
            return {(r['prompt_id'], r['llm']): r for r in existing_data['results']}
    return {}

def load_prompts(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data['prompts']

def query_llm(prompt, llm_config, temperature_override, max_retries=3):
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        OPENROUTER_API_KEY = os.environ.get("OPENAI_API_KEY")
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY and OPENAI_API_KEY environment variable not set")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "",  # Replace with your site URL
        "X-Title": "MA_Eval"  # Replace with your app name
    }

    data = {
        "model": llm_config["model"],
        "messages": [{"role": "user", "content": f"Please answer the following question: {prompt}\nAnswer:"}],
        "temperature": temperature_override if temperature_override > 0 else llm_config.get("temperature", 1.0),
        "max_tokens": llm_config.get("max_tokens", 4000),
        "top_p": llm_config.get("top_p", 1),
        "frequency_penalty": llm_config.get("frequency_penalty", 0),
        "presence_penalty": llm_config.get("presence_penalty", 0)
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            response_json = response.json()

            # Check for error in response
            if 'error' in response_json:
                error = response_json['error']
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2  # Exponential backoff
                    print(f"Error received. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                print(f"Error from provider: {error}")
                return None

            # Check for valid response structure
            if 'choices' in response_json and len(response_json['choices']) > 0:
                return response_json['choices'][0]['message']['content']
            else:
                print(f"Unexpected response format: {response_json}")
                return None

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 2
                print(f"Request failed: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Request failed after {max_retries} attempts: {e}")
                return None

    return None

def main(args):
    config = load_json(args.config)
    output = {"results": []}

    existing_results = load_existing_results()
    prompts = load_prompts(args.dataset)
    results = existing_results.copy()

    for llm in config["llms"]:
        print(f"Querying {llm['name']}...")
        for prompt in tqdm(prompts[:args.limit] if args.limit > 0 else prompts):
            result_key = (prompt["prompt_id"], llm["name"])
            if result_key not in results:
                result = {
                    "prompt_id": prompt["prompt_id"],
                    "prompt": prompt["prompt"],
                    "llm": llm["name"],
                    "output": [],
                    "timestamp": datetime.now().isoformat()
                }
                
                for _ in range(args.samples):
                    if args.debug:
                        print(f"Querying {llm['name']} with prompt: {prompt['prompt']}")
                    
                    answer = query_llm(prompt["prompt"], llm, args.temp, args.max_retries)
                    if answer is None:
                        print(f"Failed to get response for prompt {prompt['prompt_id']}")
                    if args.debug:
                        print(f"Answer: {answer}")

                    result["output"].append(answer)
                
                results[result_key] = result
                save_json({"results": list(results.values())}, args.output)
                print(f"Processed prompt: {prompt['prompt_id']}")
            else:
                print(f"Skipping already processed prompt: {prompt['prompt_id']}")

    save_json({"results": list(results.values())}, args.output)
    print(f"Query complete. Results saved to {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate LLMs on a dataset of prompts")
    parser.add_argument("--dataset", default="misguided_attention_v4.json", help="Path to the dataset JSON file")
    parser.add_argument("--output", default="output_queries.json", help="Path to the output JSON file. Existing results will be loaded and new results are appended to this file")
    parser.add_argument("--config", default="query_config.json", help="Path to the configuration JSON file")
    parser.add_argument("--samples", type=int, default=1, help="Number of repetitions for each question and LLM")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of prompts to evaluate (0 for no limit)")
    parser.add_argument("--temp", type=float, default=-1, help="Override temperature setting for LLMs (-1 to use config values)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--max-retries", type=int, default=8, help="Maximum number of retries for failed requests")

    args = parser.parse_args()
    main(args)
