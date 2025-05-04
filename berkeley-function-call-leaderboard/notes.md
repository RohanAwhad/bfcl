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
