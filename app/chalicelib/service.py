# Services are responsible for generating the reply message and additional content (e.g. images).
# They must be easily testable and shoud not depend on Slack SDK.

import tempfile
from typing import Optional

import langchain
from langchain import LLMChain, PromptTemplate
from loguru import logger

from .openai_client import OpenAIClient

CHAT_PREFIX = """AssistantはOpenAIによって訓練された巨大言語モデル（LLM）です。
Assistantは様々なタスクを補助できるように設計されています。簡単な質問に答えることはもちろん、色々な話題について深い解説や議論ができます。巨大言語モデルであるAssistantは、受け取った入力に対して人間のような文章を生成することができるので、自然な会話をしたり、目下の話題に沿った一貫性のある反応を返したりすることが可能です。
つまり、Assistantは様々なタスクの助けになる強力な道具であり、幅広い話題に対して価値ある洞察や情報を提供できます。具体的な質問に答えてほしいときであれ、単に特定の話題について雑談したいときであれ、Assistantはあなたの助けになるために待っています！"""
# Assistantはつねに学習と改善をし続けており、できることも増え続けています。大量の文章を理解して処理することができますし、その知識を使って色々な質問に対して正確で役立つ回答ができます。さらに、Assistantは入力に対して自分自身で文章を生成することができるので、議論に参加したり、幅広い話題について述べたり説明したりできます。


def generate_initial_chat(input: str) -> str:
    prompt = PromptTemplate(
        input_variables=["thread"],
        template=f"{CHAT_PREFIX}\n\n" + "{thread}",
    )
    chain = LLMChain(llm=langchain.OpenAI(), prompt=prompt)
    thread = f"人間: {input}\nAssistant: "
    try:
        reply = chain.run(thread)
    except Exception as e:
        logger.exception(f"Failed to get the text completion: {prompt=}")
        reply = f"ごめんなさい、文章が書けませんでした！\n```{type(e).__qualname__}: {e}```"
    return reply


def generate_next_chat(messages: list[tuple[str, str]], user: str) -> str:
    prompt = PromptTemplate(
        input_variables=["thread"],
        template=f"{CHAT_PREFIX}\n\n" + "{thread}",
    )
    chain = LLMChain(llm=langchain.OpenAI(), prompt=prompt)
    replies = []
    for usr, msg in messages[-3:]:  # short memory
        if usr == user:
            replies.append(f"人間: {msg}")
        else:
            # TODO: usr can be another human user
            replies.append(f"Assistant: {msg}")
    thread = "\n".join(replies + ["Assistant: "])
    try:
        reply = chain.run(thread)
    except Exception as e:
        logger.exception(f"Failed to get the text completion: {prompt=}")
        reply = f"ごめんなさい、文章が書けませんでした！\n```{type(e).__qualname__}: {e}```"
    return reply


def generate_text_completion(prompt: str) -> str:
    openai = OpenAIClient()
    reply = ""
    try:
        completion = openai.get_text_completion(prompt)
    except Exception as e:
        logger.exception(f"Failed to get the text completion: {prompt=}")
        reply = f"ごめんなさい、文章が書けませんでした！\n```{type(e).__qualname__}: {e}```"
    else:
        reply = completion
    return reply


def generate_text_edit(input: str, instruction: str) -> str:
    openai = OpenAIClient()
    try:
        edit = openai.get_text_edit(input, instruction)
    except Exception as e:
        logger.exception(f"Failed to get the text edit: {input=}, {instruction=}'")
        reply = f"ごめんなさい、文章を編集できませんでした！\n```{type(e).__qualname__}: {e}```"
    else:
        reply = edit
    return reply


def generate_text_insertion(prompt: str, suffix: str) -> str:
    openai = OpenAIClient()
    try:
        insertion = openai.get_text_insertion(prompt, suffix)
    except Exception as e:
        logger.exception(f"Failed to get the text insertion: {prompt=}, {suffix=}")
        reply = f"ごめんなさい、文章を挿入できませんでした！\n```{type(e).__qualname__}: {e}```"
    else:
        reply = insertion
    return reply


def generate_code_completion(prompt: str) -> str:
    openai = OpenAIClient()
    try:
        completion = openai.get_code_completion(prompt)
    except Exception as e:
        logger.exception(f"Failed to get the code completion: {prompt=}")
        reply = f"ごめんなさい、コードが書けませんでした！\n```{type(e).__qualname__}: {e}```"
    else:
        reply = completion
    return reply


def generate_code_edit(input: str, instruction: str) -> str:
    openai = OpenAIClient()
    try:
        edit = openai.get_code_edit(input, instruction)
    except Exception as e:
        logger.exception(f"Failed to get the code edit: {input=}, {instruction=}")
        reply = f"ごめんなさい、コードを編集できませんでした！\n```{type(e).__qualname__}: {e}```"
    else:
        reply = edit
    return reply


def generate_code_insertion(prompt: str, suffix: str) -> str:
    openai = OpenAIClient()
    try:
        insertion = openai.get_code_insertion(prompt, suffix)
    except Exception as e:
        logger.exception(f"Failed to get the code insertion: {prompt=}, {suffix=}")
        reply = f"ごめんなさい、コードを挿入できませんでした！\n```{type(e).__qualname__}: {e}```"
    else:
        reply = insertion
    return reply


def generate_image(prompt: str) -> tuple[str, Optional[list[str]]]:
    openai = OpenAIClient()
    try:
        images = openai.get_image(prompt)
    except Exception as e:
        logger.exception(f"Failed to get the image: {prompt=}")
        reply = f"ごめんなさい、画像を生成できませんでした！\n```{type(e).__qualname__}: {e}```"
        return reply, None

    reply = "画像ができたよ！"
    image_files = []
    for image in images:
        _, image_file = tempfile.mkstemp(suffix=".png")
        with open(image_file, "wb") as f:
            f.write(image)
        image_files.append(image_file)
    return reply, image_files


def generate_image_variation(image_file: str) -> tuple[str, Optional[list[str]]]:
    openai = OpenAIClient()
    try:
        images = openai.get_image_variation(image_file)
    except Exception as e:
        logger.exception(f"Failed to get the image variation: {image_file=}")
        reply = f"ごめんなさい、画像を生成できませんでした！\n```{type(e).__qualname__}: {e}```"
        return reply, None

    reply = "画像ができたよ！"
    image_files = []
    for image in images:
        _, image_file = tempfile.mkstemp(suffix=".png")
        with open(image_file, "wb") as f:
            f.write(image)
        image_files.append(image_file)
    return reply, image_files
