import os
import re
import tempfile

from loguru import logger
from slack_bolt import App

from .openai_client import OpenAIClient

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


@app.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>!")


@app.event("app_mention")
def reply(event, say):
    openai = OpenAIClient()
    channel = event["channel"]
    user = event["user"]
    text = event["text"].strip()
    match = re.match(r"<@[0-9a-zA-Z]+>(.+)$", text, re.DOTALL)

    if not match:
        resp = "入力した文章がおかしいよ～"
    else:
        prompt = match.groups()[0].strip()
        try:
            completion = openai.get_completion(prompt)
            image_bytes = openai.get_image(prompt)
        except:
            logger.exception(f"Failed to get the completion for '{prompt}'")
            resp = "ごめん、うまく答えられないよ～"
            image_file = None
        else:
            resp = completion
            _, image_file = tempfile.mkstemp(suffix=".png")
            with open(image_file, "wb") as f:
                f.write(image_bytes)

    say(f"<@{user}> {resp}")
    if image_file:
        app.client.files_upload(
            file=image_file,
            filetype="png",
            channels=channel,
            initial_comment=f"<@{user}>",
        )
        os.remove(image_file)
