# Commands are responsible for communication with Slack.
# Do not write business logic here.

import os
import re
import tempfile
from typing import Literal, Sequence

from loguru import logger
from slack_bolt.context.say import Say
from slack_sdk import WebClient

from ..service import (
    answer_question_on_website,
    generate_code_completion,
    generate_code_edit,
    generate_code_insertion,
    generate_image,
    generate_image_variation,
    generate_initial_chat,
    generate_next_chat,
    generate_text_completion,
    generate_text_edit,
    generate_text_insertion,
    summarize_slack_messages,
)
from ..util import download_file

COMMANDS = (
    "help",
    "chat",
    "text",
    "textedit",
    "textinsert",
    "code",
    "codeedit",
    "codeinsert",
    "image",
    "slacksearch",
    "webqa",
)

Command = Literal[
    "help",
    "chat",
    "text",
    "textedit",
    "textinsert",
    "code",
    "codeedit",
    "codeinsert",
    "image",
    "slacksearch",
    "webqa",
]
Args = Sequence[str]


class ParseError(Exception):
    def __init__(self, message=""):
        super().__init__(message)


def parse(text: str) -> tuple[Command, Args]:
    # Strip the leading mention string
    match_mention = re.match(r"<@[0-9a-zA-Z]+>(.+)$", text.lstrip(), re.DOTALL)
    if not match_mention:
        raise ParseError(f"{text=}")
    text = match_mention.group(1).lstrip()

    # Main command parsing
    if re.match(r"help\s*", text, re.DOTALL):
        command = "help"
        text = ""
    else:
        match_command = re.match(r"(\S+)\s+?(.+)", text, re.DOTALL)
        if not (match_command and match_command.group(1) in COMMANDS):
            command = "text"
            text = text
        else:
            command = match_command.group(1)
            text = match_command.group(2).lstrip()

    # Subcommand parsing
    if command in ("codeedit", "textedit"):
        match_subcommand = re.match(
            r"(.*?)^instruction$(.*)", text, re.MULTILINE | re.DOTALL
        )
        if not match_subcommand:
            raise ParseError(f"{command=}, {text=}")
        args = match_subcommand.groups()
    elif command in ("codeinsert", "textinsert"):
        match_subcommand = re.match(
            r"(.*?)^suffix$(.*)", text, re.MULTILINE | re.DOTALL
        )
        if not match_subcommand:
            raise ParseError(f"{command=}, {text=}")
        args = match_subcommand.groups()
    elif command in ("webqa",):
        match_subcommand = re.match(r"<?(https?://\S+?)>?\s+?(.*)", text, re.DOTALL)
        if not match_subcommand:
            raise ParseError(f"{command=}, {text=}")
        args = match_subcommand.groups()
    else:
        args = [text]

    return command, args


def command_help(say: Say):
    say(
        "??????????????????\n"
        "```"
        "help: ???????????????????????????????????????\n"
        "chat: ????????????????????????\n"
        "text: ??????????????????????????????\n"
        "textedit: ??????????????????????????????\n"
        "textinsert: ??????????????????????????????\n"
        "code: ???????????????????????????\n"
        "codeedit: ???????????????????????????\n"
        "codeinsert: ???????????????????????????\n"
        "image: ????????????????????????????????????\n"
        "????????????????????????: ????????????????????????????????????????????????\n"
        "slacksearch: Slack?????????????????????????????????\n"
        "```"
    )


def command_chat(input: str, thread_ts: str, say: Say):
    reply = generate_initial_chat(input)
    say(f"{reply}", thread_ts=thread_ts)


def command_chat_next(
    client: WebClient, user: str, channel: str, thread_ts: str, say: Say
):
    resp = client.conversations_replies(channel=channel, ts=thread_ts)
    messages = resp.get("messages")
    if messages:
        # TODO: pagination handling
        reply = generate_next_chat(
            [(m["user"], m["text"]) for m in messages], user=user
        )
        say(f"{reply}", thread_ts=thread_ts)


def command_text(prompt: str, user: str, say: Say):
    reply = generate_text_completion(prompt)
    say(f"<@{user}>{reply}")


def command_textedit(input: str, instruction: str, user: str, say: Say):
    reply = generate_text_edit(input, instruction)
    say(f"<@{user}>{reply}")


def command_textinsert(prompt: str, suffix: str, user: str, say: Say):
    reply = generate_text_insertion(prompt, suffix)
    say(f"<@{user}>{reply}")


def command_code(prompt: str, user: str, say: Say):
    reply = generate_code_completion(prompt)
    say(f"<@{user}>\n{reply}")


def command_codeedit(input: str, instruction: str, user: str, say: Say):
    reply = generate_code_edit(input, instruction)
    say(f"<@{user}>\n{reply}")


def command_codeinsert(prompt: str, suffix: str, user: str, say: Say):
    reply = generate_code_insertion(prompt, suffix)
    say(f"<@{user}>\n{reply}")


def command_image(prompt: str, client: WebClient, user: str, channel: str, say: Say):
    reply, image_files = generate_image(prompt)
    if image_files:
        client.files_upload_v2(
            file_uploads=[{"file": file} for file in image_files],
            channel=channel,
            initial_comment=f"<@{user}> {reply}",
        )
        for file in image_files:
            os.remove(file)
    else:
        say(f"<@{user}> {reply}")


def command_image_variation(
    file_urls: list[str],
    file_types: list[str],
    client: WebClient,
    user: str,
    channel: str,
    say: Say,
):
    for file_url, file_type in zip(file_urls, file_types):
        _, input_file = tempfile.mkstemp(suffix=f".{file_type}")
        try:
            download_file(file_url, input_file, client.token)
        except:
            logger.exception(f"Failed to retrieve an image: {file_url=}")
            say("{file_url} ????????????????????????????????????????????????????????????")
            continue

        reply, output_files = generate_image_variation(input_file)
        os.remove(input_file)

        if output_files:
            client.files_upload_v2(
                file_uploads=[{"file": file} for file in output_files],
                channel=channel,
                initial_comment=f"<@{user}> {reply}",
            )
            for file in output_files:
                os.remove(file)
        else:
            say(f"<@{user}> {reply}")


def command_slacksearch(
    query: str,
    count: int,
    client: WebClient,
    user: str,
    channel: str,
    say: Say,
    user_token: str,
):
    resp = client.search_messages(
        query=query,
        count=count,
        token=user_token,
    )
    messages = [
        {
            "channel": m["channel"]["id"],
            "channel_name": m["channel"]["name"],
            "user": m["user"],
            "text": m["text"],
            "url": m["permalink"],
        }
        for m in resp["messages"]["matches"]
        if m["channel"]["is_private"] is False
    ]
    reply = summarize_slack_messages(messages)
    say(f"<@{user}> {reply}")


def command_webqa(url: str, question: str, user: str, say: Say):
    reply = answer_question_on_website(url, question)
    say(f"<@{user}> {reply}")
