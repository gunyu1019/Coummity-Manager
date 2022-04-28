import discord
from enum import Enum
from typing import NamedTuple
from config.config import get_config


parser = get_config()
parser_comment = get_config("comment")
color = int(parser.get("Color", "default"), 16)
error_color = int(parser.get("Color", "error"), 16)
warning_color = int(parser.get("Color", "warning"), 16)


class LevelInfo(NamedTuple):
    id: str
    title: str
    color: int


class Level(Enum):
    Debug = LevelInfo("Debug", "디버그", color)
    Info = LevelInfo("Info", "정보", color)
    Warning = LevelInfo("Warning", "경고(Warning)", warning_color)
    Error = LevelInfo("Error", "에러(Error)", error_color)


def get_exception_comment(level: Level, code: str) -> discord.Embed:
    embed = discord.Embed(title=level.value.title)
    embed.description = parser_comment.get(level.value.id, code)
    embed.colour = level.value.color
    return embed
