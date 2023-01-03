# Commands are responsible for communication with Slack.
# Do not write business logic here.

import os
import re
import tempfile
from typing import Callable, Literal, Sequence

from loguru import logger
from slack_sdk import WebClient

from ..service import (
    generate_code_completion,
    generate_code_edit,
    generate_code_insertion,
    generate_image,
    generate_image_variation,
    generate_text_completion,
    generate_text_edit,
    generate_text_insertion,
)
from ..util import download_file

COMMANDS = ("code", "codeedit", "codeinsert", "text", "textedit", "textinsert", "image")

Command = Literal[
    "code", "codeedit", "codeinsert", "text", "textedit", "textinsert", "image"
]
Args = Sequence[str]


class ParseError(Exception):
    pass


def parse(text: str) -> tuple[Command, Args]:
    # Strip the leading mention string
    match_mention = re.match(r"<@[0-9a-zA-Z]+>(.+)$", text.lstrip(), re.DOTALL)
    if not match_mention:
        raise ParseError
    text = match_mention.group(1).lstrip()

    # Main command parsing
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
            raise ParseError
        args = match_subcommand.groups()
    elif command in ("codeinsert", "textinsert"):
        match_subcommand = re.match(
            r"(.*?)^suffix$(.*)", text, re.MULTILINE | re.DOTALL
        )
        if not match_subcommand:
            raise ParseError
        args = match_subcommand.groups()
    else:
        args = [text]

    return command, args


def command_text(prompt: str, user: str, say: Callable[[str], None]):
    reply = generate_text_completion(prompt)
    say(f"<@{user}>\n{reply}")


def command_textedit(
    input: str, instruction: str, user: str, say: Callable[[str], None]
):
    reply = generate_text_edit(input, instruction)
    say(f"<@{user}>\n{reply}")


def command_textinsert(prompt: str, suffix: str, user: str, say: Callable[[str], None]):
    reply = generate_text_insertion(prompt, suffix)
    say(f"<@{user}>\n{reply}")


def command_code(prompt: str, user: str, say: Callable[[str], None]):
    reply = generate_code_completion(prompt)
    say(f"<@{user}>\n{reply}")


def command_codeedit(
    input: str, instruction: str, user: str, say: Callable[[str], None]
):
    reply = generate_code_edit(input, instruction)
    say(f"<@{user}>\n{reply}")


def command_codeinsert(prompt: str, suffix: str, user: str, say: Callable[[str], None]):
    reply = generate_code_insertion(prompt, suffix)
    say(f"<@{user}>\n{reply}")


def command_image(
    prompt: str, client: WebClient, user: str, channel: str, say: Callable[[str], None]
):
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


def command_imageedit(
    file_urls: list[str],
    file_types: list[str],
    client: WebClient,
    user: str,
    channel: str,
    say: Callable[[str], None],
):
    for file_url, file_type in zip(file_urls, file_types):
        _, input_file = tempfile.mkstemp(suffix=f".{file_type}")
        try:
            download_file(file_url, input_file, client.token)
        except:
            logger.exception(f"Failed to retrieve an image: {file_url=}")
            say("{file_url} の画像が取得できないので編集できないよ！")
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
