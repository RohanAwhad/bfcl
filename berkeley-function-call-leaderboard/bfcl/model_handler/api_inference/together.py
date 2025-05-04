import ast
import os
import re

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


    @override
    def decode_ast(self, result, language="Python"):
        # Extract function call info for all function calls
        def get_full_func_name(func):
            if isinstance(func, ast.Name):
                return func.id
            elif isinstance(func, ast.Attribute):
                return f"{get_full_func_name(func.value)}.{func.attr}"
            return None
        def extract_all_func_calls(code: str):
            tree = ast.parse(code)
            results = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func_name = get_full_func_name(node.func)
                    if func_name in ['print', 'json.dumps', 'json.dump']: continue

                    kwargs = {
                        kw.arg: ast.literal_eval(kw.value)
                        for kw in node.keywords if kw.arg is not None
                    }

                    results.append({func_name: kwargs})

            return results


        content_match = re.search(r'<\|CODE\|>(.*?)<\|CODE\|>', result, re.DOTALL)
        if not content_match: return []
        code_content = content_match.group(1).strip()
        decoded_output = extract_all_func_calls(code_content)
        return decoded_output
