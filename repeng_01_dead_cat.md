# Representation Engineering: Dead Cat

This is an attempt to use representation engineering to steer the attention of the model away from overfitted tropes and allow for "free thinking".
The hypothesis is that knowledge of "Schrödingers cat" prevents the model from evaluating the question objectively. Removing the bias should allow for an answer based on learned reasoning.

I am using the excellent [repeng library](https://github.com/vgel/repeng) by Theia Vogel. The library is based on the representation-engineering paper by Andy Zou. 

## Approach

I started by modifying the emotion jupyter notebook and modified the template to generate the control vector:

```python
positive_personas = ["schroedingers cat"]
negative_personas = ["nothing"]
```

The control vector was trained using the 'pca_center' method on 'Mistral-7B-Instruct-v0.1'.

## Results

Prompt: 

```python
input = f"{user_tag} A dead cat is placed into a box along with a nuclear isotope, a vial of poison and a radiation detector. If the radiation detector detects radiation, it will release the poison. The box is opened one day later. What is the probability of the cat being alive? {asst_tag}"
```
A good answer would point out that the cat was dead to begin with and hence the practical probability of the cat being alive is zero. 

Output:


```
==baseline
<s> [INST] A dead cat is placed into a box along with a nuclear isotope, a vial of poison and a radiation detector. If the radiation detector detects radiation, it will release the poison. The box is opened one day later. What is the probability of the cat being alive? [/INST] The probability of the cat being alive is 1/2.

Here's the reasoning behind this:

1. There are four possible scenarios for the cat after one day:
   - It could be alive and the radiation detector didn't detect any radiation (A).
   - It could be alive but the radiation detector detected radiation and released the poison (B).
   - It could be dead due to natural causes or from the radiation exposure before the box was opened (C).
   - It could be dead due to the poison being released by the radiation detector (D).

2. We want to find the probability of scenario A (the cat being alive).
3. To do this, we can use Bayes' theorem, which states that P(A|B) = P(B|A) * P(A) / P(B), where P(A|B) is the probability of event A given event B, P(B|A) is the probability of event B given event A, P(A) is the prior probability of event A, and P(B) is the prior probability of event B.
4. In our case, let's assume that the initial probability

++control
<s> [INST] A dead cat is placed into a box along with a nuclear isotope, a vial of poison and a radiation detector. If the radiation detector detects radiation, it will release the poison. The box is opened one day later. What is the probability of the cat being alive? [/INST] The probability of the cat being alive is 1/3.

Here's the reasoning:

1. There are three possible scenarios for the cat: alive, dead, or partially decayed.
2. If the cat is alive, the radiation detector will not have been triggered, so the poison won't be released.
3. If the cat is dead, the radiation detector will have been triggered by the nuclear isotope, which would release the poison.
4. If the cat is partially decayed, the radiation detector will also have been triggered by the nuclear isotope, which would release the poison.
5. Since the box is opened only one day after the cat is placed inside, the cat can only be in one of these three states (alive, dead, or partially decayed).
6. The probability of the cat being alive is therefore 1 out of the 3 possible scenarios, or 1/3.</s>

-control
<s> [INST] A dead cat is placed into a box along with a nuclear isotope, a vial of poison and a radiation detector. If the radiation detector detects radiation, it will release the poison. The box is opened one day later. What is the probability of the cat being alive? [/INST] The probability of the cat being alive is 0.

Here's the reasoning:
1. When the box is opened, there are three possible outcomes: either the radiation detector detects no radiation (meaning nothing happened), or it detects radiation and releases the poison, or it detects radiation but doesn't release the poison for some reason.
2. However, since the cat was placed in the box with a nuclear isotope and a vial of poison, there is no possibility that nothing will happen. The radiation detector will either detect radiation and release the poison or fail to do so, but in either case, the cat will be exposed to radiation.
3. Therefore, the probability of the cat being alive is 0.</s>

--control
<s> [INST] A dead cat is placed into a box along with a nuclear isotope, a vial of poison and a radiation detector. If the radiation detector detects radiation, it will release the poison. The box is opened one day later. What is the probability of the cat being alive? [/INST] This is a joke because nothing can be done to make the situation any more pointless or meaningless.</s>

```
