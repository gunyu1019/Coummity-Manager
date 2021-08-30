"""GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (c) 2021 gunyu1019

PUBG BOT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PUBG BOT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PUBG BOT.  If not, see <https://www.gnu.org/licenses/>.
"""

import discord
import logging
from discord.ext import commands
from discord.state import ConnectionState

from config.config import parser
from module.message import Channel

logger = logging.getLogger(__name__)
DBS = None


class SocketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._connection: ConnectionState = getattr(bot, "_connection")
        self.channel_discord = self._connection.get_channel(id=parser.getint("Channel", "welcome_message"))

        if self.channel_discord is not None:
            self.channel = Channel(
                state=self._connection,
                channel=self.channel_discord
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild: discord.Guild = member.guild

        embed = discord.Embed(description="{}님! {}에 오신것을 진심으로 환영합니다!".format(member.mention, guild.name))
        embed.set_author(
            name="{}#{}님 환영합니다!".format(member.name, member.discriminator),
            icon_url=str(guild.icon_url_as(format="png"))
        )

        member_role_id = parser.getint("Role", "member")
        member_role = guild.get_role(member_role_id)
        if member_role is not None:
            await member.add_roles([
                member_role
            ])
        await self.channel.send(embed=embed)
        return


def setup(client):
    client.add_cog(SocketReceive(client))
