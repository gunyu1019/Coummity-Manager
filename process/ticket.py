import discord

from config.config import parser
from typing import Union, Optional
from module.components import ActionRow, Selection, Options
from module.interaction import ApplicationContext, ComponentsContext
from module.message import Message, MessageCommand, MessageSendable
from utils.directory import directory


class Ticket:
    def __init__(
            self,
            context: Union[ComponentsContext],
            client: discord.Client,
            channel: MessageSendable,
            contect_channel: Optional[MessageSendable] = None
    ):
        self.context = context
        self.client = client

        self.channel = channel
        self.contect_channel = contect_channel or channel

        self.before_func = None

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    async def selection_menu(self):
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = "{0}님 비공개 문의를 시작하기 전, 아래의 해당되는 카테고리를 알맞게 선택해주시기 바랍니다.".format(
            self.context.author.mention
        )
        message = await self.channel.send(
            embed=embed,
            components=[ActionRow(
                components=[
                    Selection(
                        custom_id="matches_selection",
                        options=[Options(
                                label="사용자 신고",
                                value="menu_selection_1",
                                emoji={
                                    "name": "\U0001F6A8"
                                }
                            ), Options(
                                label="파트너 관련 문의",
                                value="menu_selection_2",
                                description="커뮤니티 파트너 관련 문의는 이곳을 눌러주세요.",
                                emoji={
                                    "id": "896811934391869450",
                                    "name": "partner"
                                }
                            ), Options(
                                label="프로젝트 버그 관련 문의",
                                value="menu_selection_3",
                                description="YBOT, PUBG BOT 등의 프로젝트의 버그 신고는 이곳에서 진행해 주세요.",
                                emoji={
                                    "name": "\U0001F916"
                                }
                            ), Options(
                                label="프로젝트 기타 문의",
                                value="menu_selection_4",
                                description="YBOT, PUBG BOT 등의 프로젝트의 개선 & 요구 사항은 이곳에서 진행해 주세요.",
                                emoji={
                                    "name": "\U0001F916"
                                }
                            ), Options(
                                label="건의사항",
                                value="menu_selection_5",
                                description="커뮤니티 개선 & 요구 사항은 이곳에서 진행해 주세요.",
                                emoji={
                                    "name": "\U00002139"
                                }
                            ), Options(
                                label="기타",
                                value="menu_selection_6",
                                description="위 사항에 해당되는 것이 없다면 이곳에서 진행해 주세요.",
                                emoji={
                                    "name": "\U0000267E"
                                }
                            ), Options(
                                label="취소",
                                value="menu_selection_cancel",
                                description="문의를 취소하고자 하면 이곳을 눌러주세요.",
                                emoji={
                                    "name": "\U0000274C"
                                }
                            )
                        ],
                        min_values=1,
                        max_values=1,
                    )
                ]
            )]
        )
        return message
