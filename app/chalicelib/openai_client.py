import base64
import json
import os
import tempfile
from typing import Optional

# NOTE: Official API client is too heavy to deploy to AWS Lambda
# import openai
import requests
from langchain.llms.base import BaseLLM, LLMResult
from langchain.schema import Generation
from pydantic import BaseModel

from .util import crop_and_resize_image


class OpenAIClient(BaseLLM, BaseModel):
    base_url: str = "https://api.openai.com/v1"
    req: requests.Session = requests.Session()

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.req.headers.update(
            {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
        )

    # def __call__(self, prompt: str, stop: Optional[list[str]] = None) -> str:
    #     """Interoperable method for LangChain's LLMs"""
    #     return self.get_text_completion(prompt)
    def _generate(
        self, prompts: list[str], stop: Optional[list[str]] = None
    ) -> LLMResult:
        return LLMResult([[Generation("")]])

    def _llm_type(self) -> str:
        return ""

    def generate(
        self, prompts: list[str], stop: Optional[list[str]] = None
    ) -> LLMResult:
        return LLMResult([[Generation(self.get_text_completion(p))] for p in prompts])

    def get_text_completion(
        self, prompt: str, model: str = "text-davinci-003", max_tokens: int = 3000
    ) -> str:
        self.req.headers.update({"Content-Type": "application/json"})
        resp = self.req.post(
            f"{self.base_url}/completions",
            data=json.dumps(
                {
                    "model": model,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": 0.9,
                }
            ),
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["text"]
        return text

    def get_text_edit(
        self, input: str, instruction: str, model: str = "text-davinci-edit-001"
    ) -> str:
        self.req.headers.update({"Content-Type": "application/json"})
        resp = self.req.post(
            f"{self.base_url}/edits",
            data=json.dumps(
                {
                    "model": model,
                    "input": input,
                    "instruction": instruction,
                }
            ),
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["text"]
        return text

    def get_text_insertion(
        self,
        prompt: str,
        suffix: str,
        model: str = "text-davinci-003",
        max_tokens: int = 3000,
    ) -> str:
        self.req.headers.update({"Content-Type": "application/json"})
        resp = self.req.post(
            f"{self.base_url}/completions",
            data=json.dumps(
                {
                    "model": model,
                    "prompt": prompt,
                    "suffix": suffix,
                    "max_tokens": max_tokens,
                    "temperature": 0.9,
                }
            ),
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["text"]
        return text

    def get_code_completion(self, prompt: str) -> str:
        return self.get_text_completion(prompt, model="code-davinci-002")

    def get_code_edit(self, input: str, instruction: str) -> str:
        return self.get_text_edit(input, instruction, model="code-davinci-edit-001")

    def get_code_insertion(self, prompt: str, suffix: str) -> str:
        return self.get_text_insertion(prompt, suffix, model="code-davinci-002")

    def get_image(self, prompt: str) -> list[bytes]:
        self.req.headers.update({"Content-Type": "application/json"})
        resp = self.req.post(
            f"{self.base_url}/images/generations",
            data=json.dumps(
                {
                    "prompt": prompt,
                    "n": 3,
                    "size": "512x512",
                    "response_format": "b64_json",
                }
            ),
        )
        resp.raise_for_status()
        images = [base64.b64decode(img["b64_json"]) for img in resp.json()["data"]]
        return images

    def get_image_variation(self, image_file: str) -> list[bytes]:
        # Only square PNG up to 4MB is accepted by OpenAI
        _, resized_file = tempfile.mkstemp(suffix=".png")
        crop_and_resize_image(image_file, resized_file, size=(512, 512), format="png")

        with open(resized_file, "rb") as image:
            resp = self.req.post(
                f"{self.base_url}/images/variations",
                files={"image": image},
                data={
                    "n": 3,
                    "size": "512x512",
                    "response_format": "b64_json",
                },
            )
        os.remove(resized_file)
        resp.raise_for_status()
        images = [base64.b64decode(img["b64_json"]) for img in resp.json()["data"]]
        return images
