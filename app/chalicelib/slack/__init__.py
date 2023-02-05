import os

from slack_bolt import App

from .command import (
    ParseError,
    command_chat,
    command_chat_next,
    command_code,
    command_codeedit,
    command_codeinsert,
    command_help,
    command_image,
    command_image_variation,
    command_slacksearch,
    command_text,
    command_textedit,
    command_textinsert,
    parse,
)
from .matcher import match_file_share, match_message_replied

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_USER_TOKEN = os.environ.get("SLACK_USER_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")

bolt_app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    process_before_response=True,
)


@bolt_app.event("app_mention")
def reply_mention(event, context, say):
    ts = event["ts"]
    channel = event["channel"]
    user = event["user"]
    msg = event["text"]

    try:
        command, args = parse(msg)
    except ParseError:
        reply = "入力したコマンドと文章がおかしいよ！"
        say(f"<@{user}> {reply}")
        return

    if command == "help":
        command_help(say=say)
        return

    if command == "chat":
        command_chat(input=args[0], thread_ts=ts, say=say)
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

    if command == "slacksearch":
        command_slacksearch(
            query=args[0],
            count=10,
            client=bolt_app.client,
            user=user,
            channel=channel,
            say=say,
            user_token=SLACK_USER_TOKEN,
        )
        return

    # must be unreachable
    reply = "私、バグっているみたいです！"
    say(f"<@{user}> {reply}")


@bolt_app.event("message", matchers=[match_message_replied])
def reply_chat(event, say):
    user = event["user"]
    channel = event["channel"]
    ts = event.get("ts")
    thread_ts = event.get("thread_ts")
    if ts and thread_ts and ts != thread_ts:
        command_chat_next(
            client=bolt_app.client,
            user=user,
            channel=channel,
            thread_ts=thread_ts,
            say=say,
        )


@bolt_app.event("message", matchers=[match_file_share])
def reply_image(event, say):
    user = event["user"]
    channel = event["channel"]
    file_urls = [f["url_private"] for f in event["files"]]
    file_types = [f["filetype"] for f in event["files"]]
    command_image_variation(file_urls, file_types, bolt_app.client, user, channel, say)
