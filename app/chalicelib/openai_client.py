import base64
import os

import openai


class OpenAIClient:
    def __init__(self) -> None:
        openai.organization = os.getenv("OPENAI_ORGANIZATION")
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def get_completion(self, prompt: str) -> str:
        resp = openai.Completion.create(
            model="text-davinci-003", prompt=prompt, max_tokens=1000, temperature=0
        )
        text = resp.choices[0].text
        return text

    def get_image(self, prompt: str) -> bytes:
        resp = openai.Image.create(
            prompt=prompt, n=1, size="1024x1024", response_format="b64_json"
        )
        image_b64 = resp.data[0].b64_json
        img_bytes = base64.b64decode(image_b64)
        return img_bytes
