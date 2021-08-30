import logging
import inspect
import importlib
import os

from discord.ext import commands
from discord.state import ConnectionState
from typing import Union, List, Dict

from module.interaction import SlashContext, ComponentsContext
from module.message import Message
from module.commands import Command
from utils.directory import directory
from utils.perm import permission

logger = logging.getLogger(__name__)
DBS = None


class SocketReceive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.func: List[Dict[str, Command]] = []
        cogs = ["commands." + file[:-3] for file in os.listdir(f"{directory}/commands") if file.endswith(".py")]
        for cog in cogs:
            module = importlib.import_module(cog)
            _class = module.setup(self.bot)
            for func, attr in inspect.getmembers(_class):
                if isinstance(attr, Command):
                    self.func.append({"class": _class, "func": attr})

    @staticmethod
    def check_interaction(ctx: Union[SlashContext, Message], func: Command):
        if isinstance(ctx, SlashContext):
            return func.interaction
        elif isinstance(ctx, Message):
            return func.message

    @commands.Cog.listener()
    async def on_interaction_command(self, ctx: Union[SlashContext, Message]):
        if isinstance(ctx, Message):
            prefixes = self.bot.command_prefix
            name = ""
            for prefix in prefixes:
                prefix_length = len(prefix)
                cc = ctx.content[prefix_length:]
                prefix_cc = ctx.content[0:prefix_length]
                if prefix_cc == prefix:
                    name = cc.split()
                    break
            if len(name) >= 1:
                ctx.name = name[0]
            elif len(name) < 1:
                return

        name = ctx.name

        _state: ConnectionState = getattr(self.bot, "_connection")
        for func in self.func:
            _function = func.get("func")
            if (_function.name == name or name in _function.aliases) and self.check_interaction(ctx, _function):
                _state.dispatch("command", ctx)
                if permission(_function.permission)(ctx):
                    try:
                        await _function.callback(func.get("class"), ctx)
                    except Exception as error:
                        _state.dispatch("command_exception", ctx, error)
                    else:
                        _state.dispatch("command_complete", ctx)
                else:
                    _state.dispatch("command_permission_error", ctx)
                break
        return

    @commands.Cog.listener()
    async def on_socket_response(self, payload: dict):
        data = payload.get("d", {})
        t = payload.get("t", "")
        op = payload.get("op", "")

        if t == "PRESENCE_UPDATE" or op != 0:
            return

        logger.debug(payload)

        state: ConnectionState = getattr(self.bot, "_connection")
        if t == "INTERACTION_CREATE":
            if data.get("type") == 2:
                result = SlashContext(data, self.bot)
                state.dispatch('interaction_command', result)
            elif data.get("type") == 3:
                result = ComponentsContext(data, self.bot)
                state.dispatch('components', result)
            return
        elif t == "MESSAGE_CREATE":
            channel, _ = getattr(state, "_get_guild_channel")(data)
            message = Message(state=state, data=data, channel=channel)
            state.dispatch('interaction_command', message)
            return
        return


def setup(client):
    client.add_cog(SocketReceive(client))
