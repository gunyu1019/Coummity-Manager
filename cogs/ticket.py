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
import os
import json
from discord.ext import commands
from discord.state import ConnectionState
from typing import Optional

from config.config import parser
from module.components import ActionRow, Button
from module.interaction import ComponentsContext
from module.message import MessageSendable
from utils.directory import directory

logger = logging.getLogger(__name__)


class TicketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open(os.path.join(directory, "data", "ticket.json"), "r", encoding='utf-8') as file:
            self.ticket = json.load(fp=file)
        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.already_ticket_opened = discord.Embed(
            title="안내(Warning)",
            description="티켓이 이미 열려있습니다. 만일 티켓이 닫혀있는데, 해당 안내 문구가 나왔을 경우 디스코드 봇 관리자에게 문의해주세요.",
            color=self.warning_color
        )
        self.ticket_mode_not_found = discord.Embed(
            title="에러(Error)",
            description="티켓을 생성하는 도중 에러가 발생하였습니다. 자세한 사항은 디스코드 개발자에게 문의해주시기 바랍니다.",
            color=self.error_color
        )
        self.ticket_close_not_found = discord.Embed(
            title="안내(Warning)",
            description="닫으시려는 티켓을 찾을 수 없습니다.",
            color=self.warning_color
        )
        self.ticket_process = discord.Embed(
            title="티켓(Ticket)",
            description="정상적으로 티켓을 열었습니다. {ticket_channel} 를 참조해주세요.",
            color=self.color
        )

        self.already_ticket_opened.description += "\n```WARNING CODE: TICKET-ALREADY-OPENED(01)\n```"
        self.ticket_close_not_found.description += "```\nWARNING CODE: TICKET-NOT-FOUND\n```"
        self.ticket_mode_not_found.description += "```\nERROR CODE: TICKET-MODE-NOT-FOUND\n" \
                                                  "GUILD-TICKET-MODE: {ticket_mode} (0 <= TICKET MODE <= 3)\n```"

        self._connection: ConnectionState = getattr(bot, "_connection")

        self.channel_discord: Optional[int] = None
        self.template = parser.get("Ticket", "template")
        self.channel: Optional[discord.TextChannel] = None
        self.category: Optional[discord.CategoryChannel] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel_discord = self._connection.get_channel(id=parser.getint("Channel", "ticket_channel"))
        self.category = self._connection.get_channel(id=parser.getint("Ticket", "category"))

        if self.channel_discord is not None:
            self.channel = MessageSendable(
                state=self._connection,
                channel=self.channel_discord
            )

    @staticmethod
    def convert_template(name: str, guild: discord.Guild, member: discord.Member, **kwargs):
        return name.format(
            guild=guild.name,
            guild_id=guild.id,
            member=str(member),
            member_name=member.name,
            member_tag=member.discriminator,
            member_id=member.id,
            number=kwargs.get("count")
        )

    @commands.Cog.listener()
    async def on_ticket(self, context: ComponentsContext):
        mode = 0
        if context.custom_id == "ticket_type1":
            mode = 1
        elif context.custom_id == "ticket_type2":
            mode = 2

        for check_ticket in self.ticket:
            if context.author.id == check_ticket.get("author"):
                await context.send(embed=self.already_ticket_opened, hidden=True)
                return

        count = None
        if '{number}' in self.template:
            cut_names = self.template.split("{number}")
            opened_number = []
            if len(cut_names) > 1:
                front_name = cut_names[0]
                end_name = cut_names[1]
                channels = self.category.channels

                for channel in channels:
                    number = channel.name.lstrip(front_name).rstrip(end_name)
                    if number.isdecimal():
                        opened_number.append(int(number))
                for number in range(1, len(self.category.channels)):
                    if number not in opened_number:
                        count = number
                        break

        if mode == 1:
            channel = await self.category.create_text_channel(
                name=self.convert_template(
                    name=self.template,
                    guild=context.guild,
                    member=context.author,
                    count=count
                ),
                overwrites={
                    self.bot.user: discord.PermissionOverwrite(
                        read_message_history=True,
                        send_messages=True,
                        embed_links=True,
                        attach_files=True,
                        add_reactions=True,
                        view_channel=True
                    ),
                    context.author: discord.PermissionOverwrite(
                        read_message_history=True,
                        send_messages=True,
                        attach_files=True,
                        view_channel=True
                    ),
                    context.guild.default_role: discord.PermissionOverwrite(
                        read_message_history=False,
                        send_messages=False,
                        view_channel=False
                    )
                }
            )
        elif mode == 2:
            channel = await self.category.create_text_channel(
                name=self.convert_template(
                    name=self.template,
                    guild=context.guild,
                    member=context.author,
                    count=count
                ),
                overwrites={
                    context.guild.default_role: discord.PermissionOverwrite(
                        read_message_history=False,
                        send_messages=False,
                        view_channel=False
                    ),
                    self.bot.user: discord.PermissionOverwrite(
                        read_message_history=True,
                        send_messages=True,
                        embed_links=True,
                        attach_files=True,
                        add_reactions=True,
                        view_channel=True
                    )
                }
            )
        else:
            # Ticket Mode Not Found (Not Worked)
            self.ticket_mode_not_found.description = self.ticket_mode_not_found.description.format(ticket_mode=data.mode)
            await context.send(embed=self.ticket_mode_not_found, hidden=True)
            return

        self.ticket.append({
            "type": "ticket",
            "channel": channel.id,
            "mode": mode,
            "guild": context.guild.id,
            "author": context.author.id
        })

        if mode == 1:
            _channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=channel)
        elif mode == 2:
            channel = context.author.dm_channel
            if channel is None:
                channel = await context.author.create_dm()
            _channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=channel)

        embed = discord.Embed(colour=self.color)
        await _channel.send(
            embed=embed,
            components=[ActionRow(
                components=[
                    Button(
                        custom_id="ticket_partners",
                        style=1,
                        emoji=discord.PartialEmoji(name="\U00000031\U0000FE0F\U000020E3")
                    ),
                    Button(
                        custom_id="ticket_report",
                        style=1,
                        emoji=discord.PartialEmoji(name="\U00000032\U0000FE0F\U000020E3")
                    ),
                    Button(
                        custom_id="ticket_project",
                        style=1,
                        emoji=discord.PartialEmoji(name="\U00000033\U0000FE0F\U000020E3")
                    ),
                    Button(
                        custom_id="ticket_etc",
                        style=1,
                        emoji=discord.PartialEmoji(name="\U00000034\U0000FE0F\U000020E3")
                    ),
                    Button(
                        custom_id="ticket_cancel",
                        style=1,
                        emoji=discord.PartialEmoji(name="\U00000035\U0000FE0F\U000020E3")
                    )
                ]
            )]
        )
        self.ticket_process.description = self.ticket_process.description.format(ticket_channel=channel.mention)
        message = await context.send(embed=self.ticket_process, hidden=True)
        with open(os.path.join(directory, "data", "ticket.json"), "w", encoding='utf-8') as file:
            json.dump(self.ticket, fp=file, indent=4)
        return


def setup(client):
    client.add_cog(TicketReceive(client))
