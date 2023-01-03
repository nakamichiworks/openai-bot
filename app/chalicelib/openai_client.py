import base64
import os
import tempfile

import openai

from .util import crop_and_resize_image


class OpenAIClient:
    def __init__(self) -> None:
        openai.organization = os.getenv("OPENAI_ORGANIZATION")
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def get_text_completion(
        self, prompt: str, model: str = "text-davinci-003", max_tokens: int = 3000
    ) -> str:
        resp = openai.Completion.create(
            model=model, prompt=prompt, max_tokens=max_tokens, temperature=0
        )
        text = resp.choices[0].text
        return text

    def get_text_edit(
        self, input: str, instruction: str, model: str = "text-davinci-edit-001"
    ) -> str:
        resp = openai.Edit.create(
            model=model,
            input=input,
            instruction=instruction,
        )
        text = resp.choices[0].text
        return text

    def get_text_insertion(
        self,
        prompt: str,
        suffix: str,
        model: str = "text-davinci-003",
        max_tokens: int = 3000,
    ) -> str:
        resp = openai.Completion.create(
            model=model,
            prompt=prompt,
            suffix=suffix,
            max_tokens=max_tokens,
            temperature=0,
        )
        text = resp.choices[0].text
        return text

    def get_code_completion(self, prompt: str) -> str:
        return self.get_text_completion(
            prompt, model="code-davinci-002", max_tokens=6000
        )

    def get_code_edit(self, input: str, instruction: str) -> str:
        return self.get_text_edit(input, instruction, model="code-davinci-edit-001")

    def get_code_insertion(self, prompt: str, suffix: str) -> str:
        return self.get_text_insertion(
            prompt, suffix, model="code-davinci-002", max_tokens=6000
        )

    def get_image(self, prompt: str) -> list[bytes]:
        resp = openai.Image.create(
            prompt=prompt, n=3, size="512x512", response_format="b64_json"
        )
        images = [base64.b64decode(img.b64_json) for img in resp.data]
        return images

    def get_image_variation(self, image_file: str) -> list[bytes]:
        # Only square PNG up to 4MB is accepted by OpenAI
        _, resized_file = tempfile.mkstemp(suffix=".png")
        crop_and_resize_image(image_file, resized_file, size=(512, 512), format="png")
        resp = openai.Image.create_variation(
            image=open(resized_file, "rb"),
            n=3,
            size="512x512",
            response_format="b64_json",
        )
        os.remove(resized_file)
        images = [base64.b64decode(img.b64_json) for img in resp.data]
        return images
