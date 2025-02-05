#!/usr/bin/env python3
import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import requests
import logging
import subprocess
import os
import sys
import re
from uuid import uuid4
log = logging.getLogger(__name__)
bot = commands.Bot(command_prefix='~')

#whitelist = []

with open("owner.txt", "r") as f:
    owner = int(f.readline())
with open("token.txt", "r") as f:
    token = f.readline()
#with open("channels.txt", "r") as f:
#    for line in f.read().splitlines():
#        whitelist.append(int(line))


@bot.event
async def on_ready():
    log.debug('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

@bot.event
async def on_message(msg):
    if msg.author.bot: return
    if msg.author.id == owner and msg.content.startswith("~"): # Debug mode
        m = msg.content[1:]
        log.debug("Evaluate: {}".format(m))
        try:
            result = eval(m) # Add "await" before eval(m) to access Discord async methods
            log.debug(result)
            await msg.channel.send("```\n{}```".format(result))
        except:
            await msg.channel.send("```\nError:\n{}```".format(traceback.format_exc().replace("```", "\`\`\`")))
    #log.debug("{}: {}".format(msg.author, msg.content))
    # If someone sends a message, check content first
    if re.search(r"https?:.*", msg.content):
        urls = re.findall(r"https?:.*\.mp4", msg.content)
        for url in urls:
            r = requests.get(url)
            fname = str(uuid4())
            with open("tmp/{}.mp4".format(fname), "wb") as f:
                f.write(r.content)
                if await parse(fname, msg): # If we found a crash vid, skip the rest.
                    return
    # Check embeds too
    if msg.embeds:
        for embed in msg.embeds:
            if hasattr(embed, "video") and embed.video.url:
                if embed.video.url.endswith("mp4"):
                    r = requests.get(embed.video.url)
                    fname = str(uuid4())
                    with open("tmp/{}.mp4".format(fname), "wb") as f:
                        f.write(r.content)
                        if await parse(fname, msg):
                            return
    # Finally, check attachments
    if msg.attachments:
        for attachment in msg.attachments:
            log.debug("Filetype: {}".format(attachment.content_type))
            if attachment.content_type == "video/mp4":
                fname = str(uuid4())
                await attachment.save("tmp/{}.mp4".format(fname))
                if await parse(fname, msg):
                    return

async def parse(fname, msg):
    log.debug("Analyzing '{}' <{}>".format(fname, msg))
    was_bad = False
    try:
        probeRes = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "frame=width,height,pix_fmt", "-select_streams", "v", "-of", "csv=p=0", "tmp/{}.mp4".format(fname)], stderr=subprocess.STDOUT, universal_newlines=True).strip().split("\n")
    except subprocess.CalledProcessError as e:
        log.error("ffprobe has crashed with return code {}".format(e.returncode))
        if e.returncode == -9: # If ffprobe runs out of memory, it's likely bad, but just to be safe, we won't kick
            await msg.delete()
            mute_role = get(msg.guild.roles, name="Muted")
            invest_channel = get(msg.guild.channels, name="investigations")
            await msg.author.add_roles(mute_role)
            #await msg.author.kick(reason="Crash gif")

            embed = discord.Embed(colour=discord.Colour(0xfe001a), url="https://discordapp.com", description=msg.content)
            embed.set_author(name=f"{msg.author.name} in #{msg.channel.name}", icon_url=msg.author.avatar_url)
            embed.set_footer(text=f"User ID: {msg.author.id}")
            embed.add_field(name="Message link", value=f"[`Jump to context`](https://discordapp.com/channels/{sent_msg.guild.id}/{sent_msg.channel.id}/{sent_msg.id})")
            
            await invest_channel.send(content=f"<:WindowsDenied:824380486918078494> <@{msg.author.id}> sent a **potential** crash GIF and was muted in <#{msg.channel.id}>", embed=embed)

            was_bad = True
    else:
        first = True
        for width, height, fmt in [i.split(",") for i in probeRes]:
            if first:
                first_frame_vals = (width, height, fmt)
                log.debug("First frame vals: {}".format(first_frame_vals))
                first = False
                continue
            if (width, height, fmt) != first_frame_vals:
                log.debug("Anomaly detected: ({}, {}, {}) has deviated from {}".format(width, height, fmt, first_frame_vals))
                if fmt != first_frame_vals[2] or int(width) > 8000 or int(height) > 8000:
                    try:
                        await msg.delete()
                    except:
                        pass
                    sent_msg = await msg.channel.send("<:CliptokDenied:843582722940993556> <@{}> has been automatically muted: **Sending client-crashing GIF/video**".format(msg.author.id))
                    mute_role = get(msg.guild.roles, name="Muted")
                    invest_channel = get(msg.guild.channels, name="investigations")
                    await msg.author.add_roles(mute_role)
                    #await msg.author.kick(reason="Crash gif")

                    embed = discord.Embed(colour=discord.Colour(0xfe001a), url="https://discordapp.com", description=msg.content)
                    embed.set_author(name=f"{msg.author.name} in #{msg.channel.name}", icon_url=msg.author.avatar_url)
                    embed.set_footer(text=f"User ID: {msg.author.id}")
                    embed.add_field(name="Message link", value=f"[`Jump to context`](https://discordapp.com/channels/{sent_msg.guild.id}/{sent_msg.channel.id}/{sent_msg.id})")
                    if (len(msg.attachments) > 0):
                        for attachment in msg.attachments:
                            embed.add_field(name="Attachment", value=attachment.proxy_url, inline=False)

                    await invest_channel.send(content=f"<:CliptokDenied:843582722940993556> <@{msg.author.id}> sent a crash GIF and was muted in <#{msg.channel.id}>", embed=embed)
                    was_bad = True
                    break
    log.debug("Done analyzing.")
    os.remove("tmp/{}.mp4".format(fname))
    if was_bad:
        return True
    else:
        return False


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)

    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    try:
        bot.run(token, bot=True)
    except RuntimeError:
        sys.exit(0)

