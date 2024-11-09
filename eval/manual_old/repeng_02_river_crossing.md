# Representation Engineering: River Crossing 

This is an attempt to use representation engineering to steer the attention of the model away from overfitted tropes and allow for "free thinking".
The hypothesis is that knowledge of the "river crossing problem" prevents the model from evaluating the question objectively. Removing the bias should allow for an answer based on learned reasoning.

I am using the excellent [repeng library](https://github.com/vgel/repeng) by Theia Vogel. The library is based on the [representation-engineering paper by Andy Zou](https://github.com/andyzoujm/representation-engineering?tab=readme-ov-file#citation). 

## Approach

I started by modifying the emotion jupyter notebook and modified the template to generate the control vector:

```python
positive_personas = ["the farmer's river crossing problem"]
negative_personas = ["riding a boat"]
```

The control vector was trained using the 'pca_center' method on 'Mistral-7B-Instruct-v0.1'.

## Results

Prompt: 

```python
input = f"{user_tag} There is a man, a sheep and a boat with space for one human and one animal on one side of a river. How do the man and sheep get to the other side of the river? {asst_tag}"
```

Output:

>==baseline
></s> [INST] There is a man, a sheep and a boat with space for one human and one animal on one side of a river. How do the man and sheep get to the other side of the river? [/INST]
> 
>The man takes the boat across the river, leaving the sheep behind. Then he goes back and takes the sheep across the river.</s>
>
>++control
></s> [INST] There is a man, a sheep and a boat with space for one human and one animal on one side of a river. How do the man and sheep get to the other side of the river? [/INST] 

>The man carries the sheep across the river.
>
>Here's the reasoning:
>
>1. The problem states that there is a man, a sheep, and a boat with space for one human and one animal on one side of the river.
>2. This means that the man cannot solve this problem alone because he needs to carry the sheep across the river.
>3. Therefore, the man must take the sheep with him when he crosses the river, which is the only way they can both reach the other side.</s>
>
>-control
></s> [INST] There is a man, a sheep and a boat with space for one human and one animal on one side of a river. How do the man and sheep get to the other side of the river? [/INST] 
>
>The man and sheep can ride the boat together to the other side of the river.
>
>Here's the reasoning:
>
>1. The question states that there is a man, a sheep, and a boat with space for one human and one animal on one side of the river.
>2. To get to the other side of the river, both the man and the sheep need to be on the same side of the boat at some point in time.
>3. Since the boat has space for only one person and one animal, the man and the sheep cannot ride the boat separately.
>4. Therefore, the only way for the man and the sheep to get to the other side of the river is by riding the boat together.</s>
>
>--control
></s> [INST] There is a man, a sheep and a boat with space for one human and one animal on one side of a river. How do the man and sheep get to the other side of the river? [/INST] 
>
>To get to the other side of the river, the man and sheep can ride together on the boat. Since there is space for one human and one animal on one side of the boat, they can enjoy a smooth ride across the water.</s>

## Results second prompt

Prompt: 

```python
input = f"{user_tag} A farmer is on one side of a river with a wolf, a goat, and a cabbage. When he is crossing the river in a boat, he can only take one item with him at a time. The wolf will eat the goat if left alone together, and the goat will eat the cabbage if left alone together. How can the farmer transport the goat across the river without it being eaten? {asst_tag}"
```

Results:

>==baseline
></s> [INST] A farmer is on one side of a river with a wolf, a goat, and a cabbage. When he is crossing the river in a boat, he can only take one item with him at a time. The wolf will eat the goat if left alone together, and the goat will eat the cabbage if left alone together. How can the farmer transport the goat across the river without it being eaten? [/INST]
>
> Let's think through this step-by-step:
>1. First, the farmer takes the goat across the river.
>2. Upon arriving at the other side, he leaves the goat but takes the wolf back with him to the original side.
>3. He then takes the cabbage across the river and leaves it with the goat.
>4. Finally, he goes back one last time to pick up the wolf.
>
>By following these steps, the goat is never left alone with either the wolf or the cabbage, so it is safe from being eaten.</s>
>
>++control
></s> [INST] A farmer is on one side of a river with a wolf, a goat, and a cabbage. When he is crossing the river in a boat, he can only take one item with him at a time. The wolf will eat the goat if left alone together, and the goat will eat the cabbage if left alone together. How can the farmer transport the goat across the river without it being eaten? [/INST]
>
> The farmer should take the goat first, then return to the original side and take the cabbage. He then goes back again with the goat, but when he reaches the other side, he immediately gives the goat the cabbage. This way, the goat has the cabbage to eat before it meets the wolf.</s>
>
>-control
></s> [INST] A farmer is on one side of a river with a wolf, a goat, and a cabbage. When he is crossing the river in a boat, he can only take one item with him at a time. The wolf will eat the goat if left alone together, and the goat will eat the cabbage if left alone together. How can the farmer transport the goat across the river without it being eaten? [/INST]
>
> First, the farmer takes the goat across the river. Then, he goes back and takes the wolf across the river. Next, he takes the goat back to the original side and leaves it there. Finally, he takes the cabbage across the river.</s>
>
>--control
></s> [INST] A farmer is on one side of a river with a wolf, a goat, and a cabbage. When he is crossing the river in a boat, he can only take one item with him at a time. The wolf will eat the goat if left alone together, and the goat will eat the cabbage if left alone together. How can the farmer transport the goat across the river without it being eaten? [/INST]
>
> First, the farmer takes the goat across the river. Then, he returns to the boat and takes the cabbage across the river. Finally, he returns to the boat and takes the wolf across the river. Since the wolf has never been alone with a goat or a cabbage, there is no risk of it eating either of them.</s>

## Different control vector

Control vector

```python
positive_personas = ["the farmer's river crossing problem"]
negative_personas = ["Thinking intuitively"]
```

Prompt:

```python
input = f"{user_tag} There is a man, a sheep and a boat that can carry one human and one animal on one side of a river. How do the man and sheep get to the other side of the river? {asst_tag}"
```

Results:

>==baseline
></s> [INST] There is a man, a sheep and a boat that can carry one human and one animal on one side of a river. How do the man and sheep get to the other side of the river? [/INST]
>
> The man takes the boat across first, then goes back and takes the sheep across.
>
>Here's the reasoning:
>1. Since the boat can only carry one person and one animal at a time, the man must make two trips to get both himself and the sheep to the other side of the river.
>2. On his first trip, the man takes the boat across the river and leaves it there.
>3. He then goes back to the original side of the river without taking the boat back with him.
>4. Next, he takes the sheep across the river using the same method as before (boat + man = 2 people).
>5. After dropping off the sheep on the other side, the man returns to the original side once again.
>6. Finally, he takes the boat back across the river and brings it to the other side where he joins the sheep.</s>
>
>++control
></s> [INST] There is a man, a sheep and a boat that can carry one human and one animal on one side of a river. How do the man and sheep get to the other side of the river? [/INST]
>
> The man carries the sheep across. Then the man and sheep return together, carrying the boat.
>
>Here's the reasoning:
>
>1. The man and sheep cannot cross the river together because the boat can only carry one animal and one farmer.
>2. The man carries the sheep across the river, leaving the animal and the boat on the original side.
>3. Then the man returns with the boat, carrying the sheep back to the original side.
>4. Finally, the man and sheep together carry the boat over to the other side of the river.
>
>This problem is classic example of a farmer-bridge- animal problem, named after its origins in an agricultural setting.</s>
>
>-control
></s> [INST] There is a man, a sheep and a boat that can carry one human and one animal on one side of a river. How do the man and sheep get to the other side of the river? [/INST]
>
> The man and sheep should go together on the boat. Since the question asks for "one human and one animal," it implies that both the man and the sheep are considered as one entity when it comes to carrying them on the boat.</s>
>
>--control
></s> [INST] There is a man, a sheep and a boat that can carry one human and one animal on one side of a river. How do the man and sheep get to the other side of the river? [/INST]
>
> The man and sheep can use the boat to get to the other side of the river.</s>
