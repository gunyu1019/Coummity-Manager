import discord
import json
from discord.ext import commands as d_ext
from typing import Union

from module import commands
from module.interaction import SlashContext, Message


class Command:
    def __init__(self, bot: d_ext.Bot):
        self.bot = bot
        self.color = 0x0070ff

    @commands.command(name="파트너", permission=4)
    async def partner(self, ctx: Union[SlashContext, Message]):
        option1 = None
        prefix = (await self.bot.get_prefix(ctx))[0]
        if isinstance(ctx, SlashContext):
            option1 = ctx.options.get("종류")
        else:
            if len(ctx.options) > 0:
                option1 = ctx.options[0]
        if option1 is None:
            embed = discord.Embed(
                description="파트너 명령의 사용 방법은 다음과 같습니다.\n`{}파트너 등록`".format(prefix),
                colour=self.color
            )
            embed.set_author(
                name="파트너 도우미",
                icon_url=str(ctx.guild.icon_url_as(format="png"))
            )
            await ctx.send(embed=embed)
            return

        if option1 == "등록":
            if ctx.channel.id != 844622187809341450:
                embed = discord.Embed(
                    description="<#844622187809341450>를 통하여 파트너를 등록해보세요!\n파트너 등록은 문의 방안에서 사용이 가능합니다.",
                    colour=self.color
                )
                embed.set_author(
                    name="파트너 도우미",
                    icon_url=str(ctx.guild.icon_url_as(format="png"))
                )
                await ctx.send(embed=embed)
                return
            else:
                return

        return


def setup(client):
    return Command(client)
