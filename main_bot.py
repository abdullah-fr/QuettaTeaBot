import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
import os
import random
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio

# Import our modules
from question_bank import *
from api_helpers import (
    fetch_trivia_question, fetch_riddle, fetch_joke,
    fetch_qotd, fetch_wyr, fetch_conversation_starter,
    fetch_compliment, fetch_roast
)

load_dotenv()

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Store sticky message ID
sticky_message_id = None

# Data storage
DATA_FILE = "bot_data.json"

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "daily_streaks": {},
            "pet_system": {},
            "inventory": {},
            "vc_time": {},
            "trivia_scores": {},
            "song_guess_scores": {},
            "last_message_time": {}
        }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

bot_data = load_data()

# ---------- ALL 60 COLOR ROLES ----------
COLOR_ROLES = {
    "Red": discord.Color.from_rgb(255, 0, 0), "Crimson": discord.Color.from_rgb(220, 20, 60),
    "Rose": discord.Color.from_rgb(255, 0, 127), "Maroon": discord.Color.from_rgb(128, 0, 0),
    "Scarlet": discord.Color.from_rgb(255, 69, 0), "Brick": discord.Color.from_rgb(178, 34, 34),
    "Purple": discord.Color.from_rgb(128, 0, 128), "Amethyst": discord.Color.from_rgb(153, 102, 204),
    "Lavender": discord.Color.from_rgb(230, 190, 255), "Violet": discord.Color.from_rgb(138, 43, 226),
    "Magenta": discord.Color.from_rgb(255, 0, 255), "Plum": discord.Color.from_rgb(147, 112, 219),
    "Blue": discord.Color.from_rgb(0, 0, 255), "Sapphire": discord.Color.from_rgb(15, 82, 186),
    "Sky": discord.Color.from_rgb(135, 206, 235), "Ocean": discord.Color.from_rgb(0, 119, 190),
    "Navy": discord.Color.from_rgb(0, 0, 128), "Cyan": discord.Color.from_rgb(0, 255, 255),
    "Green": discord.Color.from_rgb(0, 128, 0), "Emerald": discord.Color.from_rgb(80, 200, 120),
    "Mint": discord.Color.from_rgb(152, 255, 152), "Lime": discord.Color.from_rgb(50, 205, 50),
    "Forest": discord.Color.from_rgb(34, 139, 34), "Teal": discord.Color.from_rgb(0, 128, 128),
    "Yellow": discord.Color.from_rgb(255, 255, 0), "Orange": discord.Color.from_rgb(255, 165, 0),
    "Gold": discord.Color.from_rgb(255, 215, 0), "Sunset": discord.Color.from_rgb(255, 99, 71),
    "Coral": discord.Color.from_rgb(255, 127, 80), "Tangerine": discord.Color.from_rgb(255, 140, 0),
    "Black": discord.Color.from_rgb(0, 0, 0), "White": discord.Color.from_rgb(255, 255, 255),
    "Gray": discord.Color.from_rgb(128, 128, 128), "Silver": discord.Color.from_rgb(192, 192, 192),
    "Pearl": discord.Color.from_rgb(240, 234, 214), "Cream": discord.Color.from_rgb(245, 245, 220),
    "Pink": discord.Color.from_rgb(255, 105, 180), "Turquoise": discord.Color.from_rgb(64, 224, 208),
    "Fuchsia": discord.Color.from_rgb(255, 20, 147), "Orchid": discord.Color.from_rgb(218, 112, 214),
    "Blush": discord.Color.from_rgb(255, 182, 193), "Indigo": discord.Color.from_rgb(75, 0, 130),
    "Peach": discord.Color.from_rgb(255, 218, 185), "Lilac": discord.Color.from_rgb(221, 160, 221),
    "Powder": discord.Color.from_rgb(173, 216, 230), "Vanilla": discord.Color.from_rgb(255, 239, 213),
    "Linen": discord.Color.from_rgb(250, 240, 230), "Amber": discord.Color.from_rgb(255, 191, 0),
    "Fire": discord.Color.from_rgb(255, 0, 0), "Neon": discord.Color.from_rgb(0, 255, 0),
    "Electric": discord.Color.from_rgb(255, 255, 0), "Plasma": discord.Color.from_rgb(255, 0, 255),
    "Laser": discord.Color.from_rgb(0, 255, 255), "Azure": discord.Color.from_rgb(30, 144, 255),
    "Coffee": discord.Color.from_rgb(139, 69, 19), "Copper": discord.Color.from_rgb(160, 82, 45),
    "Sand": discord.Color.from_rgb(210, 180, 140), "Bronze": discord.Color.from_rgb(205, 133, 63),
    "Taupe": discord.Color.from_rgb(152, 140, 126), "Olive": discord.Color.from_rgb(128, 128, 0),
}

class ColorRoleButton(Button):
    def __init__(self, color_name):
        super().__init__(label=color_name, style=discord.ButtonStyle.gray, custom_id=f"color_role_{color_name}")
        self.color_name = color_name
    async def callback(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=self.color_name)
        if not role:
            await interaction.response.send_message(f"⚠️ Role {self.color_name} not found!", ephemeral=True)
            return
        current_roles = [r for r in interaction.user.roles if r.name in COLOR_ROLES]
        if current_roles:
            await interaction.user.remove_roles(*current_roles)
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"You have selected **{self.color_name}** ✅", ephemeral=True)
        except:
            await interaction.response.send_message(f"⚠️ Error assigning role", ephemeral=True)

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
    @discord.ui.button(label="🔔 VC Pings", style=discord.ButtonStyle.gray, custom_id="notif_vc_ping")
    async def vc_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="VC Ping")
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message("🔕 VC Ping disabled", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("🔔 VC Ping enabled", ephemeral=True)
    @discord.ui.button(label="💬 Chat Pings", style=discord.ButtonStyle.gray, custom_id="notif_chat_ping")
    async def chat_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Chat Ping")
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message("🔕 Chat Ping disabled", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("🔔 Chat Ping enabled", ephemeral=True)
    @discord.ui.button(label="🎮 Game Pings", style=discord.ButtonStyle.gray, custom_id="notif_game_ping")
    async def game_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Game Ping")
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message("🔕 Game Ping disabled", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("🔔 Game Ping enabled", ephemeral=True)
    @discord.ui.button(label="🎉 Event Pings", style=discord.ButtonStyle.gray, custom_id="notif_event_ping")
    async def event_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Event Ping")
        if role:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message("🔕 Event Ping disabled", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("🔔 Event Ping enabled", ephemeral=True)

# ==================== TRIVIA GAME (API - Unlimited) ====================
# Store active trivia questions
active_trivias = {}

@tasks.loop(hours=24)
async def daily_trivia():
    channel = discord.utils.get(bot.guilds[0].text_channels, name="general")  # Changed to general
    if channel:
        question = await fetch_trivia_question()
        if not question:
            question = {"q": "What is the capital of Pakistan?", "a": "Islamabad",
                       "options": ["Karachi", "Islamabad", "Lahore", "Quetta"]}

        embed = discord.Embed(
            title="🧠 Daily Trivia!",
            description=question["q"],
            color=discord.Color.blue()
        )
        for i, opt in enumerate(question["options"], 1):
            embed.add_field(name=f"Option {i}", value=opt, inline=False)
        embed.set_footer(text="Reply with your answer! Results in 2 minutes.")

        msg = await channel.send(embed=embed)

        # Store trivia data
        active_trivias[msg.id] = {
            "question": question,
            "answers": {},
            "channel": channel
        }

        # Wait 2 minutes then reveal answer
        await asyncio.sleep(120)
        await reveal_trivia_answer(msg.id)

@bot.command()
async def trivia(ctx):
    """Unlimited trivia from API"""
    question = await fetch_trivia_question()
    if not question:
        question = {"q": "What is the capital of Pakistan?", "a": "Islamabad",
                   "options": ["Karachi", "Islamabad", "Lahore", "Quetta"]}

    embed = discord.Embed(
        title="🧠 Trivia Time!",
        description=question["q"],
        color=discord.Color.blue()
    )
    for i, opt in enumerate(question["options"], 1):
        embed.add_field(name=f"Option {i}", value=opt, inline=False)
    embed.set_footer(text="Reply with your answer! Results in 2 minutes.")

    msg = await ctx.send(embed=embed)
    await ctx.send("`!trivia` - Copy this command", delete_after=20)

    # Store trivia data
    active_trivias[msg.id] = {
        "question": question,
        "answers": {},
        "channel": ctx.channel
    }

    # Wait 2 minutes then reveal answer
    await asyncio.sleep(120)
    await reveal_trivia_answer(msg.id)

async def reveal_trivia_answer(trivia_id):
    """Reveal the correct answer and show who got it right"""
    if trivia_id not in active_trivias:
        return

    trivia_data = active_trivias[trivia_id]
    question = trivia_data["question"]
    answers = trivia_data["answers"]
    channel = trivia_data["channel"]

    # Find correct answers
    correct_users = []
    for user_id, answer in answers.items():
        if answer.lower() == question["a"].lower():
            correct_users.append(f"<@{user_id}>")
            # Award points
            if user_id not in bot_data["trivia_scores"]:
                bot_data["trivia_scores"][user_id] = 0
            bot_data["trivia_scores"][user_id] += 1

    save_data(bot_data)

    # Create results embed
    embed = discord.Embed(
        title="🎯 Trivia Results!",
        description=f"**Correct Answer:** {question['a']}",
        color=discord.Color.green()
    )

    if correct_users:
        embed.add_field(
            name="✅ Correct Answers",
            value=", ".join(correct_users),
            inline=False
        )
    else:
        embed.add_field(
            name="❌ No Correct Answers",
            value="Better luck next time!",
            inline=False
        )

    embed.add_field(
        name="📊 Total Responses",
        value=f"{len(answers)} people answered",
        inline=False
    )

    await channel.send(embed=embed)

    # Clean up
    del active_trivias[trivia_id]

@bot.event
async def on_message_trivia_answer(message):
    """Track trivia answers"""
    if message.author.bot:
        return

    # Check if this is a trivia answer
    for trivia_id, trivia_data in active_trivias.items():
        if message.channel == trivia_data["channel"]:
            # Store the answer
            trivia_data["answers"][str(message.author.id)] = message.content.strip()

@bot.command()
async def triviascores(ctx):
    """Show trivia leaderboard - Copy: !triviascores"""
    scores = bot_data["trivia_scores"]
    if not scores:
        await ctx.send("No trivia scores yet!")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    embed = discord.Embed(title="🏆 Trivia Leaderboard", color=discord.Color.gold())

    for i, (user_id, score) in enumerate(sorted_scores, 1):
        user = await bot.fetch_user(int(user_id))
        embed.add_field(name=f"{i}. {user.name}", value=f"{score} points", inline=False)

    await ctx.send(embed=embed)

# ==================== WOULD YOU RATHER (API - Unlimited) ====================
@tasks.loop(hours=24)
async def daily_wyr():
    channel = discord.utils.get(bot.guilds[0].text_channels, name="general")  # Changed to general
    if channel:
        question = await fetch_wyr()
        if not question:
            question = random.choice(WYR_QUESTIONS)

        embed = discord.Embed(
            title="🤔 Would You Rather?",
            description=question,
            color=discord.Color.purple()
        )
        msg = await channel.send(embed=embed)
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")

@bot.command()
async def wyr(ctx):
    """Unlimited Would You Rather from API"""
    question = await fetch_wyr()
    if not question:
        question = random.choice(WYR_QUESTIONS)

    embed = discord.Embed(
        title="🤔 Would You Rather?",
        description=question,
        color=discord.Color.purple()
    )
    msg = await ctx.send(embed=embed)
    await ctx.send("`!wyr` - Copy this command", delete_after=20)
    await msg.add_reaction("1️⃣")
    await msg.add_reaction("2️⃣")

# ==================== GUESS THE SONG ====================
@bot.command()
async def guessong(ctx):
    """Guess the song from lyrics"""
    song = random.choice(SONGS)
    embed = discord.Embed(
        title="🎵 Guess the Song!",
        description=f"**Lyrics:** {song['lyrics']}",
        color=discord.Color.green()
    )
    embed.set_footer(text="Reply with the song name!")
    await ctx.send(embed=embed)
    await ctx.send("`!guessong` - Copy this command", delete_after=20)

    def check(m):
        return m.channel == ctx.channel and song["answer"].lower() in m.content.lower()

    try:
        answer = await bot.wait_for('message', check=check, timeout=30.0)
        user_id = str(answer.author.id)
        if user_id not in bot_data["song_guess_scores"]:
            bot_data["song_guess_scores"][user_id] = 0
        bot_data["song_guess_scores"][user_id] += 1
        save_data(bot_data)
        await ctx.send(f"🎉 {answer.author.mention} got it! The song is **{song['answer']}**")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up! The song was: **{song['answer']}**")

# ==================== RIDDLES (API - Unlimited) ====================
# Store active riddles
active_riddles = {}

@tasks.loop(hours=24)
async def daily_riddle():
    channel = discord.utils.get(bot.guilds[0].text_channels, name="general")  # Changed to general
    if channel:
        riddle = await fetch_riddle()
        if not riddle:
            riddles_list = [
                {"q": "What has keys but no locks?", "a": "keyboard"},
                {"q": "I speak without a mouth. What am I?", "a": "echo"},
                {"q": "The more you take, the more you leave behind.", "a": "footsteps"},
            ]
            riddle = random.choice(riddles_list)

        embed = discord.Embed(
            title="🤯 Daily Riddle!",
            description=riddle["q"],
            color=discord.Color.orange()
        )
        embed.set_footer(text="You have 5 minutes to guess! First correct answer wins.")

        msg = await channel.send(embed=embed)

        # Store riddle data
        active_riddles[msg.id] = {
            "riddle": riddle,
            "channel": channel,
            "solved": False
        }

        # Wait 5 minutes then reveal if not solved
        await asyncio.sleep(300)
        await reveal_riddle_answer(msg.id)

@bot.command()
async def riddle(ctx):
    """Unlimited riddles from API - Copy: !riddle"""
    riddle = await fetch_riddle()
    if not riddle:
        riddles_list = [
            {"q": "What has keys but no locks?", "a": "keyboard"},
            {"q": "I speak without a mouth. What am I?", "a": "echo"},
        ]
        riddle = random.choice(riddles_list)

    embed = discord.Embed(
        title="🤯 Riddle Time!",
        description=riddle["q"],
        color=discord.Color.orange()
    )
    embed.set_footer(text="You have 5 minutes to guess! First correct answer wins.")

    msg = await ctx.send(embed=embed)

    # Store riddle data
    active_riddles[msg.id] = {
        "riddle": riddle,
        "channel": ctx.channel,
        "solved": False
    }

    # Wait 5 minutes then reveal if not solved
    await asyncio.sleep(300)
    await reveal_riddle_answer(msg.id)

async def reveal_riddle_answer(riddle_id):
    """Reveal the riddle answer if not solved"""
    if riddle_id not in active_riddles:
        return

    riddle_data = active_riddles[riddle_id]

    # Only reveal if not already solved
    if not riddle_data["solved"]:
        riddle = riddle_data["riddle"]
        channel = riddle_data["channel"]

        embed = discord.Embed(
            title="⏰ Time's Up!",
            description=f"**Answer:** {riddle['a']}",
            color=discord.Color.red()
        )
        embed.add_field(
            name="❌ No one guessed it!",
            value="Better luck next time!",
            inline=False
        )

        await channel.send(embed=embed)

    # Clean up
    del active_riddles[riddle_id]

@bot.event
async def on_message_riddle_answer(message):
    """Check riddle answers"""
    if message.author.bot:
        return

    # Check if this is a riddle answer
    for riddle_id, riddle_data in list(active_riddles.items()):
        if message.channel == riddle_data["channel"] and not riddle_data["solved"]:
            riddle = riddle_data["riddle"]

            # Check if answer is correct
            if riddle["a"].lower() in message.content.lower():
                riddle_data["solved"] = True

                embed = discord.Embed(
                    title="🎉 Riddle Solved!",
                    description=f"{message.author.mention} got it right!",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="✅ Correct Answer",
                    value=riddle["a"],
                    inline=False
                )

                await message.channel.send(embed=embed)

                # Clean up immediately
                del active_riddles[riddle_id]
                break

# ==================== ROAST GENERATOR (Unlimited with SFW Filter) ====================
@bot.command()
async def roast(ctx, member: discord.Member = None):
    """Unlimited roasts with SFW filter - Copy: !roast @user"""
    if member is None:
        member = ctx.author

    # Try to get a clean roast from API (tries 5 times with filter)
    roast_text = await fetch_roast()

    # If API fails or all roasts were NSFW, use our safe fallback list
    if not roast_text:
        roast_text = random.choice(ROASTS)

    embed = discord.Embed(
        title="🔥 Roast Battle!",
        description=f"{member.mention} {roast_text}",
        color=discord.Color.red()
    )
    embed.set_footer(text="It's all in good fun! ❤️ (SFW filtered)")
    await ctx.send(embed=embed)

# ==================== QOTD (FULLY AUTOMATED - API Unlimited) ====================
@tasks.loop(hours=24)
async def daily_qotd():
    """Automatically posts QOTD daily - NO COMMAND NEEDED"""
    channel = discord.utils.get(bot.guilds[0].text_channels, name="general")
    if channel:
        question = await fetch_qotd()
        if not question:
            question = random.choice(QOTD_QUESTIONS)

        embed = discord.Embed(
            title="💭 Question of the Day",
            description=question,
            color=discord.Color.teal()
        )
        await channel.send(embed=embed)

@bot.command()
async def qotd(ctx):
    """Manual QOTD (Unlimited via API) - Copy: !qotd"""
    question = await fetch_qotd()
    if not question:
        question = random.choice(QOTD_QUESTIONS)

    embed = discord.Embed(
        title="💭 Question of the Day",
        description=question,
        color=discord.Color.teal()
    )
    await ctx.send(embed=embed)

# ==================== CONVERSATION STARTERS (AUTO when chat dead) ====================
@tasks.loop(minutes=30)
async def check_dead_chat():
    """Automatically posts conversation starter if chat is dead for 2 hours"""
    channel = discord.utils.get(bot.guilds[0].text_channels, name="general")
    if not channel:
        return

    channel_id = str(channel.id)
    current_time = datetime.now()

    # Get last message time
    try:
        async for message in channel.history(limit=1):
            last_msg_time = message.created_at.replace(tzinfo=None)
            time_diff = (current_time - last_msg_time).total_seconds() / 3600  # hours

            # If chat dead for 2+ hours, post starter
            if time_diff >= 2:
                # Check if we already posted recently
                if channel_id in bot_data["last_message_time"]:
                    last_bot_post = datetime.fromisoformat(bot_data["last_message_time"][channel_id])
                    if (current_time - last_bot_post).total_seconds() / 3600 < 3:
                        return  # Don't spam

                # Post conversation starter
                starter = await fetch_conversation_starter()
                if not starter:
                    starter = random.choice(CONVERSATION_STARTERS)

                embed = discord.Embed(
                    title="💬 Chat seems quiet... Let's talk!",
                    description=starter,
                    color=discord.Color.blue()
                )
                await channel.send(embed=embed)

                # Update last post time
                bot_data["last_message_time"][channel_id] = current_time.isoformat()
                save_data(bot_data)
    except:
        pass

@bot.command()
async def starter(ctx):
    """Manual conversation starter (Unlimited via API) - Copy: !starter"""
    starter = await fetch_conversation_starter()
    if not starter:
        starter = random.choice(CONVERSATION_STARTERS)

    embed = discord.Embed(
        title="💬 Conversation Starter",
        description=starter,
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# ==================== COMPLIMENT GENERATOR (AUTOMATED DAILY) ====================
@tasks.loop(hours=24)
async def daily_compliment():
    """Automatically posts random compliment daily - NO COMMAND NEEDED"""
    channel = discord.utils.get(bot.guilds[0].text_channels, name="general")
    if channel:
        # Pick a random online member
        online_members = [m for m in channel.guild.members if m.status != discord.Status.offline and not m.bot]
        if online_members:
            member = random.choice(online_members)

            compliment_text = await fetch_compliment()
            if not compliment_text:
                compliment_text = random.choice(COMPLIMENTS)

            embed = discord.Embed(
                title="💝 Daily Compliment",
                description=f"{member.mention} {compliment_text}",
                color=discord.Color.pink()
            )
            await channel.send(embed=embed)

@bot.command()
async def compliment(ctx, member: discord.Member = None):
    """Give someone a compliment (Unlimited via API) - Copy: !compliment @user"""
    if member is None:
        member = ctx.author

    compliment_text = await fetch_compliment()
    if not compliment_text:
        compliment_text = random.choice(COMPLIMENTS)

    embed = discord.Embed(
        title="💝 Compliment",
        description=f"{member.mention} {compliment_text}",
        color=discord.Color.pink()
    )
    await ctx.send(embed=embed)

# ==================== CHAT GAMES ====================
@bot.command()
async def firsttype(ctx):
    """First to type wins! - Copy: !firsttype"""
    word = random.choice(["PIZZA", "DISCORD", "GAMING", "COFFEE", "MUSIC"])
    embed = discord.Embed(
        title="⚡ First to Type Wins!",
        description=f"Type: **{word}**",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

    def check(m):
        return m.channel == ctx.channel and m.content.upper() == word

    try:
        winner = await bot.wait_for('message', check=check, timeout=15.0)
        await ctx.send(f"🏆 {winner.author.mention} wins!")
    except asyncio.TimeoutError:
        await ctx.send("⏰ Nobody won!")

# ==================== DAILY STREAKS ====================
@bot.command()
async def daily(ctx):
    """Claim your daily reward - Copy: !daily"""
    user_id = str(ctx.author.id)
    today = datetime.now().date().isoformat()

    if user_id not in bot_data["daily_streaks"]:
        bot_data["daily_streaks"][user_id] = {"last_claim": today, "streak": 1}
    else:
        last_claim = datetime.fromisoformat(bot_data["daily_streaks"][user_id]["last_claim"]).date()
        today_date = datetime.now().date()

        if last_claim == today_date:
            await ctx.send("❌ You already claimed your daily reward today!")
            return
        elif (today_date - last_claim).days == 1:
            bot_data["daily_streaks"][user_id]["streak"] += 1
        else:
            bot_data["daily_streaks"][user_id]["streak"] = 1

        bot_data["daily_streaks"][user_id]["last_claim"] = today

    save_data(bot_data)
    streak = bot_data["daily_streaks"][user_id]["streak"]

    embed = discord.Embed(
        title="🎁 Daily Reward Claimed!",
        description=f"Current streak: **{streak} days** 🔥",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

@bot.command()
async def streak(ctx):
    """Check your daily streak - Copy: !streak"""
    user_id = str(ctx.author.id)
    if user_id in bot_data["daily_streaks"]:
        streak = bot_data["daily_streaks"][user_id]["streak"]
        await ctx.send(f"🔥 Your current streak: **{streak} days**")
    else:
        await ctx.send("You don't have a streak yet! Use `!daily` to start.")

# ==================== MILESTONE CELEBRATIONS ====================
@bot.event
async def on_member_join(member):
    # Auto-assign Unverified role
    unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
    if unverified_role:
        await member.add_roles(unverified_role)
        print(f"✅ Assigned Unverified role to {member.name}")

    # Check for milestones
    guild = member.guild
    member_count = guild.member_count

    milestones = [50, 100, 200, 500, 1000]
    if member_count in milestones:
        channel = discord.utils.get(guild.text_channels, name="general")
        if channel:
            embed = discord.Embed(
                title="🎉 MILESTONE REACHED!",
                description=f"We just hit **{member_count} members**! 🎊",
                color=discord.Color.gold()
            )
            await channel.send(embed=embed)

# ==================== MESSAGE LOGS ====================
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    logs_channel = discord.utils.get(message.guild.text_channels, name="logs")
    if logs_channel:
        # Try to get audit log to see who deleted it
        deleted_by = "Self-deleted or Unknown"
        try:
            await asyncio.sleep(0.5)  # Small delay for audit log to update
            async for entry in message.guild.audit_logs(limit=5, action=discord.AuditLogAction.message_delete):
                # Check if this entry matches our deleted message
                if (entry.target.id == message.author.id and
                    entry.extra.channel.id == message.channel.id and
                    (datetime.now() - entry.created_at.replace(tzinfo=None)).total_seconds() < 2):
                    deleted_by = entry.user.mention
                    break
        except Exception as e:
            print(f"Error fetching audit log: {e}")

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Deleted by:** {deleted_by}\n**Content:** {message.content[:1024] if message.content else 'No content'}",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        await logs_channel.send(embed=embed)

# Removed on_message_edit - no longer logging edits

# ==================== SERVER STATS ====================
@bot.command()
async def stats(ctx):
    """Show server statistics - Copy: !stats"""
    guild = ctx.guild
    total_members = guild.member_count
    online_members = sum(1 for m in guild.members if m.status != discord.Status.offline)
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)

    embed = discord.Embed(
        title=f"📊 {guild.name} Statistics",
        color=discord.Color.blue()
    )
    embed.add_field(name="Total Members", value=total_members, inline=True)
    embed.add_field(name="Online Members", value=online_members, inline=True)
    embed.add_field(name="Text Channels", value=text_channels, inline=True)
    embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

    await ctx.send(embed=embed)

# ==================== VOICE TIME TRACKER ====================
@bot.event
async def on_voice_state_update(member, before, after):
    user_id = str(member.id)

    # Initialize user data if not exists
    if user_id not in bot_data["vc_time"]:
        bot_data["vc_time"][user_id] = {"total_minutes": 0}

    # Joined VC
    if before.channel is None and after.channel is not None:
        bot_data["vc_time"][user_id]["join_time"] = datetime.now().isoformat()
        save_data(bot_data)
        print(f"✅ {member.name} joined VC at {datetime.now()}")

    # Left VC
    elif before.channel is not None and after.channel is None:
        if "join_time" in bot_data["vc_time"][user_id]:
            join_time = datetime.fromisoformat(bot_data["vc_time"][user_id]["join_time"])
            duration = (datetime.now() - join_time).total_seconds() / 60

            bot_data["vc_time"][user_id]["total_minutes"] += duration
            del bot_data["vc_time"][user_id]["join_time"]
            save_data(bot_data)
            print(f"✅ {member.name} left VC. Session: {duration:.1f} min, Total: {bot_data['vc_time'][user_id]['total_minutes']:.1f} min")

@bot.command()
async def vctime(ctx):
    """Check your voice chat time - Copy: !vctime"""
    user_id = str(ctx.author.id)

    # Initialize if not exists
    if user_id not in bot_data["vc_time"]:
        bot_data["vc_time"][user_id] = {"total_minutes": 0}
        save_data(bot_data)

    total_minutes = bot_data["vc_time"][user_id].get("total_minutes", 0)

    if total_minutes > 0:
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        await ctx.send(f"🎤 You've spent **{hours}h {minutes}m** in voice channels!")
    else:
        await ctx.send("You haven't joined any voice channels yet! Join a VC to start tracking your time.")

# ==================== REACTION ROLES ====================
class HobbyRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎮 Gaming", style=discord.ButtonStyle.gray, custom_id="hobby_gaming")
    async def gaming(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Gaming")
        await self.toggle_role(interaction, role)

    @discord.ui.button(label="🎨 Art", style=discord.ButtonStyle.gray, custom_id="hobby_art")
    async def art(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Art")
        await self.toggle_role(interaction, role)

    @discord.ui.button(label="🎵 Music", style=discord.ButtonStyle.gray, custom_id="hobby_music")
    async def music(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Music")
        await self.toggle_role(interaction, role)

    @discord.ui.button(label="📚 Reading", style=discord.ButtonStyle.gray, custom_id="hobby_reading")
    async def reading(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Reading")
        await self.toggle_role(interaction, role)

    async def toggle_role(self, interaction, role):
        if not role:
            await interaction.response.send_message("❌ Role not found!", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"Removed {role.name} role", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Added {role.name} role", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def setuphobbies(ctx):
    """Setup hobby reaction roles"""
    embed = discord.Embed(
        title="🎯 Choose Your Hobbies!",
        description="Click the buttons below to get hobby roles",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=HobbyRoleView())

# ==================== AUTO-REACTIONS ====================
@bot.event
async def on_message(message):
    global sticky_message_id

    if message.author.bot:
        return

    # Sticky intro message
    if message.channel.name == "intro" and sticky_message_id:
        try:
            sticky_msg = await message.channel.fetch_message(sticky_message_id)
            await sticky_msg.delete()
            embed = discord.Embed(
                title="👋 Welcome to Quetta Tea Corner!",
                description=(
                    "Before you can access the server, please introduce yourself here!\n\n"
                    "**Tell us about:**\n• Your name/nickname\n• Your age\n• Your gender\n"
                    "• Your country/city\n• Your interests/hobbies\n\n"
                    "Once a moderator reviews your intro, you'll get the **Verified** role "
                    "and full access to the server! ☕"
                ),
                color=discord.Color.from_rgb(139, 69, 19)
            )
            embed.set_footer(text="Be genuine and friendly! We're excited to meet you.")
            new_sticky = await message.channel.send(embed=embed)
            sticky_message_id = new_sticky.id
        except:
            pass

    # Check trivia answers
    await on_message_trivia_answer(message)

    # Check riddle answers
    await on_message_riddle_answer(message)

    # Auto-react in specific channels
    if message.channel.name == "art-showcase":
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    await bot.process_commands(message)

# ==================== PET SYSTEM ====================
@bot.command()
async def adopt(ctx):
    """Adopt a virtual pet - Copy: !adopt"""
    user_id = str(ctx.author.id)
    if user_id in bot_data["pet_system"]:
        await ctx.send("You already have a pet! Use `!feedpet` to take care of it.")
        return

    pet = random.choice(PETS)
    bot_data["pet_system"][user_id] = {"pet": pet, "hunger": 100, "happiness": 100}
    save_data(bot_data)

    embed = discord.Embed(
        title="🎉 Pet Adopted!",
        description=f"You adopted a {pet}!",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def feedpet(ctx):
    """Feed your pet - Copy: !feedpet"""
    user_id = str(ctx.author.id)
    if user_id not in bot_data["pet_system"]:
        await ctx.send("You don't have a pet! Use `!adopt` first.")
        return

    bot_data["pet_system"][user_id]["hunger"] = min(100, bot_data["pet_system"][user_id]["hunger"] + 20)
    bot_data["pet_system"][user_id]["happiness"] = min(100, bot_data["pet_system"][user_id]["happiness"] + 10)
    save_data(bot_data)

    pet = bot_data["pet_system"][user_id]["pet"]
    await ctx.send(f"{pet} has been fed! 🍖")

@bot.command()
async def mypet(ctx):
    """Check your pet's status - Copy: !mypet"""
    user_id = str(ctx.author.id)
    if user_id not in bot_data["pet_system"]:
        await ctx.send("You don't have a pet! Use `!adopt` first.")
        return

    pet_data = bot_data["pet_system"][user_id]
    embed = discord.Embed(
        title=f"Your {pet_data['pet']}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Hunger", value=f"{pet_data['hunger']}%", inline=True)
    embed.add_field(name="Happiness", value=f"{pet_data['happiness']}%", inline=True)
    await ctx.send(embed=embed)

# ==================== INVENTORY SYSTEM ====================
@bot.command()
async def collect(ctx):
    """Collect a random item - Copy: !collect"""
    user_id = str(ctx.author.id)
    if user_id not in bot_data["inventory"]:
        bot_data["inventory"][user_id] = []

    item = random.choice(ITEMS)
    bot_data["inventory"][user_id].append(item)
    save_data(bot_data)

    await ctx.send(f"You collected {item}!")

@bot.command()
async def inventory(ctx):
    """View your inventory - Copy: !inventory"""
    user_id = str(ctx.author.id)
    if user_id not in bot_data["inventory"] or not bot_data["inventory"][user_id]:
        await ctx.send("Your inventory is empty! Use `!collect` to get items.")
        return

    items = bot_data["inventory"][user_id]
    embed = discord.Embed(
        title="🎒 Your Inventory",
        description="\n".join(items),
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

# ==================== REKHTA POETRY ====================
@bot.command()
async def rekhta(ctx):
    """Get random Urdu poetry - Copy: !rekhta"""
    poetry = random.choice(URDU_POETRY)
    embed = discord.Embed(
        title="📜 Urdu Poetry",
        description=poetry,
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

# ==================== STUDY TIMER (POMODORO) ====================
@bot.command()
async def pomodoro(ctx, minutes: int = 25):
    """Start a Pomodoro study timer - Copy: !pomodoro 25"""
    if minutes > 60:
        await ctx.send("Maximum 60 minutes!")
        return

    await ctx.send(f"⏰ Pomodoro timer started for {minutes} minutes!")
    await asyncio.sleep(minutes * 60)
    await ctx.send(f"{ctx.author.mention} ⏰ Time's up! Take a break! 🎉")

# ==================== PICTIONARY GAME ====================
@bot.command()
async def pictionary(ctx):
    """Start a Pictionary game - Copy: !pictionary"""
    word = random.choice(PICTIONARY_WORDS)
    embed = discord.Embed(
        title="🎨 Pictionary!",
        description=f"Draw: **{word}**\nOthers: Guess what's being drawn!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# ==================== BONUS: JOKE COMMAND ====================
@bot.command()
async def joke(ctx):
    """Get unlimited jokes from API - Copy: !joke"""
    joke_text = await fetch_joke()
    if not joke_text:
        joke_text = "Why don't scientists trust atoms? Because they make up everything!"

    embed = discord.Embed(
        title="😂 Here's a Joke!",
        description=joke_text,
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

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
    print("✅ Registered all color role buttons (60 colors)")
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
                    "**Tell us about:**\n• Your name/nickname\n• Your age\n• Your gender\n"
                    "• Your country/city\n• Your interests/hobbies\n\n"
                    "Once a moderator reviews your intro, you'll get the **Verified** role "
                    "and full access to the server! ☕"
                ),
                color=discord.Color.from_rgb(139, 69, 19)
            )
            embed.set_footer(text="Be genuine and friendly! We're excited to meet you.")
            sticky_msg = await intro_channel.send(embed=embed)
            sticky_message_id = sticky_msg.id
            print(f"✅ Created sticky intro message")

    # Start all automated daily tasks (only if not already running)
    if not daily_trivia.is_running():
        daily_trivia.start()
    if not daily_wyr.is_running():
        daily_wyr.start()
    if not daily_riddle.is_running():
        daily_riddle.start()
    if not daily_qotd.is_running():
        daily_qotd.start()
    if not daily_compliment.is_running():
        daily_compliment.start()
    if not check_dead_chat.is_running():
        check_dead_chat.start()

    print("✅ All automated tasks started!")
    print("   - Daily Trivia (unlimited)")
    print("   - Daily WYR (unlimited)")
    print("   - Daily Riddle (unlimited)")
    print("   - Daily QOTD (unlimited)")
    print("   - Daily Compliment (unlimited)")
    print("   - Auto Conversation Starter (when chat dead)")

    # Post announcements in channels (only on first start)
    if not hasattr(bot, '_announcements_posted'):
        await post_channel_announcements()
        bot._announcements_posted = True

async def post_channel_announcements():
    """Post pinned announcements in each channel about new features"""
    guild = bot.guilds[0]

    # Daily-fun channel - REMOVED announcement as requested

    # Music channel
    music = discord.utils.get(guild.text_channels, name="music")
    if music:
        embed = discord.Embed(
            title="🎵 New Features!",
            description="New music game added!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="🎵 Guess the Song",
            value="• `!guessong` - Guess song from lyrics\n• First to guess wins points!",
            inline=False
        )
        msg = await music.send(embed=embed)
        try:
            await msg.pin()
        except:
            pass

    # Extras channel
    extras = discord.utils.get(guild.text_channels, name="extras")
    if extras:
        embed = discord.Embed(
            title="✨ New Features!",
            description="Tons of new commands and features!",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="🎮 Games & Fun",
            value="• `!roast @user` - Friendly roasts (unlimited)\n• `!firsttype` - Typing game\n• `!joke` - Random jokes (unlimited)",
            inline=False
        )
        embed.add_field(
            name="🏆 Progress & Rewards",
            value="• `!daily` - Claim daily reward\n• `!streak` - Check your streak\n• `!vctime` - Voice chat time",
            inline=False
        )
        embed.add_field(
            name="🐾 Social Features",
            value="• `!adopt` - Adopt a pet\n• `!feedpet` - Feed your pet\n• `!mypet` - Check pet status\n• `!collect` - Collect items\n• `!inventory` - View inventory",
            inline=False
        )
        embed.add_field(
            name="📊 Info",
            value="• `!stats` - Server statistics",
            inline=False
        )
        msg = await extras.send(embed=embed)
        try:
            await msg.pin()
        except:
            pass

    # General channel
    general = discord.utils.get(guild.text_channels, name="general")
    if general:
        embed = discord.Embed(
            title="🎉 New Automated Features!",
            description="This channel now has smart automated engagement!",
            color=discord.Color.teal()
        )
        embed.add_field(
            name="🤖 Auto-Posted Daily",
            value="• 💭 **Question of the Day** - Unlimited questions\n• 💝 **Daily Compliment** - Random member gets complimented",
            inline=False
        )
        embed.add_field(
            name="🎯 Smart Auto-Post",
            value="• 💬 **Conversation Starter** - Auto-posts when chat is dead for 2+ hours",
            inline=False
        )
        embed.add_field(
            name="💬 Manual Commands",
            value="• `!qotd` - Get QOTD anytime\n• `!compliment @user` - Compliment someone\n• `!starter` - Get conversation starter",
            inline=False
        )
        embed.add_field(
            name="🎉 Auto Features",
            value="• Milestone celebrations when we hit member goals!",
            inline=False
        )
        msg = await general.send(embed=embed)
        try:
            await msg.pin()
        except:
            pass

    # Rekhta channel
    rekhta = discord.utils.get(guild.text_channels, name="rekhta")
    if rekhta:
        embed = discord.Embed(
            title="📜 New Feature!",
            description="Urdu poetry generator added!",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="📜 Urdu Poetry",
            value="• `!rekhta` - Get random Urdu poetry",
            inline=False
        )
        msg = await rekhta.send(embed=embed)
        try:
            await msg.pin()
        except:
            pass

    # Sketch-guess channel
    sketch = discord.utils.get(guild.text_channels, name="sketch-guess")
    if sketch:
        embed = discord.Embed(
            title="🎨 New Feature!",
            description="Pictionary game added!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🎨 Pictionary",
            value="• `!pictionary` - Start a drawing game\n• One person draws, others guess!",
            inline=False
        )
        msg = await sketch.send(embed=embed)
        try:
            await msg.pin()
        except:
            pass

    print("✅ Channel announcements posted and pinned!")

# ==================== RUN BOT ====================
bot.run(os.getenv('DISCORD_TOKEN'))
