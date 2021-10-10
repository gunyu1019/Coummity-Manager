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
from process.ticket import Ticket
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
            content_channel = channel = await self.category.create_text_channel(
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
            _content_channel = _channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=channel)
        elif mode == 2:
            content_channel = await self.category.create_text_channel(
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
            channel = context.author.dm_channel
            if channel is None:
                channel = await context.author.create_dm()
            channel.permissions_for()
            _channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=channel)
            _content_channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=content_channel)
        else:
            # Ticket Mode Not Found (Not Worked)
            self.ticket_mode_not_found.description = self.ticket_mode_not_found.description.format(ticket_mode=mode)
            await context.send(embed=self.ticket_mode_not_found, hidden=True)
            return

        ticket_client = Ticket(
            context=context,
            client=self.bot,
            channel=_channel,
            contect_channel=_content_channel
        )
        process_message = await ticket_client.selection_menu()

        self.ticket.append({
            "type": "ticket",
            "contect_channel": content_channel.id,
            "channel": channel.id,
            "mode": mode,
            "guild": context.guild.id,
            "author": context.author.id,
            "process_message_id": process_message.id
        })

        self.ticket_process.description = self.ticket_process.description.format(ticket_channel=channel.mention)
        message = await context.send(embed=self.ticket_process, hidden=True)
        with open(os.path.join(directory, "data", "ticket.json"), "w", encoding='utf-8') as file:
            json.dump(self.ticket, fp=file, indent=4)
        return

    @commands.Cog.listener()
    async def on_component(self, context: ComponentsContext):
        if context.custom_id.startswith("menu_selection"):
            mode: Optional[int] = None
            contect_channel_id: Optional[int] = None
            channel_id: Optional[int] = None
            guild_id: Optional[int] = None
            process_message_id: Optional[int] = None

            for _channel_data in self.ticket:
                if _channel_data.get("channel", 0) == int(context.channel_id):
                    channel_id = int(_channel_data.get("channel", 0))
                    guild_id = int(_channel_data.get("guild", 0))
                    mode = int(_channel_data.get("mode", 0))
                    contect_channel_id = int(_channel_data.get("contect_channel", 0))
                    process_message_id = int(_channel_data.get("process_message_id", 0))
                    break
            if channel_id is None or channel_id == 0:
                return

            guild = self.bot.get_guild(guild_id)
            channel = guild.get_channel(channel_id)
            contect_channel = guild.get_channel(contect_channel_id)
            process_message = await channel.fetch_message(process_message_id)

            if mode == 1:
                _content_channel = _channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=channel)
            elif mode == 2:
                _channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=channel)
                _content_channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=contect_channel)
            else:
                return

            ticket_client = Ticket(
                context=context,
                client=self.bot,
                channel=_channel,
                contect_channel=_content_channel
            )

            _buffer = "menu_selection"
            len_buffer = len(_buffer)
            selection_menu = context.custom_id[len_buffer:]

            if hasattr(ticket_client, "menu{}".format(selection_menu)):
                await discord.utils.maybe_coroutine(
                    f=getattr(ticket_client, "menu{}".format(selection_menu)),
                    process_message=process_message
                )
            return
        return


def setup(client):
    client.add_cog(TicketReceive(client))
