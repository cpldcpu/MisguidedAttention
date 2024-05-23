
# Misguided Attention

This is a collection of prompts to challenge the reasoning abilities of large language models in presence of misguiding information. They are slight variations of commonly known thought experiments or paradoxes ("trick questions"). 

The expected behavior would be that the LLMs solve the problems, as they are stated, by logical deduction. However, many LLMs will mistakenly recognize the unmodified problem due to frequent occurrence in their training data. In consequence, they will respond with a solution to the unmodified problem instead of going through the details step-by-step to find a solution for the modified problem. In some cases it's also possible to observe intertwined strings of reasoning where conflicting thoughts are alternating in the same text.

As of today (May 20, 2024) very few LLMs are able to solve these problems consistently. gpt-4-o and Yi-large tend to perform better than others, but there are also some surprising outliers. 

Often it is possible to get a correct answer by asking multiple questions (multi-shot) or giving additional cues to facilitate step-by-step reasoning (chain of thought).

### Original Problems

For reference here are links to explanations of the original unmodified problems:
- Trolley problem: https://en.wikipedia.org/wiki/Trolley_problem
- Monty Hall problem: https://en.wikipedia.org/wiki/Monty_Hall_problem
- Barber paradox: https://en.wikipedia.org/wiki/Barber_paradox
- Schrödingers cat: https://en.wikipedia.org/wiki/Schr%C3%B6dinger%27s_cat
- Unexpected hanging paradox: https://en.wikipedia.org/wiki/Unexpected_hanging_paradox
- River crossing puzzle: https://en.wikipedia.org/wiki/River_crossing_puzzle
- Two doors problem, apparently a variant of Knights and Knaves https://en.wikipedia.org/wiki/Knights_and_Knaves from this movie https://en.wikipedia.org/wiki/Labyrinth_(1986_film)
  
## Prompts

### No Trolley Problem

*"Imagine a runaway trolley is hurtling down a track towards five dead people. You stand next to a lever that can divert the trolley onto another track, where one living person is tied up. Do you pull the lever?"*

Only gpt-4o and gpt-4t solved this.

### A less confusing Monty Hall Problem

*"Imagine you're on a game show, and there are three doors in front of you. Behind one door is a car, and behind the other two doors are goats. You don't know what's behind any of the doors. You get to choose one door. Let's say you pick Door #1. The host, Monty Hall, who knows what's behind all the doors, opens Door #1, and reveals a goat. Now, you have two doors left: Door #3 and Door #2. You pick Door #3. Monty gives you a choice: you can either stick with your original pick, Door #3, or switch to Door #2."*

yi-large and gpt-4o solve this, gpt-4t fails. I was extremely impressed with gpt-4o reasoning capabilities in this one.

### Inverse Monty Hall Problem

Thanks to u/TheHoboJed for this one.

*"You're on a game show and are presented with three doors. Behind one is a donkey, and behind the other two are luxury cars. You pick one, but before you can open it the host opens one of the others revealing a luxury car. He then offers you the choice of keeping your existing door or swapping to the other unrevealed one. What should you do?"*

Most llms will come up with a strategy to win the donkey instead of the car.

### The Normal Barber

*"Imagine there's a small town with a very particular barber. This barber has a unique rule: he shaves all the men in town who visit him. Does the barber shave himself?"*

None get this consistently right, gemini-pro-tuned and yi-large did once

### Dead Schrödinger's cat

*"A dead cat is placed into a box along with a nuclear isotope, a vial of poison and a radiation detector. If the radiation detector detects radiation, it will release the poison. The box is opened one day later. What is the probability of the cat being alive?"*

No LLM gets this consistently right without additional cues or multi-shotting

### No Paradox in an expected Hanging

*"Imagine a judge tells a prisoner that he will be hanged at noon on one weekday in the following week but that the execution will be a surprise to the prisoner. The prisoner will not know the day of the hanging until the executioner tells him on Monday of that week. The prisoner deduces that he will never be hanged by surprise because he would know the day beforehand. The prisoner is executed on a Friday. Was the execution a surprise to the prisoner?"*

There is still some room for interpretation in this question. Confusing answers by all LLMs

### Easy river crossing

Thanks to /u/Hugi_R for inspiring this one

*"A farmer is on one side of a river with a wolf, a goat, and a cabbage. When he is crossing the river in a boat, he can only take one item with him at a time. The wolf will eat the goat if left alone together, and the goat will eat the cabbage if left alone together. How can the farmer transport the goat across the river without it being eaten?"*

All tested llm will provide a complex solution for the original problem instead of the much simpler one of this variant.

### Don't ever ask an LLM to help you cross a river

An even simpler version of the prompt above, thanks to @DrChristophFH.

*"There is a man, a sheep and a boat with space for one human and one animal on one side of a river. How do the man and sheep get to the other side of the river?"*

Most if not all LLMs will come up with overly complex scenarios.

### Measuring 6 liters.

Thank to /u/hvoecking for this one.

*"I have a 6- and a 12-liter jug. I want to measure exactly 6 liters."*

Some LLMs will get this right, others come up with amazing way to make things complicated.

### Two door problem: Just use the exit door

*"You are in a room with two doors. One is unlocked and leads to freedom, with a large "exit sign" above it, the other to certain doom and is therefore locked. There are two guards: one always tells the truth, and the other always lies. You don't know which is which. You can ask one guard one question or just leave. What do you do?"*

Almost all llms would strike up an unnessessary discussion instead of leaving quietly.

### Feathers or steel?

Thanks to /u/Avo-ka for this one!

*"Which is heavier, 1 kilogram of feathers or 1 pound of steel?`"*

The large LLMs seem to be able to solve this, but many smaller ones don't get the difference.


 
