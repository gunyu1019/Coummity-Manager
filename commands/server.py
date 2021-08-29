import discord
import io

from matplotlib import pyplot as plt
from typing import Union

import pymysql.cursors

from module import commands
from module.interaction import SlashContext, Message


class Command:
    def __init__(self, bot):
        self.client = bot
        self.color = 0xffd619

    @commands.command(name="상태", permission=4)
    async def status(self, ctx: Union[SlashContext, Message]):
        return


def setup(client):
    return Command(client)
