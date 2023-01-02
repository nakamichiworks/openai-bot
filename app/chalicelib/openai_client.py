import os

import openai


class OpenAIClient:
    def __init__(self) -> None:
        openai.organization = os.getenv("OPENAI_ORGANIZATION")
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def get_completion(self, prompt: str):
        completion = openai.Completion.create(
            model="text-davinci-003", prompt=prompt, max_tokens=1000, temperature=0
        )
        text = completion.choices[0].text
        return text
