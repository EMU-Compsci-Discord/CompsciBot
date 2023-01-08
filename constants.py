"""
Various constants used throughout the bot.
"""

from typing import Optional, TypedDict
import tomllib
from nextcord import Color

MAIN_COLOR = Color(0xD75BF4)
ERROR_COLOR = Color(0xE02B2B)
SUCCESS_COLOR = Color(0x42F56C)
WARNING_COLOR = Color(0xF59E42)
INFO_COLOR = Color(0x4299F5)


class DBConfig(TypedDict):
    """
    The database config from the config file.
    """

    host: str
    user: str
    password: str
    database: str


class Config(TypedDict):
    """
    The config file.
    """

    token: str
    application_id: str
    owners: list[int]
    blacklist: list[int]
    db: Optional[DBConfig]


config: Config

with open("config.toml", "rb") as f:
    config = tomllib.load(f)
