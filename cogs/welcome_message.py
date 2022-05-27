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
from typing import Optional
from discord.ext import commands
from discord.state import ConnectionState
from discord.ext.interaction import MessageSendable

from config.config import get_config

logger = logging.getLogger(__name__)
parser = get_config()
labeling_parser = get_config('labeling')


class WelcomeMessage:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._connection: ConnectionState = getattr(bot, "_connection")
        self.color = int(parser.get("Color", "default"), 16)

        self.channel_discord = None
        self.channel = None
        self._guild = None
        self._invites = []

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel_discord = self._connection.get_channel(
            id=parser.getint("Channel", "welcome_message", fallback=0)
        )
        if self.channel_discord is not None and self.channel is None:
            self.channel = MessageSendable(
                state=self._connection,
                channel=self.channel_discord
            )

        guild_id = parser.getint("InviteLabeling", "guild", fallback=0)
        self._guild: discord.Guild = self.bot.get_guild(guild_id)
        self._invites = await self._guild.invites()

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        self._invites.append(invite)
        print(invite)
        return

    @commands.Cog.listener()
    async def on_invite_delete(self, _: discord.Invite):
        self._invites = await self._guild.invites()
        return

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        footer_invite = []
        invites = {}
        pre_invites = self._invites[:]
        for invite in pre_invites:
            invites[invite.code] = {
                "preData": invite,
                "postData": None
            }
        self._invites = await self._guild.invites()
        post_invites = self._invites[:]
        for invite in post_invites:
            if invite.code not in invites:
                invites[invite.code] = {
                    "preData": None,
                    "postData": None
                }
            invites[invite.code]['postData'] = invite
        for changed_invite in invites.values():
            if changed_invite['preData'] is None or changed_invite['postData'] is None:
                continue

            if changed_invite['preData'].uses != changed_invite['postData'].uses:
                _invite: discord.Invite = changed_invite['postData']
                if labeling_parser.has_option('InviteLabeling', _invite.code):
                    footer_invite.append(
                        labeling_parser.get('InviteLabeling', _invite.code)
                    )
                    continue
                inviter: Optional[discord.User] = _invite.inviter
                if inviter is None:
                    continue
                footer_invite.append('{}#{}'.format(inviter.name, inviter.discriminator))

        guild: discord.Guild = member.guild
        if member.bot:
            bot_role_id = parser.getint("Role", "bot", fallback=None)
            if bot_role_id is None:
                return
            bot_role = member.guild.get_role(bot_role_id)
            if bot_role is None:
                return
            await member.add_roles(bot_role)
            return

        member_role_id = parser.getint("Role", "member", fallback=None)
        if member_role_id is not None:
            member_role = member.guild.get_role(member_role_id)
            if member_role is not None:
                await member.add_roles(member_role)

        embed = discord.Embed(
            description="{}님! {}에 오신것을 진심으로 환영합니다!".format(member.mention, guild.name),
            colour=self.color
        )
        embed.set_author(
            name="{}#{}님 환영합니다!".format(member.name, member.discriminator),
            icon_url=str(guild.icon_url)
        )
        embed.set_thumbnail(url=member.avatar_url)
        if len(footer_invite) == 0:
            embed.set_footer(text="가입 경로: 존재하지 않습니다.")
        else:
            embed.set_footer(text="가입 경로: {}".format(", ".join(footer_invite)))
        await self.channel.send(embed=embed)
        return


async def setup(client):
    client.add_icog(WelcomeMessage(client))
