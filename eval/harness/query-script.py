import argparse
import json
import requests
import os
import time
import re
from tqdm import tqdm
from datetime import datetime
import google.generativeai as genai

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

def load_cot_data(file_path):
    """Load chain of thought data from a JSON file."""
    if not file_path:
        return {}
    
    with open(file_path, 'r') as f:
        data = json.load(f)
        # Create a mapping of prompt_id to thinking entries
        return {result['prompt_id']: result['thinking'] for result in data['results']}

def extract_thinking_from_response(response_text):
    """
    Extract content within <think></think> tags and return both the thinking content and cleaned response.
    
    Args:
        response_text (str): The full response text that may contain <think> tags
        
    Returns:
        tuple: (cleaned_response, thinking_content)
    """
    if not response_text or '<think>' not in response_text:
        return response_text, None

    # print("---> thinking content found!")
    # print("extracting thinking content...")        

    pattern = re.compile(r'<think>(.*?)</think>', re.DOTALL)
    thinking_segments = pattern.findall(response_text)
    thinking_content = '\n'.join(thinking_segments) if thinking_segments else None
    cleaned_response = pattern.sub('', response_text).strip()

    # print(f"Extracted thinking content: {thinking_content[0:200]}...")  # Print first 200 characters for brevity
    # print(f"Cleaned response: {cleaned_response[:200]}...")  
    return cleaned_response, thinking_content

def query_llm(prompt, llm_config, temperature_override, cot_entry=None, max_retries=3, extract_thinking=False):
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")   
    NOUS_API_KEY = os.environ.get("NOUS_API_KEY")  # Add Nous API key

    if OPENROUTER_API_KEY == None:
        OPENROUTER_API_KEY = OPENAI_API_KEY

    # Construct the prompt with CoT if provided
    prompt_text = f"Please answer the following question: {prompt}\n"
    if cot_entry:
        prompt_text += f"<think>{cot_entry}</think>\n"
    prompt_text += "Answer:"
    
    # Helper function to prepare messages with system prompt if available
    def prepare_messages(prompt_text, llm_config):
        messages = []
        if "system_prompt" in llm_config and llm_config["system_prompt"]:
            messages.append({"role": "system", "content": llm_config["system_prompt"]})
        messages.append({"role": "user", "content": prompt_text})
        return messages

    # Handle Gemini API separately
    if "g3mini" in llm_config["model"].lower():
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(llm_config["model"])
        
        # wait for 6s to avoid rate limiting
        time.sleep(6)
        try:
            response = model.generate_content(
                prompt_text,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature_override if temperature_override > 0 else llm_config.get("temperature", 1.0)
                )
            )
            
            # Process the response to extract <think> tags if requested
            if extract_thinking and response.text:
                cleaned_response, thinking_content = extract_thinking_from_response(response.text)
                return {
                    'content': cleaned_response,
                    'thinking': thinking_content
                }
            return {
                'content': response.text,
                'thinking': None
            }
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    # Determine API endpoint and key based on model
    if "hermes" in llm_config["model"].lower():
        api_key = NOUS_API_KEY
        base_url = "https://inference-api.nousresearch.com/v1/chat/completions"
        if not api_key:
            raise ValueError("NOUS_API_KEY environment variable not set")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        messages = prepare_messages(prompt_text, llm_config)
        # print(f"Prompt: {messages}")
        data = {
            "model": llm_config["model"],
            "messages": messages,
            "temperature": temperature_override if temperature_override > 0 else llm_config.get("temperature", 1.0),
            "max_tokens": llm_config.get("max_tokens", 4000)
        }
    elif "d33pseek" in llm_config["model"].lower():
        api_key = DEEPSEEK_API_KEY    
        base_url = "https://api.deepseek.com/v1/chat/completions"
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        messages = prepare_messages(prompt_text, llm_config)
        
        data = {
            "model": llm_config["model"],
            "messages": messages,
            "temperature": temperature_override if temperature_override > 0 else llm_config.get("temperature", 1.0),
        }
    else:
        api_key = OPENROUTER_API_KEY or OPENAI_API_KEY
        base_url = "https://openrouter.ai/api/v1/chat/completions"
        if not api_key:
            raise ValueError("Neither OPENROUTER_API_KEY nor OPENAI_API_KEY environment variable is set")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "",  # Replace with your site URL
            "X-Title": "MA_Eval"  # Replace with your app name
        }

        messages = prepare_messages(prompt_text, llm_config)

        data = {
            "model": llm_config["model"],
            "messages": messages,
            "temperature": temperature_override if temperature_override > 0 else llm_config.get("temperature", 1.0),
            "max_tokens": llm_config.get("max_tokens", 4000),
            "top_p": llm_config.get("top_p", 1),
            "min_p": llm_config.get("min_p", 0),
            "top_k": llm_config.get("top_k", 0),  # Add top_k parameter with default 0
            "include_reasoning": True,
            "frequency_penalty": llm_config.get("frequency_penalty", 0),
            "presence_penalty": llm_config.get("presence_penalty", 0),
            "provider": {"order": [llm_config.get("provider", "")]} if llm_config.get("provider") else None
        }
    # print(data)
    for attempt in range(max_retries):
        try:
            response = requests.post(
                # "https://openrouter.ai/api/v1/chat/completions",
                # "https://api.deepseek.com/v1/chat/completions",
                base_url,
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
                    print(f"Error received: {error.get('message', 'Unknown API error')}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                print(f"Error from provider after {max_retries} attempts: {error}")
                return None

            # Check for valid response structure
            if 'choices' in response_json and len(response_json['choices']) > 0:
                response_content = response_json['choices'][0]['message']['content']
                thinking_content = None
                
                # Always check for <think> tags in the response content
                if response_content and '<think>' in response_content:
                    cleaned_response, extracted_thinking = extract_thinking_from_response(response_content)
                    response_content = cleaned_response
                    thinking_content = extracted_thinking
                    # print(f"Extracted thinking content: {thinking_content}")
                else:
                    # Fall back to checking other fields if no <think> tags found
                    if 'reasoning' in response_json['choices'][0]['message']:
                        thinking_content = response_json['choices'][0]['message']['reasoning']
                        # print(f"Extracted reasoning: {thinking_content}")
                    elif 'reasoning_content' in response_json['choices'][0]['message']:
                        thinking_content = response_json['choices'][0]['message']['reasoning_content']
                        # print(f"Extracted reasoning content: {thinking_content}")
                    elif 'thinking' in response_json['choices'][0]:
                        thinking_content = response_json['choices'][0]['thinking']
                        # print(f"Extracted thinking: {thinking_content}")
                
                return {
                    'content': response_content,
                    'thinking': thinking_content
                }
            else:
                print(f"Unexpected response format: {response_json}")
                return None

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 2
                print(f"Request failed ({type(e).__name__}): {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Request failed after {max_retries} attempts ({type(e).__name__}): {e}")
                return None

    return None

def main(args):
    config = load_json(args.config)
    output = {"results": []}

    existing_results = load_existing_results()
    prompts = load_prompts(args.dataset)
    results = existing_results.copy()
    processed_count = 0

    # Load CoT data if specified
    cot_data = load_cot_data(args.cotfile)

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
                    "thinking": [],  # New array for thinking tokens
                    "timestamp": datetime.now().isoformat()
                }

                # Get CoT entries for this prompt if available
                cot_entries = cot_data.get(prompt["prompt_id"], []) if cot_data else []
                
                for i in range(args.samples):
                    if args.cotfile:
                        # Verify we have enough CoT entries
                        if i >= len(cot_entries):
                            raise ValueError(f"Not enough CoT entries for prompt {prompt['prompt_id']}. "
                                          f"Need {args.samples}, but only have {len(cot_entries)}")
                        cot_entry = cot_entries[i]
                    else:
                        cot_entry = None

                    if args.debug:
                        print(f"Querying {llm['name']} with prompt: {prompt['prompt']}")
                        if cot_entry:
                            print(f"Using CoT entry: {cot_entry[:200]}...")

                    response = query_llm(prompt["prompt"], llm, args.temp, cot_entry, args.max_retries, args.think)
                    if response is None:
                        print(f"Failed to get response for prompt {prompt['prompt_id']}")
                        result["output"].append(None)
                        result["thinking"].append(None)
                    else:
                        if args.debug:
                            print(f"Answer: ...{response['content'][:200]}")
                            if response['thinking']:
                                print(f"Thinking: ...{response['thinking'][:200]}")

                        result["output"].append(response['content'])
                        result["thinking"].append(response['thinking'])
                
                results[result_key] = result
                processed_count += 1
                
                # Save every three processed queries
                if processed_count % 3 == 0:
                    save_json({"results": list(results.values())}, args.output)
                    print(f"Saved after processing {processed_count} queries")
                
                print(f"Processed prompt: {prompt['prompt_id']}")
            else:
                print(f"Skipping already processed prompt: {prompt['prompt_id']}")

    # Final save
    save_json({"results": list(results.values())}, args.output)
    print(f"Query complete. Results saved to {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate LLMs on a dataset of prompts")
    parser.add_argument("--dataset", default="misguided_attention_v4_long.json", help="Path to the dataset JSON file")
    parser.add_argument("--output", default="output_queries.json", help="Path to the output JSON file. Existing results will be loaded and new results are appended to this file")
    parser.add_argument("--config", default="query_config.json", help="Path to the configuration JSON file")
    parser.add_argument("--samples", type=int, default=1, help="Number of repetitions for each question and LLM")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of prompts to evaluate (0 for no limit)")
    parser.add_argument("--temp", type=float, default=-1, help="Override temperature setting for LLMs (-1 to use config values)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--max-retries", type=int, default=8, help="Maximum number of retries for failed requests")
    parser.add_argument("--cotfile", help="Path to the Chain of Thought input JSON file")
    parser.add_argument("--think", action="store_true", help="Extract content within <think> tags as thinking content")

    args = parser.parse_args()
    main(args)
