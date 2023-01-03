import os
import tempfile
from typing import Optional
from urllib.request import Request, urlopen

from loguru import logger
from slack_bolt import App

from .command_parser import ParseError, parse
from .openai_client import OpenAIClient

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


@app.event("app_mention")
def reply_mention(event, say):
    channel = event["channel"]
    user = event["user"]
    msg = event["text"]

    try:
        command, args = parse(msg)
    except ParseError:
        reply = "入力した文章がおかしいよ！"
        say(f"<@{user}> {reply}")
        return

    if command == "text":
        prompt = args[0]
        reply = generate_text_completion(prompt)
        say(f"<@{user}> {reply}")
        return

    if command == "textedit":
        reply = generate_text_edit(*args)
        say(f"<@{user}> {reply}")
        return

    if command == "textinsert":
        reply = generate_text_insertion(*args)
        say(f"<@{user}> {reply}")
        return

    if command == "image":
        prompt = args[0]
        reply, images = generate_image(prompt)
        if images:
            app.client.files_upload_v2(
                file_uploads=[{"file": image} for image in images],
                channel=channel,
                initial_comment=f"<@{user}> {reply}",
            )
            for image in images:
                os.remove(image)
        else:
            say(f"<@{user}> {reply}")
        return

    raise Exception("私、バグっているみたいです！")  # must not be reached


@app.event({"type": "message", "subtype": "file_share"})
def reply_image(event, say):
    user = event["user"]
    channel = event["channel"]
    file_urls = [f["url_private"] for f in event["files"]]
    file_types = [f["filetype"] for f in event["files"]]

    for file_url, file_type in zip(file_urls, file_types):
        if file_type not in ("png",):
            # Only PNG up to 4MB is accepted by OpenAI
            say("f{file_url}はpngファイルじゃないから変換できないよ！）")
            continue

        req = Request(file_url)
        req.add_header("Authorization", f"Bearer {app.client.token}")
        try:
            input_image = urlopen(req).read()
        except:
            logger.exception(f"Failed to retrieve an image: {file_url}")
            say("{file_url}が取得できなかったよ！")
            continue

        _, input_file = tempfile.mkstemp(suffix=".png")
        with open(input_file, "wb") as f:
            f.write(input_image)

        reply, output_files = generate_image_variation(input_file)
        os.remove(input_file)

        if output_files:
            app.client.files_upload_v2(
                file_uploads=[{"file": file} for file in output_files],
                channel=channel,
                initial_comment=f"<@{user}> {reply}",
            )
            for file in output_files:
                os.remove(file)
        else:
            say(f"<@{user}> {reply}")


def generate_text_completion(prompt: str) -> str:
    openai = OpenAIClient()
    try:
        completion = openai.get_text_completion(prompt)
    except:
        logger.exception(f"Failed to get the text completion for '{prompt}'")
        reply = "ごめんなさい、文章が作れませんでした！"
    else:
        reply = completion
    return reply


def generate_text_edit(input: str, instruction: str) -> str:
    openai = OpenAIClient()
    try:
        edit = openai.get_text_edit(input, instruction)
    except:
        logger.exception(
            f"Failed to get the text edit for '{input}' and '{instruction}'"
        )
        reply = "ごめんなさい、文章を編集できませんでした！"
    else:
        reply = edit
    return reply


def generate_text_insertion(prompt: str, suffix: str) -> str:
    openai = OpenAIClient()
    try:
        insertion = openai.get_text_insertion(prompt, suffix)
    except:
        logger.exception(
            f"Failed to get the text insertion for '{prompt}' and '{suffix}'"
        )
        reply = "ごめんなさい、文章を挿入できませんでした！"
    else:
        reply = insertion
    return reply


def generate_image(prompt: str) -> tuple[str, Optional[list[str]]]:
    openai = OpenAIClient()
    try:
        images = openai.get_image(prompt)
    except:
        logger.exception(f"Failed to get the image for '{prompt}'")
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
    except:
        logger.exception(f"Failed to get the image variation for '{image_file}'")
        reply = "ごめんなさい、画像を変換できませんでした！"
        return reply, None

    reply = "画像が変換できたよ！"
    image_files = []
    for image in images:
        _, image_file = tempfile.mkstemp(suffix=".png")
        with open(image_file, "wb") as f:
            f.write(image)
        image_files.append(image_file)
    return reply, image_files
