"""MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import inspect
import discord

from discord.state import ConnectionState
from discord.enums import try_enum
from typing import List, Union, Optional
from datetime import datetime

from module.components import ActionRow, Button, Selection, from_payload
from module.errors import InvalidArgument
from module.http import HttpClient


def _files_to_form(files: list, payload: dict):
    form = [{'name': 'payload_json', 'value': getattr(discord.utils, "_to_json")(payload)}]
    if len(files) == 1:
        file = files[0]
        form.append(
            {
                'name': 'file',
                'value': file.fp,
                'filename': file.filename,
                'content_type': 'application/octet-stream',
            }
        )
    else:
        for index, file in enumerate(files):
            form.append(
                {
                    'name': f'file{index}',
                    'value': file.fp,
                    'filename': file.filename,
                    'content_type': 'application/octet-stream',
                }
            )
    return form


def _allowed_mentions(state, allowed_mentions):
    if allowed_mentions is not None:
        if state.allowed_mentions is not None:
            allowed_mentions = state.allowed_mentions.merge(allowed_mentions).to_dict()
        else:
            allowed_mentions = allowed_mentions.to_dict()
    else:
        allowed_mentions = state.allowed_mentions and state.allowed_mentions.to_dict()
    return allowed_mentions


def _get_payload(
        content=None,
        embed=None,
        tts: bool = False,
        allowed_mentions=None,
        components=None
) -> dict:
    payload = {'tts': tts}
    if content:
        payload['content'] = content
    if embed:
        payload['embeds'] = embed
    if allowed_mentions:
        payload['allowed_mentions'] = allowed_mentions
    if components:
        payload['components'] = components
    return payload


class Message(discord.Message):
    def __init__(
            self,
            *,
            state: ConnectionState,
            channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel],
            data: dict
    ):
        if "message_reference" in data and "channel_id" not in data.get("message_reference", {}):
            data["message_reference"]["channel_id"] = channel.id
        super().__init__(state=state, channel=channel, data=data)
        self.components = from_payload(data.get("components", []))
        self.http = HttpClient(http=self._state.http)

    async def send(
            self,
            content=None,
            *,
            tts: bool = False,
            embed: discord.Embed = None,
            embeds: List[discord.Embed] = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        channel = MessageSendable(state=self._state, channel=self.channel)
        return await channel.send(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            allowed_mentions=allowed_mentions,
            components=components
        )

    async def edit(
            self,
            content=None,
            *,
            embed: discord.Embed = None,
            embeds: List[discord.Embed] = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        if file is not None and files is not None:
            raise InvalidArgument()
        if embed is not None and embeds is not None:
            raise InvalidArgument()

        content = str(content) if content is not None else None
        if embed is not None:
            embeds = [embed]
        if embeds is not None:
            embeds = [embed.to_dict() for embed in embeds]
        if file:
            files = [file]
        if components is not None:
            components = [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]

        allowed_mentions = _allowed_mentions(self._state, allowed_mentions)

        payload = _get_payload(
            content=content,
            embed=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
        )

        if files:
            payload["attachments"] = []
            form = _files_to_form(files=files, payload=payload)
        else:
            form = None

        await self.http.edit_message(
            channel_id=self.channel.id, message_id=self.id,
            payload=payload, form=form, files=files
        )

        if files:
            for file in files:
                file.close()
        return


class MessageDelete:
    def __init__(self, data: dict, state: ConnectionState, bulk: bool = False):
        self.id = data["id"] if not bulk else data["ids"]
        self.channel_id = int(data["channel_id"])
        self.guild_id = int(data.get("guild_id"))

        self._state = state

    @property
    def guild(self):
        return getattr(self._state, "_get_guild")(int(self.guild_id))

    @property
    def channel(self):
        return self._state.get_channel(self.channel_id)


class MessageCommand(Message):
    def __init__(
            self,
            *,
            state: ConnectionState,
            channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel],
            data: dict
    ):
        super().__init__(state=state, channel=channel, data=data)

        options = self.content.split()

        if len(options) >= 1:
            self.name = options[0]
        else:
            self.name = None

        if len(options) >= 2:
            self.options = self.content.split()[1:]
        else:
            self.options = []


class MessageSendable:
    def __init__(self, state: ConnectionState, channel):
        self._state = state
        self.http = HttpClient(http=self._state.http)
        self.channel = channel

    async def send(
            self,
            content=None,
            *,
            tts: bool = False,
            embed: discord.Embed = None,
            embeds: List[discord.Embed] = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        if file is not None and files is not None:
            raise InvalidArgument()
        if embed is not None and embeds is not None:
            raise InvalidArgument()

        content = str(content) if content is not None else None
        if embed is not None:
            embeds = [embed]
        if embeds is not None:
            embeds = [embed.to_dict() for embed in embeds]
        if file:
            files = [file]
        if components is not None:
            components = [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]
        allowed_mentions = _allowed_mentions(self._state, allowed_mentions)

        payload = _get_payload(
            content=content,
            tts=tts,
            embed=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
        )

        if files:
            form = _files_to_form(files=files, payload=payload)
            resp = await self.http.create_message(form=form, files=files, channel_id=self.channel.id)
        else:
            resp = await self.http.create_message(payload=payload, channel_id=self.channel.id)
        ret = Message(state=self._state, channel=self.channel, data=resp)

        if files:
            for i in files:
                i.close()
        return ret


class MessageEdited(MessageSendable):
    def __init__(
            self,
            *,
            state: ConnectionState,
            channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel],
            data: dict
    ):
        super().__init__(state=state, channel=channel)
        self._func = {}
        self._state: ConnectionState = state
        self._data = data
        for index, func in inspect.getmembers(MessageEdited):
            if index.startswith("_handler_"):
                self._func[index] = func
        self.id: int = int(data['id'])
        self.channel = channel

    def __getattr__(self, item):
        if "_handler_" + item in self._func.keys():
            return getattr(self, "_handler_{0}".format(item))()
        return self._data.get(item)

    def _handler_webhook_id(self) -> Optional[int]:
        return getattr(discord.utils, "_get_as_snowflake")(self._data, 'webhook_id')

    def _handler_reactions(self) -> List[discord.Reaction]:
        return [
            discord.Reaction(message=self, data=d) for d in self._data.get('reactions', [])
        ]

    def _handler_embed(self) -> List[discord.Embed]:
        return [discord.Embed.from_dict(a) for a in self._data.get('embeds', [])]

    def _handler_attachments(self) -> List[discord.Attachment]:
        return [
            discord.Attachment(data=a, state=self._state) for a in self._data.get('attachments', [])
        ]

    def _handler_type(self) -> discord.MessageType:
        return try_enum(discord.MessageType, self._data.get('type'))

    def _handler_flags(self) -> discord.MessageType:
        return getattr(discord.MessageFlags, "_from_value")(self._data.get('flags', 0))

    def _handler_stickers(self) -> List[discord.StickerItem]:
        return [
            discord.StickerItem(data=d, state=self._state) for d in self._data.get('sticker_items', [])
        ]

    def _handler_guild(self) -> Optional[discord.Guild]:
        return getattr(self.channel, "guild", getattr(self._state, "_get_guild")(self._data.get('guild_id')))

    def _handler_components(self) -> List[discord.StickerItem]:
        return from_payload(self._data.get("components", []))

    def _handler_created_at(self) -> datetime:
        return discord.utils.snowflake_time(self.id)

    def _handler_edited_at(self) -> Optional[datetime]:
        return discord.utils.parse_time(self._data.get('edited_timestamp'))

    def _handler_author(self) -> Union[discord.Member, discord.User]:
        author = self._state.store_user(self._data.get("author"))
        if isinstance(self.guild, discord.Guild):
            found = self.guild.get_member(author.id)
            if found is not None:
                author = found
        return author

    def _handle_mentions(self) -> List[Union[discord.Member, discord.User]]:
        mentions = []
        guild = self.guild
        state = self._state
        if not isinstance(guild, discord.Guild):
            mentions = [state.store_user(m) for m in self._data.get('mentions', [])]
        return mentions

    def _handle_mention_roles(self) -> List[discord.Role]:
        role_mentions = []
        if isinstance(self.guild, discord.Guild):
            for role_id in map(int, self._data.get('role_mentions', [])):
                role = self.guild.get_role(role_id)
                if role is not None:
                    role_mentions.append(role)
        return role_mentions

    def _handler_jump_url(self) -> str:
        guild_id = getattr(self.guild, 'id', '@me')
        return f'https://discord.com/channels/{guild_id}/{self.channel.id}/{self.id}'
