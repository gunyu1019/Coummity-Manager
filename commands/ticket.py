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
from typing import Union

from config.config import parser
from module import commands as _command
from module.interaction import ApplicationContext
from module.components import ActionRow, Button
from module.message import MessageSendable, MessageCommand


class Command:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    @_command.command(name="티켓", permission=1, interaction=False)
    async def ticket(self, ctx: Union[ApplicationContext, MessageCommand]):
        option1 = None
        if isinstance(ctx, ApplicationContext):
            option1 = ctx.options.get("종류")
        elif isinstance(ctx, MessageCommand) and len(ctx.options) > 0:
            option1 = ctx.options[0]

        if option1 == "불러오기":
            channel = MessageSendable(
                state=getattr(self.bot, "_connection"),
                channel=ctx.guild.get_channel(parser.getint("Channel", "ticket_channel"))
            )
            embed = discord.Embed(title="\U0001F39F 문의하기", colour=self.color)
            embed.description = "__**파트너 신청**, **사용자 신고**, **버그 제보**__ 등 " \
                                "__**프로젝트**, **커뮤니티**__에 관련되어 개인적으로 건의하거나 문의하고 싶은 사항이 있으시다면, " \
                                "아래의 버튼에 있는 티켓을 통하여 문의를 부탁드립니다.\n" \
                                "장난식 티켓 생성은 처벌 대상입니다. 자제해주시길 부탁드립니다."
            await channel.send(
                embed=embed,
                components=[ActionRow(
                    components=[
                        Button(
                            custom_id="ticket_type1",
                            label="채널 티켓",
                            style=1,
                            emoji=discord.PartialEmoji(name="\U0001F39F")
                        ), Button(
                            custom_id="ticket_type2",
                            label="1:1(DM) 티켓",
                            style=1,
                            emoji=discord.PartialEmoji(name="\U0001F39F")
                        )
                    ]
                )]
            )
        elif option1 == "닫기":
            self.bot.dispatch("ticket_close", ctx)
        return


def setup(client):
    return Command(client)
