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
from discord.ext import interaction
from discord.ext.interaction import ActionRow, Button, ComponentsContext, MessageSendable, Message
from discord.state import ConnectionState
from typing import Optional

from config.config import get_config
from process.ticket import Ticket
from utils.directory import directory
from utils.exception import get_exception_comment, Level

logger = logging.getLogger(__name__)
parser = get_config()


class TicketReceive(commands.Cog):
    def __init__(self, bot: interaction.Client):
        self.bot = bot
        with open(os.path.join(directory, "data", "ticket.json"), "r", encoding='utf-8') as file:
            self.ticket = json.load(fp=file)
        self.color = int(parser.get("Color", "default"), 16)

        self._connection: ConnectionState = getattr(bot, "_connection")

        self.channel_discord: Optional[int] = None
        self.template = parser.get("Ticket", "template")
        self.channel: Optional[discord.TextChannel] = None
        self.category: Optional[discord.CategoryChannel] = None

        self.ticket_process = discord.Embed(
            title="티켓(Ticket)",
            description="정상적으로 티켓을 열었습니다. {ticket_channel} 를 참조해주세요.",
            color=self.color
        )

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
    def conversion_template(name: str, guild: discord.Guild, member: discord.Member, **kwargs):
        return name.format(
            guild=guild.name,
            guild_id=guild.id,
            member=str(member),
            member_name=member.name,
            member_tag=member.discriminator,
            member_id=member.id,
            number=kwargs.get("count")
        )

    async def on_ticket(self, context: ComponentsContext):
        mode = 0
        if context.custom_id == "ticket_type1":
            mode = 1
        elif context.custom_id == "ticket_type2":
            mode = 2
        elif context.custom_id == "ticket_close":
            await self.ticket_close(context)

        for check_ticket in self.ticket:
            if context.author.id == check_ticket.get("author"):
                await context.send(
                    embed=get_exception_comment(Level.Warning, "TICKET-ALREADY-OPENED"),
                    hidden=True
                )
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
                name=self.conversion_template(
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
                        send_messages=False,
                        attach_files=False,
                        add_reactions=False,
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
                name=self.conversion_template(
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
            await context.send(
                embed=get_exception_comment(Level.Error, "TICKET-MODE-NOT-FOUND"),
                hidden=True
            )
            return

        ticket_client = Ticket(
            context=context,
            client=self.bot,
            channel=_channel,
            content_channel=_content_channel,
            ticket_close=self.ticket_close
        )
        await ticket_client.selection_menu()

        self.ticket.append({
            "type": "ticket",
            "contect_channel": content_channel.id,
            "channel": channel.id,
            "mode": mode,
            "guild": context.guild.id,
            "author": context.author.id,
            "process": False
        })
        if mode == 1:
            self.ticket_process.description = self.ticket_process.description.format(ticket_channel=channel.mention)
        elif mode == 2:
            self.ticket_process.description = self.ticket_process.description.format(ticket_channel="1:1 메시지(DM)")
        await context.send(embed=self.ticket_process, hidden=True)
        with open(os.path.join(directory, "data", "ticket.json"), "w", encoding='utf-8') as file:
            json.dump(self.ticket, fp=file, indent=4)
        return

    @commands.Cog.listener()
    async def on_components(self, context: ComponentsContext):
        if context.custom_id.startswith("ticket"):
            return await self.on_ticket(context)

        if context.custom_id.startswith("menu_selection") or context.custom_id.startswith("process_ticket"):
            mode: Optional[int] = None
            content_channel_id: Optional[int] = None
            channel_id: Optional[int] = None
            guild_id: Optional[int] = None
            # process_message_id: Optional[int] = None
            index = -1
            for _index, _channel_data in enumerate(self.ticket):
                if _channel_data.get("channel", 0) == int(context.channel_id):
                    index = _index
                    channel_id = int(_channel_data.get("channel", 0))
                    guild_id = int(_channel_data.get("guild", 0))
                    mode = int(_channel_data.get("mode", 0))
                    content_channel_id = int(_channel_data.get("contect_channel", 0))
                    break
            if channel_id is None or channel_id == 0:
                return

            guild = self.bot.get_guild(guild_id)
            channel = guild.get_channel(channel_id)
            content_channel = guild.get_channel(content_channel_id)

            if mode == 1:
                _content_channel = _channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=channel)
            elif mode == 2:
                _channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=channel)
                _content_channel = MessageSendable(state=getattr(self.bot, "_connection"), channel=content_channel)
            else:
                return

            ticket_client = Ticket(
                context=context,
                client=self.bot,
                channel=_channel,
                content_channel=_content_channel,
                ticket_close=self.ticket_close
            )

            if context.component_type == 2 and context.custom_id.startswith("menu_selection"):
                _buffer = "menu_selection"
                len_buffer = len(_buffer)
                selection_menu = context.custom_id[len_buffer:]

                # if hasattr(ticket_client, "menu{}".format(selection_menu)):
                await discord.utils.maybe_coroutine(
                    f=ticket_client.menu_code,
                    context=context,
                    code=selection_menu
                )
            elif context.component_type == 3 and context.custom_id.startswith("menu_selection"):
                _buffer = "menu_selection"
                len_buffer = len(_buffer)
                if len(context.values) == 0:
                    return
                value = context.values[0]
                selection_menu = value[len_buffer:]

                # if hasattr(ticket_client, "menu{}".format(selection_menu)):
                await discord.utils.maybe_coroutine(
                    f=ticket_client.menu_code,
                    context=context,
                    code=selection_menu
                )
            elif context.custom_id.startswith("process_ticket"):
                _buffer = "process_ticket"
                len_buffer = len(_buffer)
                ticket_menu = context.custom_id[len_buffer:]
                if ticket_menu == "_prev":
                    await ticket_client.selection_menu(update=True)
                if ticket_menu.startswith("_start"):
                    ticket_section = ticket_menu.lstrip("_start")
                    if ticket_section != '':
                        ticket_client.section = ""
                    await ticket_client.start_chatting()
                    if mode == 1:
                        await _content_channel.channel.set_permissions(
                            context.author,
                            overwrite=discord.PermissionOverwrite(
                                read_message_history=True,
                                send_messages=True,
                                embed_links=True,
                                attach_files=True,
                                add_reactions=True,
                                view_channel=True
                            )
                        )
                    self.ticket[index]["process"] = True
                    with open(os.path.join(directory, "data", "ticket.json"), "w", encoding='utf-8') as file:
                        json.dump(self.ticket, fp=file, indent=4)
            return
        return

    async def on_process_ticket(self, ctx: ComponentsContext):
        return

    @staticmethod
    async def send(message: Message, send_func):
        files = []
        if len(message.attachments) != 0:
            for attachment in message.attachments:
                file = await attachment.to_file()
                files.append(file)
        msg = await send_func(
            content="**{author}**: {message}".format(
                author=message.author,
                message=message.content if message.content is not None else ""
            ),
            files=None if len(message.attachments) == 0 else files
        )
        await message.add_reaction("\U00002705")
        return msg

    @commands.Cog.listener()
    async def on_interaction_message(self, message: Message):
        if message.author.bot:
            return

        if message.content is not None:
            if message.content.startswith("#"):
                await message.add_reaction("\U0000274C")
                return

        if message.channel.type == discord.ChannelType.private:
            ticket = None
            for _data in self.ticket:
                if _data.get("author", 0) == message.author.id and _data.get("mode") == 2 and _data.get("process"):
                    ticket = _data
            if ticket is None:
                return
            channel_id = ticket.get("contect_channel")
            guild_id = ticket.get("guild", 0)
            channel = self.bot.get_guild(guild_id).get_channel(channel_id)
            await self.send(message, channel.send)
        elif message.channel.type == discord.ChannelType.text:
            ticket = None
            for _data in self.ticket:
                if (
                        _data.get("contect_channel", 0) == message.channel.id and
                        _data.get("mode") == 2 and
                        _data.get("process")
                ):
                    ticket = _data
            if ticket is None:
                return
            author_id = ticket.get("author")
            author = message.guild.get_member(author_id)
            await self.send(message, author.send)
        return

    async def ticket_close(
            self,
            context: ComponentsContext,
            backup: bool = True
    ):
        ticket = None
        guild = context.guild
        for _data in self.ticket:
            if _data.get("channel") == context.channel.id or _data.get("contect_channel") == context.channel.id:
                ticket = _data
        if ticket is None:
            await context.send(
                embed=get_exception_comment(Level.Warning, "TICKET-NOT-FOUND"),
                hidden=True
            )
            return

        if context.channel.type == discord.ChannelType.private or guild is None:
            guild = self.bot.get_guild(ticket.get("guild"))
        author = guild.get_member(ticket.get("author"))
        channel = guild.get_channel(ticket.get("channel"))
        contect_channel = guild.get_channel(ticket.get("contect_channel"))
        mode = ticket.get("mode", -1)
        if mode == 1:
            channel: discord.TextChannel
            await channel.set_permissions(
                author,
                overwrite=discord.PermissionOverwrite(
                    read_message_history=False,
                    send_messages=False,
                    view_channel=False
                )
            )

        if backup and parser.has_option("Ticket", "logging"):
            logging_data = "{guild}\n".format(guild=guild.name)
            async for message in contect_channel.history(oldest_first=True):
                content = message.content
                _author = message.author
                if message.author == self.bot.user and mode == 2:
                    content = content.lstrip("**{author}**: ".format(author=author))

                if len(message.attachments) != 0:
                    content += " ({0})".format(", ".join([attachment.url for attachment in message.attachments]))

                if mode == 2 and _author.id == self.bot.user.id:
                    _author = author
                logging_data += "[ {datetime} | {author} ]: {content}\n".format(
                    datetime=message.created_at.strftime("%Y-%m-%d %p %I:%M:%S"),
                    author=_author, content=content
                )
            logging_channel_id = parser.getint("Ticket", "logging")
            logging_channel = guild.get_channel(logging_channel_id)
            if logging_channel is None:
                return
            with open(
                    os.path.join(directory, "data", "ticket", "{0}.txt".format(contect_channel.id)),
                    "w", encoding='utf-8'
            ) as file:
                file.write(logging_data)
            d_file = discord.File(os.path.join(directory, "data", "ticket", "{0}.txt".format(contect_channel.id)))
            embed = discord.Embed(title="Ticket Logging", colour=0x0080ff)
            embed.add_field(name="Opener", value=author, inline=True)
            embed.add_field(name="Closer", value=context.author, inline=True)
            await logging_channel.send(embed=embed, file=d_file)

        await contect_channel.delete()
        if not backup and mode == 2:
            await context.delete()
        position = self.ticket.index(ticket)
        self.ticket.pop(position)
        with open(os.path.join(directory, "data", "ticket.json"), "w", encoding='utf-8') as file:
            json.dump(self.ticket, fp=file, indent=4)
        return

    @commands.command()
    async def ticket(self, ctx):
        option = ctx.message.content.split()[1:]
        if len(option) > 0:
            option1 = option[0]
        else:
            return

        if option1 == "불러오기":
            if 844620551153909760 not in [role.id for role in ctx.author.roles]:
                await ctx.send("권한이 부족합니다.")
                return

            channel = MessageSendable(
                state=self._connection,
                channel=ctx.guild.get_channel(parser.getint("Channel", "ticket_channel"))
            )
            embed = discord.Embed(title="\U0001F39F 문의하기", colour=self.color)
            embed.description = (
                "__**파트너 신청**, **사용자 신고**, **버그 제보**__ 등 "
                "__**프로젝트**, **커뮤니티**__에 관련되어 개인적으로 건의하거나 문의하고 싶은 사항이 있으시다면, "
                "아래의 버튼에 있는 티켓을 통하여 문의를 부탁드립니다.\n"
                "장난식 티켓 생성은 처벌 대상입니다. 자제해주시길 부탁드립니다."
            )
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
            await self.ticket_close(ctx)
        return


def setup(client):
    client.add_cog(TicketReceive(client))
