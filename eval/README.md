# Evaluation Update for v0.3 *update in progress*

This folder contains code for and results of evaluating various Large Language Models (LLMs) on a [subset of 13 prompts](prompts.md) from the Misguided Attention prompt list. Starting with v0.3 I also curated a longer benchmark with 52 prompts as the old one is beginning to be saturated by reasoning models. Preliminary results are shown below and more results will be added over time

The evaluation is performed by directly prompting the model without any guiding examples (zero shot) at their default temperature via the API. Typically 5 results were sampled for each prompt (3 for the long dataset). For v0.3 I changed the evaluation strategy to reduce the influence of "opinionated" judge models (See [Findings and issues encountered](#findings-and-issues-encountered) for more details).

## Results 52 Question (long) Eval

The heatmap below shows initial results for the long evaluation with 52 questions. We can see that reasoning models score better also in the long benchmark.

![bar chartl](./summaries/barchart_long_eval.png)

![Long eval](./summaries/heatmap_long.png)

## Results 12 Question (short) Eval

The results were summarized in a heatmap. Scores range from 0.0 to 1.0, where 1.0 indicates consistent expected behavior across all trials, and 0.0 indicates consistent failure to produce expected behavior. The rightmost column displays each model's mean performance score across all test cases.

Below you can find a summary of current flagship models, midrange models, and small models. 

### Flagship models
Large models perform quite well in this benchmark, although there are some surprising outlier. The good performance of GPT-4-32k is quite remarkable and can be partially attributed to the fact that it is less prone to "list writing" than later models. The model is also speculated to be much larger than the later, distilled, derivate models like gpt-4o. The distillation process possibly removed some weaker features of the model.

"Newsonnet" is doing quite well even without a system prompt. Curiously, in [Oct 2024 Anthropic added a new paragraph to the 3.5-Sonnet system prompt](https://docs.anthropic.com/en/release-notes/system-prompts#oct-22nd-2024) that may address this eval *"If Claude is shown a familiar puzzle, it writes out the puzzle’s constraints explicitly stated in the message, quoting the human’s message to support the existence of each constraint. Sometimes Claude can accidentally overlook minor changes to well-known puzzles and get them wrong as a result."* I have to mention that using the system prompt does not improve the score too much 😀

![Flagship models](./summaries/heatmap_flagship.png)

### Midrange models
As expected, the performance of mid-range models is worse than that of the flagship models. Flash-1.5 performs well, because it seems to be finetuned to be more "skeptical" and will hence call out impossible prompts.

![Midrange models](./summaries/heatmap_midrange.png)

### Small models
Generally, small models are very sensitive to overfitting and perform badly in this benchmark. Due to smaller number of heads and lower embedding size they can focus on fewer features at a time. Qwen-2.5-72b is an exception and performs quite well.

![Small models](./summaries/heatmap_small.png)

### Reasoning models

Due to limited availability of many of these models in an API I had to manually run the evaluation in a web interface. This means that most of the models used a system prompt. (Exceptions: o1-mini, QwQ)

Reasoning models are able to iterate on the problems and inherently introduce chain-of-thought reasoning before providing an answer. This allows them to perform much better in this benchmark. However, there are still some problems that create such a strong attractor that even many iterations do not allow the models to solve the prompt correctly. 

One particularity critical corner case are problems that are impossible to solve (e.g. "rope_burning_impossible" and the "jugs_4_liters"). Most of the current generation of reasoning models is not able to identify these cases and draw the correct conclusion. One notable exception is o1 which is close to solving all prompts. This is a notable improvement over o1-preview, which still struggled with "rope_burning_impossible". [See log here](https://chatgpt.com/share/66e951e2-d7a8-8010-8a3d-041fa1b1eabe).

The exceptionally good performance of QwQ-32B-Preview is quite remarkable given its small size - I actually ran this eval locally on a RTX3090.

![Reasoning models](./summaries/heatmap_reasoning.png)


## Updates

**Update 2024-11-16**
I reran the evaluation for Qwen-2.5-72b after noticing that it suddenly was able to solved the inverse monty hall problem, which is pretty remarkable as only o1 and o1-mini were able to solve it consistently before. The new results are included in the heatmap above and show a considerable improvement compare to the first eval of Qwen-2.5-72b  from mid of October '24. What did change? Not sure. Possibly some settings on the provider side were modified? FP8 vs FP16?

**Update 2024-12-27**
- Reasoning models were split into a separate category and folder.
- Added DeepSeek V3 evaluation results.
- Added more explanations

**Update 2025-01-06**
- Release of v0.3 evaluation harness

## How to run the evaluation

Due to limited availability of evaluation frameworks with llm-as-a-judge and some issues specific to this dataset (see below), I came up with my own simple framework.

The evaluation scripts can be found in the [`harness`](./harness) folder. Check out the [readme](./harness/README.md) for more information.


## Findings and issues encountered

One key issue with using an LLM as a judge is that the model can be opinionated and provide answers that are not necessarily correct. This occurs when the judge model falls victim to overfitting while the evaluated model does not. One issue in v0.2 was that I used contrasting evaluation questions which inadvertently communicated to the judge model which answers were deemed "correct" versus incorrect.

To better understand the judge model's decision-making process, I enabled output comments for each evaluation. In addition to criteria-specific comments, I also requested overall comments and a "vibe score" to capture the model's general assessment.

Below is an example from the v0.2 evaluation where Claude Sonnet was used as a judge model to evaluate the "inverse Monty Hall problem". Keep in mind that this variant, due to its inverted nature, has the opposite solution compared to the regular problem.

```json
"expected_behavior": [
    {
    "behavior": "Answer suggests to keep the existing door",
    "met": false,
    "comment": "The output incorrectly suggests keeping the initial choice, which is opposite to the correct strategy."
    }
],
"common_mistakes": [
    {
    "mistake": "Answer suggests to switch the door",
    "made": false,
    "comment": "The output does not suggest switching doors, which would have been the correct strategy."
    },
    {
    "mistake": "Answer explains that the initial choice has a 2/3 chance of choosing a donkey",
    "made": false,
    "comment": "The output correctly states that there's a 1/3 chance of initially choosing the donkey."
    },
    {
    "mistake": "Answer does not explain that the initial choice has a 2/3 chance of winning a car",
    "made": true,
    "comment": "The output incorrectly states that staying with the initial choice gives a 2/3 chance of winning, which is the opposite of the correct probability."
    }
],
"overall_score": 1,
"overall_comment": "The output completely misunderstands the Monty Hall problem, providing the opposite of the correct strategy. It fails to recognize that switching doors is the optimal choice, giving a 2/3 chance of winning, while staying with the initial choice only provides a 1/3 chance. This fundamental misunderstanding leads to an entirely incorrect explanation and conclusion.", ...
"original_response": "To maximize your chances of winning a luxury car in this scenario, **you should keep your initial choice**. Here's a detailed explanation of why staying with your original selection is the optimal strategy:\n\n### Breakdown of the Situation\n\n1. **Initial Setup:**\n...
```

We can see that Sonnet does not "believe" the given solution is correct and defiantly claims the answer to be false even though it meets the criteria. *"The output completely misunderstands the Monty Hall problem..."* well, yes. This was pretty hilarious for the first few times, but required me to manually correct responses for many prompts. This effect could be seen for many prompt and was usually more pronounced for smaller models.

### Changes in v0.3

To reduce this issue, I decided to remove the contrasting questions and instead used only neutral questions that did not suggest that an answer was right or wrong. In addition I introduced weighting to scores, so that "quality" questions could be added that did not contribute the to the overall score. These changes did significantly reduce the influence of the judge model on the final score. After testing various options, I found Phi-4 and llama-3.3-70b to be suitable judge models, ultimately selecting the latter for the evaluation.

Here's an example of the neutral criteria used for the inverse Monty Hall problem:

```json
"prompt_id": "monty_hall_inverse",
"category": "Logic Puzzle",
"type" : "modification",
"title": "Inverse Monty Hall Problem",
"prompt": "You're on a game show and are presented with three doors. Behind one is a donkey, and behind the other two are luxury cars. You pick one, but before you can open it the host opens one of the others revealing a luxury car. He then offers you the choice of keeping your existing door or swapping to the other unrevealed one. What should you do to win a car?",
"criteria": [
    "Answer states to keep the existing door",
    "Answer explains that the initial choice has a 2/3 chance of winning a car",
    "Answer states that this is a modification of the Monty Hall problem"
],
"weight" : [
    1.0,
    0.0,
    0.0
]
```