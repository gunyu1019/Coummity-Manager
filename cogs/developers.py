import logging

import discord
from discord.ext import commands
from discord.ext import interaction
from discord.state import ConnectionState
from typing import Optional

from config.config import get_config
from utils.directory import directory

logger = logging.getLogger(__name__)
parser = get_config()


class DeveloperReceive(commands.Cog):
    def __init__(self, bot: interaction.Client):
        self.bot = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self._connection: ConnectionState = getattr(bot, "_connection")

        self.channel_discord: Optional[int] = None
        self.channel: Optional[discord.TextChannel] = None
        self.category: Optional[discord.CategoryChannel] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel_discord = self.bot.get_channel(id=parser.getint("Channel", "developer_channel"))
        self.category = self.bot.get_channel(id=parser.getint("Developer", "category"))

        if self.channel_discord is not None:
            self.channel = interaction.MessageSendable(
                state=self._connection,
                channel=self.channel_discord
            )

    @commands.Cog.listener()
    async def on_components(self, ctx: interaction.ComponentsContext):
        if ctx.custom_id == "developer_room":
            return
        return

    @commands.command()
    async def developer(self, ctx):
        if 844620551153909760 not in [role.id for role in ctx.author.roles]:
            await ctx.send("권한이 부족합니다.")
            return

        channel = interaction.MessageSendable(
            state=self._connection,
            channel=ctx.guild.get_channel(parser.getint("Channel", "ticket_channel"))
        )
        embed = discord.Embed(title="\U0001F5A5 개발자 정보", colour=self.color)
        embed.description = (
            "개발자 역할을 갖고 있다면, 자유롭게 자신만의 채널을 생성해보세요!"
            "방 안에서 자유롭게 디스코드 봇을 디버그하거나, 프로젝트를 홍보해보세요!"
        )
        await channel.send(
            embed=embed,
            components=[interaction.ActionRow(
                components=[
                    interaction.Button(
                        custom_id="developer_room",
                        label="채널 생성",
                        style=1,
                        emoji=discord.PartialEmoji(name="\U0001F4C1")
                    )
                ]
            )]
        )


def setup(client):
    pass
    # client.add_cog(DeveloperReceive(client))
