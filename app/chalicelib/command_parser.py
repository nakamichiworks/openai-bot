import re
from typing import Literal

Command = Literal["text", "image"]


class ParseError(Exception):
    pass


def parse(text: str) -> tuple[Command, str]:
    text = text.strip()

    # Strip the leading mention string
    match_mention = re.match(r"<@[0-9a-zA-Z]+>(.+)$", text, re.DOTALL)
    if not match_mention:
        raise ParseError
    text = match_mention.groups()[0].strip()

    # Extract the command string
    match_command = re.match(r"(\S+)\s+?(.+)", text, re.DOTALL)
    if match_command and match_command.groups()[0] in ("text", "image"):
        command = match_command.groups()[0]
        prompt = match_command.groups()[1].strip()
    else:
        command = "text"
        prompt = text

    return command, prompt
