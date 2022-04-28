import os
import json
import discord
from discord.ext.interaction import ActionRow, Button, Selection, Options, ComponentsContext, MessageSendable
from typing import Union, Optional, Callable

from config.config import get_config
from modules.models.ticket import TicketMenu, TicketChoices
from utils.directory import directory

parser = get_config()
with open(os.path.join(directory, "config", "ticket_menu.json"), 'r', encoding='utf8') as fp:
    _ticket_menu = json.load(fp)
    ticket_menu = [TicketChoices(value, index) for index, value in enumerate(_ticket_menu)]


class Ticket:
    def __init__(
            self,
            context: Union[ComponentsContext],
            client: discord.Client,
            channel: MessageSendable,
            ticket_close: Optional[Callable] = None,
            content_channel: Optional[MessageSendable] = None,
    ):
        self.ticket_close: Optional[Callable] = ticket_close
        self.context = context
        self.client = client

        self.channel = channel
        self.content_channel = content_channel or channel

        self.before_func = None
        self.section = "None"

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.prev_btn = Button(
            custom_id="process_ticket_prev",
            style=1,
            emoji=discord.PartialEmoji(
                name="\U00002B05"
            )
        )
        self.start_btn = Button(
            custom_id="process_ticket_start",
            style=1,
            emoji=discord.PartialEmoji(
                name="\U00002705"
            )
        )

    @property
    def final_btn(self):
        return ActionRow(
            components=[
                self.prev_btn,
                self.start_btn
            ]
        )

    async def selection_menu(self, update: bool = False):
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = "{0}님 비공개 문의를 시작하기 전, 아래의 해당되는 카테고리를 알맞게 선택해주시기 바랍니다.".format(
            self.context.author.mention
        )
        if not update:
            f = self.channel.send
        else:
            f = self.context.update

        options = [
            Options(
                label=value.title,
                description=value.description,
                emoji=value.emoji,
                value="menu_selection_{}".format(index)
            ) for index, value in enumerate(ticket_menu)
        ]
        options.append(
            Options(
                label="취소",
                value="menu_selection_cancel",
                description="문의를 취소하고자 하면 이곳을 눌러주세요.",
                emoji={
                    "name": "\U0000274C"
                }
            )
        )
        message = await f(
            embed=embed,
            components=[ActionRow(
                components=[
                    Selection(
                        custom_id="menu_selection",
                        options=options,
                        min_values=1,
                        max_values=1,
                    )
                ]
            )]
        )
        return message

    async def start_chatting(self):
        self.prev_btn.disabled = True
        self.start_btn.style = 3
        await self.context.update(
            components=[
                self.final_btn
            ]
        )
        if self.content_channel != self.channel:
            embed = discord.Embed(colour=self.color)
            embed.title = "\U0001F39F 티켓 내용"
            embed.add_field(name="사용자: ", value=self.context.author, inline=True)
            embed.add_field(name="주제: ", value=self.section, inline=True)
            await self.content_channel.send(
                embed=embed,
                components=[
                    ActionRow(components=[
                        Button(
                            custom_id="ticket_close",
                            label="티켓 종료",
                            style=4
                        )
                    ])
                ]
            )
            return

    async def menu_code(
            self,
            context: ComponentsContext,
            code: str
    ):
        if code == '_cancel':
            await self.menu_cancel(context)
            return
        indexes = [int(x) for x in code.lstrip('_').split('-')]
        page = None
        for index, page_index in enumerate(indexes):
            if index == 0:
                page = ticket_menu[page_index].clicked
            else:
                page = page.response[page_index]
        embed = discord.Embed(title="\U0001F39F 문의하기", colour=self.color)
        embed.description = page.description
        for field in page.fields:
            embed.add_field(
                name=field['name'],
                value=field['value'] if isinstance(field['value'], str) else "\n".join(field['value']),
                inline=field.get('inline', False)
            )

        if page.callback == 1:
            components = [ActionRow(page.buttons)]
        else:
            components = [self.final_btn]

        await context.update(
            embed=embed,
            components=components
        )
        return

    # 티켓 삭제
    async def menu_cancel(
            self,
            context: ComponentsContext
    ):
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "문의를 취소합니다. 잠시만 기다려 주세요."
        )
        embed.set_footer(text="취소")
        await context.update(
            embed=embed
        )
        await self.ticket_close(
            context=context,
            backup=False
        )
        return
