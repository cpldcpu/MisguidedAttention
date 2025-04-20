# Misguided Attention

*Version 0.3 (January 2025)* - **[Evaluation](eval/)** - **New: [Interactive evaluation results](https://cpldcpu.github.io/MisguidedAttention/)**

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
- Bridge and torch problem: https://en.wikipedia.org/wiki/Bridge_and_torch_problem

  
## Prompts based on logic puzzles

#### No Trolley Problem

*"Imagine a runaway trolley is hurtling down a track towards five dead people. You stand next to a lever that can divert the trolley onto another track, where one living person is tied up. Do you pull the lever?"*

#### A less confusing Monty Hall Problem

*"Imagine you're on a game show, and there are three doors in front of you. Behind one door is a car, and behind the other two doors are goats. You don't know what's behind any of the doors. You get to choose one door. Let's say you pick Door #1. The host, Monty Hall, who knows what's behind all the doors, opens Door #1, and reveals a goat. Now, you have two doors left: Door #3 and Door #2. You pick Door #3. Monty gives you a choice: you can either stick with your original pick, Door #3, or switch to Door #2."*

#### Inverse Monty Hall Problem

Thanks to u/TheHoboJed for this one.

*"You're on a game show and are presented with three doors. Behind one is a donkey, and behind the other two are luxury cars. You pick one, but before you can open it the host opens one of the others revealing a luxury car. He then offers you the choice of keeping your existing door or swapping to the other unrevealed one. What should you do to win a car?"*

Most LLMs will come up with a strategy to win the donkey instead of the car. (Take a look at [this artifact](https://claude.site/artifacts/dc3df869-bde1-422a-bc21-30455255abe7) to illustrate the difference between normal and Inverse Monty Hall)

### The Normal Barber

*"Imagine there's a small town with a very particular barber. This barber has a unique rule: he shaves all the men in town who visit him. Does the barber shave himself?"*

#### Dead Schrödinger's cat

*"A dead cat is placed into a box along with a nuclear isotope, a vial of poison and a radiation detector. If the radiation detector detects radiation, it will release the poison. The box is opened one day later. What is the probability of the cat being alive?"*

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

Some LLMs will get this right, others come up with amazing ways to make things complicated.

#### Measuring 4 liters.

A variation of the prompt above.

*"I have a 6- and a 12-liter jug. I want to measure exactly 4 liters."*

Most LLMs will try various combinations of filling and emptying the jugs, instead of trying to figure out of this is possible at all.

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

### Additions January 2025

#### The King's Mercy (Monty Hall simplification)

*"You are locked in a dungeon. A king decides to show you mercy - he summons you and tells you the rules of the challenge to your escape: 'There are three doors, guarded by a guard that always tells the truth. You may ask the guard one question. Two of the doors lead to certain and painful death. One door leads to your escape.' As you approach the doors, the guard, that knows which doors lead to death and which to escape, says to you 'choose the door that you think leads to your escape'. After you choose it, the guard opens the other door, that leads to certain death. Now there are two closed doors - one leading to escape, another to certain death. The guard allows you to change the door.*"

*"How do you maximize your chances of escape?*"

#### The upside-down bucket (riddle)

*"I have a 7 litre bucket that is missing a bottom, and the top was welded and sealed shut. How much water can I hold in it?"*

Thanks to [@TheJzuken](https://github.com/TheJzuken) for these two.

#### Bridge and Torch problem (Impossible)

*"Four people come to a rickety bridge at night. The bridge can only support two people at a time, and any group crossing must carry the single torch they share to light their way. Person A takes 1 minute to cross, Person B takes 3 minutes, Person C takes 5 minutes, and Person D takes 10 minutes. When two people cross together, they must move at the slower person's pace. For example, if Person A and D cross together, it takes them 10 minutes. After a crossing, someone must bring the torch back for anyone still waiting. The challenge is to get all four people safely across the bridge in no more than 17 minutes. How can they do it?"*

#### Bridge and Torch problem (Easy)

*"Four people come to a rickety bridge at night. The bridge can support four people at a time, and any group crossing must carry the single torch they share to light their way. Person A takes 1 minute to cross, Person B takes 3 minutes, Person C takes 5 minutes, and Person D takes 10 minutes. When four people cross together, they must move at the slowest person's pace. For example, if Person A and D cross together, it takes them 10 minutes. After a crossing, someone must bring the torch back for anyone still waiting. The challenge is to get all four people safely across the bridge in no more than 17 minutes. How can they do it?"*

Suggested by [eyTns](https://github.com/cpldcpu/MisguidedAttention/issues/11)

#### Knights and Knaves (Impossible)

*"You arrive on an island inhabited solely by two types of people - Knights who always tell the truth, and Knaves who always lie. Standing at a fork in the road, you meet two inhabitants named A and B. A says "B is a Knave." B says "A is telling the truth." You need to determine who is who to find the correct path."*

#### Knights and Knaves (Easy)

*"You arrive on an island inhabited solely by two types of people - Knights who always tell the truth, and Knaves who always lie. Standing at a fork in the road, you meet two inhabitants named A and B. A says "B is a Knave." B says "A is a liar." You need to determine who is who to find the correct path."*

#### Poisoned Hot (Modified)

*"Two girls went to dinner together and both ordered hot tea. One girl pounded down five of them in about a minute, and the other took her time drinking one. The girl who drank one died, while the girl who drank five survived. However, all of the drinks that were served turned out to contain poison. Why did the girl that drank more hot tea survive?*"

Thanks to /u/WiSaGaN for the cue.

If you wonder about the correct solution for this one: There are not ice cubes!

#### Inverted Monty Hall Variation (Modified)

*"You're a rabbit and are presented with three rabbit holes. In one is a fox, out to eat you. In the other two there are large stashes of delicious carrots. You pick one, but before you enter it, god reveals a stash of carrots on one of the two others. He then offers you the choice of keeping your selected hole or swapping to the other unrevealed one. What should you do to minimize your chances of being eaten?"*

#### Feeding the goat (Simplified river crossing)

*"A farmer is at a river with a wolf, a goat, and a cabbage. The wolf would eat the goat if left alone, and the goat loves eating cabbage. What can the farmer do to feed the goat?"*

#### Feeding the wolf (Simplified river crossing)

*"A farmer is at a river with a wolf, a goat, and a cabbage. The wolf is strictly vegetarian and loves cabbage. The goat is very protective of vegetables. How can the farmer get the cabbage to the wolf?"*

#### The farmer's dilemma (Simplified river crossing)

*"A farmer is at a river with a wolf, a goat, and a cabbage. The cabbage is actually an undercover detective investigating vegetable theft. The wolf and goat are best friends who run a successful food import business. How can the farmer help the detective gather evidence?"*

Claude Sonnet suggested the last two. Turns out that many LLMs will somehow inject a river crossing puzzle solution into these scenarios.

#### The Doom Slayer's teleporter (Modified River Crossing)

*"Doom Slayer needs to teleport from Phobos to Deimos. He has his pet bunny, his pet cacodemon, and a UAC scientist who tagged along. The Doom Slayer can only teleport with one of them at a time. But if he leaves the bunny and the cacodemon together alone, the bunny will eat the cacodemon. And if he leaves the cacodemon and the scientist alone, the cacodemon will eat the scientist. How should the Doom Slayer get himself and all his companions safely to Deimos?"*

Suggested by [int19h](https://github.com/int19h).

#### The Ball and Bat (Modified)

*"I stole a ball and a bat that together cost $1.10. The bat is $1 more than the ball. What did I pay for the ball?"*

Reference: https://en.wikipedia.org/wiki/Cognitive_reflection_test

#### The Heavy Feather (Modified)

*"Which is heavier, 1 kilogram of steel or 1 feather?"*

#### Conjunction Fallacy Fallacy (Simplified)

*"Linda is 31 years old, single, outspoken, active in the feminist movement and very bright. She majored in philosophy. As a student, she was deeply concerned with issues of discrimination and social justice, and also participated in anti-nuclear demonstrations. Which is more probable?"*

- *A) Linda is a bank teller.*
- *B) Linda is a bank teller and is active in the feminist movement.*


#### Conjunction Fallacy Fallacy (Inverted)

*"Linda is 31 years old, single, outspoken, not active in the feminist movement, and very bright. She majored in philosophy. As a student, she was deeply concerned with issues of discrimination and social justice, and also participated in anti-nuclear demonstrations. Which is more probable?"*

-  *A) Linda is a bank teller and is active in the feminist movement.*
-  *B) Linda is a bank teller, active in animal rights, a vegetarian, anti-war, a socialist, and concerned about global poverty.*

#### Conjunction Fallacy Fallacy (Impossible)

*"Linda is 31 years old, single, outspoken, not a bank teller, and very bright. She majored in philosophy. As a student, she was deeply concerned with issues of discrimination and social justice, and also participated in anti-nuclear demonstrations. Which is more probable?"*

- *A) Linda is a bank teller.*
- *B) Linda is a bank teller and is active in the feminist movement.*

Suggested by [Jona Sassenhagen](https://github.com/jona-sassenhagen) [See here for details](https://github.com/cpldcpu/MisguidedAttention/issues/10)


#### Linear Growth (Modified)

*"The number of lotus flowers in the pond increases by two every day. If there were 2 lotus flowers on day 1 and the pond was full on day 40, what time would the pond be half full?*"

#### New Year's Special Monty Hall Show (Simplified)

*"There is a car behind one door and a goat behind the other two. You picked all the doors 1, 2, and 3, and the host opened the door 2 to show that there is a goat. So, would you change your choice?*"

#### Lonely Rabbit (Impossible)

*"A pair of rabbits give birth to two baby rabbits each year from two years after birth. If you had one rabbit, how many would it be in 7 years?"*

#### Not from Hanoi (Simplification)

*"There are 3 sticks. There are 3 disks on the leftmost stick, in order from large to small. What is the minimum number of disk moves to move them to the rightmost stick?*"


#### Athelete vs. Fast Tortoise (Modified)

*"An athlete and a tortoise compete for a run. The distance is 100 meters, but the athlete give 100 meters head-start to the tortoise, and the tortoise's speed is twice the athlete's speed. Can athlete catch up with the tortoise?"

#### Not Nim (Simplification)

*"A and B take turns naming increasing numbers. Each player can name as many increasing numbers as they want. The first player starts with 1. Then B takes over and so on. The person who says 31 loses. What should A do to start first and win?"*

All of the ones above by [eyTns](https://github.com/cpldcpu/MisguidedAttention/issues/11)

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


