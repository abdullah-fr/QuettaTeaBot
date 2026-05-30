import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import View, Button
import random
from datetime import datetime, timezone
import asyncio

try:
    from config import settings
    from data_store import JsonDataStore
    from logging_config import configure_logging, get_logger
except ImportError:
    from .config import settings
    from .data_store import JsonDataStore
    from .logging_config import configure_logging, get_logger

# Import our modules
from question_bank import (
    COMPLIMENTS,
    PETS,
    QOTD_QUESTIONS,
    ROASTS,
    URDU_POETRY,
    WYR_QUESTIONS,
)
from api_helpers import (
    fetch_trivia_question,
    fetch_riddle,
    fetch_qotd,
    fetch_wyr,
    fetch_compliment,
    fetch_roast,
    fetch_ai_summary,
    fetch_ai_chat_reply,
    fetch_ai_mention_reply,
    fetch_ai_persona_reply,
    fetch_ai_dead_chat_starter,
)


# Configure structured logging
configure_logging()
logger = get_logger(__name__)

# Bot setup with intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
logger.info("Bot initialized", extra={"command_prefix": "!"})

# Store sticky message ID
sticky_message_id = None

# Data storage (async-safe; serializes writes, atomic on-disk swap)
data_store = JsonDataStore(settings.bot_data_file)
bot_data = data_store.load_sync()

# User profile storage — separate file so profile writes don't block bot_data
_user_profiles_store = JsonDataStore(
    settings.bot_data_file.parent / "user_profiles.json",
    default={},
)
_user_profiles: dict = {}

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
    "Fire": discord.Color.from_rgb(255, 69, 0),
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
        current_roles = [r for r in interaction.user.roles if r.name in COLOR_ROLES]
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

    await data_store.save(bot_data)

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
            trivia_data["answers"][str(message.author.id)] = message.content.strip()


@bot.tree.command(name="triviascores", description="Show trivia leaderboard")
async def triviascores(interaction: discord.Interaction):
    scores = bot_data["trivia_scores"]
    if not scores:
        await interaction.response.send_message("No trivia scores yet!")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    embed = discord.Embed(title="🏆 Trivia Leaderboard", color=discord.Color.gold())

    for i, (user_id, score) in enumerate(sorted_scores, 1):
        user = await bot.fetch_user(int(user_id))
        embed.add_field(name=f"{i}. {user.name}", value=f"{score} points", inline=False)

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
    embed.set_footer(text="You have 5 minutes to guess! First correct answer wins.")

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()

    active_riddles[msg.id] = {
        "riddle": riddle,
        "channel": interaction.channel,
        "solved": False,
    }
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
    online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
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
        await data_store.save(bot_data)
        print(f"✅ {member.name} joined VC in {member.guild.name} at {datetime.now()}")

    elif before.channel is not None and after.channel is None:
        if "join_time" in bot_data["vc_time"][server_key]:
            join_time = datetime.fromisoformat(
                bot_data["vc_time"][server_key]["join_time"]
            )
            duration = (datetime.now() - join_time).total_seconds() / 60

            bot_data["vc_time"][server_key]["total_minutes"] += duration
            del bot_data["vc_time"][server_key]["join_time"]
            await data_store.save(bot_data)
            print(
                f"✅ {member.name} left VC in {member.guild.name}. Session: {duration:.1f} min, Total: {bot_data['vc_time'][server_key]['total_minutes']:.1f} min"
            )


@bot.tree.command(
    name="vctime", description="Check your voice chat time in this server"
)
async def vctime(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = str(interaction.user.id)
    guild_id = str(interaction.guild.id)
    server_key = f"{user_id}_{guild_id}"

    if server_key not in bot_data["vc_time"]:
        bot_data["vc_time"][server_key] = {"total_minutes": 0}
        await data_store.save(bot_data)

    total_minutes = bot_data["vc_time"][server_key].get("total_minutes", 0)

    if "join_time" in bot_data["vc_time"][server_key]:
        join_time = datetime.fromisoformat(bot_data["vc_time"][server_key]["join_time"])
        current_session = (datetime.now() - join_time).total_seconds() / 60
        total_minutes += current_session

    if total_minutes > 0:
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        await interaction.followup.send(
            f"🎤 You've spent **{hours}h {minutes}m** in voice channels in **{interaction.guild.name}**!"
        )
    else:
        await interaction.followup.send(
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


@bot.tree.command(
    name="setuphobbies", description="Setup hobby reaction roles (Admin only)"
)
@app_commands.checks.has_permissions(administrator=True)
async def setuphobbies(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎯 Choose Your Hobbies!",
        description="Click the buttons below to get hobby roles",
        color=discord.Color.green(),
    )
    await interaction.response.send_message(embed=embed, view=HobbyRoleView())


# ==================== CITY ROLES ====================
CITY_ROLES = {
    "🔴 Karachite":           "Karachite",
    "🟠 Lahori":              "Lahori",
    "🟡 Faisalabadi":         "Faisalabadi",
    "🟢 Peshawari":           "Peshawari",
    "🔵 Multani":             "Multani",
    "🟣 Islamabadi/Pindi":    "Islamabadi/Pindi",
    "⚫ Quettaite":           "Quettaite",
    "🟤 Gujranwala":          "Gujranwala",
    "🔶 Hyderabadi":          "Hyderabadi",
    "🔷 Sialkoti":            "Sialkoti",
    "🟥 Bahawalpuri":         "Bahawalpuri",
    "🟦 Sukkuri":             "Sukkuri",
    "🟩 Abbottabadi":         "Abbottabadi",
    "🔸 Gujrati":             "Gujrati",
    "🔹 Jhelumi":             "Jhelumi",
    "🏳️ Elsewhere 🇵🇰":      "Elsewhere",
    "🌍 International":       "International",
}


class CityRoleButton(Button):
    def __init__(self, label: str, role_name: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"city_role_{role_name}",
        )
        self.role_name = role_name

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if not role:
            await interaction.followup.send(
                f"⚠️ Role '{self.role_name}' not found!", ephemeral=True
            )
            return

        # Remove any other city roles the user has
        city_role_names = list(CITY_ROLES.values())
        roles_to_remove = [
            r for r in interaction.user.roles
            if r.name in city_role_names and r.name != self.role_name
        ]
        if roles_to_remove:
            await interaction.user.remove_roles(*roles_to_remove)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.followup.send(
                f"Removed **{self.role_name}** role.", ephemeral=True
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.followup.send(
                f"You're now tagged as **{self.role_name}** ✅", ephemeral=True
            )


class CityRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for label, role_name in CITY_ROLES.items():
            self.add_item(CityRoleButton(label=label, role_name=role_name))


# ==================== PET SYSTEM ====================
@bot.tree.command(name="adopt", description="Adopt a virtual pet")
async def adopt(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id in bot_data["pet_system"]:
        await interaction.response.send_message("You already have a pet!")
        return

    pet = random.choice(PETS)
    bot_data["pet_system"][user_id] = {"pet": pet, "hunger": 100, "happiness": 100}
    await data_store.save(bot_data)

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

    await interaction.response.send_message(
        f"⏰ Pomodoro timer started for {minutes} minutes!"
    )
    await asyncio.sleep(minutes * 60)
    await interaction.channel.send(
        f"{interaction.user.mention} ⏰ Time's up! Take a break! 🎉"
    )


# ==================== TLDR COMMAND ====================
@bot.tree.command(name="tldr", description="Summarize previous messages in the channel")
@app_commands.describe(count="Number of messages to summarize (50, 100, 200, or 500)")
@app_commands.choices(
    count=[
        app_commands.Choice(name="50 messages", value=50),
        app_commands.Choice(name="100 messages", value=100),
        app_commands.Choice(name="200 messages", value=200),
        app_commands.Choice(name="500 messages", value=500),
    ]
)
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
                color=discord.Color.blue(),
            )
            embed.set_footer(
                text=f"AI-generated summary of {len(messages)} messages | Powered by Gemini"
            )
            await interaction.followup.send(embed=embed)
        else:
            # Fallback to basic summary
            summary = "**Summary of the Conversation 💬**\n\n"
            summary += f"**Total messages:** {len(messages)}\n\n"

            # Show participants
            authors = list(
                set(
                    [
                        msg.split("]")[1].split(":")[0].strip()
                        for msg in messages
                        if "]" in msg and ":" in msg
                    ]
                )
            )
            summary += f"**Participants:** {', '.join(authors[:10])}\n\n"

            # Show sample messages
            summary += "**Sample messages:**\n"
            sample_count = min(10, len(messages))
            step = max(1, len(messages) // sample_count)
            for i in range(0, len(messages), step):
                if i < len(messages):
                    msg_preview = messages[i][:200]
                    summary += f"{msg_preview}\n"

            summary += "\n⚠️ **Note:** Set GEMINI_API_KEY environment variable for AI-powered summaries!\n"
            summary += "Get free API key from: https://aistudio.google.com/app/apikey"

            if len(summary) > 4000:
                summary = summary[:3997] + "..."

            embed = discord.Embed(
                title="📝 Channel Summary",
                description=summary,
                color=discord.Color.orange(),
            )
            embed.set_footer(text=f"Analyzed {len(messages)} messages")
            await interaction.followup.send(embed=embed)

    except Exception as e:
        logger.exception("tldr summary failed")
        await interaction.followup.send(f"❌ Error creating summary: {str(e)}")


# ==================== ADMIN COMMANDS ====================
@bot.tree.command(
    name="purge", description="Bulk delete messages (requires Manage Messages)"
)
@app_commands.describe(
    count="Input number of messages to search for (max 100)",
    message_link="Paste a message link — deletes all messages after it",
    filter="Filter by message type: all, text, image, voice, links",
)
@app_commands.choices(
    filter=[
        app_commands.Choice(name="All messages", value="all"),
        app_commands.Choice(name="Text only", value="text"),
        app_commands.Choice(name="Images only", value="image"),
        app_commands.Choice(name="Voice messages only", value="voice"),
        app_commands.Choice(name="Links only", value="links"),
    ]
)
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
        await interaction.followup.send(
            "❌ Count must be between 1 and 100.", ephemeral=True
        )
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
                a.content_type and "ogg" in a.content_type for a in msg.attachments
            )
        if filter == "links":
            return bool(msg.content) and (
                "http://" in msg.content or "https://" in msg.content
            )
        return True

    # Purge messages
    try:
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
                batch = to_delete[i : i + 100]
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
            "all": "messages",
            "text": "text messages",
            "image": "images",
            "voice": "voice messages",
            "links": "messages with links",
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
        await interaction.followup.send(
            "❌ I don't have permission to delete messages here.", ephemeral=True
        )
    except Exception as e:
        logger.exception("purge command failed")
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)


@purge.error
async def purge_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You need **Manage Messages** permission to use this command.",
            ephemeral=True,
        )


@bot.tree.command(
    name="checkroles",
    description="Debug command to check all server roles (Admin only)",
)
@app_commands.checks.has_permissions(administrator=True)
async def checkroles(interaction: discord.Interaction):
    roles_list = [f"• {role.name} (ID: {role.id})" for role in interaction.guild.roles]
    roles_text = "\n".join(roles_list)

    embed = discord.Embed(
        title="🔍 Server Roles Debug",
        description=f"**All roles in this server:**\n{roles_text}",
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="welcome",
    description="Send welcome message for newly verified member (Mod only)",
)
@app_commands.describe(member="The member to welcome")
@app_commands.checks.has_permissions(manage_roles=True)
async def welcome(interaction: discord.Interaction, member: discord.Member):
    verified_role = discord.utils.get(interaction.guild.roles, name="✔️Verified")

    if not verified_role:
        await interaction.response.send_message("❌ Verified role not found!")
        return

    if verified_role not in member.roles:
        await interaction.response.send_message(
            f"❌ {member.mention} doesn't have the Verified role yet!"
        )
        return

    general_channel = discord.utils.get(interaction.guild.text_channels, name="general")
    self_roles_channel = discord.utils.get(
        interaction.guild.text_channels, name="self-roles"
    )

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
        await interaction.response.send_message(
            f"✅ Welcome message sent for {member.mention}!"
        )
        print(f"✅ Manual welcome message sent for {member.name}")
    else:
        await interaction.response.send_message("❌ General channel not found!")


@bot.tree.command(
    name="checkintents",
    description="Check if bot has required intents enabled (Admin only)",
)
@app_commands.checks.has_permissions(administrator=True)
async def checkintents(interaction: discord.Interaction):
    intents_status = []
    intents_status.append(
        f"{'✅' if bot.intents.members else '❌'} Members Intent: {bot.intents.members}"
    )
    intents_status.append(
        f"{'✅' if bot.intents.guilds else '❌'} Guilds Intent: {bot.intents.guilds}"
    )
    intents_status.append(
        f"{'✅' if bot.intents.message_content else '❌'} Message Content: {bot.intents.message_content}"
    )

    embed = discord.Embed(
        title="🔍 Bot Intents Status",
        description="\n".join(intents_status),
        color=discord.Color.green() if bot.intents.members else discord.Color.red(),
    )

    if not bot.intents.members:
        embed.add_field(
            name="⚠️ Members Intent Disabled",
            value="You need to enable 'Server Members Intent' in Discord Developer Portal",
            inline=False,
        )
    else:
        embed.add_field(
            name="✅ All Good",
            value="The on_member_update event should work. If it's not triggering, try restarting the bot.",
            inline=False,
        )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="checkaudit", description="Check recent audit log entries (Admin only)"
)
@app_commands.describe(limit="Number of entries to show (default 10)")
@app_commands.checks.has_permissions(administrator=True)
async def checkaudit(interaction: discord.Interaction, limit: int = 10):
    await interaction.response.defer()

    try:
        audit_logs = []
        async for entry in interaction.guild.audit_logs(limit=limit):
            action_type = str(entry.action).replace("AuditLogAction.", "")
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
                    color=discord.Color.blue(),
                )
                if i == 0:
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.channel.send(embed=embed)
        else:
            await interaction.followup.send("No audit log entries found.")
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ Bot doesn't have permission to view audit logs!"
        )
    except Exception as e:
        logger.exception("checkaudit command failed")
        await interaction.followup.send(f"❌ Error: {str(e)}")


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
        print("⚠️ No '✔️Verified' role found in server roles")

    if verified_role and verified_role in added_roles:
        print(f"✅ Verified role detected for {after.name}")

        general_channel = discord.utils.get(after.guild.text_channels, name="general")
        self_roles_channel = discord.utils.get(
            after.guild.text_channels, name="self-roles"
        )

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
            print("❌ General channel not found")
            print(f"Available channels: {[c.name for c in after.guild.text_channels]}")


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
        except Exception:
            logger.exception("audit log fetch failed")

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Deleted by:** {deleted_by}\n**Content:** {message.content[:1024] if message.content else 'No content'}",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        await logs_channel.send(embed=embed)


# ==================== USER PROFILE SYSTEM ====================
import re as _re
from collections import deque

_PROFILE_SAVE_INTERVAL = 70  # flush to disk every N messages per user
_PROFILE_MIN_MESSAGES = 50  # minimum before persona reply activates
_PROFILE_MAX_WORD_FREQ = 200  # cap word_freq dict size
_PROFILE_MAX_NGRAM_FREQ = 100  # cap ngram_freq dict size
_PROFILE_MAX_QUOTES = 10  # stored notable quotes per user
_NGRAM_SIGNATURE_THRESHOLD = 3  # occurrences before phrase becomes signature
_profile_dirty_counts: dict[str, int] = {}  # user_id -> messages since last save

_STOP_WORDS = {
    "the",
    "a",
    "an",
    "is",
    "it",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "and",
    "or",
    "but",
    "with",
    "that",
    "this",
    "was",
    "are",
    "be",
    "have",
    "had",
    "do",
    "did",
    "not",
    "no",
    "yes",
    "i",
    "you",
    "he",
    "she",
    "we",
    "they",
    "my",
    "your",
    "his",
    "her",
    "our",
    "me",
    "him",
    "us",
    "them",
    "so",
    "up",
    "just",
    "like",
    "get",
    "got",
    "its",
    "been",
    "will",
    "can",
    "would",
    "im",
    # roman urdu common words (grammatical, not meaningful)
    "hai",
    "hain",
    "ho",
    "tha",
    "thi",
    "ka",
    "ki",
    "ke",
    "se",
    "ko",
    "ne",
    "bhi",
    "toh",
    "na",
    "kya",
    "koi",
    "aur",
    "ya",
    "ek",
    "sab",
    "mein",
    "pe",
    "par",
    "ab",
    "kab",
    "jab",
    "tab",
    "phir",
    "woh",
    "ye",
    "jo",
    "bas",
    "hi",
    "mat",
    "nahi",
    "nhi",
    "okay",
    "ok",
    "lol",
    "haha",
    "hahaha",
    "lmao",
    "bhai",
    "yaar",
}

_URDU_SIGNAL_WORDS = {
    "bhai",
    "yaar",
    "nahi",
    "nhi",
    "tha",
    "thi",
    "mein",
    "toh",
    "phir",
    "kal",
    "aaj",
    "raat",
    "subah",
    "banda",
    "mast",
    "theek",
    "acha",
    "sahi",
    "pagal",
    "mera",
    "tera",
    "apna",
    "humara",
    "tumhara",
    "baat",
    "samajh",
    "dekh",
    "sun",
    "bol",
    "yahan",
    "wahan",
    "pehle",
    "seedha",
    "bilkul",
    "zaroor",
    "shayad",
    "lagta",
    "lagti",
    "wala",
}


def _tokenize_for_profile(content: str) -> list[str]:
    content = _re.sub(r"<a?:[A-Za-z0-9_~]+:\d+>", "", content)
    content = _re.sub(r"https?://\S+", "", content)
    content = _re.sub(r"<@!?\d+>", "", content)
    content = _re.sub(r"[^\w\s]", " ", content.lower())
    return [w for w in content.split() if len(w) >= 3]


def _extract_ngrams(tokens: list[str], n: int) -> list[str]:
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _build_user_context(profile: dict) -> str:
    parts = [f"name: {profile['display_name']}"]

    phrases = profile.get("signature_phrases", [])
    if phrases:
        parts.append(f"their phrases: {', '.join(repr(p) for p in phrases[:5])}")

    topics = [
        w
        for w, _ in sorted(
            profile.get("word_freq", {}).items(), key=lambda x: x[1], reverse=True
        )
        if w not in _STOP_WORDS
    ][:4]
    if topics:
        parts.append(f"topics: {', '.join(topics)}")

    avg = profile.get("avg_length", 0)
    style = (
        "short punchy" if avg < 6 else ("conversational" if avg < 14 else "detailed")
    )
    vibe = "chaotic/funny" if profile.get("funny_ratio", 0) > 0.3 else "chill"
    urdu = (
        "heavy roman urdu" if profile.get("urdu_ratio", 0) > 0.5 else "english-leaning"
    )
    parts.append(f"style: {style}, {vibe}, {urdu}")

    quotes = profile.get("recent_quotes", [])
    if quotes:
        sampled = quotes[-2:]
        parts.append(f"recently said: {' / '.join(repr(q) for q in sampled)}")

    return " | ".join(parts)


async def _update_user_profile(message: discord.Message) -> None:
    """Passively build per-user chat profile from every message. Saves every 70 messages."""
    user_id = str(message.author.id)
    now_hour = str(datetime.now().hour)
    content = message.content

    profile = _user_profiles.setdefault(
        user_id,
        {
            "display_name": message.author.display_name,
            "message_count": 0,
            "word_freq": {},
            "ngram_freq": {},
            "signature_phrases": [],
            "recent_quotes": [],
            "avg_length": 0.0,
            "urdu_ratio": 0.0,
            "funny_ratio": 0.0,
            "active_hours": {},
            "_urdu_count": 0,
            "_funny_count": 0,
        },
    )

    profile["display_name"] = message.author.display_name
    profile["message_count"] += 1
    n = profile["message_count"]

    profile["active_hours"][now_hour] = profile["active_hours"].get(now_hour, 0) + 1

    tokens = _tokenize_for_profile(content)
    if not tokens:
        return

    # Rolling average message length
    profile["avg_length"] = (profile["avg_length"] * (n - 1) + len(tokens)) / n

    # Word frequency
    wf = profile["word_freq"]
    for w in tokens:
        if w not in _STOP_WORDS:
            wf[w] = wf.get(w, 0) + 1
    if len(wf) > _PROFILE_MAX_WORD_FREQ:
        profile["word_freq"] = dict(
            sorted(wf.items(), key=lambda x: x[1], reverse=True)[
                :_PROFILE_MAX_WORD_FREQ
            ]
        )

    # Ngram frequency (2-grams + 3-grams)
    nf = profile["ngram_freq"]
    for gram in _extract_ngrams(tokens, 2) + _extract_ngrams(tokens, 3):
        nf[gram] = nf.get(gram, 0) + 1
    if len(nf) > _PROFILE_MAX_NGRAM_FREQ:
        profile["ngram_freq"] = dict(
            sorted(nf.items(), key=lambda x: x[1], reverse=True)[
                :_PROFILE_MAX_NGRAM_FREQ
            ]
        )

    # Urdu ratio
    content_lower = content.lower()
    if any(w in content_lower for w in _URDU_SIGNAL_WORDS):
        profile["_urdu_count"] += 1
    profile["urdu_ratio"] = profile["_urdu_count"] / n

    # Funny ratio
    funny_signals = {"lol", "lmao", "haha", "😂", "💀", "bruh", "oof", "omg", "😭"}
    if any(k in content_lower for k in funny_signals):
        profile["_funny_count"] += 1
    profile["funny_ratio"] = profile["_funny_count"] / n

    # Notable quotes (long enough, not low-signal)
    cleaned = _sanitize_ai_history_content(content)
    if len(cleaned) > 20 and not _is_low_signal_ai_message(content):
        quotes = profile["recent_quotes"]
        quotes.append(cleaned[:200])
        profile["recent_quotes"] = quotes[-_PROFILE_MAX_QUOTES:]

    # Batch save every 70 messages
    dirty = _profile_dirty_counts.get(user_id, 0) + 1
    _profile_dirty_counts[user_id] = dirty
    if dirty >= _PROFILE_SAVE_INTERVAL:
        profile["signature_phrases"] = [
            phrase
            for phrase, count in sorted(
                profile["ngram_freq"].items(), key=lambda x: x[1], reverse=True
            )
            if count >= _NGRAM_SIGNATURE_THRESHOLD
        ][:10]
        _profile_dirty_counts[user_id] = 0
        await _user_profiles_store.save(_user_profiles)


# ==================== INTELLIGENT AUTO-REPLY SYSTEM ====================

_channel_history: dict[int, list[str]] = {}
_channel_last_seen: dict[int, float] = {}
_last_replied_users: dict[int, int] = {}
_recent_bot_replies: dict[int, deque[str]] = {}
_RECENT_REPLIES_PER_CHANNEL = 12
AI_CHAT_CHANNEL_TYPES = (discord.TextChannel, discord.VoiceChannel, discord.Thread)

# Proactive dead-chat state
_channel_objects: dict[int, discord.TextChannel] = {}
_proactive_last_fired: dict[int, float] = {}
_PROACTIVE_QUIET_MIN = 1800  # channel must be quiet for at least 30 min
_PROACTIVE_QUIET_MAX = 7200  # but not more than 2 hrs (then it's just dead)
_PROACTIVE_ALLOWED_CHANNELS = {"general", "General", "boises", "bot-tunning"}
_PROACTIVE_COOLDOWN = 10800  # 3 hrs minimum between proactive fires per channel
LOW_SIGNAL_AI_MESSAGES = {
    "bot",
    "check",
    "test",
    "testing",
    "1",
    "2",
    "3",
    "123",
    "meow",
    "ah",
    "ahh",
    "ahhh",
    "ahhhh",
    "aaaa",
    "aaaaa",
    "ew",
    "eww",
    "ewww",
    "ewwww",
    "noew",
    "wtf",
    "ok",
    "okay",
}


def _resolve_mentions(content: str, message: discord.Message) -> str:
    """Replace <@userid> Discord mention tokens with display names."""
    import re

    def _replace(match):
        uid = int(match.group(1))
        member = message.guild.get_member(uid)
        if member:
            return f"@{member.display_name}"
        return "@someone"

    return re.sub(r"<@!?(\d+)>", _replace, content)


def _sanitize_ai_history_content(content: str) -> str:
    import re

    content = re.sub(r"<a?:[A-Za-z0-9_~]+:\d+>", "[emoji]", content)
    content = re.sub(r":[A-Za-z0-9_~]+:", "[emoji]", content)
    return re.sub(r"\s+", " ", content).strip()


def _is_low_signal_ai_message(content: str) -> bool:
    import re

    text = _sanitize_ai_history_content(content).lower()
    text = re.sub(r"<@!?\d+>|@\S+", "", text)
    text = re.sub(r"https?://\S+", "", text).strip()
    text_without_emoji = text.replace("[emoji]", "").strip()
    compact = re.sub(r"[^a-z0-9]+", "", text_without_emoji)

    if not compact:
        return True
    if compact in LOW_SIGNAL_AI_MESSAGES:
        return True
    if compact.isdigit():
        return True
    if len(compact) <= 2:
        return True
    if len(compact) <= 8 and len(set(compact)) <= 2:
        return True
    if re.fullmatch(r"(.)\1{3,}", compact):
        return True
    return False


def _has_custom_emoji_token(text: str) -> bool:
    import re

    return bool(re.search(r"<a?:[A-Za-z0-9_~]+:\d+>", text))


def _pick_ai_custom_emoji(
    content_lower: str,
    reply: str,
    emoji_tokens_by_name: dict[str, str],
) -> str | None:
    combined = f"{content_lower} {reply.lower()}"
    candidates: list[str] = []

    if any(k in combined for k in ["lol", "lmao", "haha", "😂", "🤣", "funny"]):
        candidates += ["tikkilaughing", "point_lol", "chas_agai", "dead", "bruh"]
    if any(k in combined for k in ["kya", "what", "wait", "huh", "hein", "confused"]):
        candidates += ["kya", "huhhhhhh", "heinnnn", "hmmm", "interesting"]
    if any(k in combined for k in ["sad", "cry", "😭", "dukh"]):
        candidates += ["pepe_sad", "dukhi_meso", "cryagya"]
    if any(k in combined for k in ["sus", "cooking", "cook", "plot"]):
        candidates += ["sus", "something_cooking", "whats_cooking_man"]
    if any(k in combined for k in ["nice", "yay", "vibe", "real", "valid"]):
        candidates += ["yayyyyy", "cybvibe", "vibes_pakruga", "cool_smirk"]

    candidates += ["bruh", "kya", "hmmm", "dead", "chas_agai", "cool_smirk"]
    available = [
        emoji_tokens_by_name[name]
        for name in candidates
        if name in emoji_tokens_by_name
    ]
    return random.choice(available) if available else None


def _normalize_for_similarity(text: str) -> str:
    import re

    text = re.sub(r"<a?:[A-Za-z0-9_~]+:\d+>", "", text)
    text = re.sub(r"[\W_]+", " ", text, flags=re.UNICODE)
    return " ".join(text.lower().split())


def _is_too_similar_to_recent(candidate: str, recent: list[str]) -> bool:
    """Reject candidate replies that are duplicates or near-duplicates of
    something the bot already said recently in this channel."""
    norm_candidate = _normalize_for_similarity(candidate)
    if not norm_candidate:
        return True
    for prior in recent:
        norm_prior = _normalize_for_similarity(prior)
        if not norm_prior:
            continue
        if norm_candidate == norm_prior:
            return True
        if (
            len(norm_candidate) >= 6
            and len(norm_prior) >= 6
            and (norm_candidate in norm_prior or norm_prior in norm_candidate)
        ):
            return True
    return False


def _typing_delay(reply: str) -> float:
    words = len(reply.split())
    if words <= 3:
        return random.uniform(0.3, 0.8)
    if words <= 7:
        return random.uniform(0.6, 1.2)
    return random.uniform(1.0, 2.0)


async def maybe_send_ai_chat_reply(message):
    import time

    if message.author.bot or not message.guild:
        return

    now = time.time()
    channel_id = message.channel.id
    content_lower = message.content.lower() if message.content else ""
    cleaned_content = _sanitize_ai_history_content(_resolve_mentions((message.content or "")[:200], message))

    # Track recent messages for context
    if now - _channel_last_seen.get(channel_id, 0) > 900:
        _channel_history[channel_id] = []
    _channel_last_seen[channel_id] = now
    if isinstance(message.channel, discord.TextChannel):
        _channel_objects[channel_id] = message.channel

    # Capture history *before* appending the trigger so we can pass it as
    # context separately from the message we're reacting to.
    prior_history = list(_channel_history.get(channel_id, []))

    # --- Bot Fathers role mention: bot reacts defensively ---
    if any(role.name == "Bot's Fathers" for role in message.role_mentions):
        _defensive_replies = [
            "aye aye aye mere fathers ko tag mat karo 😭",
            "bhai please unhe disturb mat karo yaar",
            "kya kiya maine, please unhe mat batao",
            "nahi nahi unhe mat bulao main theek ho jaunga",
            "yaar mere fathers ko involve mat karo please 😭",
            "bhai ruk ruk unhe tag karne ki zarurat nahi",
            "please unhe mat batao main kuch nahi kiya",
            "arre nahi yaar fathers ko kyun tag kiya 😭",
        ]
        reply = random.choice(_defensive_replies)
        try:
            async with message.channel.typing():
                await asyncio.sleep(_typing_delay(reply))
            await message.reply(reply, mention_author=False)
        except Exception:
            logger.exception("Bot Fathers role mention reply failed")
        return

    # --- Direct mention: always reply, bypass probability ---
    if bot.user in message.mentions:
        if channel_id not in _channel_history:
            _channel_history[channel_id] = []
        _channel_history[channel_id].append(
            f"{message.author.display_name}: {cleaned_content}"
        )
        _channel_history[channel_id] = _channel_history[channel_id][-15:]
        emoji_tokens_by_name = {
            e.name.lower(): f"<:{e.name}:{e.id}>"
            for e in message.guild.emojis
            if not e.animated
        }
        emoji_names = [token for _, token in sorted(emoji_tokens_by_name.items())][:75]
        mention_text = _resolve_mentions(cleaned_content.replace(f"<@{bot.user.id}>", ""), message).strip()
        # Inject bot's own recent replies so the model sees the full conversation
        bot_recent = [
            f"{bot.user.name}: {r}"
            for r in list(_recent_bot_replies.get(channel_id, ()))[-5:]
        ]
        full_mention_history = prior_history + bot_recent

        reply = await fetch_ai_mention_reply(
            mention_text or "(just pinged, no message)",
            message.author.display_name,
            emoji_names,
            full_mention_history,
            bot_name=bot.user.name,
        )
        if reply and len(reply) > 2:
            recent_replies_mention = list(_recent_bot_replies.get(channel_id, ()))
            if _is_too_similar_to_recent(reply, recent_replies_mention):
                return
            if not _has_custom_emoji_token(reply) and random.random() < 0.60:
                custom_emoji = _pick_ai_custom_emoji(
                    content_lower, reply, emoji_tokens_by_name
                )
                if custom_emoji:
                    reply = f"{reply.rstrip()} {custom_emoji}"
            try:
                async with message.channel.typing():
                    await asyncio.sleep(_typing_delay(reply))
                await message.reply(reply, mention_author=True)
                if channel_id not in _recent_bot_replies:
                    _recent_bot_replies[channel_id] = deque(
                        maxlen=_RECENT_REPLIES_PER_CHANNEL
                    )
                _recent_bot_replies[channel_id].append(reply)
                print(f"🤖 Mention reply in #{message.channel.name}: {reply[:60]}")
            except Exception:
                logger.exception("AI mention reply failed")
        return

    # Non-mention path: apply channel/content guards
    if (
        not isinstance(message.channel, AI_CHAT_CHANNEL_TYPES)
        or not message.content
        or len(message.content) <= 3
        or message.content.startswith("/")
    ):
        return

    if channel_id not in _channel_history:
        _channel_history[channel_id] = []
    _channel_history[channel_id].append(
        f"{message.author.display_name}: {cleaned_content}"
    )
    _channel_history[channel_id] = _channel_history[channel_id][-15:]

    if _is_low_signal_ai_message(message.content):
        return

    # Serious topic detection — skip only the AI reply, not command handling.
    serious_keywords = [
        "death",
        "hospital",
        "sad",
        "depressed",
        "funeral",
        "hurt",
        "crying",
        "suicide",
        "cancer",
        "died",
        "marna",
        "mar gaya",
        "rona",
        "dukh",
        "takleef",
        "sympathy",
        "gonna be fine",
        "one day u gonna be fine",
        "missing you",
        "cuddle",
        "bbg",
        # grief / loss
        "loss",
        "passed away",
        "wafat",
        "intiqal",
        "jannat",
        "jannah",
        "maghfirat",
        "sabr",
        "inna lillahi",
        "innalillahi",
        "may allah",
        "jazak allah",
        "jazakallah",
        "rahmat",
        "guzar gaye",
        "guzar gaya",
        "nahi rahe",
        "nahi rahi",
        "miss him",
        "miss her",
        "miss them",
        "parents",
        "ammi",
        "abbu",
        "walida",
        "walid",
        "condolence",
        "sorry for your loss",
        "eid ke baad",
    ]
    if any(k in content_lower for k in serious_keywords):
        return

    # Avoid replying to same person twice in a row per channel
    user_id = message.author.id
    if _last_replied_users.get(channel_id) == user_id:
        return

    # Activity detection — prefer active chats
    is_active_chat = len(prior_history) >= 3

    # Probability based on message vibe
    funny_keywords = [
        "lol",
        "lmao",
        "haha",
        "😂",
        "💀",
        "bhai",
        "yaar",
        "kya",
        "oof",
        "bruh",
        "wtf",
        "omg",
        "😭",
        "🤣",
        "exposed",
        "ratio",
        "nahh",
        "bro",
        "skill issue",
    ]
    is_funny = any(k in content_lower for k in funny_keywords)
    base_chance = 0.06 if is_funny else 0.02
    if is_active_chat:
        base_chance *= 1.5

    if not is_active_chat and not is_funny:
        return

    if random.random() >= base_chance:
        return

    emoji_tokens_by_name = {
        e.name.lower(): f"<:{e.name}:{e.id}>"
        for e in message.guild.emojis
        if not e.animated
    }
    emoji_names = [token for _, token in sorted(emoji_tokens_by_name.items())][:75]

    recent_replies = list(_recent_bot_replies.get(channel_id, ()))

    # Use persona reply if this user has a mature profile, fallback to generic
    profile = _user_profiles.get(str(user_id))
    has_persona = (
        profile is not None and profile.get("message_count", 0) >= _PROFILE_MIN_MESSAGES
    )

    if has_persona:
        user_context = _build_user_context(profile)
        reply = await fetch_ai_persona_reply(
            prior_history,
            emoji_names,
            cleaned_content,
            user_context,
            avoid_phrases=recent_replies,
        )
        if not reply or len(reply) <= 2:
            reply = await fetch_ai_chat_reply(
                prior_history,
                emoji_names,
                cleaned_content,
                avoid_phrases=recent_replies,
            )
    else:
        reply = await fetch_ai_chat_reply(
            prior_history,
            emoji_names,
            cleaned_content,
            avoid_phrases=recent_replies,
        )

    if not reply or len(reply) <= 2:
        return

    # Anti-repetition guard: drop near-duplicates of the bot's recent replies.
    if _is_too_similar_to_recent(reply, recent_replies):
        logger.info(
            "AI reply suppressed as repetitive",
            extra={"channel_id": channel_id, "reply": reply[:60]},
        )
        return

    # Random "think and say nothing" — feels human
    if random.random() <= 0.20:
        return

    if not _has_custom_emoji_token(reply) and random.random() < 0.70:
        custom_emoji = _pick_ai_custom_emoji(content_lower, reply, emoji_tokens_by_name)
        if custom_emoji:
            reply = f"{reply.rstrip()} {custom_emoji}"

    try:
        async with message.channel.typing():
            await asyncio.sleep(_typing_delay(reply))
        await message.reply(reply, mention_author=False)
        _last_replied_users[channel_id] = user_id
        if channel_id not in _recent_bot_replies:
            _recent_bot_replies[channel_id] = deque(maxlen=_RECENT_REPLIES_PER_CHANNEL)
        _recent_bot_replies[channel_id].append(reply)
        print(f"🤖 AI replied in #{message.channel.name}: {reply[:60]}")
    except Exception:
        logger.exception("AI chat reply failed")


@bot.event
async def on_message(message):
    global sticky_message_id

    # Passively build user profile on every non-bot guild message
    if not message.author.bot and message.guild and message.content:
        await _update_user_profile(message)

    # ==================== INTELLIGENT AI CHAT REPLIES ====================
    await maybe_send_ai_chat_reply(message)

    # Ignore DMs — all channel-specific logic below requires a guild channel
    if not message.guild or not isinstance(
        message.channel, (discord.TextChannel, discord.VoiceChannel, discord.Thread)
    ):
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
            embed.set_footer(text="Be genuine and friendly! We're excited to meet you.")
            new_sticky = await message.channel.send(embed=embed)
            sticky_message_id = new_sticky.id
        except Exception:
            pass

    # Check trivia answers
    await on_message_trivia_answer(message)

    # Check riddle answers
    await on_message_riddle_answer(message)

    await bot.process_commands(message)


# ==================== TOLLPLAZA - JOIN/LEAVE LOGS ====================
@bot.event
async def on_member_join(member: discord.Member):
    # Assign Unverified role on join
    unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
    if unverified_role:
        try:
            await member.add_roles(unverified_role)
        except Exception:
            print(f"⚠️ Failed to assign Unverified role to {member.name}")

    # Milestone celebration in #general
    milestones = {50, 100, 200, 500, 1000}
    if member.guild.member_count in milestones:
        general = discord.utils.get(member.guild.text_channels, name="general")
        if general:
            await general.send(
                embed=discord.Embed(
                    title="🎉 MILESTONE REACHED!",
                    description=f"We just hit **{member.guild.member_count} members**! 🎊",
                    color=discord.Color.gold(),
                )
            )

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
                if (
                    invite.code == cached_invite.code
                    and invite.uses > cached_invite.uses
                ):
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
    # Warn in #logs if a Verified member left
    verified_role = discord.utils.get(member.guild.roles, name="✔️Verified")
    if verified_role and verified_role in member.roles:
        logs_channel = discord.utils.get(member.guild.text_channels, name="logs")
        if logs_channel:
            warn_embed = discord.Embed(
                title="⚠️ Verified Member Left",
                description=f"{member.mention} ({member.name}) left the server",
                color=discord.Color.orange(),
            )
            warn_embed.add_field(name="User ID", value=member.id, inline=True)
            if member.joined_at:
                warn_embed.add_field(
                    name="Joined",
                    value=f"<t:{int(member.joined_at.timestamp())}:R>",
                    inline=True,
                )
            warn_embed.add_field(
                name="Roles",
                value=", ".join([r.name for r in member.roles if r.name != "@everyone"])
                or "None",
                inline=False,
            )
            await logs_channel.send(embed=warn_embed)

    channel = discord.utils.get(member.guild.text_channels, name="tollplaza")
    if not channel:
        return

    joined = (
        discord.utils.format_dt(member.joined_at, style="R")
        if member.joined_at
        else "Unknown"
    )
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



# ==================== BOT READY ====================
_bot_started_at: datetime | None = None


@tasks.loop(minutes=5)
async def heartbeat_log():
    """Periodic structured heartbeat so silent disconnects are detectable."""
    if _bot_started_at is None:
        return
    uptime = datetime.now(timezone.utc) - _bot_started_at
    logger.info(
        "heartbeat",
        extra={
            "uptime_seconds": int(uptime.total_seconds()),
            "guilds": len(bot.guilds),
            "latency_ms": round(bot.latency * 1000, 1),
            "user": str(bot.user) if bot.user else None,
        },
    )


@tasks.loop(minutes=7)
async def proactive_chat_check():
    """If a tracked channel was active recently but has gone quiet, drop a casual message."""
    import time

    now = time.time()
    candidates = [
        (cid, ch)
        for cid, ch in _channel_objects.items()
        if ch.name in _PROACTIVE_ALLOWED_CHANNELS
        and _PROACTIVE_QUIET_MIN
        <= now - _channel_last_seen.get(cid, 0)
        <= _PROACTIVE_QUIET_MAX
        and now - _proactive_last_fired.get(cid, 0) >= _PROACTIVE_COOLDOWN
    ]
    if not candidates:
        return

    channel_id, channel = random.choice(candidates)
    starter = await fetch_ai_dead_chat_starter()
    if not starter:
        return

    try:
        await channel.send(starter)
        _proactive_last_fired[channel_id] = now
        _channel_last_seen[channel_id] = now
        logger.info(
            "proactive chat starter sent",
            extra={"channel": channel.name, "starter": starter},
        )
    except Exception:
        logger.exception("proactive chat starter failed")


@bot.event
async def on_ready():
    global sticky_message_id, _bot_started_at

    if _bot_started_at is None:
        _bot_started_at = datetime.now(timezone.utc)
    if not heartbeat_log.is_running():
        heartbeat_log.start()
    if not proactive_chat_check.is_running():
        proactive_chat_check.start()

    # Load user profiles from disk
    loaded = await _user_profiles_store.load()
    _user_profiles.update(loaded)
    logger.info("user profiles loaded", extra={"count": len(_user_profiles)})

    logger.info(
        "bot online",
        extra={"user": str(bot.user), "guilds": len(bot.guilds)},
    )
    print(f"✅ {bot.user} is online!")
    print("🤖 FULLY AUTOMATED BOT - Everything runs automatically!")
    print("📡 All features use unlimited APIs")

    from api_helpers import _get_gemini_keys
    gemini_keys = _get_gemini_keys()
    print(f"🔑 Gemini API keys loaded: {len(gemini_keys)}")

    guild = bot.guilds[0]

    # Register persistent views
    bot.add_view(ColorRoleView())
    bot.add_view(ColorRoleView2())
    bot.add_view(ColorRoleView3())
    bot.add_view(NotificationView())
    bot.add_view(HobbyRoleView())
    bot.add_view(CityRoleView())
    print("✅ Registered all color role buttons (37 colors)")
    print("✅ Registered notification buttons")
    print("✅ Registered city role buttons")

    # Setup sticky intro message
    intro_channel = discord.utils.get(guild.text_channels, name="intro")
    if intro_channel:
        async for message in intro_channel.history(limit=50):
            if message.author == bot.user and message.embeds:
                if "Welcome to Quetta Tea Corner" in message.embeds[0].title:
                    sticky_message_id = message.id
                    print("✅ Found sticky intro message")
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
            embed.set_footer(text="Be genuine and friendly! We're excited to meet you.")
            sticky_msg = await intro_channel.send(embed=embed)
            sticky_message_id = sticky_msg.id
            print("✅ Created sticky intro message")

    # Sync slash commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
        # Also sync to guild for instant update
        guild = discord.Object(id=bot.guilds[0].id)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print("✅ Guild sync complete")
    except Exception:
        logger.exception("command sync failed")

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
bot.run(settings.get_discord_token())
