import discord
from discord.ext import commands
from discord.ui import View, Button
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------- BOT SETUP ----------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Store sticky message ID
sticky_message_id = None

# ---------- ALL 60 COLOR ROLES ----------
COLOR_ROLES = {
    # Red Tones
    "Red": discord.Color.from_rgb(255, 0, 0),
    "Crimson": discord.Color.from_rgb(220, 20, 60),
    "Rose": discord.Color.from_rgb(255, 0, 127),
    "Maroon": discord.Color.from_rgb(128, 0, 0),
    "Scarlet": discord.Color.from_rgb(255, 69, 0),
    "Brick": discord.Color.from_rgb(178, 34, 34),

    # Purple Tones
    "Purple": discord.Color.from_rgb(128, 0, 128),
    "Amethyst": discord.Color.from_rgb(153, 102, 204),
    "Lavender": discord.Color.from_rgb(230, 190, 255),
    "Violet": discord.Color.from_rgb(138, 43, 226),
    "Magenta": discord.Color.from_rgb(255, 0, 255),
    "Plum": discord.Color.from_rgb(147, 112, 219),

    # Blue Tones
    "Blue": discord.Color.from_rgb(0, 0, 255),
    "Sapphire": discord.Color.from_rgb(15, 82, 186),
    "Sky": discord.Color.from_rgb(135, 206, 235),
    "Ocean": discord.Color.from_rgb(0, 119, 190),
    "Navy": discord.Color.from_rgb(0, 0, 128),
    "Cyan": discord.Color.from_rgb(0, 255, 255),

    # Green Tones
    "Green": discord.Color.from_rgb(0, 128, 0),
    "Emerald": discord.Color.from_rgb(80, 200, 120),
    "Mint": discord.Color.from_rgb(152, 255, 152),
    "Lime": discord.Color.from_rgb(50, 205, 50),
    "Forest": discord.Color.from_rgb(34, 139, 34),
    "Teal": discord.Color.from_rgb(0, 128, 128),

    # Warm Tones
    "Yellow": discord.Color.from_rgb(255, 255, 0),
    "Orange": discord.Color.from_rgb(255, 165, 0),
    "Gold": discord.Color.from_rgb(255, 215, 0),
    "Sunset": discord.Color.from_rgb(255, 99, 71),
    "Coral": discord.Color.from_rgb(255, 127, 80),
    "Tangerine": discord.Color.from_rgb(255, 140, 0),

    # Neutral Tones
    "Black": discord.Color.from_rgb(0, 0, 0),
    "White": discord.Color.from_rgb(255, 255, 255),
    "Gray": discord.Color.from_rgb(128, 128, 128),
    "Silver": discord.Color.from_rgb(192, 192, 192),
    "Pearl": discord.Color.from_rgb(240, 234, 214),
    "Cream": discord.Color.from_rgb(245, 245, 220),

    # Special Tones
    "Pink": discord.Color.from_rgb(255, 105, 180),
    "Turquoise": discord.Color.from_rgb(64, 224, 208),
    "Fuchsia": discord.Color.from_rgb(255, 20, 147),
    "Orchid": discord.Color.from_rgb(218, 112, 214),
    "Blush": discord.Color.from_rgb(255, 182, 193),
    "Indigo": discord.Color.from_rgb(75, 0, 130),

    # Pastel Tones
    "Peach": discord.Color.from_rgb(255, 218, 185),
    "Lilac": discord.Color.from_rgb(221, 160, 221),
    "Powder": discord.Color.from_rgb(173, 216, 230),
    "Vanilla": discord.Color.from_rgb(255, 239, 213),
    "Linen": discord.Color.from_rgb(250, 240, 230),
    "Amber": discord.Color.from_rgb(255, 191, 0),

    # Vibrant Tones
    "Fire": discord.Color.from_rgb(255, 0, 0),
    "Neon": discord.Color.from_rgb(0, 255, 0),
    "Electric": discord.Color.from_rgb(255, 255, 0),
    "Plasma": discord.Color.from_rgb(255, 0, 255),
    "Laser": discord.Color.from_rgb(0, 255, 255),
    "Azure": discord.Color.from_rgb(30, 144, 255),

    # Earth Tones
    "Coffee": discord.Color.from_rgb(139, 69, 19),
    "Copper": discord.Color.from_rgb(160, 82, 45),
    "Sand": discord.Color.from_rgb(210, 180, 140),
    "Bronze": discord.Color.from_rgb(205, 133, 63),
    "Taupe": discord.Color.from_rgb(152, 140, 126),
    "Olive": discord.Color.from_rgb(128, 128, 0),
}

# ---------- COLOR ROLE BUTTONS ----------
class ColorRoleButton(Button):
    def __init__(self, color_name):
        # Use gray style for all buttons since we can't set custom colors
        button_style = discord.ButtonStyle.gray
        super().__init__(
            label=color_name,
            style=button_style,
            custom_id=f"color_role_{color_name}"
        )
        self.color_name = color_name

    async def callback(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=self.color_name)
        if not role:
            await interaction.response.send_message(
                f"⚠️ Role {self.color_name} not found!", ephemeral=True
            )
            return

        # Remove any other color roles
        current_roles = [r for r in interaction.user.roles if r.name in COLOR_ROLES]
        if current_roles:
            await interaction.user.remove_roles(*current_roles)

        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"You have selected **{self.color_name}** ✅", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                f"⚠️ I can't assign this role. Make sure my role is above {self.color_name}.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"⚠️ Error: {str(e)}", ephemeral=True
            )

class ColorRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        # Add first 25 colors (Discord's limit per view)
        color_names = list(COLOR_ROLES.keys())
        for name in color_names[:25]:
            self.add_item(ColorRoleButton(name))

class ColorRoleView2(View):
    def __init__(self):
        super().__init__(timeout=None)
        color_names = list(COLOR_ROLES.keys())
        for name in color_names[25:50]:
            self.add_item(ColorRoleButton(name))

class ColorRoleView3(View):
    def __init__(self):
        super().__init__(timeout=None)
        color_names = list(COLOR_ROLES.keys())
        for name in color_names[50:]:
            self.add_item(ColorRoleButton(name))

# ---------- NOTIFICATION BUTTONS ----------
class NotificationView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔔 VC Pings", style=discord.ButtonStyle.gray, custom_id="notif_vc_ping")
    async def vc_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="VC Ping")
        if not role:
            await interaction.response.send_message("❌ Role not found!", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("🔕 VC Ping notifications disabled", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("🔔 VC Ping notifications enabled", ephemeral=True)

    @discord.ui.button(label="💬 Chat Pings", style=discord.ButtonStyle.gray, custom_id="notif_chat_ping")
    async def chat_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Chat Ping")
        if not role:
            await interaction.response.send_message("❌ Role not found!", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("🔕 Chat Ping notifications disabled", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("🔔 Chat Ping notifications enabled", ephemeral=True)

    @discord.ui.button(label="🎮 Game Pings", style=discord.ButtonStyle.gray, custom_id="notif_game_ping")
    async def game_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Game Ping")
        if not role:
            await interaction.response.send_message("❌ Role not found!", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("🔕 Game Ping notifications disabled", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("🔔 Game Ping notifications enabled", ephemeral=True)

    @discord.ui.button(label="🎉 Event Pings", style=discord.ButtonStyle.gray, custom_id="notif_event_ping")
    async def event_ping(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name="Event Ping")
        if not role:
            await interaction.response.send_message("❌ Role not found!", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("🔕 Event Ping notifications disabled", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("🔔 Event Ping notifications enabled", ephemeral=True)

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    global sticky_message_id

    guild = bot.guilds[0]
    print(f"\n{'='*50}")
    print(f"🤖 Bot logged in as {bot.user}")
    print(f"🏰 Server: {guild.name}")
    print(f"{'='*50}\n")

    # Register persistent views
    bot.add_view(ColorRoleView())
    bot.add_view(ColorRoleView2())
    bot.add_view(ColorRoleView3())
    bot.add_view(NotificationView())
    print("✅ Registered all color role buttons (60 colors)")
    print("✅ Registered notification buttons")

    # Setup sticky intro message
    intro_channel = discord.utils.get(guild.text_channels, name="intro")
    if intro_channel:
        async for message in intro_channel.history(limit=50):
            if message.author == bot.user and message.embeds:
                if "Welcome to Quetta Tea Corner" in message.embeds[0].title:
                    sticky_message_id = message.id
                    print(f"✅ Found sticky intro message (ID: {sticky_message_id})")
                    break

        if not sticky_message_id:
            embed = discord.Embed(
                title="👋 Welcome to Quetta Tea Corner!",
                description=(
                    "Before you can access the server, please introduce yourself here!\n\n"
                    "**Tell us about:**\n"
                    "• Your name/nickname\n"
                    "• Your age\n"
                    "• Your gender\n"
                    "• Your country/city\n"
                    "• Your interests/hobbies\n\n"
                    "Once a moderator reviews your intro, you'll get the **Verified** role "
                    "and full access to the server! ☕"
                ),
                color=discord.Color.from_rgb(139, 69, 19)
            )
            embed.set_footer(text="Be genuine and friendly! We're excited to meet you.")

            sticky_msg = await intro_channel.send(embed=embed)
            sticky_message_id = sticky_msg.id
            print(f"✅ Created sticky intro message (ID: {sticky_message_id})")

    print(f"\n{'='*50}")
    print("✅ Bot is ready and running!")
    print(f"{'='*50}\n")

@bot.event
async def on_member_join(member):
    """Auto-assign Unverified role (NO welcome message)"""
    unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
    if unverified_role:
        await member.add_roles(unverified_role)
        print(f"✅ Assigned Unverified role to {member.name}")

@bot.event
async def on_message(message):
    global sticky_message_id

    # Ignore bot messages
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
                    "**Tell us about:**\n"
                    "• Your name/nickname\n"
                    "• Your age\n"
                    "• Your gender\n"
                    "• Your country/city\n"
                    "• Your interests/hobbies\n\n"
                    "Once a moderator reviews your intro, you'll get the **Verified** role "
                    "and full access to the server! ☕"
                ),
                color=discord.Color.from_rgb(139, 69, 19)
            )
            embed.set_footer(text="Be genuine and friendly! We're excited to meet you.")

            new_sticky = await message.channel.send(embed=embed)
            sticky_message_id = new_sticky.id
            print(f"📌 Restickied intro message")
        except:
            pass

    await bot.process_commands(message)

# ---------- RUN ----------
bot.run(os.getenv('DISCORD_TOKEN'))