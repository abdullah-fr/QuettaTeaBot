import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# ---------- BOT SETUP ----------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guild_messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Store recent audit entries to avoid duplicates
processed_entries = set()

# ---------- HELPER FUNCTIONS ----------
async def post_public_notification(user, action_type, reason, guild):
    """Post kick/ban reason in a public channel when DM fails"""
    try:
        # Try to find a suitable channel (in order of preference)
        notification_channel = None

        # Look for specific channels
        for channel_name in ["mod-logs", "logs", "general", "main-door"]:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                notification_channel = channel
                break

        # If no specific channel found, use the first available text channel
        if not notification_channel:
            notification_channel = guild.text_channels[0] if guild.text_channels else None

        if notification_channel:
            action_emoji = "🚪" if action_type == "kick" else "🔨"
            action_word = "kicked" if action_type == "kick" else "banned"

            embed = discord.Embed(
                title=f"{action_emoji} Moderation Action",
                description=f"**{user.name}** ({user.mention}) was {action_word}",
                color=discord.Color.orange() if action_type == "kick" else discord.Color.red()
            )
            embed.add_field(
                name="📝 Reason",
                value=reason if reason else "No reason provided",
                inline=False
            )
            embed.add_field(
                name="ℹ️ Note",
                value=f"This message was posted because {user.name} has DMs disabled.",
                inline=False
            )
            embed.set_footer(text="Moderation notification")
            embed.timestamp = discord.utils.utcnow()

            await notification_channel.send(embed=embed)
            print(f"✅ Posted public notification for {user.name} in #{notification_channel.name}")
        else:
            print(f"❌ No suitable channel found to post notification for {user.name}")

    except Exception as e:
        print(f"❌ Failed to post public notification: {e}")

async def send_dm_with_reason(user, action_type, reason, guild_name, guild):
    """Send DM to user with kick/ban reason, with fallback to public channel"""
    try:
        if action_type == "kick":
            embed = discord.Embed(
                title="🚪 You were kicked from the server",
                description=f"You have been kicked from **{guild_name}**",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="📝 Reason",
                value=reason if reason else "No reason provided",
                inline=False
            )
            embed.add_field(
                name="ℹ️ Note",
                value="You can rejoin the server with a new invite link if you have one.",
                inline=False
            )

        elif action_type == "ban":
            embed = discord.Embed(
                title="🔨 You were banned from the server",
                description=f"You have been banned from **{guild_name}**",
                color=discord.Color.red()
            )
            embed.add_field(
                name="📝 Reason",
                value=reason if reason else "No reason provided",
                inline=False
            )
            embed.add_field(
                name="ℹ️ Note",
                value="This is a permanent ban. You cannot rejoin unless unbanned by a moderator.",
                inline=False
            )

        embed.set_footer(text=f"Action taken in {guild_name}")
        embed.timestamp = discord.utils.utcnow()

        await user.send(embed=embed)
        print(f"✅ Sent {action_type} DM to {user.name} (ID: {user.id})")

    except discord.Forbidden:
        print(f"❌ Cannot DM {user.name} - DMs are disabled")
        # Fallback: Post in public channel
        await post_public_notification(user, action_type, reason, guild)

    except discord.HTTPException as e:
        print(f"❌ Failed to DM {user.name}: {e}")
        # Fallback: Post in public channel
        await post_public_notification(user, action_type, reason, guild)

    except Exception as e:
        print(f"❌ Unexpected error DMing {user.name}: {e}")
        # Fallback: Post in public channel
        await post_public_notification(user, action_type, reason, guild)

async def check_audit_logs(guild):
    """Check recent audit log entries for kicks and bans"""
    try:
        # Check for kicks
        async for entry in guild.audit_logs(action=discord.AuditLogAction.kick, limit=5):
            entry_id = f"kick_{entry.id}"
            if entry_id not in processed_entries:
                processed_entries.add(entry_id)

                # Only process recent entries (within last 30 seconds)
                if (discord.utils.utcnow() - entry.created_at).total_seconds() < 30:
                    await send_dm_with_reason(
                        entry.target,
                        "kick",
                        entry.reason,
                        guild.name,
                        guild
                    )

        # Check for bans
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=5):
            entry_id = f"ban_{entry.id}"
            if entry_id not in processed_entries:
                processed_entries.add(entry_id)

                # Only process recent entries (within last 30 seconds)
                if (discord.utils.utcnow() - entry.created_at).total_seconds() < 30:
                    await send_dm_with_reason(
                        entry.target,
                        "ban",
                        entry.reason,
                        guild.name,
                        guild
                    )

        # Clean up old processed entries (keep only last 100)
        if len(processed_entries) > 100:
            processed_entries.clear()

    except discord.Forbidden:
        print("❌ Bot doesn't have permission to view audit logs")
    except Exception as e:
        print(f"❌ Error checking audit logs: {e}")

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    guild = bot.guilds[0]
    print(f"\n{'='*50}")
    print(f"🤖 Audit DM Bot logged in as {bot.user}")
    print(f"🏰 Server: {guild.name}")
    print(f"📋 Monitoring kicks and bans...")
    print(f"{'='*50}\n")

    # Start audit log monitoring
    bot.loop.create_task(audit_monitor_loop())

@bot.event
async def on_member_remove(member):
    """Triggered when a member leaves (kick or leave)"""
    # Wait a moment for audit log to update
    await asyncio.sleep(2)
    await check_audit_logs(member.guild)

@bot.event
async def on_member_ban(guild, user):
    """Triggered when a member is banned"""
    # Wait a moment for audit log to update
    await asyncio.sleep(2)
    await check_audit_logs(guild)

async def audit_monitor_loop():
    """Continuously monitor audit logs every 10 seconds"""
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            for guild in bot.guilds:
                await check_audit_logs(guild)

            # Wait 10 seconds before next check
            await asyncio.sleep(10)

        except Exception as e:
            print(f"❌ Error in audit monitor loop: {e}")
            await asyncio.sleep(30)  # Wait longer on error

# ---------- COMMANDS (for testing) ----------
@bot.command(name="test_kick_dm")
@commands.has_permissions(kick_members=True)
async def test_kick_dm(ctx, user: discord.User, *, reason="Test kick"):
    """Test command to simulate a kick DM"""
    await send_dm_with_reason(user, "kick", reason, ctx.guild.name, ctx.guild)
    await ctx.send(f"✅ Sent test kick DM to {user.mention}")

@bot.command(name="test_ban_dm")
@commands.has_permissions(ban_members=True)
async def test_ban_dm(ctx, user: discord.User, *, reason="Test ban"):
    """Test command to simulate a ban DM"""
    await send_dm_with_reason(user, "ban", reason, ctx.guild.name, ctx.guild)
    await ctx.send(f"✅ Sent test ban DM to {user.mention}")

@bot.command(name="audit_status")
@commands.has_permissions(manage_guild=True)
async def audit_status(ctx):
    """Check if bot can access audit logs"""
    try:
        # Try to fetch one audit log entry
        async for entry in ctx.guild.audit_logs(limit=1):
            await ctx.send("✅ Bot can access audit logs successfully!")
            break
        else:
            await ctx.send("⚠️ No audit log entries found")
    except discord.Forbidden:
        await ctx.send("❌ Bot doesn't have permission to view audit logs!\nPlease give the bot 'View Audit Log' permission.")
    except Exception as e:
        await ctx.send(f"❌ Error accessing audit logs: {e}")

# ---------- ERROR HANDLING ----------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.UserNotFound):
        await ctx.send("❌ User not found.")
    else:
        print(f"Command error: {error}")

# ---------- RUN ----------
if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))