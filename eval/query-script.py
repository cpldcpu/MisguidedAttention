import argparse
import json
import requests
import os
from tqdm import tqdm

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def query_llm(prompt, llm_config, temperature_override):
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        # print("Using OPENAI_API_KEY instead of OPENROUTER_API_KEY")
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
        "temperature": temperature_override if temperature_override > 0 else llm_config.get("temperature", 0.7),
        "max_tokens": llm_config.get("max_tokens", 1000),
        "top_p": llm_config.get("top_p", 1),
        "frequency_penalty": llm_config.get("frequency_penalty", 0),
        "presence_penalty": llm_config.get("presence_penalty", 0)
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def main(args):
    dataset = load_json(args.dataset)
    config = load_json(args.config)
    output = {"results": []}

    for llm in config["llms"]:
        print(f"Querying {llm['name']}...")
        for prompt in tqdm(dataset["prompts"][:args.limit] if args.limit > 0 else dataset["prompts"]):
            result = {
                "prompt_id": prompt["prompt_id"],
                "prompt": prompt["prompt"],
                "llm": llm["name"],
                "output": []
            }
            
            for _ in range(args.samples):
                if args.debug:
                    print(f"Querying {llm['name']} with prompt: {prompt['prompt']}")
                
                answer = query_llm(prompt["prompt"], llm, args.temp)
                result["output"].append(answer)
            
            output["results"].append(result)

    save_json(output, args.output)
    print(f"Evaluation complete. Results saved to {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate LLMs on a dataset of prompts")
    parser.add_argument("--dataset", default="misguided_attention.json", help="Path to the dataset JSON file")
    parser.add_argument("--output", default="output_queries.json", help="Path to the output JSON file")
    parser.add_argument("--config", default="query_config.json", help="Path to the configuration JSON file")
    parser.add_argument("--samples", type=int, default=1, help="Number of repetitions for each question and LLM")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of prompts to evaluate (0 for no limit)")
    parser.add_argument("--temp", type=float, default=-1, help="Override temperature setting for LLMs (-1 to use config values)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()
    main(args)
