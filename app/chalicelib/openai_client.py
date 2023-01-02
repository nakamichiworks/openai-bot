import base64
import os

import openai


class OpenAIClient:
    def __init__(self) -> None:
        openai.organization = os.getenv("OPENAI_ORGANIZATION")
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def get_completion(self, prompt: str) -> str:
        resp = openai.Completion.create(
            model="text-davinci-003", prompt=prompt, max_tokens=3000, temperature=0
        )
        text = resp.choices[0].text
        return text

    def get_image(self, prompt: str) -> list[bytes]:
        resp = openai.Image.create(
            prompt=prompt, n=3, size="512x512", response_format="b64_json"
        )
        images = [base64.b64decode(img.b64_json) for img in resp.data]
        return images

    def get_edit(self, input: str, instruction: str):
        resp = openai.Edit.create(
            model="text-davinci-edit-001",
            input=input,
            instruction=instruction,
        )
        text = resp.choices[0].text
        return text
