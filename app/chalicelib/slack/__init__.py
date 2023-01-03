import os

from slack_bolt import App

from .command import (
    ParseError,
    command_code,
    command_codeedit,
    command_codeinsert,
    command_image,
    command_imageedit,
    command_text,
    command_textedit,
    command_textinsert,
    parse,
)

bolt_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)


@bolt_app.event("app_mention")
def reply_mention(event, say):
    channel = event["channel"]
    user = event["user"]
    msg = event["text"]

    try:
        command, args = parse(msg)
    except ParseError:
        reply = "入力したコマンドと文章がおかしいよ！"
        say(f"<@{user}> {reply}")
        return

    if command == "text":
        command_text(prompt=args[0], user=user, say=say)
        return

    if command == "textedit":
        command_textedit(input=args[0], instruction=args[1], user=user, say=say)
        return

    if command == "textinsert":
        command_textinsert(prompt=args[0], suffix=args[1], user=user, say=say)
        return

    if command == "code":
        command_code(prompt=args[0], user=user, say=say)
        return

    if command == "codeedit":
        command_codeedit(input=args[0], instruction=args[1], user=user, say=say)
        return

    if command == "codeinsert":
        command_codeinsert(prompt=args[0], suffix=args[1], user=user, say=say)
        return

    if command == "image":
        command_image(
            prompt=args[0], client=bolt_app.client, user=user, channel=channel, say=say
        )
        return

    # must be unreachable
    reply = "私、バグっているみたいです！"
    say(f"<@{user}> {reply}")


@bolt_app.event({"type": "message", "subtype": "file_share"})
def reply_image(event, say):
    user = event["user"]
    channel = event["channel"]
    file_urls = [f["url_private"] for f in event["files"]]
    file_types = [f["filetype"] for f in event["files"]]
    command_imageedit(file_urls, file_types, bolt_app.client, user, channel, say)
