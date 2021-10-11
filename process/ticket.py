import random
import discord

from config.config import parser
from typing import Union, Optional
from module.components import ActionRow, Button, Selection, Options
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

        message = await f(
            embed=embed,
            components=[ActionRow(
                components=[
                    Selection(
                        custom_id="menu_selection",
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

    async def start_chatting(self):
        self.prev_btn.disabled = True
        self.start_btn.style = 3
        await self.context.update(
            components=[
                self.final_btn
            ]
        )

    # 사용자 신고
    async def menu_1(
            self,
            context: ComponentsContext
    ):
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "\U0001F6A8 사용자 신고를 누르셨습니다. "
            "자세한 상황 파악을 위해 아래의 양식과 육하원칙을 준수하여, 상황을 설명하여 주시기 바랍니다.\n\n"
            "**[양식]**```\n"
            "* 닉네임(태그):\n"
            "* 신고 사유:\n"
            "* 증거 자료:\n"
            "```\n"
            "**__단, 커뮤니티 테러, 도배, DM홍보 등의 다소 심각한 사항은 즉시 관리자를 맨션해주시기 바랍니다.__**"
        )
        embed.set_footer(text="사용자 신고")
        await context.update(
            embed=embed,
            components=[
                self.final_btn
            ]
        )
        return

    # 파트너 관련 문의
    async def menu_2(
            self,
            context: ComponentsContext
    ):
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "파트너 관련 문의를 누르셨습니다. "
            "파트너 서버 체결 문의는 아래의 3가지`(커뮤니티, 방송인, 웹사이트)` 중 해당되는 유형의 버튼을 선택해 주세요."
            "파트너 부정 행위 신고, 파트너 해지 등의 파트너 서버 등재 외 문의는 `기타`를 눌러주세요."
        )
        embed.set_footer(text="파트너 관련 문의")
        await context.update(
            embed=embed,
            components=[ActionRow(
                components=[
                    self.prev_btn,
                    Button(
                        custom_id="menu_selection_21",
                        style=2,
                        emoji=discord.PartialEmoji(
                            id=893147827797123112,
                            name="discord"
                        )
                    ), Button(
                        custom_id="menu_selection_22",
                        style=2,
                        emoji=random.choice([discord.PartialEmoji(
                            id=897068075885682701,
                            name="youtube"
                        ), discord.PartialEmoji(
                            id=897067731000639498,
                            name="twitch"
                        )])
                    ), Button(
                        custom_id="menu_selection_23",
                        style=2,
                        emoji=discord.PartialEmoji(
                            id=897068621480738837,
                            name="website"
                        )
                    ), Button(
                        label="기타",
                        custom_id="menu_selection_24",
                        style=2
                    )
                ]
            )]
        )
        return

    # 파트너 관련 문의 > 디스코드 서버
    async def menu_21(
            self,
            context: ComponentsContext
    ):
        emoji = discord.PartialEmoji(
            id=893147827797123112,
            name="discord"
        )
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "{0} 디스코드 서버 파트너 체결 문의를 누르셨습니다.\n"
            "만약에 잘못 누르셨다면 \U00002B05를 눌러 시작해주세요.\n"
            "아래의 양식을 준수하여 파트너를 신청해주시기 바랍니다.".format(emoji)
        )
        embed.add_field(
            name="양식",
            value="```\n"
                  "* 커뮤니티 이름:\n"
                  "* 초대 링크:\n"
                  "* 순 멤버(봇 제외):\n"
                  "* 커뮤니티 종류:\n"
                  "* 커뮤니티와 관계: <서버장/관리자/팀원>\n"
                  "* 서버 소개:\n"
                  "```",
            inline=False
        )
        embed.add_field(
            name="<신청 전 유의사항>",
            value="파트너를 신청하시기 전에, 아래의 양식을 준수하는지 반드시 확인해주세요!\n"
                  "* 파트너 서버에 확실한 콘텐츠가 필요합니다.\n"
                  "* 디스코드 이용약관을 준수해야 합니다.\n"
                  "* 서버만의 고유한 규칙을 보유하고 있어야 합니다.\n"
                  "* 봇을 제외한 순 멤버 20명 이상 있어야 합니다.\n"
                  "* 친목을 형성하는 것은 좋으나, 과도한 친목은 지양해야 합니다."
                  "* (우대 사항) 서버 유형이 게임/개발 분야에 속한 커뮤니티",
            inline=False
        )
        embed.set_footer(text="파트너 관련 문의 > 디스코드 서버")
        await context.update(
            embed=embed,
            components=[
                self.final_btn
            ]
        )
        return

    # 파트너 관련 문의 > 방송인
    async def menu_22(
            self,
            context: ComponentsContext
    ):
        emoji = random.choice(
            [discord.PartialEmoji(
                id=897068075885682701,
                name="youtube"
            ), discord.PartialEmoji(
                id=897067731000639498,
                name="twitch"
            )]
        )
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "{0} 방송인 파트너 체결 문의를 누르셨습니다.\n"
            "만약에 잘못 누르셨다면 \U00002B05를 눌러 시작해주세요.\n"
            "아래의 양식을 준수하여 파트너를 신청해주시기 바랍니다.".format(emoji)
        )
        embed.add_field(
            name="양식",
            value="```\n"
                  "* 채널 이름: \n"
                  "* 채널 링크: \n"
                  "* 채널 유형: <트위치/유튜브/아프리카 TV/기타>\n"
                  "* 팔로워/구독자 수: \n"
                  "* 주요 콘텐츠: \n"
                  "* 채널 소개: \n"
                  "```",
            inline=False
        )
        embed.add_field(
            name="<신청 전 유의사항>",
            value="파트너를 신청하시기 전에, 아래의 양식을 준수하는지 반드시 확인해주세요!\n"
                  "* 트위치 팔로워 수 50인 이상 / 유튜브 구독자 수 20명 이상이여야 합니다.\n"
                  "* 30일 중 최소 7일 이상의 방송 이력이 존재해야합니다.\n"
                  "* 스트리밍 사이트의 이용약관을 필수로 준수해야 합니다.\n"
                  "* (우대 사항) 스트리밍 컨텐츠에서 $1 이상의 수익이 발생합니다.",
            inline=False
        )
        embed.set_footer(text="파트너 관련 문의 > 방송인")
        await context.update(
            embed=embed,
            components=[
                self.final_btn
            ]
        )
        return

    # 파트너 관련 문의 > 웹사이트
    async def menu_23(
            self,
            context: ComponentsContext
    ):
        emoji = discord.PartialEmoji(
            id=897068621480738837,
            name="website"
        )
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "{0} 웹사이트 파트너 체결 문의를 누르셨습니다.\n"
            "만약에 잘못 누르셨다면 \U00002B05를 눌러 시작해주세요.\n"
            "아래의 양식을 준수하여 파트너를 신청해주시기 바랍니다.".format(emoji)
        )
        embed.add_field(
            name="양식",
            value="```\n"
                  "* 웹사이트 이름: \n"
                  "* 웹사이트 링크: \n"
                  "* 웹사이트 콘텐츠: \n"
                  "* 웹사이트 소개: \n"
                  "```",
            inline=False
        )
        embed.add_field(
            name="<신청 전 유의사항>",
            value="파트너를 신청하시기 전에, 아래의 양식을 준수하는지 반드시 확인해주세요!\n"
                  "* 구글, 네이버 등의 검색 엔진을 통해 접근할 수 있어야 합니다.\n"
                  "* 웹사이트의 컨텐츠가 모호해서는 안됩니다.\n"
                  "* 최소한 웹사이트의 기본을 갖추셔야 합니다. (HTTPs 적용, 웹도메인 존재)\n"
                  "* 대한민국 법률을 위배하는 사이트여서는 안됩니다.",
            inline=False
        )
        embed.set_footer(text="파트너 관련 문의 > 웹사이트")
        await context.update(
            embed=embed,
            components=[
                self.final_btn
            ]
        )
        return

    # 파트너 관련 문의 > 기타
    async def menu_24(
            self,
            context: ComponentsContext
    ):
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "파트너 관련 사항 기타 문의를 누르셨습니다.\n"
            "만약에 잘못 누르셨다면 \U00002B05를 눌러 다시 시작해주세요.\n"
            "파트너 부정 행위, 파트너 해지 등의 문의를 시작하고자 한다면, "
            "아래의 \U00002705를 눌러서 채팅을 시작해주세요"
        )
        embed.set_footer(text="파트너 관련 문의 > 기타")
        await context.update(
            embed=embed,
            components=[
                self.final_btn
            ]
        )
        return

    # 프로젝트 버그 문의
    async def menu_3(
            self,
            context: ComponentsContext
    ):
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "\U0001F916 프로젝트 버그 관련 문의를 누르셨습니다. \n"
            "만약 채팅을 시작하고자 하자면, 아래의 \U00002705를 눌러서 채팅을 시작해주세요.\n\n"
            "__**오픈 소스 프로젝트 버그 관련 문의는 커뮤니티 보다, 깃허브 Repositories 이슈를 사용하시면, 더 빠르게 처리 됩니다.**__"
        )
        embed.set_footer(text="프로젝트 버그 관련 문의")
        await context.update(
            embed=embed,
            components=[
                self.final_btn
            ]
        )
        return

    # 프로젝트 기타 문의
    async def menu_4(
            self,
            context: ComponentsContext
    ):
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "\U0001F916 프로젝트 기타 관련 문의를 누르셨습니다. \n"
            "프로젝트 버그 외의 개선 사항, 요구 사항이 있으시다면 이곳을 통해 문의해주시기 바랍니다. \n"
            "만약 채팅을 시작하고자 하자면, 아래의 \U00002705를 눌러서 채팅을 시작해주세요."
        )
        embed.set_footer(text="프로젝트 기타 관련 문의")
        await context.update(
            embed=embed,
            components=[
                self.final_btn
            ]
        )
        return

    # 커뮤니티 문의
    async def menu_5(
            self,
            context: ComponentsContext
    ):
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "\U00002139 건의사항을 누르셨습니다. \n"
            "커뮤니티 내 개선 사항 등이 있으시다면 이곳을 통해 문의해주시기 바랍니다. \n"
            "만약 채팅을 시작하고자 하자면, 아래의 \U00002705를 눌러서 채팅을 시작해주세요."
        )
        embed.set_footer(text="건의사항")
        await context.update(
            embed=embed,
            components=[
                self.final_btn
            ]
        )
        return

    # 기타 문의
    async def menu_6(
            self,
            context: ComponentsContext
    ):
        embed = discord.Embed(colour=self.color)
        embed.title = "\U0001F39F 문의하기"
        embed.description = (
            "\U0000267E 기타 문의사항을 누르셨습니다. \n"
            "위 카테고리에 속하지 않는 문의사항은 이곳을 통해 문의해주시기 바랍니다.\n"
            "만약 채팅을 시작하고자 하자면, 아래의 \U00002705를 눌러서 채팅을 시작해주세요."
        )
        embed.set_footer(text="기타")
        await context.update(
            embed=embed,
            components=[
                self.final_btn
            ]
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
        context.client.dispatch(
            "ticket_close",
            context=context,
            backup=False
        )
        return
