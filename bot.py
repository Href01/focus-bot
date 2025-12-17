import discord
from discord.ext import commands
from datetime import datetime
import os

# CONFIG
WORK_VOICE_CHANNEL = "💻 work-focus"
LOG_TEXT_CHANNEL = "work-logs"
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

active_sessions = {}

@bot.event
async def on_ready():
    print(f"✅ Bot connected as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    log_channel = discord.utils.get(guild.text_channels, name=LOG_TEXT_CHANNEL)

    if not log_channel:
        return

    # JOIN WORK CHANNEL
    if after.channel and after.channel.name == WORK_VOICE_CHANNEL:
        active_sessions[member.id] = datetime.now()
        await log_channel.send(
            f"▶️ **Session started**\n"
            f"👤 {member.display_name}\n"
            f"⏰ {datetime.now().strftime('%H:%M')}"
        )

    # LEAVE WORK CHANNEL
    if before.channel and before.channel.name == WORK_VOICE_CHANNEL and (
        not after.channel or after.channel.name != WORK_VOICE_CHANNEL
    ):
        start = active_sessions.pop(member.id, None)
        if start:
            end = datetime.now()
            minutes = round((end - start).total_seconds() / 60, 1)

            await log_channel.send(
                f"⏹ **Session ended**\n"
                f"👤 {member.display_name}\n"
                f"⏰ Start: {start.strftime('%H:%M')}\n"
                f"⏰ End: {end.strftime('%H:%M')}\n"
                f"⌛ **{minutes} minutes**\n"
                f"📅 {end.date()}"
            )

bot.run(TOKEN)
