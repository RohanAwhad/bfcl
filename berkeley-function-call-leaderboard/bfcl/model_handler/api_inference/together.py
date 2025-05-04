import os

from bfcl.model_handler.api_inference.openai import OpenAIHandler
from bfcl.model_handler.model_style import ModelStyle
from openai import OpenAI


class TogetherAPIHandler(OpenAIHandler):
    def __init__(self, model_name, temperature) -> None:
        super().__init__(model_name, temperature)
        self.model_style = ModelStyle.OpenAI
        self.client = OpenAI(
            base_url="https://api.together.xyz/v1", api_key=os.getenv("TOGETHER_API_KEY")
        )
