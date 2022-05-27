import logging
from config.config import get_config

import discord
from discord.ext import commands

from discord.ext.interaction import ApplicationContext, ComponentsContext

logger = logging.getLogger(__name__)
logger_command = logging.getLogger(__name__ + ".command")
logger_guild = logging.getLogger(__name__ + ".guild")
parser = get_config()


class Events:
    def __init__(self, bot: discord.Client):
        self.bot = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'디스코드 봇 로그인이 완료되었습니다.')
        logger.info(f"디스코드봇 이름: {self.bot.user.name}")
        logger.info(f"디스코드봇 ID: {str(self.bot.user.id)}")
        logger.info(f"디스코드봇 버전: {discord.__version__}")

        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(
                name="https://yhs.kr/"
            )
        )

    @commands.Cog.listener()
    async def on_interaction_command(self, ctx: ApplicationContext):
        if ctx.guild is not None:
            logger_command.info(f"({ctx.guild} | {ctx.channel} | {ctx.author}) {ctx.content}")
        else:
            logger_command.info(f"(DM채널 | {ctx.author}) {ctx.content}")

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        if not isinstance(ctx, commands.Context):
            return

        if ctx.guild is not None:
            logger_command.info(f"({ctx.guild} | {ctx.channel} | {ctx.author}) {ctx.message.content}")
        else:
            logger_command.info(f"(DM채널 | {ctx.author}) {ctx.message.content}")

    @commands.Cog.listener()
    async def on_components_cancelled(self, ctx: ComponentsContext):
        if (
                ctx.custom_id.startswith("menu_selection") or
                ctx.custom_id.startswith("process_ticket") or
                ctx.custom_id.startswith("ticket") or
                ctx.custom_id == "developer_room"
        ):
            return

        embed = discord.Embed(
            title="\U000026A0 안내",
            description="상호작용을 찾을 수 없습니다. 명령어로 기능을 통하여 다시 이용해 주시기 바랍니다.",
            color=self.warning_color
        )
        embed.add_field(
            name="왜 상호작용을 찾을 수 없나요?",
            value="상호작용을 찾을 수 없는 대표적 이유는 `대기 시간초과(5분)`이 있습니다.",
            inline=False
        )
        await ctx.send(embed=embed, hidden=True)
        return


async def setup(client):
    client.add_icog(Events(client))
