"""
One-time setup script: creates city roles and sends the city role selection
message in #self-roles.

Run once from the project root:
    .venv/bin/python scripts/setup_city_roles.py

After running, the roles and message will persist. The main bot registers
the CityRoleView on every startup so buttons keep working.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import discord
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

TOKEN = os.getenv("DISCORD_TOKEN")

# City roles: display label → role name
CITY_ROLES = {
    "🔴 Karachite":       "Karachite",
    "🟠 Lahori":          "Lahori",
    "🟡 Faisalabadi":     "Faisalabadi",
    "🟢 Peshawari":       "Peshawari",
    "🔵 Multani":         "Multani",
    "🟣 Islamabadi":      "Islamabadi",
    "⚫ Quettaite":       "Quettaite",
    "⚪ Other":           "Other",
    "🌍 International":   "International",
}


class CityRoleButton(discord.ui.Button):
    def __init__(self, label: str, role_name: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"city_role_{role_name}",
        )
        self.role_name = role_name

    async def callback(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if not role:
            await interaction.response.send_message(
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
            await interaction.response.send_message(
                f"Removed **{self.role_name}** role.", ephemeral=True
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"You're now tagged as **{self.role_name}** ✅", ephemeral=True
            )


class CityRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for label, role_name in CITY_ROLES.items():
            self.add_item(CityRoleButton(label=label, role_name=role_name))


intents = discord.Intents.default()
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)


TARGET_GUILD_NAME = "Quetta Tea Corner ☕"


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

    for guild in client.guilds:
        if guild.name != TARGET_GUILD_NAME:
            print(f"⏭️  Skipping: {guild.name}")
            continue
        print(f"📋 Setting up city roles in: {guild.name}")

        # Create roles that don't exist yet
        existing_role_names = {r.name for r in guild.roles}
        for role_name in CITY_ROLES.values():
            if role_name not in existing_role_names:
                await guild.create_role(name=role_name, reason="City role setup")
                print(f"  ✅ Created role: {role_name}")
            else:
                print(f"  ⏭️  Role already exists: {role_name}")

        # Find #self-roles channel
        self_roles_channel = discord.utils.get(guild.text_channels, name="self-roles")
        if not self_roles_channel:
            print("  ❌ #self-roles channel not found — skipping message send")
            continue

        # Send the city role selection message
        embed = discord.Embed(
            title="🏙️ City Roles",
            description="Select the city you're from! Click again to remove.",
            color=discord.Color.blurple(),
        )
        await self_roles_channel.send(embed=embed, view=CityRoleView())
        print(f"  ✅ Sent city role message in #{self_roles_channel.name}")

    print("\n✅ Setup complete. You can now stop this script.")
    await client.close()


asyncio.run(client.start(TOKEN))
