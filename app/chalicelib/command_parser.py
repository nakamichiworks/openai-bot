import re
from typing import Literal, Sequence, Union

COMMANDS = ("text", "textedit", "image")

Command = Literal["text", "textedit", "image"]
Args = Sequence[str]


class ParseError(Exception):
    pass


def parse(text: str) -> tuple[Command, Args]:
    # Strip the leading mention string
    match_mention = re.match(r"<@[0-9a-zA-Z]+>(.+)$", text.strip(), re.DOTALL)
    if not match_mention:
        raise ParseError
    text = match_mention.group(1).strip()

    # Extract the command and the following text
    match_command = re.match(r"(\S+)\s+?(.+)", text, re.DOTALL)
    if not (match_command and match_command.group(1) in COMMANDS):
        command = "text"
        text = text
    else:
        command = match_command.group(1)
        text = match_command.group(2).strip()

    # Subcommand parsing
    if command == "textedit":
        match_subcommand = re.match(
            r"(.*?)^instruction$(.*)", text, re.MULTILINE | re.DOTALL
        )
        if not match_subcommand:
            raise ParseError
        args = match_subcommand.groups()
    else:
        args = [text]

    return command, args
