import os

from bfcl.constants.default_prompts import DEFAULT_SYSTEM_PROMPT_LIVE
from bfcl.model_handler.api_inference.openai import OpenAIHandler
from bfcl.model_handler.model_style import ModelStyle
from bfcl.model_handler.utils import (
    func_doc_to_python_func_signature,
    system_prompt_pre_processing_chat_model,
)
from openai import OpenAI
from overrides import override


class TogetherAPIHandler(OpenAIHandler):
    def __init__(self, model_name, temperature) -> None:
        super().__init__(model_name, temperature)
        self.model_style = ModelStyle.OpenAI
        self.client = OpenAI(
            base_url="https://api.together.xyz/v1", api_key=os.getenv("TOGETHER_API_KEY")
        )


    @override
    def _pre_query_processing_prompting(self, test_entry: dict) -> dict:
        functions: list = test_entry["function"]
        test_category: str = test_entry["id"].rsplit("_", 1)[0]

        functions = func_doc_to_python_func_signature(functions, test_category)

        test_entry["question"][0] = system_prompt_pre_processing_chat_model(
            test_entry["question"][0], functions, test_category, system_prompt_template = DEFAULT_SYSTEM_PROMPT_LIVE
        )

        return {"message": []}

    @override
    def _query_prompting(self, inference_data: dict):
        inference_data["inference_input_log"] = {"message": repr(inference_data["message"])}
        res = self.generate_with_backoff(
            messages=inference_data["message"],
            model=self.model_name,
            temperature=self.temperature,
            tool_choice="none",
            tools=[],
        )
        return res
