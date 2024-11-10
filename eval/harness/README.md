
# Evaluation Scripts

These are scripts that were used to evaluate the LLMs on the Misguided Attention prompts. They were custom created (mostly by sonnet) and do not necessarily represent best practices. Use with caution.

## How to use the evaluation script

The evaluation consists of three steps:

1. **Query the LLMs** using [query-script.py](query-script.py)
2. **Evaluate the responses** using [Evaluation-script.py](evaluation-script.py)
3.  **Visualize the data** as bar plots in pdf with the [summary-script.py](summary-script.py) as heat maps with the [heatmap-script.py](heatmap-script.py)
  
## Querying LLMs

First, set up your environment:
1. Set either `OPENROUTER_API_KEY` or `OPENAI_API_KEY` as environment variable
2. Configure your LLMs in [query_config.json](query_config.json)

The scrip will:

* Load prompts from the dataset file
* Query configured LLMs
* Save responses to the output file

Usage:

```bash
python query-script.py [options]

Options:

--dataset: Prompt dataset path (default: "misguided_attention.json")
--config: LLM configuration path (default: "query_config.json")
--output: Output file path (default: "output_queries.json")
--samples: Number of responses per prompt (default: 1)
--limit: Maximum prompts to evaluate (default: 0 = no limit)
--temp: Override temperature setting (default: -1 = use config)
--debug: Enable debug output

Example:

python query-script.py --samples 5 --limit 1 --debug
```

## Evaluating Responses

Run the evaluation script to analyze LLM responses.
Note that this will query an LLM via the Openroute API
to evaluate the responses from the response file. The LLM
to use as a judge is defined in the source. Currently Gemini-Flash is used.

The script will:

 - Load query responses from the output file
 - Compare responses against expected behaviors
 - Generate evaluation metrics
 - Save evaluation results to output file

Usage:

```bash
python evaluation-script.py [options]

Options:

--queries: Path to query results JSON (default: "output_queries.json")
--dataset: Original prompt dataset (default: "misguided_attention.json")
--output: Output file for evaluation (default: "output_eval.json")
--debug: Enable debug output
```
### Visualizing the data

Use the [summary-script.py](summary-script.py) to create a PDF report or the[heatmap-script.py](heatmap-script.py) to create heatmaps of the evaluation results. Note thate the heatmap script will process all the `evaluation_summary` files in the given folder. Refer to the help function for details.