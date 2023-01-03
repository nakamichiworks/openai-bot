import re
from typing import Literal, Sequence

COMMANDS = ("code", "codeedit", "codeinsert", "text", "textedit", "textinsert", "image")

Command = Literal[
    "code", "codeedit", "codeinsert", "text", "textedit", "textinsert", "image"
]
Args = Sequence[str]


class ParseError(Exception):
    pass


def parse(text: str) -> tuple[Command, Args]:
    # Strip the leading mention string
    match_mention = re.match(r"<@[0-9a-zA-Z]+>(.+)$", text.strip(), re.DOTALL)
    if not match_mention:
        raise ParseError
    text = match_mention.group(1).strip()

    # Main command parsing
    match_command = re.match(r"(\S+)\s+?(.+)", text, re.DOTALL)
    if not (match_command and match_command.group(1) in COMMANDS):
        command = "text"
        text = text
    else:
        command = match_command.group(1)
        text = match_command.group(2).strip()

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
