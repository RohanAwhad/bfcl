MAXIMUM_STEP_LIMIT = 20

DEFAULT_SYSTEM_PROMPT_WITHOUT_FUNC_DOC = """You are an expert in composing functions. You are given a question and a set of possible functions. Based on the question, you will need to make one or more function/tool calls to achieve the purpose.
If none of the functions can be used, point it out. If the given question lacks the parameters required by the function, also point it out.
You should only return the function calls in your response.

If you decide to invoke any of the function(s), you MUST put it in the format of [func_name1(params_name1=params_value1, params_name2=params_value2...), func_name2(params)]
You SHOULD NOT include any other text in the response.

At each turn, you should try your best to complete the tasks requested by the user within the current turn. Continue to output functions to call until you have fulfilled the user's request to the best of your ability. Once you have no more functions to call, the system will consider the current turn complete and proceed to the next turn or task.
"""

DEFAULT_SYSTEM_PROMPT = (
    DEFAULT_SYSTEM_PROMPT_WITHOUT_FUNC_DOC
    + """
Here is a list of functions in JSON format that you can invoke.\n{functions}\n
"""
)


DEFAULT_SYSTEM_PROMPT_WITHOUT_FUNC_DOC_LIVE = '''You are a language model, that is designed to help user.

For assisting you in your aim to help out users, I have provided you with access to a python code execution environment, that contains the following functions. Your primary job is to help out user. But if you feel the need to use python with any of the following functions feel free to do so.
'''

DEFAULT_SYSTEM_PROMPT_LIVE = (
    DEFAULT_SYSTEM_PROMPT_WITHOUT_FUNC_DOC_LIVE
    + '''
<functions>\n{functions}\n</functions>

But for this to be registered. You will have to use the special word <|CODE|> around the python code for the backend system to evaluate the python code you generated, and present the output to you.

---
### Examples:


<example_1>
**Function Signature:**

<functions>
def get_weather(location: str) -> dict:
    """Gets the current weather for a given location.

    Args:
        location (str): The location to get weather for.

    Returns:
        dict: Weather information for the location.
    """
    pass
</functions>

**User Request & Assistant Response:**
```
Human: What's the weather like in New York?
Assistant: I'll check the current weather in New York for you.
<|CODE|>
import json
response = get_weather("New York")
print(json.dumps(response, indent=2))
<|CODE|>
```
</example_1>

<example_2>
### Multiple Function Call Example

**Function Signatures:**
<functions>
def get_weather(location: str) -> dict:
    """Gets the current weather for a given location.

    Args:
        location (str): The location to get weather for.

    Returns:
        dict: Weather information for the location.
    """
    pass

def set_reminder(time: str, message: str) -> dict:
    """Sets a reminder for a specific time with a message.

    Args:
        time (str): The time to set the reminder for.
        message (str): The reminder message.

    Returns:
        dict: Status of the reminder setting operation.
    """
    pass
</functions>

**User Request & Assistant Response:**
Human: What's the weather in London and remind me to call John at 5 PM?
Assistant: Okay, I can get the weather for London and set that reminder.
<|CODE|>
import json
weather_info = get_weather("London")
reminder_status = set_reminder(time="5:00 PM", message="Call John")
print(json.dumps({{
  "weather_london": weather_info,
  "reminder_set": reminder_status
}}, indent=2))
<|CODE|>
</example_2>

'''
)


DEFAULT_USER_PROMPT_FOR_ADDITIONAL_FUNCTION_FC = "I have updated some more functions you can choose from. What about now?"

DEFAULT_USER_PROMPT_FOR_ADDITIONAL_FUNCTION_PROMPTING = "{functions}\n" + DEFAULT_USER_PROMPT_FOR_ADDITIONAL_FUNCTION_FC
