import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
import os
import random
import json
from datetime import datetime
from dotenv import load_dotenv
import asyncio
from pathlib import Path

# Import our modules
from question_bank import *
from api_helpers import (
    fetch_trivia_question,
    fetch_riddle,
    fetch_qotd,
    fetch_wyr,
    fetch_compliment,
    fetch_roast,
    fetch_ai_summary,
)
from music_player import setup_music_commands

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Bot setup with intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
_music_controller = setup_music_commands(bot)

# Store sticky message ID
sticky_message_id = None

# Data storage
_DEFAULT_DATA_FILE = str(
    (Path(__file__).resolve().parent.parent / "data" / "bot_data.json")
)
DATA_FILE = os.getenv("BOT_DATA_FILE", _DEFAULT_DATA_FILE)


def _ensure_data_file():
    """Create the data file with default structure if it does not exist."""
    path = Path(DATA_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            json.dumps(
                {
                    "pet_system": {},
                    "vc_time": {},
                    "trivia_scores": {},
                },
                indent=4,
            )
            + "\n",
            encoding="utf-8",
        )


def load_data():
    """Load bot data from the JSON file, creating it if necessary."""
    _ensure_data_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _ensure_data_file()
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def save_data(data):
    """Persist bot data to the JSON file."""
    _ensure_data_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


bot_data = load_data()

# ---------- COLOR ROLES (37 remaining after cleanup) ----------
COLOR_ROLES = {
    "Red": discord.Color.from_rgb(255, 0, 0),
    "Crimson": discord.Color.from_rgb(220, 20, 60),
    "Rose": discord.Color.from_rgb(255, 0, 127),
    "Maroon": discord.Color.from_rgb(128, 0, 0),
    "Lavender": discord.Color.from_rgb(230, 190, 255),
    "Violet": discord.Color.from_rgb(138, 43, 226),
    "Plum": discord.Color.from_rgb(147, 112, 219),
    "Blue": discord.Color.from_rgb(0, 0, 255),
    "Sapphire": discord.Color.from_rgb(15, 82, 186),
    "Sky": discord.Color.from_rgb(135, 206, 235),
    "Emerald": discord.Color.from_rgb(80, 200, 120),
    "Lime": discord.Color.from_rgb(50, 205, 50),
    "Teal": discord.Color.from_rgb(0, 128, 128),
    "Gold": discord.Color.from_rgb(255, 215, 0),
    "Tangerine": discord.Color.from_rgb(255, 140, 0),
    "Gray": discord.Color.from_rgb(128, 128, 128),
    "Silver": discord.Color.from_rgb(192, 192, 192),
    "Pearl": discord.Color.from_rgb(240, 234, 214),
    "Cream": discord.Color.from_rgb(245, 245, 220),
    "Pink": discord.Color.from_rgb(255, 105, 180),
    "Fuchsia": discord.Color.from_rgb(255, 20, 147),
    "Blush": discord.Color.from_rgb(255, 182, 193),
    "Indigo": discord.Color.from_rgb(75, 0, 130),
    "Lilac": discord.Color.from_rgb(221, 160, 221),
    "Powder": discord.Color.from_rgb(173, 216, 230),
    "Vanilla": discord.Color.from_rgb(255, 239, 213),
    "Linen": discord.Color.from_rgb(250, 240, 230),
    "Fire": discord.Color.from_rgb(255, 0, 0),
    "Neon": discord.Color.from_rgb(0, 255, 0),
    "Plasma": discord.Color.from_rgb(255, 0, 255),
    "Laser": discord.Color.from_rgb(0, 255, 255),
    "Azure": discord.Color.from_rgb(30, 144, 255),
    "Copper": discord.Color.from_rgb(160, 82, 45),
    "Sand": discord.Color.from_rgb(210, 180, 140),
    "Bronze": discord.Color.from_rgb(205, 133, 63),
    "Taupe": discord.Color.from_rgb(152, 140, 126),
}


class ColorRoleButton(Button):
    def __init__(self, color_name):
        super().__init__(
            label=color_name,
            style=discord.ButtonStyle.gray,
            custom_id=f"color_role_{color_name}",
        )
        self.color_name = color_name

    async def callback(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=self.color_name)
        if not role:
            await interaction.response.send_message(
                f"⚠️ Role {self.color_name} not found!", ephemeral=True
            )
            return
        current_roles = [
            r for r in interaction.user.roles if r.name in COLOR_ROLES]
        if current_roles:
            await interaction.user.remove_roles(*current_roles)
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"You have selected **{self.color_name}** ✅", ephemeral=True
            )
        except Exception:
            await interaction.response.send_message(
                "⚠️ Error assigning role", ephemeral=True
            )


class ColorRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for name in list(COLOR_ROLES.keys())[:25]:
            self.add_item(ColorRoleButton(name))


class ColorRoleView2(View):
    def __init__(self):
        super().__init__(timeout=None)
        for name in list(COLOR_ROLES.keys())[25:50]:
            self.add_item(ColorRoleButton(name))


class ColorRoleView3(View):
    def __init__(self):
        super().__init__(timeout=None)
        for name in list(COLOR_ROLES.keys())[50:]:
            self.add_item(ColorRoleButton(name))


class NotificationView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔔 VC Pings", style=discord.ButtonStyle.gray, custom_id="notif_vc_ping"
    )
    async def vc_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="VC Ping")
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    "🔕 VC Ping disabled", ephemeral=True
                )
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    "🔔 VC Ping enabled", ephemeral=True
                )

    @discord.ui.button(
        label="💬 Chat Pings",
        style=discord.ButtonStyle.gray,
        custom_id="notif_chat_ping",
    )
    async def chat_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Chat Ping")
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    "🔕 Chat Ping disabled", ephemeral=True
                )
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    "🔔 Chat Ping enabled", ephemeral=True
                )

    @discord.ui.button(
        label="🎮 Game Pings",
        style=discord.ButtonStyle.gray,
        custom_id="notif_game_ping",
    )
    async def game_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Game Ping")
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    "🔕 Game Ping disabled", ephemeral=True
                )
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    "🔔 Game Ping enabled", ephemeral=True
                )

    @discord.ui.button(
        label="🎉 Event Pings",
        style=discord.ButtonStyle.gray,
        custom_id="notif_event_ping",
    )
    async def event_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Event Ping")
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    "🔕 Event Ping disabled", ephemeral=True
                )
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    "🔔 Event Ping enabled", ephemeral=True
                )


# ==================== TRIVIA GAME (API - Unlimited) ====================
active_trivias = {}


@bot.tree.command(name="trivia", description="Get unlimited trivia questions from API")
async def trivia(interaction: discord.Interaction):
    question = await fetch_trivia_question()
    if not question:
        question = {
            "q": "What is the capital of Pakistan?",
            "a": "Islamabad",
            "options": ["Karachi", "Islamabad", "Lahore", "Quetta"],
        }

    embed = discord.Embed(
        title="🧠 Trivia Time!", description=question["q"], color=discord.Color.blue()
    )
    for i, opt in enumerate(question["options"], 1):
        embed.add_field(name=f"Option {i}", value=opt, inline=False)
    embed.set_footer(text="Reply with your answer! Results in 2 minutes.")

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()

    active_trivias[msg.id] = {
        "question": question,
        "answers": {},
        "channel": interaction.channel,
    }
    await asyncio.sleep(120)
    await reveal_trivia_answer(msg.id)


async def reveal_trivia_answer(trivia_id):
    """Reveal the correct answer and award points after the trivia timer expires."""
    if trivia_id not in active_trivias:
        return

    trivia_data = active_trivias[trivia_id]
    question = trivia_data["question"]
    answers = trivia_data["answers"]
    channel = trivia_data["channel"]

    correct_users = []
    for user_id, answer in answers.items():
        if answer.lower() == question["a"].lower():
            correct_users.append(f"<@{user_id}>")
            if user_id not in bot_data["trivia_scores"]:
                bot_data["trivia_scores"][user_id] = 0
            bot_data["trivia_scores"][user_id] += 1

    save_data(bot_data)

    embed = discord.Embed(
        title="🎯 Trivia Results!",
        description=f"**Correct Answer:** {question['a']}",
        color=discord.Color.green(),
    )

    if correct_users:
        embed.add_field(
            name="✅ Correct Answers", value=", ".join(correct_users), inline=False
        )
    else:
        embed.add_field(
            name="❌ No Correct Answers", value="Better luck next time!", inline=False
        )

    embed.add_field(
        name="📊 Total Responses", value=f"{len(answers)} people answered", inline=False
    )

    await channel.send(embed=embed)
    del active_trivias[trivia_id]


@bot.event
async def on_message_trivia_answer(message):
    if message.author.bot:
        return

    for trivia_id, trivia_data in active_trivias.items():
        if message.channel == trivia_data["channel"]:
            trivia_data["answers"][str(
                message.author.id)] = message.content.strip()


@bot.tree.command(name="triviascores", description="Show trivia leaderboard")
async def triviascores(interaction: discord.Interaction):
    scores = bot_data["trivia_scores"]
    if not scores:
        await interaction.response.send_message("No trivia scores yet!")
        return

    sorted_scores = sorted(
        scores.items(), key=lambda x: x[1], reverse=True)[:10]
    embed = discord.Embed(title="🏆 Trivia Leaderboard",
                          color=discord.Color.gold())

    for i, (user_id, score) in enumerate(sorted_scores, 1):
        user = await bot.fetch_user(int(user_id))
        embed.add_field(name=f"{i}. {user.name}",
                        value=f"{score} points", inline=False)

    await interaction.response.send_message(embed=embed)


# ==================== WOULD YOU RATHER (API - Unlimited) ====================

@bot.tree.command(name="wyr", description="Get unlimited Would You Rather questions")
async def wyr(interaction: discord.Interaction):
    question = await fetch_wyr()
    if not question:
        question = random.choice(WYR_QUESTIONS)

    embed = discord.Embed(
        title="🤔 Would You Rather?", description=question, color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("1️⃣")
    await msg.add_reaction("2️⃣")


# ==================== RIDDLES (API - Unlimited) ====================
active_riddles = {}


@bot.tree.command(name="riddle", description="Get unlimited riddles from API")
async def riddle(interaction: discord.Interaction):
    riddle = await fetch_riddle()
    if not riddle:
        riddles_list = [
            {"q": "What has keys but no locks?", "a": "keyboard"},
            {"q": "I speak without a mouth. What am I?", "a": "echo"},
        ]
        riddle = random.choice(riddles_list)

    embed = discord.Embed(
        title="🤯 Riddle Time!", description=riddle["q"], color=discord.Color.orange()
    )
    embed.set_footer(
        text="You have 5 minutes to guess! First correct answer wins.")

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()

    active_riddles[msg.id] = {"riddle": riddle,
                              "channel": interaction.channel, "solved": False}
    await asyncio.sleep(300)
    await reveal_riddle_answer(msg.id)


async def reveal_riddle_answer(riddle_id):
    """Reveal the riddle answer if nobody solved it before timeout."""
    if riddle_id not in active_riddles:
        return

    riddle_data = active_riddles[riddle_id]

    if not riddle_data["solved"]:
        riddle = riddle_data["riddle"]
        channel = riddle_data["channel"]

        embed = discord.Embed(
            title="⏰ Time's Up!",
            description=f"**Answer:** {riddle['a']}",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="❌ No one guessed it!", value="Better luck next time!", inline=False
        )

        await channel.send(embed=embed)

    del active_riddles[riddle_id]


@bot.event
async def on_message_riddle_answer(message):
    if message.author.bot:
        return

    for riddle_id, riddle_data in list(active_riddles.items()):
        if message.channel == riddle_data["channel"] and not riddle_data["solved"]:
            riddle = riddle_data["riddle"]

            if riddle["a"].lower() in message.content.lower():
                riddle_data["solved"] = True

                embed = discord.Embed(
                    title="🎉 Riddle Solved!",
                    description=f"{message.author.mention} got it right!",
                    color=discord.Color.green(),
                )
                embed.add_field(
                    name="✅ Correct Answer", value=riddle["a"], inline=False
                )

                await message.channel.send(embed=embed)
                del active_riddles[riddle_id]
                break


# ==================== ROAST GENERATOR (Friendly & Unlimited) ====================
@bot.tree.command(name="roast", description="Give someone a friendly roast")
@app_commands.describe(member="The member to roast (optional)")
async def roast(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user

    roast_text = await fetch_roast()
    if not roast_text:
        roast_text = random.choice(ROASTS)

    embed = discord.Embed(
        title="🔥 Roast Battle!",
        description=f"{member.mention} {roast_text}",
        color=discord.Color.red(),
    )
    await interaction.response.send_message(embed=embed)


# ==================== QOTD ====================
@bot.tree.command(name="qotd", description="Get Question of the Day")
async def qotd(interaction: discord.Interaction):
    question = await fetch_qotd()
    if not question:
        question = random.choice(QOTD_QUESTIONS)

    embed = discord.Embed(
        title="💭 Question of the Day", description=question, color=discord.Color.teal()
    )
    await interaction.response.send_message(embed=embed)


# ==================== COMPLIMENT GENERATOR ====================

@bot.tree.command(name="compliment", description="Give someone a compliment")
@app_commands.describe(member="The member to compliment (optional)")
async def compliment(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user

    compliment_text = await fetch_compliment()
    if not compliment_text:
        compliment_text = random.choice(COMPLIMENTS)

    embed = discord.Embed(
        title="💝 Compliment",
        description=f"{member.mention} {compliment_text}",
        color=discord.Color.pink(),
    )
    await interaction.response.send_message(embed=embed)


# ==================== SERVER STATS ====================
@bot.tree.command(name="stats", description="Show server statistics")
async def stats(interaction: discord.Interaction):
    guild = interaction.guild
    total_members = guild.member_count
    online_members = sum(
        1 for m in guild.members if m.status != discord.Status.offline)
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)

    embed = discord.Embed(
        title=f"📊 {guild.name} Statistics", color=discord.Color.blue()
    )
    embed.add_field(name="Total Members", value=total_members, inline=True)
    embed.add_field(name="Online Members", value=online_members, inline=True)
    embed.add_field(name="Text Channels", value=text_channels, inline=True)
    embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

    await interaction.response.send_message(embed=embed)


# ==================== VOICE TIME TRACKER ====================
@bot.event
async def on_voice_state_update(member, before, after):
    """Track voice channel join/leave times per user per server."""
    user_id = str(member.id)
    guild_id = str(member.guild.id)
    server_key = f"{user_id}_{guild_id}"

    if server_key not in bot_data["vc_time"]:
        bot_data["vc_time"][server_key] = {"total_minutes": 0}

    if before.channel is None and after.channel is not None:
        bot_data["vc_time"][server_key]["join_time"] = datetime.now().isoformat()
        save_data(bot_data)
        print(
            f"✅ {member.name} joined VC in {member.guild.name} at {datetime.now()}")

    elif before.channel is not None and after.channel is None:
        if "join_time" in bot_data["vc_time"][server_key]:
            join_time = datetime.fromisoformat(
                bot_data["vc_time"][server_key]["join_time"]
            )
            duration = (datetime.now() - join_time).total_seconds() / 60

            bot_data["vc_time"][server_key]["total_minutes"] += duration
            del bot_data["vc_time"][server_key]["join_time"]
            save_data(bot_data)
            print(
                f"✅ {member.name} left VC in {member.guild.name}. Session: {duration:.1f} min, Total: {bot_data['vc_time'][server_key]['total_minutes']:.1f} min"
            )


@bot.tree.command(name="vctime", description="Check your voice chat time in this server")
async def vctime(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    guild_id = str(interaction.guild.id)
    server_key = f"{user_id}_{guild_id}"

    if server_key not in bot_data["vc_time"]:
        bot_data["vc_time"][server_key] = {"total_minutes": 0}
        save_data(bot_data)

    total_minutes = bot_data["vc_time"][server_key].get("total_minutes", 0)

    if "join_time" in bot_data["vc_time"][server_key]:
        join_time = datetime.fromisoformat(
            bot_data["vc_time"][server_key]["join_time"])
        current_session = (datetime.now() - join_time).total_seconds() / 60
        total_minutes += current_session

    if total_minutes > 0:
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        await interaction.response.send_message(f"🎤 You've spent **{hours}h {minutes}m** in voice channels in **{interaction.guild.name}**!")
    else:
        await interaction.response.send_message(
            "You haven't joined any voice channels in this server yet! Join a VC to start tracking your time."
        )


# ==================== REACTION ROLES ====================
class HobbyRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎮 Gaming", style=discord.ButtonStyle.gray, custom_id="hobby_gaming"
    )
    async def gaming(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Gaming")
        await self.toggle_role(interaction, role)

    @discord.ui.button(
        label="🎨 Art", style=discord.ButtonStyle.gray, custom_id="hobby_art"
    )
    async def art(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Art")
        await self.toggle_role(interaction, role)

    @discord.ui.button(
        label="🎵 Music", style=discord.ButtonStyle.gray, custom_id="hobby_music"
    )
    async def music(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Music")
        await self.toggle_role(interaction, role)

    @discord.ui.button(
        label="📚 Reading", style=discord.ButtonStyle.gray, custom_id="hobby_reading"
    )
    async def reading(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        role = discord.utils.get(interaction.guild.roles, name="Reading")
        await self.toggle_role(interaction, role)

    async def toggle_role(self, interaction, role):
        """Add or remove a role from the user, toggling its state."""
        if not role:
            await interaction.response.send_message(
                "❌ Role not found!", ephemeral=True
            )
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                f"Removed {role.name} role", ephemeral=True
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"Added {role.name} role", ephemeral=True
            )


@bot.tree.command(name="setuphobbies", description="Setup hobby reaction roles (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def setuphobbies(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎯 Choose Your Hobbies!",
        description="Click the buttons below to get hobby roles",
        color=discord.Color.green(),
    )
    await interaction.response.send_message(embed=embed, view=HobbyRoleView())


# ==================== PET SYSTEM ====================
@bot.tree.command(name="adopt", description="Adopt a virtual pet")
async def adopt(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id in bot_data["pet_system"]:
        await interaction.response.send_message("You already have a pet!")
        return

    pet = random.choice(PETS)
    bot_data["pet_system"][user_id] = {
        "pet": pet, "hunger": 100, "happiness": 100}
    save_data(bot_data)

    embed = discord.Embed(
        title="🎉 Pet Adopted!",
        description=f"You adopted a {pet}!",
        color=discord.Color.green(),
    )
    await interaction.response.send_message(embed=embed)


# ==================== REKHTA POETRY ====================
@bot.tree.command(name="rekhta", description="Get random Urdu poetry")
async def rekhta(interaction: discord.Interaction):
    poetry = random.choice(URDU_POETRY)
    embed = discord.Embed(
        title="📜 Urdu Poetry", description=poetry, color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)


# ==================== POMODORO TIMER ====================
@bot.tree.command(name="pomodoro", description="Start a Pomodoro study timer")
@app_commands.describe(minutes="Timer duration in minutes (max 60)")
async def pomodoro(interaction: discord.Interaction, minutes: int = 25):
    if minutes > 60:
        await interaction.response.send_message("Maximum 60 minutes!")
        return

    await interaction.response.send_message(f"⏰ Pomodoro timer started for {minutes} minutes!")
    await asyncio.sleep(minutes * 60)
    await interaction.channel.send(f"{interaction.user.mention} ⏰ Time's up! Take a break! 🎉")


# ==================== TLDR COMMAND ====================
@bot.tree.command(name="tldr", description="Summarize previous messages in the channel")
@app_commands.describe(count="Number of messages to summarize (50, 100, 200, or 500)")
@app_commands.choices(count=[
    app_commands.Choice(name="50 messages", value=50),
    app_commands.Choice(name="100 messages", value=100),
    app_commands.Choice(name="200 messages", value=200),
    app_commands.Choice(name="500 messages", value=500),
])
async def tldr(interaction: discord.Interaction, count: int):
    await interaction.response.defer()

    try:
        messages = []

        # Collect messages
        async for message in interaction.channel.history(limit=count):
            if not message.author.bot and message.content:
                timestamp = message.created_at.strftime("%H:%M")
                author_name = message.author.display_name
                content = message.content
                messages.append(f"[{timestamp}] {author_name}: {content}")

        messages.reverse()

        if not messages:
            await interaction.followup.send("No messages found to summarize!")
            return

        # Prepare text for AI (limit to avoid token limits)
        messages_text = "\n".join(messages[:200])  # Max 200 messages for AI

        # Try to get AI summary
        ai_summary = await fetch_ai_summary(messages_text)

        if ai_summary:
            # AI generated summary
            embed = discord.Embed(
                title="📝 Channel Summary",
                description=ai_summary,
                color=discord.Color.blue()
            )
            embed.set_footer(
                text=f"AI-generated summary of {len(messages)} messages | Powered by Gemini")
            await interaction.followup.send(embed=embed)
        else:
            # Fallback to basic summary
            summary = "**Summary of the Conversation 💬**\n\n"
            summary += f"**Total messages:** {len(messages)}\n\n"

            # Show participants
            authors = list(set([msg.split("]")[1].split(":")[0].strip()
                           for msg in messages if "]" in msg and ":" in msg]))
            summary += f"**Participants:** {', '.join(authors[:10])}\n\n"

            # Show sample messages
            summary += "**Sample messages:**\n"
            sample_count = min(10, len(messages))
            step = max(1, len(messages) // sample_count)
            for i in range(0, len(messages), step):
                if i < len(messages):
                    msg_preview = messages[i][:200]
                    summary += f"{msg_preview}\n"

            summary += f"\n⚠️ **Note:** Set GEMINI_API_KEY environment variable for AI-powered summaries!\n"
            summary += "Get free API key from: https://aistudio.google.com/app/apikey"

            if len(summary) > 4000:
                summary = summary[:3997] + "..."

            embed = discord.Embed(
                title="📝 Channel Summary",
                description=summary,
                color=discord.Color.orange()
            )
            embed.set_footer(text=f"Analyzed {len(messages)} messages")
            await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"❌ Error creating summary: {str(e)}")


# ==================== ADMIN COMMANDS ====================
@bot.tree.command(name="purge", description="Bulk delete messages (requires Manage Messages)")
@app_commands.describe(
    count="Input number of messages to search for (max 100)",
    message_link="Paste a message link — deletes all messages after it",
    filter="Filter by message type: all, text, image, voice, links",
)
@app_commands.choices(filter=[
    app_commands.Choice(name="All messages", value="all"),
    app_commands.Choice(name="Text only", value="text"),
    app_commands.Choice(name="Images only", value="image"),
    app_commands.Choice(name="Voice messages only", value="voice"),
    app_commands.Choice(name="Links only", value="links"),
])
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(
    interaction: discord.Interaction,
    count: int = 10,
    message_link: str = None,
    filter: str = "all",
):
    await interaction.response.defer(ephemeral=True)

    # If message_link is provided and count wasn't explicitly set, default to 100
    if message_link and count == 10:
        count = 100

    if count < 1 or count > 100:
        await interaction.followup.send("❌ Count must be between 1 and 100.", ephemeral=True)
        return

    # Resolve the anchor message if a link was provided
    after_message = None
    if message_link:
        try:
            # Extract message ID from link
            # Format: https://discord.com/channels/guild_id/channel_id/message_id
            parts = message_link.rstrip("/").split("/")
            msg_id = int(parts[-1])
            after_message = await interaction.channel.fetch_message(msg_id)
        except Exception:
            await interaction.followup.send(
                "❌ Could not find that message. Make sure the link is from this channel.",
                ephemeral=True,
            )
            return

    # Define filter function
    def msg_filter(msg: discord.Message) -> bool:
        if filter == "all":
            return True
        if filter == "text":
            return bool(msg.content) and not msg.attachments
        if filter == "image":
            return any(
                a.content_type and a.content_type.startswith("image/")
                for a in msg.attachments
            )
        if filter == "voice":
            return any(
                a.content_type and "ogg" in a.content_type
                for a in msg.attachments
            )
        if filter == "links":
            return bool(msg.content) and ("http://" in msg.content or "https://" in msg.content)
        return True

    # Purge messages
    try:
        from datetime import timedelta

        total_deleted = 0

        if after_message:
            # Collect messages after the anchor message, then bulk delete
            to_delete = []
            async for msg in interaction.channel.history(
                limit=count, after=after_message, oldest_first=True
            ):
                if msg_filter(msg):
                    to_delete.append(msg)

            # Bulk delete in batches of 100
            for i in range(0, len(to_delete), 100):
                batch = to_delete[i:i+100]
                try:
                    await interaction.channel.delete_messages(batch)
                except Exception:
                    pass
            total_deleted = len(to_delete)
        else:
            deleted = await interaction.channel.purge(
                limit=count,
                check=msg_filter,
                bulk=True,
            )
            total_deleted = len(deleted)

        filter_label = {
            "all": "messages", "text": "text messages",
            "image": "images", "voice": "voice messages", "links": "messages with links"
        }

        if total_deleted == 0:
            await interaction.followup.send(
                "No messages deleted, make sure the messages aren't over two weeks old.",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"✅ Deleted **{total_deleted}** {filter_label.get(filter, 'messages')}.",
                ephemeral=True,
            )
    except discord.Forbidden:
        await interaction.followup.send("❌ I don't have permission to delete messages here.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)


@purge.error
async def purge_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You need **Manage Messages** permission to use this command.", ephemeral=True
        )


@bot.tree.command(name="checkroles", description="Debug command to check all server roles (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def checkroles(interaction: discord.Interaction):
    roles_list = [
        f"• {role.name} (ID: {role.id})" for role in interaction.guild.roles]
    roles_text = "\n".join(roles_list)

    embed = discord.Embed(
        title="🔍 Server Roles Debug",
        description=f"**All roles in this server:**\n{roles_text}",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="welcome", description="Send welcome message for newly verified member (Mod only)")
@app_commands.describe(member="The member to welcome")
@app_commands.checks.has_permissions(manage_roles=True)
async def welcome(interaction: discord.Interaction, member: discord.Member):
    verified_role = discord.utils.get(
        interaction.guild.roles, name="✔️Verified")

    if not verified_role:
        await interaction.response.send_message("❌ Verified role not found!")
        return

    if verified_role not in member.roles:
        await interaction.response.send_message(f"❌ {member.mention} doesn't have the Verified role yet!")
        return

    general_channel = discord.utils.get(
        interaction.guild.text_channels, name="general")
    self_roles_channel = discord.utils.get(
        interaction.guild.text_channels, name="self-roles")

    if general_channel:
        if self_roles_channel:
            welcome_message = (
                f"🎉 Welcome {member.mention} to {interaction.guild.name}! 🎉\n"
                f"Hop over to {self_roles_channel.mention} to grab your roles and join the fun!"
            )
        else:
            welcome_message = (
                f"🎉 Welcome {member.mention} to {interaction.guild.name}! 🎉\n"
                f"Hop over to #self-roles to grab your roles and join the fun!"
            )

        await general_channel.send(welcome_message)
        await interaction.response.send_message(f"✅ Welcome message sent for {member.mention}!")
        print(f"✅ Manual welcome message sent for {member.name}")
    else:
        await interaction.response.send_message("❌ General channel not found!")


@bot.tree.command(name="checkintents", description="Check if bot has required intents enabled (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def checkintents(interaction: discord.Interaction):
    intents_status = []
    intents_status.append(
        f"{'✅' if bot.intents.members else '❌'} Members Intent: {bot.intents.members}")
    intents_status.append(
        f"{'✅' if bot.intents.guilds else '❌'} Guilds Intent: {bot.intents.guilds}")
    intents_status.append(
        f"{'✅' if bot.intents.message_content else '❌'} Message Content: {bot.intents.message_content}")

    embed = discord.Embed(
        title="🔍 Bot Intents Status",
        description="\n".join(intents_status),
        color=discord.Color.green() if bot.intents.members else discord.Color.red()
    )

    if not bot.intents.members:
        embed.add_field(
            name="⚠️ Members Intent Disabled",
            value="You need to enable 'Server Members Intent' in Discord Developer Portal",
            inline=False
        )
    else:
        embed.add_field(
            name="✅ All Good",
            value="The on_member_update event should work. If it's not triggering, try restarting the bot.",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="checkaudit", description="Check recent audit log entries (Admin only)")
@app_commands.describe(limit="Number of entries to show (default 10)")
@app_commands.checks.has_permissions(administrator=True)
async def checkaudit(interaction: discord.Interaction, limit: int = 10):
    await interaction.response.defer()

    try:
        audit_logs = []
        async for entry in interaction.guild.audit_logs(limit=limit):
            action_type = str(entry.action).replace('AuditLogAction.', '')
            audit_logs.append(
                f"**{action_type}** by {entry.user.mention}\n"
                f"Target: {entry.target}\n"
                f"Time: <t:{int(entry.created_at.timestamp())}:R>\n"
            )

        if audit_logs:
            chunks = []
            current_chunk = ""
            for log in audit_logs:
                if len(current_chunk) + len(log) > 1900:
                    chunks.append(current_chunk)
                    current_chunk = log
                else:
                    current_chunk += log + "\n"
            if current_chunk:
                chunks.append(current_chunk)

            for i, chunk in enumerate(chunks):
                embed = discord.Embed(
                    title=f"📋 Recent Audit Log ({i+1}/{len(chunks)})",
                    description=chunk,
                    color=discord.Color.blue()
                )
                if i == 0:
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.channel.send(embed=embed)
        else:
            await interaction.followup.send("No audit log entries found.")
    except discord.Forbidden:
        await interaction.followup.send("❌ Bot doesn't have permission to view audit logs!")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")


# ==================== MILESTONE CELEBRATIONS ====================
@bot.event
async def on_member_join(member):
    unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
    if unverified_role:
        await member.add_roles(unverified_role)
        print(f"✅ Assigned Unverified role to {member.name}")

    guild = member.guild
    member_count = guild.member_count

    milestones = [50, 100, 200, 500, 1000]
    if member_count in milestones:
        channel = discord.utils.get(guild.text_channels, name="general")
        if channel:
            embed = discord.Embed(
                title="🎉 MILESTONE REACHED!",
                description=f"We just hit **{member_count} members**! 🎊",
                color=discord.Color.gold(),
            )
            await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    print(f"⚠️ {member.name} ({member.id}) left the server")
    print(
        f"   Roles they had: {[role.name for role in member.roles if role.name != '@everyone']}")
    print(f"   Joined at: {member.joined_at}")
    print(f"   Account created: {member.created_at}")

    verified_role = discord.utils.get(member.guild.roles, name="✔️Verified")
    if verified_role and verified_role in member.roles:
        print(f"   ⚠️ WARNING: This member had the Verified role!")

        logs_channel = discord.utils.get(
            member.guild.text_channels, name="logs")
        if logs_channel:
            embed = discord.Embed(
                title="⚠️ Verified Member Left",
                description=f"{member.mention} ({member.name}) left the server",
                color=discord.Color.orange()
            )
            embed.add_field(name="User ID", value=member.id, inline=True)
            embed.add_field(
                name="Joined", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
            embed.add_field(name="Roles", value=", ".join(
                [r.name for r in member.roles if r.name != '@everyone']) or "None", inline=False)
            await logs_channel.send(embed=embed)


# ==================== VERIFIED ROLE WELCOME ====================
@bot.event
async def on_member_update(before, after):
    print(f"🔍 Member update detected: {after.name}")

    before_roles = set(before.roles)
    after_roles = set(after.roles)
    added_roles = after_roles - before_roles

    if added_roles:
        print(f"📝 Roles added: {[role.name for role in added_roles]}")

    verified_role = None
    for role in after.guild.roles:
        if role.name == "✔️Verified":
            verified_role = role
            print(f"🔎 Found verified role: {role.name}")
            break

    if not verified_role:
        print(f"⚠️ No '✔️Verified' role found in server roles")

    if verified_role and verified_role in added_roles:
        print(f"✅ Verified role detected for {after.name}")

        general_channel = discord.utils.get(
            after.guild.text_channels, name="general")
        self_roles_channel = discord.utils.get(
            after.guild.text_channels, name="self-roles")

        print(f"🔎 General channel: {general_channel}")
        print(f"🔎 Self-roles channel: {self_roles_channel}")

        if general_channel:
            if self_roles_channel:
                welcome_message = (
                    f"🎉 Welcome {after.mention} to {after.guild.name}! 🎉\n"
                    f"Hop over to {self_roles_channel.mention} to grab your roles and join the fun!"
                )
            else:
                welcome_message = (
                    f"🎉 Welcome {after.mention} to {after.guild.name}! 🎉\n"
                    f"Hop over to #self-roles to grab your roles and join the fun!"
                )

            await general_channel.send(welcome_message)
            print(f"✅ Sent welcome message for {after.name} in general")
        else:
            print(f"❌ General channel not found")
            print(
                f"Available channels: {[c.name for c in after.guild.text_channels]}")


# ==================== MESSAGE LOGS ====================
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    logs_channel = discord.utils.get(message.guild.text_channels, name="logs")
    if logs_channel:
        deleted_by = "Self-deleted or Unknown"
        try:
            await asyncio.sleep(0.5)
            async for entry in message.guild.audit_logs(
                limit=5, action=discord.AuditLogAction.message_delete
            ):
                if (
                    entry.target.id == message.author.id
                    and entry.extra.channel.id == message.channel.id
                    and (
                        datetime.now() - entry.created_at.replace(tzinfo=None)
                    ).total_seconds()
                    < 2
                ):
                    deleted_by = entry.user.mention
                    break
        except Exception as e:
            print(f"Error fetching audit log: {e}")

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Deleted by:** {deleted_by}\n**Content:** {message.content[:1024] if message.content else 'No content'}",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        await logs_channel.send(embed=embed)


# ==================== AUTO-REACTIONS & STICKY MESSAGE ====================
@bot.event
async def on_message(message):
    global sticky_message_id

    # ==================== NAAMWAHAB AUTO-REPLY ====================
    if message.author.name == "naamwahab" and not message.author.bot and message.guild:
        try:
            emoji = discord.utils.get(message.guild.emojis, name="terichyenahiraye")
            if emoji:
                await message.add_reaction(emoji)
                print(f"✅ Reacted to naamwahab")
            else:
                print(f"❌ Emoji terichyenahiraye not found")
        except Exception as e:
            print(f"❌ naamwahab reaction error: {e}")

    # ==================== DEXTER AUTO-REPLY (every 10th message) ====================
    if message.author.name == "_notdexter_" and not message.author.bot:
        if not hasattr(bot, "_dexter_msg_count"):
            bot._dexter_msg_count = 0
        bot._dexter_msg_count += 1
        print(f"🔢 Dexter: {bot._dexter_msg_count}/10")
        if bot._dexter_msg_count >= 10:
            bot._dexter_msg_count = 0
            try:
                await message.reply("https://tenor.com/view/dungeong-gif-13362807664297827620")
                print(f"✅ Replied to Dexter")
            except Exception as e:
                print(f"❌ Dexter reply error: {e}")

    # ==================== COOL AUTO-REPLY (every 5th message, rotating msgs) ====================
    if message.author.name == "imsohail_" and not message.author.bot:
        if not hasattr(bot, "_cool_msg_count"):
            bot._cool_msg_count = 0
        if not hasattr(bot, "_cool_msg_index"):
            bot._cool_msg_index = 0
        bot._cool_msg_count += 1
        print(f"🔢 Cool: {bot._cool_msg_count}/5")
        if bot._cool_msg_count >= 5:
            bot._cool_msg_count = 0
            cool_replies = [
                "take this anti hawas tablets 20 times a day pls 💊",
                "Esi baat par @Cool Kalma parhlo.",
                "yaqeen kro farishto ki jooti ka size shahrah e faisal se bara he uska khouf kha lo",
                "i just checked google emran hashmi dad's generation is in pakistan too he married here too @Cool is related to that tree",
                "cool thinks 2 planet apas me masti kr rhe the earth ban gayi or hum sab agaye...",
            ]
            reply_text = cool_replies[bot._cool_msg_index % len(cool_replies)]
            bot._cool_msg_index += 1
            try:
                await message.reply(reply_text)
                print(f"✅ Replied to Cool (msg {bot._cool_msg_index})")
            except Exception as e:
                print(f"❌ Cool reply error: {e}")

    # ==================== AUDI AUTO-REPLY (every 10th message) ====================
    if message.author.name == "iidentifyasaudi" and not message.author.bot:
        if not hasattr(bot, "_audi_msg_count"):
            bot._audi_msg_count = 0
        bot._audi_msg_count += 1
        print(f"🔢 Audi: {bot._audi_msg_count}/10")
        if bot._audi_msg_count >= 10:
            bot._audi_msg_count = 0
            try:
                await message.reply("bhai bhai bhai")
                print(f"✅ Replied to Audi")
            except Exception as e:
                print(f"❌ Audi reply error: {e}")

    # ==================== FORBIDDEN DESSERT AUTO-REPLY (every 10th message) ====================
    if message.author.name == "forbiddendessert" and not message.author.bot:
        if not hasattr(bot, "_forbidden_msg_count"):
            bot._forbidden_msg_count = 0
        bot._forbidden_msg_count += 1
        print(f"🔢 Forbidden: {bot._forbidden_msg_count}/10")
        if bot._forbidden_msg_count >= 10:
            bot._forbidden_msg_count = 0
            try:
                await message.reply("Aunty chill")
                print(f"✅ Replied to Forbidden Dessert")
            except Exception as e:
                print(f"❌ Forbidden reply error: {e}")

    # Ignore DMs — all channel-specific logic below requires a guild channel
    if not isinstance(message.channel, discord.TextChannel):
        await bot.process_commands(message)
        return

    # ==================== AUTO CONFESSION THREADS ====================
    # Confessions bot posts anonymously in freedom-of-speech channel
    # Auto-create a public thread so members can discuss without typing
    if message.channel.name == "freedom-of-speech" and message.author.bot:
        try:
            # Extract confession number from embed title e.g. "Anonymous Confession (#1322)"
            thread_name = "💬 Confession"
            if message.embeds:
                title = message.embeds[0].title or ""
                import re
                match = re.search(r"#(\d+)", title)
                if match:
                    thread_name = f"💬 Confession #{match.group(1)}"
            await message.create_thread(
                name=thread_name,
                auto_archive_duration=1440,  # archive after 24h of inactivity
            )
        except Exception:
            pass

    if message.author.bot:
        return

    # ==================== FOODIE: IMAGE ONLY + AUTO THREAD ====================
    if message.channel.name == "foodie" and not message.author.bot:
        has_image = any(
            a.content_type and a.content_type.startswith("image/")
            for a in message.attachments
        )
        if not has_image:
            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention} ❌ Only food images are allowed in **#foodie**.\n"
                    "• Post your food photos here\n"
                    "• A discussion thread will be created automatically\n"
                    "• Text and voice messages are not allowed",
                    delete_after=8,
                )
            except Exception:
                pass
            return

        try:
            thread_name = f"🍽️ {message.author.display_name}'s post"
            await message.create_thread(
                name=thread_name,
                auto_archive_duration=1440,
            )
        except Exception:
            pass

    # ==================== ART-N-CLICKS: IMAGE ONLY + AUTO THREAD ====================
    # Delete non-image messages, auto-create thread on images for comments
    if message.channel.name == "art-n-clicks" and not message.author.bot:
        has_image = any(
            a.content_type and a.content_type.startswith("image/")
            for a in message.attachments
        )
        if not has_image:
            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention} ❌ Only images are allowed in **#art-n-clicks**.\n"
                    "• Post your photos, art, or screenshots here\n"
                    "• A discussion thread will be created automatically\n"
                    "• Text and voice messages are not allowed",
                    delete_after=8,
                )
            except Exception:
                pass
            return

        # Image posted — create a thread for comments
        try:
            thread_name = f"🎨 {message.author.display_name}'s post"
            await message.create_thread(
                name=thread_name,
                auto_archive_duration=1440,
            )
        except Exception:
            pass

    # ==================== AUTO INTRO THREADS ====================
    # When an unverified member posts their intro, auto-create a thread
    # so verified members can welcome and discuss without cluttering the channel
    if message.channel.name == "intro":
        try:
            # Use first 50 chars of intro as thread name
            preview = message.content[:50].strip()
            if len(message.content) > 50:
                preview += "..."
            thread_name = f"👋 {message.author.display_name}'s intro"
            await message.create_thread(
                name=thread_name,
                auto_archive_duration=1440,  # archive after 24h of inactivity
            )
        except Exception:
            pass

    # Sticky intro message
    if message.channel.name == "intro" and sticky_message_id:
        try:
            sticky_msg = await message.channel.fetch_message(sticky_message_id)
            await sticky_msg.delete()
            embed = discord.Embed(
                title="👋 Welcome to Quetta Tea Corner!",
                description=(
                    "Before you can access the server, please introduce yourself here!\n\n"
                    "**Tell us about:**\n• Name/nickname:\n• Age:\n• Gender:\n"
                    "• Country/city:\n• Interests/hobbies:\n\n"
                    "Once a moderator reviews your intro, you'll get the Verified role "
                    "and full access to the server! ☕"
                ),
                color=discord.Color.from_rgb(139, 69, 19),
            )
            embed.set_footer(
                text="Be genuine and friendly! We're excited to meet you.")
            new_sticky = await message.channel.send(embed=embed)
            sticky_message_id = new_sticky.id
        except:
            pass

    # Check trivia answers
    await on_message_trivia_answer(message)

    # Check riddle answers
    await on_message_riddle_answer(message)

    await bot.process_commands(message)


# ==================== TOLLPLAZA - JOIN/LEAVE LOGS ====================
@bot.event
async def on_member_join(member: discord.Member):
    channel = discord.utils.get(member.guild.text_channels, name="tollplaza")
    if not channel:
        return

    # Try to find who invited this member via audit log
    inviter = "Unknown"
    try:
        async for entry in member.guild.audit_logs(
            limit=10, action=discord.AuditLogAction.invite_create
        ):
            pass  # just warm up the cache

        # Compare invite uses before and after
        invites_after = await member.guild.invites()
        cached = getattr(bot, "_invite_cache", {}).get(member.guild.id, [])
        for invite in invites_after:
            for cached_invite in cached:
                if invite.code == cached_invite.code and invite.uses > cached_invite.uses:
                    inviter = invite.inviter.mention if invite.inviter else "Unknown"
                    break
    except Exception:
        pass

    # Update invite cache
    try:
        bot._invite_cache[member.guild.id] = await member.guild.invites()
    except Exception:
        pass

    created_at = discord.utils.format_dt(member.created_at, style="R")
    member_count = member.guild.member_count

    embed = discord.Embed(
        title="User joined",
        color=discord.Color.green(),
    )
    embed.description = (
        f"**User:** {member.mention} ( @{member.name} )\n"
        f"**Invited by:** {inviter}\n"
        f"**Created:** {created_at}\n"
        f"**Members:** {member_count}"
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.timestamp = discord.utils.utcnow()

    await channel.send(embed=embed)


@bot.event
async def on_member_remove(member: discord.Member):
    channel = discord.utils.get(member.guild.text_channels, name="tollplaza")
    if not channel:
        return

    joined = discord.utils.format_dt(member.joined_at, style="R") if member.joined_at else "Unknown"
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    member_count = member.guild.member_count

    embed = discord.Embed(
        title="User left",
        color=discord.Color.red(),
    )
    embed.description = (
        f"**User:** {member.mention} ( @{member.name} )\n"
        f"**Joined:** {joined}\n"
        f"**Roles:** {' '.join(roles) if roles else 'None'}\n"
        f"**Members:** {member_count}"
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.timestamp = discord.utils.utcnow()

    await channel.send(embed=embed)


@bot.event
async def on_ready_invite_cache():
    """Cache invites on startup so we can track who invited whom."""
    bot._invite_cache = {}
    for guild in bot.guilds:
        try:
            bot._invite_cache[guild.id] = await guild.invites()
        except Exception:
            pass


# ==================== BOT READY ====================
@bot.event
async def on_ready():
    global sticky_message_id

    print(f"✅ {bot.user} is online!")
    print("🤖 FULLY AUTOMATED BOT - Everything runs automatically!")
    print("📡 All features use unlimited APIs")

    guild = bot.guilds[0]

    # Register persistent views
    bot.add_view(ColorRoleView())
    bot.add_view(ColorRoleView2())
    bot.add_view(ColorRoleView3())
    bot.add_view(NotificationView())
    bot.add_view(HobbyRoleView())
    print("✅ Registered all color role buttons (37 colors)")
    print("✅ Registered notification buttons")

    # Setup sticky intro message
    intro_channel = discord.utils.get(guild.text_channels, name="intro")
    if intro_channel:
        async for message in intro_channel.history(limit=50):
            if message.author == bot.user and message.embeds:
                if "Welcome to Quetta Tea Corner" in message.embeds[0].title:
                    sticky_message_id = message.id
                    print(f"✅ Found sticky intro message")
                    break
        if not sticky_message_id:
            embed = discord.Embed(
                title="👋 Welcome to Quetta Tea Corner!",
                description=(
                    "Before you can access the server, please introduce yourself here!\n\n"
                    "**Tell us about:**\n• Name/nickname:\n• Age:\n• Gender:\n"
                    "• Country/city:\n• Interests/hobbies:\n\n"
                    "Once a moderator reviews your intro, you'll get the Verified role "
                    "and full access to the server! ☕"
                ),
                color=discord.Color.from_rgb(139, 69, 19),
            )
            embed.set_footer(
                text="Be genuine and friendly! We're excited to meet you.")
            sticky_msg = await intro_channel.send(embed=embed)
            sticky_message_id = sticky_msg.id
            print(f"✅ Created sticky intro message")

    # Sync slash commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
        # Also sync to guild for instant update
        guild = discord.Object(id=bot.guilds[0].id)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"✅ Guild sync complete")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

    # Cache invites for join tracking
    bot._invite_cache = {}
    for g in bot.guilds:
        try:
            bot._invite_cache[g.id] = await g.invites()
            print(f"✅ Cached invites for {g.name}")
        except Exception:
            pass


@bot.event
async def on_invite_create(invite: discord.Invite):
    """Keep invite cache up to date when new invites are created."""
    if invite.guild:
        try:
            bot._invite_cache[invite.guild.id] = await invite.guild.invites()
        except Exception:
            pass


# ==================== RUN BOT ====================
bot.run(os.getenv("DISCORD_TOKEN"))
