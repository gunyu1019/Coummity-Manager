import discord


def is_owner(author, guild: discord.Guild):
    return author == guild.owner_id


def is_admin(author):
    for i in author.roles:
        if i.permissions.administrator:
            return True
    return False


def check_perm(ctx):
    if ctx.guild is None:
        return

    if is_owner(ctx.author.id, ctx.guild):
        return 1
    elif is_admin(ctx.author):
        return 2
    else:
        return 4


def permission(perm):
    def check(ctx):
        return perm >= check_perm(ctx)
    return check
