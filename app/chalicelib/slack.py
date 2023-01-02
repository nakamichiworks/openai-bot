import os
import tempfile
from typing import Optional

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
        command, prompt = parse(msg)
    except ParseError:
        reply = "入力した文章がおかしいよ！"
        say(f"<@{user}> {reply}")
        return

    if command == "text":
        reply = generate_text(prompt)
        say(f"<@{user}> {reply}")
        return

    if command == "image":
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


def generate_text(prompt: str) -> str:
    openai = OpenAIClient()
    try:
        completion = openai.get_completion(prompt)
    except:
        logger.exception(f"Failed to get the text completion for '{prompt}'")
        reply = "ごめんなさい、文章が作れませんでした！"
    else:
        reply = completion
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
