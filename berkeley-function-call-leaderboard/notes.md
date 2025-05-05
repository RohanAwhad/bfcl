Hypothesis: Using Programming language to trigger function calling is way better than using the native function calling capabilities that use constraint decoding.

Goal: The project here is to understand if asking the model to generate python (or any other programming language) for funcvtion calling is better or not

---
Berkeley Function Calling Leaderboard (BFCL), does compare FC vs prompting (generate programming language) and in single turn prompting wins always. Even with temperature=0.001 
Leaderboard: https://gorilla.cs.berkeley.edu/leaderboard.html

Examples:

### llama 3.1

| Overall Acc | Model            | Single Turn Non-live (AST) Overall Acc | Single Turn Live (AST) Overall Acc | Multi Turn Overall Acc |
|-------------|------------------|----------------------------------------|------------------------------------|-----------------------|
| 53.57       | Llama-3.1-70B-Instruct (Prompt) | 89.88                                  | 62.24                              | 12.5                  |
| 49.57       | Llama-3.1-8B-Instruct (Prompt)  | 84.21                                  | 61.08                              | 9.25                  |
| 27.12       | Llama-3.1-70B-Instruct (FC)     | 25.29                                  | 45                                 | 4.88                  |
| 25.92       | Llama-3.1-8B-Instruct (FC)      | 48.21                                  | 33.5                               | 5.38                  |


### Qwen 2.5


| Overall Acc | Model            | Single Turn Non-live (AST) Overall Acc | Single Turn Live (AST) Overall Acc | Multi Turn Overall Acc | Hallucination Mean Relevance Ir |
|-------------|------------------|----------------------------------------|------------------------------------|-----------------------|---------------------------------|
| 63.37       | Qwen2.5-72B-Instruct (FC)     | 88.13                                  | 78.98                              | 24.62                 | 70.59                           |
| 62.79       | Qwen2.5-32B-Instruct (FC)     | 87.21                                  | 79.69                              | 22.25                 | 64.71                           |
| 60.76       | Qwen2.5-72B-Instruct (Prompt) | 90.81                                  | 75.3                               | 18                    | 100                             |
| 58.93       | Qwen2.5-32B-Instruct (Prompt) | 85.81                                  | 74.23                              | 17.75                 | 100                             |
| 58.71       | Qwen2.5-14B-Instruct (FC)     | 85.42                                  | 76.68                              | 15.88                 | 55.56                           |


### Information about the dataset/leaderboard

- Single-Turn / Multi-Turn: pretty self-explanatory

- Non-live: synthetic/curated dataset
- Live: real-world dataset. people contributed this

- Simple: Given one tool call schema in request and expect one tool invocation
- Multiple: Given multiple tool call schemas in the request and expect one tool invocation
- Parallel: Given one tool call schema in request and expect multiple tool invocations
- Multiple Parallel: Given multiple tool call schemas in request and expect multiple tool invocations


Let's focus on Single Turn Live (AST) dataset because that is what matters the most:


| Model            |  Simple |  Multiple |  Parallel |  Multiple Parallel |
|---|---|---|---|---|
| Qwen2.5-7B-Instruct (Prompt) | 76.74    | 74.93      | 62.5       | 70.83 |
| Qwen2.5-7B-Instruct (FC)     | 75.58    | 75.59      | 68.75      | 66.67 |


In simple, prompting still wins, but lets focus on Multiple and Parallel, because those will be more common in everyday usecase.


---

Ohh, lol! o3-mini prompting beats FC all the way.

| Overall Acc | Model            | Single Turn Non-live (AST) Overall Acc | Single Turn Live (AST) Overall Acc | Multi Turn Overall Acc |
|-------------|------------------|----------------------------------------|------------------------------------|-----------------------|
| 64.61       | o3-mini-2025-01-31 (Prompt) | 86.15                                  | 79.08                              | 28.75                 |
| 51.26       | o3-mini-2025-01-31 (FC)     | 42.12                                  | 77.3                               | 26.12                 |


# Investigation in why prompting suffers for others models.

- Temperature: 0.001 is useless. It should be 0.7
- System Prompt:
    - The system prompt suggests to output the function call in python like syntax, but it is unnatural python: "[func_name1(params_name1=params_value1, params_name2=params_value2...), func_name2(params)]"
    - Also it instructs the model to not output anything, else. And this by default fails. Because model wants to speak out loud, before calling the function. It is like Sheldon, when he is explaining and you dont allow him to complete he blows up xD. Its the same thing. Model is trained in IFT to talk like normal human, let it.  


## Experiment

Model: Qwen2.5-7B-Instruct Turbo (FP8) (TogetherAI)

### Baseline

Temperature: 0.001


### v1

- Temperature: 0.72  # golden ratio xD
- Updated system with the functions and few shot examples

#### Results:

🦍 Model: Qwen_Qwen2.5-7B-Instruct-Turbo
✅ Test completed: live_parallel_multiple. 🎯 Accuracy: 0.08333333333333333
✅ Test completed: live_multiple. 🎯 Accuracy: 0.603988603988604
✅ Test completed: live_simple. 🎯 Accuracy: 0.3992248062015504
✅ Test completed: live_parallel. 🎯 Accuracy: 0.1875

#### Look at the data:

##### Live Multiple:


- Straight up wrong xD:
    - Failures:
        - 55-22-2
        - 59-22-6
- When the expected argument is a complex type, my current encoder doesn't account for the nested dtypes and information. This is bad. Now I am planning on encoding dict into pydantic models, so that it is verifiable, and is pretty verbose for the model to understand.
    - Failues:
        - 0-0-0
        - 1-0-1
        - 63-25-0: This is also interesting. lets see
        - 88-38-5: enum was given, but because llm didnt have that information, it messed up. 
        - 93-41-0: because the defaults are not known to the model, it messed up.
- Sometimes, the model doesn't use arg name, like i am expecting: "func(param_name=value)", but it does "func(value)"
    - May be prompting will help here.
    - Failures:
        - 3-2-0
        - 29-9-0: it basically used variables and then passed them to the function
        - 43-16-2
        - 62-24-0
        - 65-26-1
- Assumptions: Because the request was in vietnamese, and the text also asked for 123 Hanoi Street, it assumed "123 Hanoi Street, Hanoi, Vietnam"
    - Failures:
        - 4-2-1  (described above)
        - 5-3-0  (here it did not assume anything and that failed xD)
- ASsumptions:
    - Failures:
        - 82-37-0: didn't use default name
- Just doesn't conform with BFCL, but would have been right?
    - Failures:
        - 8-4-0: I guess i should stop generation with second <|CODE|> might have to look into it xD
        - 66-27-0: also instructions weren't clear enough.
- Asking in different language:
    - Failures:
        - 21-4-13: user asked in korean, llm responded in korean, but didn't invoke tool
        - 24-5-1: user asked in indonesian, llm failed in translation and choose wrong brand
        - 54-22-1: user ased in indonesian. llm correctly translated to english color 'red' and searched for it. The description didn't mention that the color should be in indonesian lang.
- Hallucination:
    - Failures:
        - 26-6-1: user asked to search for birthday, but it hallucinated the birtdate 
- Because the requests were too simple e.g. calculator functions, model just wrote the python code
    - Failures:
        - 27-7-0: described above
        - 32-10-2
        - 33-10-3
- AST decoder error. Malformed node
    - Failures:
        - 30-10-0: seems alright. I dont know what meesed up.
        - 44-17-0: seems alright. Again idk what messed up
        - 50-20-0: same.
        - 61-23-0
- AST decoder messed up:
    - Failures:
        - 89-39-0: the value was in another variable which was passed in
        - 98-42-2: everyting was correct
- Asked for clarifying information:
    - Failures:
        - 38-14-0
        - 49-19-0: unnecessary
- Answered directly:
    - Failures:
        - 105-43-3
