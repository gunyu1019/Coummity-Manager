import discord
from discord.ext import interaction
from typing import Dict, Any, Optional, List


class TicketChoices:
    def __init__(self, payload: Dict[str, Any], index: int = 0):
        self.index = index
        self.title = payload['title']
        self.description = payload.get('description')
        self._emoji = payload.get('emoji')
        self._clicked = payload.get('clicked', {})

    @property
    def emoji(self) -> Optional[discord.PartialEmoji]:
        if self._emoji is not None:
            if isinstance(self._emoji, str):
                return discord.PartialEmoji(name=self._emoji)
            return discord.PartialEmoji.from_dict(self._emoji)
        return

    @property
    def clicked(self):
        clicked_data = self._clicked
        if 'title' not in self._clicked:
            clicked_data['title'] = self.title
        return TicketMenu(clicked_data, str(self.index))


class TicketMenu:
    def __init__(self, payload: Dict[str, Any], index: str = 0, footer: List[str] = None):
        self.index = index
        self.title = payload['title']
        self._description = payload['description']
        self.fields = payload.get("fields", [])
        self._buttons = payload.get("buttons", [])

        self.callback = payload['callback']
        self._response = payload.get('response')

        if footer is None:
            footer = []
        self.footer = footer[:]
        self.footer.append(self.title)

    @property
    def description(self) -> str:
        if isinstance(self._description, str):
            return self._description
        return "\n".join(self._description)

    @property
    def response(self):
        return [
            TicketMenu(value, "{}-{}".format(self.index, index), self.footer)
            for index, value in enumerate(self._response)
        ]

    @property
    def buttons(self) -> List[interaction.Button]:
        return [
            interaction.Button(
                style=2,
                custom_id='menu_selection_{}-{}'.format(self.index, index),
                label=value.get("label"),
                emoji=value.get("emoji")
            ) for index, value in enumerate(self._buttons)
        ]
