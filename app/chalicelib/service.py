# Services are responsible for generating the reply message and additional content (e.g. images).
# They must be easily testable and shoud not depend on Slack SDK.

import tempfile
from typing import Optional

from loguru import logger
from openai.error import OpenAIError

from .openai_client import OpenAIClient


def generate_text_completion(prompt: str) -> str:
    openai = OpenAIClient()
    reply = ""
    try:
        completion = openai.get_text_completion(prompt)
    except OpenAIError as e:
        reply = f"ごめんなさい、文章が書けませんでした！\n```{type(e).__qualname__}: {e}```"
    except:
        logger.exception(
            f"Failed to get the text completion for unknown reason: {prompt=}"
        )
        reply = "ごめんなさい、文章が書けませんでした！"
    else:
        reply = completion
    return reply


def generate_text_edit(input: str, instruction: str) -> str:
    openai = OpenAIClient()
    try:
        edit = openai.get_text_edit(input, instruction)
    except OpenAIError as e:
        reply = f"ごめんなさい、文章を編集できませんでした！\n```{type(e).__qualname__}: {e}```"
    except:
        logger.exception(
            f"Failed to get the text edit for unknown reason: {input=}, {instruction=}'"
        )
        reply = "ごめんなさい、文章を編集できませんでした！"
    else:
        reply = edit
    return reply


def generate_text_insertion(prompt: str, suffix: str) -> str:
    openai = OpenAIClient()
    try:
        insertion = openai.get_text_insertion(prompt, suffix)
    except OpenAIError as e:
        reply = f"ごめんなさい、文章を挿入できませんでした！\n```{type(e).__qualname__}: {e}```"
    except:
        logger.exception(
            f"Failed to get the text insertion for unknown reason: {prompt=}, {suffix=}"
        )
        reply = "ごめんなさい、文章を挿入できませんでした！"
    else:
        reply = insertion
    return reply


def generate_code_completion(prompt: str) -> str:
    openai = OpenAIClient()
    try:
        completion = openai.get_code_completion(prompt)
    except OpenAIError as e:
        reply = f"ごめんなさい、コードが書けませんでした！\n```{type(e).__qualname__}: {e}```"
    except:
        logger.exception(
            f"Failed to get the code completion for unknown reason: {prompt=}"
        )
        reply = "ごめんなさい、コードが書けませんでした！"
    else:
        reply = completion
    return reply


def generate_code_edit(input: str, instruction: str) -> str:
    openai = OpenAIClient()
    try:
        edit = openai.get_code_edit(input, instruction)
    except OpenAIError as e:
        reply = f"ごめんなさい、コードを編集できませんでした！\n```{type(e).__qualname__}: {e}```"
    except:
        logger.exception(
            f"Failed to get the code edit for unknown reason: {input=}, {instruction=}"
        )
        reply = "ごめんなさい、コードを編集できませんでした！"
    else:
        reply = edit
    return reply


def generate_code_insertion(prompt: str, suffix: str) -> str:
    openai = OpenAIClient()
    try:
        insertion = openai.get_code_insertion(prompt, suffix)
    except OpenAIError as e:
        reply = f"ごめんなさい、コードを挿入できませんでした！\n```{type(e).__qualname__}: {e}```"
    except:
        logger.exception(
            f"Failed to get the code insertion for unknown reason: {prompt=}, {suffix=}"
        )
        reply = "ごめんなさい、コードを挿入できませんでした！"
    else:
        reply = insertion
    return reply


def generate_image(prompt: str) -> tuple[str, Optional[list[str]]]:
    openai = OpenAIClient()
    try:
        images = openai.get_image(prompt)
    except OpenAIError as e:
        reply = f"ごめんなさい、画像が作れませんでした！\n```{type(e).__qualname__}: {e}```"
        return reply, None
    except:
        logger.exception(f"Failed to get the image for unknown reason: {prompt=}")
        reply = "ごめんなさい、画像が作れませんでした！"
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
    except OpenAIError as e:
        reply = f"ごめんなさい、画像を編集できませんでした！\n```{type(e).__qualname__}: {e}```"
        return reply, None
    except:
        logger.exception(
            f"Failed to get the image variation for unknown reason: {image_file=}"
        )
        reply = "ごめんなさい、画像を編集できませんでした！"
        return reply, None

    reply = "画像が変換できたよ！"
    image_files = []
    for image in images:
        _, image_file = tempfile.mkstemp(suffix=".png")
        with open(image_file, "wb") as f:
            f.write(image)
        image_files.append(image_file)
    return reply, image_files
