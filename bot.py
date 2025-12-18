from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+ for Casablanca timezone
import os

# ---------------- CONFIG ----------------
WORK_VOICE_CHANNEL = "💻 work-focus"
LOG_TEXT_CHANNEL = "work-logs"
TOKEN = os.getenv("DISCORD_TOKEN")
CASABLANCA_TZ = ZoneInfo("Africa/Casablanca")

# ---------------- DISCORD BOT ----------------
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
active_sessions = {}  # store join times

# --- Discord Events ---
@bot.event
async def on_ready():
    print(f"✅ Bot connected as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    log_channel = discord.utils.get(guild.text_channels, name=LOG_TEXT_CHANNEL)
    if not log_channel:
        return

    # -------- JOIN WORK CHANNEL --------
    if after.channel and after.channel.name == WORK_VOICE_CHANNEL:
        now = datetime.now(CASABLANCA_TZ)
        active_sessions[member.id] = now
        await log_channel.send(
            f"▶️ **Session started**\n"
            f"👤 {member.display_name}\n"
            f"⏰ {now.strftime('%H:%M')}\n"
            f"📅 {now.date()}"
        )

    # -------- LEAVE WORK CHANNEL --------
    if before.channel and before.channel.name == WORK_VOICE_CHANNEL and (
        not after.channel or after.channel.name != WORK_VOICE_CHANNEL
    ):
        start = active_sessions.pop(member.id, None)
        if start:
            end = datetime.now(CASABLANCA_TZ)
            minutes = round((end - start).total_seconds() / 60, 1)
            await log_channel.send(
                f"⏹ **Session ended**\n"
                f"👤 {member.display_name}\n"
                f"⏰ Start: {start.strftime('%H:%M')}\n"
                f"⏰ End: {end.strftime('%H:%M')}\n"
                f"⌛ **{minutes} minutes**\n"
                f"📅 {end.date()}"
            )

# ---------------- FLASK KEEP-ALIVE ----------------
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()  # start Flask server

# ---------------- RUN BOT ----------------
bot.run(TOKEN)
