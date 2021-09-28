import logging

import discord
from discord.ext import commands
from typing import Union

from module.interaction import ApplicationContext
from module.message import MessageCommand

logger = logging.getLogger(__name__)
logger_command = logging.getLogger(__name__ + ".command")
logger_guild = logging.getLogger(__name__ + ".guild")


class Events(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'디스코드 봇 로그인이 완료되었습니다.')
        logger.info(f"디스코드봇 이름: {self.bot.user.name}")
        logger.info(f"디스코드봇 ID: {str(self.bot.user.id)}")
        logger.info(f"디스코드봇 버전: {discord.__version__}")

        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(
                name="오늘도 힘차게 서버를 관리해보자!"
            )
        )

    @commands.Cog.listener()
    async def on_command(self, ctx: Union[ApplicationContext, MessageCommand]):
        if ctx.guild is not None:
            logger_command.info(f"({ctx.guild} | {ctx.channel} | {ctx.author}) {ctx.content}")
        else:
            logger_command.info(f"(DM채널 | {ctx.author}) {ctx.content}")


def setup(client):
    client.add_cog(Events(client))
