// models.js
const modelInfo = {
  "o4-mini-high-long": {
    "model_type": "reasoning",
    "lab": "openai",
    "max_tokens": 30000
  },
  "llama-3.1-405b-instruct": {
    "model_type": "flagship",
    "lab": "meta-llama",
    "max_tokens": 2000
  },
  "hermes-3-llama-3.1-405": {
    "model_type": "flagship",
    "lab": "nousresearch"
  },
  "claude-2.1": {
    "model_type": "flagship",
    "lab": "anthropic"
  },
  "claude-3-sonnet": {
    "model_type": "flagship",
    "lab": "anthropic"
  },
  "claude-3.5-sonnet": {
    "model_type": "flagship",
    "lab": "anthropic"
  },
  "gpt-4o": {
    "model_type": "flagship",
    "lab": "openai"
  },
  "gemini-pro-1.5": {
    "model_type": "flagship",
    "lab": "google"
  },
  "grok-2": {
    "model_type": "flagship",
    "lab": "x-ai"
  },
  "mistral-large": {
    "model_type": "flagship",
    "lab": "mistralai"
  },
  "gpt-4-32k": {
    "model_type": "flagship",
    "lab": "openai"
  },
  "claude-3-opus": {
    "model_type": "flagship",
    "lab": "anthropic"
  },
  "claude-3.5-sonnet-new": {
    "model_type": "flagship",
    "lab": "anthropic"
  },
  "gpt-4o-2024-11-20": {
    "model_type": "flagship",
    "lab": "openai"
  },
  "DeepSeek-V3-OR": {
    "model_type": "flagship",
    "lab": "deepseek"
  },
  "DeepSeek-V3": {
    "model_type": "flagship",
    "lab": "deepseek"
  },
  "grok-2-1212": {
    "model_type": "flagship",
    "lab": "x-ai"
  },
  "minimax-01": {
    "model_type": "flagship",
    "lab": "minimax",
    "max_tokens": 2000
  },
  "gemini-exp-1206": {
    "model_type": "flagship",
    "lab": "gemini",
    "max_tokens": 2000
  },
  "qwen-max": {
    "model_type": "flagship",
    "lab": "qwen",
    "max_tokens": 2000
  },
  "gemini-2.0-pro-exp-02-05": {
    "model_type": "flagship",
    "lab": "gemini",
    "max_tokens": 2000
  },
  "claude-3.7-sonnet": {
    "model_type": "flagship",
    "lab": "anthropic"
  },
  "gpt-4o-20250129": {
    "model_type": "flagship",
    "lab": "openai"
  },
  "jamba-1.6-large": {
    "model_type": "flagship",
    "lab": "ai21",
    "max_tokens": 4000
  },
  "deepseek-chat-v3-0324": {
    "model_type": "flagship",
    "lab": "deepseek",
    "max_tokens": 4000
  },
  "quasar-alpha": {
    "model_type": "flagship",
    "lab": "openrouter",
    "max_tokens": 8000
  },
  "llama-4-maverick": {
    "model_type": "flagship",
    "lab": "meta-llama",
    "max_tokens": 5000
  },
  "grok-3-beta": {
    "model_type": "flagship",
    "lab": "x-ai",
    "max_tokens": 4000
  },
  "optimus-alpha": {
    "model_type": "flagship",
    "lab": "openrouter",
    "max_tokens": 8192
  },
  "gpt-4.1": {
    "model_type": "flagship",
    "lab": "openai",
    "max_tokens": 4999
  },
  "qwen3-235b-a22b-nothink": {
    "model_type": "flagship",
    "lab": "qwen",
    "max_tokens": 4000
  },
  "claude-sonnet-4": {
    "model_type": "flagship",
    "lab": "anthropic"
  },
  "claude-opus-4": {
    "model_type": "flagship",
    "lab": "anthropic"
  },
  "Hermes-3-Llama-3.1-70B": {
    "model_type": "midrange",
    "lab": "Hermes",
    "max_tokens": 5000
  },
  "gpt-3.5-turbo": {
    "model_type": "midrange",
    "lab": "openai"
  },
  "claude-3-haiku": {
    "model_type": "midrange",
    "lab": "anthropic"
  },
  "gpt-4o-mini": {
    "model_type": "midrange",
    "lab": "openai"
  },
  "gemini-flash-1.5": {
    "model_type": "midrange",
    "lab": "google"
  },
  "llama-3.1-70b-instruct": {
    "model_type": "midrange",
    "lab": "meta-llama",
    "max_tokens": 2000
  },
  "qwen-2.5-72b-instruct": {
    "model_type": "midrange",
    "lab": "qwen",
    "max_tokens": 2000
  },
  "qwen-2.5-72b-instruct-241116": {
    "model_type": "midrange",
    "lab": "qwen",
    "max_tokens": 2000
  },
  "llama-3.1-nemotron-70b-instruct": {
    "model_type": "midrange",
    "lab": "nvidia"
  },
  "mixtral-8x22b-instruct": {
    "model_type": "midrange",
    "lab": "mistralai",
    "max_tokens": 4000
  },
  "dolphin-mixtral-8x22b": {
    "model_type": "midrange",
    "lab": "cognitivecomputations"
  },
  "wizardlm-2-8x22b": {
    "model_type": "midrange",
    "lab": "microsoft"
  },
  "gpt-4-turbo": {
    "model_type": "midrange",
    "lab": "openai"
  },
  "gemini-2.0-flash-exp": {
    "model_type": "midrange",
    "lab": "google"
  },
  "llama-3.3-70b-instruct": {
    "model_type": "midrange",
    "lab": "meta-llama",
    "max_tokens": 2000
  },
  "gemini-2.0-flash": {
    "model_type": "midrange",
    "lab": "gemini",
    "max_tokens": 2000
  },
  "gemma-3-27b": {
    "model_type": "midrange",
    "lab": "google",
    "max_tokens": 4000
  },
  "mistral-small-3": {
    "model_type": "midrange",
    "lab": "mistral",
    "max_tokens": 2000
  },
  "command-a-03-2025": {
    "model_type": "midrange",
    "lab": "cohere",
    "max_tokens": 4000
  },
  "olmo-2-0325-32b": {
    "model_type": "midrange",
    "lab": "allenai",
    "max_tokens": 4000
  },
  "mistral-small-3.1-2503": {
    "model_type": "midrange",
    "lab": "mistralai",
    "max_tokens": 2000
  },
  "llama-4-scout": {
    "model_type": "midrange",
    "lab": "meta-llama",
    "max_tokens": 5000
  },
  "gpt-4.1-mini": {
    "model_type": "midrange",
    "lab": "openai",
    "max_tokens": 4999
  },
  "gpt-4.1-nano": {
    "model_type": "midrange",
    "lab": "openai",
    "max_tokens": 4999
  },
  "qwen3-30b-a3b-nothink": {
    "model_type": "midrange",
    "lab": "qwen",
    "max_tokens": 4000
  },
  "mistral-medium-3": {
    "model_type": "midrange",
    "lab": "mistralai",
    "max_tokens": 50000
  },
  "gemini-2.5-flash-preview-05-20": {
    "model_type": "midrange",
    "lab": "google",
    "max_tokens": 30000
  },
  "o1-preview": {
    "model_type": "reasoning",
    "lab": "openai",
    "max_tokens": 4000
  },
  "o1-mini": {
    "model_type": "reasoning",
    "lab": "openai",
    "max_tokens": 4000
  },
  "QwQ-32B-Preview-Q4_K_M": {
    "model_type": "reasoning",
    "lab": "unknown",
    "max_tokens": 4000
  },
  "gemini-2.0-flash-thinking-exp": {
    "model_type": "reasoning",
    "lab": "google"
  },
  "o1": {
    "model_type": "reasoning",
    "lab": "unknown",
    "max_tokens": 4000
  },
  "deepseek-r1": {
    "model_type": "reasoning",
    "lab": "deepseek",
    "max_tokens": 16000
  },
  "DeepSeek-R1-Lite-Preview": {
    "model_type": "reasoning",
    "lab": "deepseek",
    "max_tokens": 4000
  },
  "deepseek-r1-distill-llama-70b": {
    "model_type": "reasoning",
    "lab": "deepseek"
  },
  "o3-mini": {
    "model_type": "reasoning",
    "lab": "openai",
    "max_tokens": 8000
  },
  "claude-3.7-thinking-4k": {
    "model_type": "reasoning",
    "lab": "anthropic",
    "max_tokens": 4096
  },
  "QwQ-32b": {
    "model_type": "reasoning",
    "lab": "qwen",
    "max_tokens": 32000
  },
  "gemini-2.5-pro-preview-03-25": {
    "model_type": "reasoning",
    "lab": "google",
    "max_tokens": 50000
  },
  "grok-3-mini-beta-think": {
    "model_type": "reasoning",
    "lab": "x-ai",
    "max_tokens": 16000
  },
  "ll3.1-nemotron-253b-v1-thk": {
    "model_type": "reasoning",
    "lab": "nvidia",
    "max_tokens": 4096
  },
  "DeepHermes-3-Mistral-24B-Pre": {
    "model_type": "reasoning",
    "lab": "DeepHermes",
    "max_tokens": 20000
  },
  "o4-mini-high": {
    "model_type": "reasoning",
    "lab": "openai",
    "max_tokens": 16000
  },
  "glm-z1-32b": {
    "model_type": "reasoning",
    "lab": "thudm",
    "max_tokens": 16000
  },
  "ll3.3-nemotron-49b-v1-thk": {
    "model_type": "reasoning",
    "lab": "nvidia",
    "max_tokens": 4096
  },
  "qwen3-235b-a22b-think": {
    "model_type": "reasoning",
    "lab": "qwen",
    "max_tokens": 30000
  },
  "qwen3-30b-a3b-think": {
    "model_type": "reasoning",
    "lab": "qwen",
    "max_tokens": 30000
  },
  "phi-4-reasoning-plus": {
    "model_type": "reasoning",
    "lab": "microsoft",
    "max_tokens": 30000
  },
  "gemini-2.5-flash-preview-05-20:thinking": {
    "model_type": "reasoning",
    "lab": "google",
    "max_tokens": 30000
  },
  "deepseek-r1-0528": {
    "model_type": "reasoning",
    "lab": "deepseek",
    "max_tokens": 16000
  },
  "gemini-2.5-pro-preview-05-06": {
    "model_type": "reasoning",
    "lab": "google",
    "max_tokens": 50000
  },
  "gemini-2.5-pro-release": {
    "model_type": "reasoning",
    "lab": "google",
    "max_tokens": 50000
  },
  "magistral-medium-2506-thinking": {
    "model_type": "reasoning",
    "lab": "mistralai",
    "max_tokens": 40000
  },
  "gemini-2.5-pro-low": {
    "model_type": "reasoning",
    "lab": "google",
    "max_tokens": 30000
  },
  "gemini-2.5-pro-high": {
    "model_type": "reasoning",
    "lab": "google",
    "max_tokens": 30000
  },
  "claude-4-sonnet-0522-thinking": {
    "model_type": "reasoning",
    "lab": "anthropic",
    "max_tokens": 30000
  },
  "gemini-2.5-flash-high": {
    "model_type": "reasoning",
    "lab": "google",
    "max_tokens": 30000
  },
  "grok-3-mini-think": {
    "model_type": "reasoning",
    "lab": "x-ai",
    "max_tokens": 30000
  },
  "mistral-7b-instruct-v0.3": {
    "model_type": "small",
    "lab": "mistralai"
  },
  "ministral-8b": {
    "model_type": "small",
    "lab": "mistralai"
  },
  "ministral-3b": {
    "model_type": "small",
    "lab": "mistralai"
  },
  "llama-3.1-8b-instruct": {
    "model_type": "small",
    "lab": "meta-llama"
  },
  "llama-3.2-3b-instruct": {
    "model_type": "small",
    "lab": "meta-llama"
  },
  "llama-3.2-1b-instruct": {
    "model_type": "small",
    "lab": "meta-llama"
  },
  "qwen-2.5-7b-instruct": {
    "model_type": "small",
    "lab": "qwen"
  },
  "lfm-7b": {
    "model_type": "small",
    "lab": "liquid"
  },
  "gemma-3n-e4b-it": {
    "model_type": "small",
    "lab": "google",
    "max_tokens": 30000
  }
};
