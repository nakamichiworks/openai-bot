import base64
import os
import tempfile

import numpy as np
import openai
import spacy
import tiktoken
from openai.embeddings_utils import distances_from_embeddings

from .util import crop_and_resize_image

MAX_EMBEDDING_TOKENS = 8191
MAX_COMPLETION_TOKENS = 4097


class OpenAIClient:
    def __init__(self):
        openai.organization = os.getenv("OPENAI_ORGANIZATION")
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def get_text_completion(
        self, prompt: str, model: str = "text-davinci-003", max_tokens: int = 3000
    ) -> str:
        resp = openai.Completion.create(
            model=model, prompt=prompt, max_tokens=max_tokens, temperature=0.9
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
            temperature=0.9,
        )
        text = resp.choices[0].text
        return text

    def get_code_completion(self, prompt: str) -> str:
        return self.get_text_completion(prompt, model="code-davinci-002")

    def get_code_edit(self, input: str, instruction: str) -> str:
        return self.get_text_edit(input, instruction, model="code-davinci-edit-001")

    def get_code_insertion(self, prompt: str, suffix: str) -> str:
        return self.get_text_insertion(prompt, suffix, model="code-davinci-002")

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

    def get_text_embedding(self, input: str) -> np.ndarray:
        resp = openai.Embedding.create(input=input, model="text-embedding-ada-002")
        emb = np.array(resp.data[0].embedding)
        return emb

    def answer_question_on_text(self, text: str, question: str, max_ctx_len=1800):
        tokenizer = tiktoken.encoding_for_model("text-davinci-003")
        context = self._create_context(question, text, max_ctx_len=max_ctx_len)
        prompt = (
            "以下の文脈に基づいて質問に回答してください。"
            "もしこの文脈からは質問への回答が不明な場合、「わかりません」と回答してください。"
            f"\n\n文脈：{context}\n\n---\n\n質問：{question}\n回答："
        )
        max_tokens = MAX_COMPLETION_TOKENS - len(tokenizer.encode(prompt))
        answer = self.get_text_completion(prompt, max_tokens=max_tokens)
        return answer

    def _create_context(self, question: str, text: str, max_ctx_len: int = 1800) -> str:
        tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")
        q_emb = self.get_text_embedding(question)
        text_list = self._split_text(text)
        n_tokens_list = [len(tokenizer.encode(t)) for t in text_list]
        t_emb_list = [self.get_text_embedding(t) for t in text_list]
        distances = distances_from_embeddings(
            q_emb, t_emb_list, distance_metric="cosine"
        )
        text_and_dist_list = [
            (t, n, d) for t, n, d in zip(text_list, n_tokens_list, distances)
        ]
        returns = []
        cur_ctx_len = 0
        for text, n_tokens, dist in sorted(text_and_dist_list, key=lambda x: x[2]):
            cur_ctx_len += n_tokens + 4
            if cur_ctx_len > max_ctx_len:
                break
            returns.append(text)
        return "\n\n###\n\n".join(returns)

    def _split_text(self, text: str, max_tokens: int = 500) -> list[str]:
        max_tokens = min(max_tokens, MAX_EMBEDDING_TOKENS)
        tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")
        nlp = spacy.load("ja_ginza")
        sentences = [str(sent) for sent in nlp(text).sents]
        n_tokens_list = [len(tokenizer.encode(sentence)) for sentence in sentences]
        chunks = []
        n_tokens_so_far = 0
        chunk: list[str] = []
        for sentence, n_tokens in zip(sentences, n_tokens_list):
            if n_tokens_so_far + n_tokens > max_tokens:
                joined = "".join(chunk).strip()
                if joined:
                    chunks.append(joined)
                chunk = []
                n_tokens_so_far = 0
            if n_tokens > max_tokens:
                # TODO: better handling of long sentences
                continue
            chunk.append(sentence)
            n_tokens_so_far += n_tokens
        return chunks
