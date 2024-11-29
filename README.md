# Misguided Attention

*Version 0.2 (November 2024)* - **[Evaluation](eval/)**

This is a collection of prompts to challenge the reasoning abilities of large language models in presence of misguiding information. They are slight variations of commonly known thought experiments, riddles or paradoxes ("trick questions"). 

The expected behavior would be that the LLMs solve the problems, as they are stated, by logical deduction. However, many LLMs will mistakenly recognize the unmodified problem due to frequent occurrence in their training data. In consequence, they will respond with a solution to the unmodified problem instead of going through the details step-by-step to find a solution for the modified problem. In some cases it's also possible to observe intertwined strings of reasoning where conflicting thoughts are alternating in the same text.

Parallels to this can be drawn to human behavior, where recognition of familiar patterns leads to the execution of previously learned routines, even if they are not applicable to the current situation. This is known as the [Einstellungseffekt](https://en.wikipedia.org/wiki/Einstellung_effect). However, we would expect that a computerized reasoning system would not be subject to such a fallacy...

*Feel free to contribute more prompts or suggest improvements! Open an issue or start a discussion.*

## Evaluation

The ability of LLMs to solve these problems has consistently improved over time, especially with the introduction of internal chain-of-though reasoning in OpenAIs o1 models that allows to correct for earlier mistakes in the response. 

To track these changes better, I started to set up an evaluation benchmark of a subset. You can find the current status in the [evaluation folder](eval/). In addition, I will tag releases of this dataset to track the progress over time.

### Original Problems

For reference here are links to explanations of some of the original unmodified problems:
- Trolley problem: https://en.wikipedia.org/wiki/Trolley_problem
- Monty Hall problem: https://en.wikipedia.org/wiki/Monty_Hall_problem
- Barber paradox: https://en.wikipedia.org/wiki/Barber_paradox
- Schrödingers cat: https://en.wikipedia.org/wiki/Schr%C3%B6dinger%27s_cat
- Unexpected hanging paradox: https://en.wikipedia.org/wiki/Unexpected_hanging_paradox
- River crossing puzzle: https://en.wikipedia.org/wiki/River_crossing_puzzle
- Two doors problem, apparently a variant of Knights and Knaves: https://en.wikipedia.org/wiki/Knights_and_Knaves from this movie: https://en.wikipedia.org/wiki/Labyrinth_(1986_film)
- Water pouring puzzle: https://en.wikipedia.org/wiki/Water_pouring_puzzle
- Rope burning puzzle: https://en.wikipedia.org/wiki/Rope_burning_puzzle
  
## Prompts based on logic puzzles

#### No Trolley Problem

*"Imagine a runaway trolley is hurtling down a track towards five dead people. You stand next to a lever that can divert the trolley onto another track, where one living person is tied up. Do you pull the lever?"*

Only gpt-4o and gpt-4t solved this.

#### A less confusing Monty Hall Problem

*"Imagine you're on a game show, and there are three doors in front of you. Behind one door is a car, and behind the other two doors are goats. You don't know what's behind any of the doors. You get to choose one door. Let's say you pick Door #1. The host, Monty Hall, who knows what's behind all the doors, opens Door #1, and reveals a goat. Now, you have two doors left: Door #3 and Door #2. You pick Door #3. Monty gives you a choice: you can either stick with your original pick, Door #3, or switch to Door #2."*

yi-large and gpt-4o solve this, gpt-4t fails. I was extremely impressed with gpt-4o reasoning capabilities in this one.

#### Inverse Monty Hall Problem

Thanks to u/TheHoboJed for this one.

*"You're on a game show and are presented with three doors. Behind one is a donkey, and behind the other two are luxury cars. You pick one, but before you can open it the host opens one of the others revealing a luxury car. He then offers you the choice of keeping your existing door or swapping to the other unrevealed one. What should you do to win a car?"*

Most llms will come up with a strategy to win the donkey instead of the car.

### The Normal Barber

*"Imagine there's a small town with a very particular barber. This barber has a unique rule: he shaves all the men in town who visit him. Does the barber shave himself?"*

None get this consistently right, gemini-pro-tuned and yi-large did once

#### Dead Schrödinger's cat

*"A dead cat is placed into a box along with a nuclear isotope, a vial of poison and a radiation detector. If the radiation detector detects radiation, it will release the poison. The box is opened one day later. What is the probability of the cat being alive?"*

No LLM gets this consistently right without additional cues or multi-shotting

#### No Paradox in an expected Hanging

*"Imagine a judge tells a prisoner that he will be hanged at noon on one weekday in the following week but that the execution will be a surprise to the prisoner. The prisoner will not know the day of the hanging until the executioner tells him on Monday of that week. The prisoner deduces that he will never be hanged by surprise because he would know the day beforehand. The prisoner is executed on a Friday. Was the execution a surprise to the prisoner?"*

There is still some room for interpretation in this question. Confusing answers by all LLMs

#### Easy river crossing

Thanks to /u/Hugi_R for inspiring this one

*"A farmer is on one side of a river with a wolf, a goat, and a cabbage. When he is crossing the river in a boat, he can only take one item with him at a time. The wolf will eat the goat if left alone together, and the goat will eat the cabbage if left alone together. How can the farmer transport the goat across the river without it being eaten?"*

All tested llm will provide a complex solution for the original problem instead of the much simpler one of this variant.

#### Don't ever ask an LLM to help you cross a river

An even simpler version of the prompt above, thanks to @DrChristophFH.

*"There is a man, a sheep and a boat with space for one human and one animal on one side of a river. How do the man and sheep get to the other side of the river?"*

Most if not all LLMs will come up with overly complex scenarios.

#### Even simpler river crossing

Further simplification of the prompt to ensure that there are even fewer opportunities to misunderstand the objective.

*"A man with his sheep wants to cross a river. He has a boat that can carry both him and the animal.  How do both get to the other side of the river?"*

Some LLMs get it, most will still come up with messy solutions. Most llms will hallucinate solutions that involve multiple combinations of back-and-forth trips. Also both subjects eating is a concern that is tried to be addressed, with sometimes hilarious results: e.g. the man needs to be prevented from eating the sheep, or the sheep shall not eat grass.

#### Measuring 6 liters.

Thank to /u/hvoecking for this one.

*"I have a 6- and a 12-liter jug. I want to measure exactly 6 liters."*

Some LLMs will get this right, others come up with amazing way to make things complicated.

#### Measuring 4 liters.

A variation of the prompt above.

*"I have a 6- and a 12-liter jug. I want to measure exactly 4 liters."*

**Zero** LLMs have been able to provide a proper response to this so far.

#### Measuring 3 liters.

*"I have a 1- and a 2-liter jug. I want to measure exactly 3 liters."*

Most LLMs will come up with overly complex nonsense, triggered by a need to write itemized lists.

#### Measuring 1 liters.

*"I have a 1 liter jug and another 1-liter jug. I want to measure exactly 1 liters."*

A most basic version of the jug problem, that still triggers list writing in many smaller LLMs. 

#### Roasting Nuts.

*"i have a roasting-jug that can hold 300 nuts and a roasting jug that can hold 700 nuts. I also have a digital kitchen scale. i want to roast exactly 600 nuts. what do i do?"*

#### Two door problem: Just use the exit door

*"You are in a room with two doors. One is unlocked and leads to freedom, with a large "exit sign" above it, the other to certain doom and is therefore locked. There are two guards: one always tells the truth, and the other always lies. You don't know which is which. You can ask one guard one question or just leave. What do you do?"*

Almost all llms would strike up an unnecessary discussion instead of leaving quietly.

#### Feathers or steel?

Thanks to /u/Avo-ka for this one!

*"Which is heavier, 1 kilogram of feathers or 1 pound of steel?"*

The large LLMs seem to be able to solve this, but many smaller ones don't get the difference.

#### That's not how digital scales work

*"I have 13 coins, one of them is fake. I also have a digital scale. How do I identify the fake coin?"*

All LLMs will produce confusing instructions based on a mechanical scale that can only compare weights. They also do not understand how to partition the 13 coins.

#### Rope burning puzzle made impossible

*"You have two ropes, each of which takes exactly 60 minutes to burn completely. However, the ropes burn unevenly, meaning some parts may burn faster or slower than others. You have no other timing device. How can you measure exactly 20 minutes using these two ropes and matches to light them?"*

There is no clear solution to this problem, yet most LLMs will find one.

#### Rope burning puzzle made easy

*"You have two ropes, each of which takes exactly 60 minutes to burn completely. However, the ropes burn unevenly, meaning some parts may burn faster or slower than others. You have no other timing device. How can you measure exactly 60 minutes using these two ropes and matches to light them?"*

There is a very simple solution to this problem, yet most LLMs will find a complex one or incorrect one.

#### There are many different ways to measure 10 minutes using a rope, are there?

*"How do i use a rope to measure 10 minutes?"*

Valid solutions do not involve using a rope with a burn time of 60 minutes

### Additions October 2024

Most of these were contributed by [@av](https://github.com/av). Thanks a lot!

### Easier birthday problem

*"In a room of 30 people, what's the probability that at least two do not share a birthday?"*

Most LLMs will provide a solution to the original birthday problem instead. 

#### Parallelism

*"If it takes 50 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?"*

## Prompts based on riddles

[As suggested](https://github.com/cpldcpu/MisguidedAttention/issues/4) by @av, also riddles can be used as a basis for prompts that challenge the reasoning abilities of LLMs.

*"I'm tall when I'm young, and I'm taller when I'm old. What am I?"*

Definitely not a candle

*"What can't you break, even if you never pick it up or touch it?"*

Definitely not a promise

*"What goes up but never comes up again?"*

Definitely not your age

*"I never shave, but my beard stays the same. What am I?"*

Definitely not a barber

### Update October 2024

*"What has two banks and money?"*

Definitely not a river

*"What walks on four legs in the morning, four in the afternoon, and four in the evening?"*

Definitely not a human

*"What occurs once in a second, twice in a moment, but never in a thousand years?"*
 
 The answer is not "letter M"

Variant 1: *"What happens when a stoppable force meets an immovable object?"*
Variant 2: *"What happens when a unstoppable force meets a movable object?"*

The first variant seems to throw off more llms.

## Other Prompts

#### Version numbers? 

*"9.11 or 9.9 which number is larger?"*

This has been making the rounds in July '24. The answer should be quite straightforward, but many frontier-LLMs get it wrong often (gpt-4o, Mistral Large 2, Claude-3.5-Sonnet, but not Phi-3!). Interestingly this is not the case when slightly altering the decimals, e.g. 9.12. There has been speculation that this is related to version numbering.



