import os
import json

import discord
from discord.ext import commands

from config.config import parser
from config.log_config import log

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    prefixes = parser.get("DEFAULT", "default_prefixes")
    default_prefixes = list(json.loads(prefixes))

    log.info("건유1019 매니저를 불러오는 중입니다.")
    if parser.getboolean("DEFAULT", "AutoShard"):
        log.info("Config 파일에서 AutoShard가 켜져있습니다. AutoShard 기능을 킵니다.")
        bot = commands.AutoShardedBot(command_prefix=default_prefixes, intents=discord.Intents.default())
    else:
        bot = commands.Bot(command_prefix=default_prefixes, intents=discord.Intents.default())

    bot.remove_command("help")
    cogs = ["cogs." + file[:-3] for file in os.listdir(f"{directory}/cogs") if file.endswith(".py")]
    for cog in cogs:
        bot.load_extension(cog)

    token = parser.get("DEFAULT", "token")
    bot.run(token)
