import os
import json

import discord
from discord.ext import interaction

from config.config import parser
from config.log_config import log

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))
    prefixes = parser.get("DEFAULT", "default_prefixes")
    default_prefixes = list(json.loads(prefixes))

    log.info("건유1019 매니저를 불러오는 중입니다.")
    if parser.getboolean("DEFAULT", "AutoShard"):
        log.info("Config 파일에서 AutoShard가 켜져있습니다. AutoShard 기능을 킵니다.")
        bot = interaction.AutoShardedClient(
            command_prefix=default_prefixes,
            intents=discord.Intents.all(),
            global_sync_command=False,
            enable_debug_events=True
        )
    else:
        bot = interaction.Client(
            command_prefix=default_prefixes,
            intents=discord.Intents.all(),
            global_sync_command=False,
            enable_debug_events=True
        )

    bot.remove_command("help")
    bot.load_extensions('cogs', directory)

    token = parser.get("DEFAULT", "token")
    bot.run(token)
