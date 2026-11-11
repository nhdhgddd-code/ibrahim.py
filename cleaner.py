import asyncio
import random
import aiohttp
import discord
from discord.ext import commands

_ws = aiohttp.ClientSession.ws_connect
aiohttp.ClientSession.ws_connect = lambda self, *a, **kw: _ws(self, *a, **{**kw, "max_msg_size": 0})

TOKEN = ""

bot = commands.Bot(
    command_prefix="&",
    self_bot=True,
    chunk_guilds_at_startup=False,
    help_command=None
)

running = False

@bot.event
async def on_ready():
    print(f"Ready: {bot.user}")

@bot.before_invoke
async def auto_del(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass

async def clear_msgs(ch):
    global running
    n = 0
    try:
        async for m in ch.history(limit=None):
            if not running:
                break
            if m.author.id == bot.user.id:
                try:
                    await m.delete()
                    n += 1
                    print(f"Deleted [{n}] in { getattr(ch, 'name', ch.id) }")
                    await asyncio.sleep(random.uniform(1.0, 1.4))
                except discord.Forbidden:
                    break
                except discord.HTTPException as e:
                    if e.status == 429:
                        await asyncio.sleep(5)
                    else:
                        await asyncio.sleep(2)
    except Exception:
        pass
    return n

@bot.command()
async def cdm(ctx, uid: int):
    global running
    if running:
        return
    try:
        u = await bot.fetch_user(uid)
        dm = u.dm_channel or await u.create_dm()
    except Exception:
        return

    running = True
    await clear_msgs(dm)
    running = False
    print("DM clean done.")

@bot.command()
async def cchat(ctx, cid: int = None):
    global running
    if running:
        return
    ch = ctx.channel
    if cid:
        ch = bot.get_channel(cid) or await bot.fetch_channel(cid)
    if not ch:
        return

    running = True
    await clear_msgs(ch)
    running = False
    print("Chat clean done.")

@bot.command()
async def cserver(ctx, gid: int):
    global running
    if running:
        return
    g = bot.get_guild(gid)
    if not g:
        return

    running = True
    for ch in g.text_channels:
        if not running:
            break
        await clear_msgs(ch)
    running = False
    print("Server clean done.")

@bot.command()
async def stopclean(ctx):
    global running
    running = False
    print("Stopped.")

@bot.command()
async def help(ctx):
    m = await ctx.send("`&cdm <id>`\n`&cchat <id>`\n`&cserver <id>`\n`&stopclean`")
    await asyncio.sleep(8)
    try:
        await m.delete()
    except Exception:
        pass

bot.run(TOKEN)
