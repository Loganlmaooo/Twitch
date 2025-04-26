import discord
from discord import app_commands
from discord.ext import commands
import threading
import os
import json
import asyncio
import time
from datetime import datetime

from twitch_bot import TwitchBot
from data_manager import DataManager
from utils import format_time, get_emoji_status

# Bot configuration - will be loaded from config.json or environment variables
TOKEN = os.environ.get("DISCORD_TOKEN", "")
GUILD_ID = os.environ.get("DISCORD_GUILD_ID", None)
if GUILD_ID and GUILD_ID.isdigit():
    GUILD_ID = int(GUILD_ID)
else:
    GUILD_ID = None  # Optional: for restricting commands to a specific server

# Store active bots and sessions
active_bots = {}
data_manager = DataManager()

class FarmingClient(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
        # Remove default help command
        self.remove_command('help')
        
    async def setup_hook(self):
        # Load commands
        await self.tree.sync()
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
    
    async def on_ready(self):
        print(f'Bot is ready! Logged in as {self.user}')
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Twitch channels"
        ))


bot = FarmingClient()

# Bot worker function
def bot_worker(channel, user_id):
    """Background thread to monitor and update Twitch bot status"""
    while channel in active_bots and active_bots[channel]["running"]:
        try:
            twitch_bot = active_bots[channel]["bot"]
            
            # Get latest logs and points
            points_gained = twitch_bot.get_gained_points()
            if points_gained > 0:
                active_bots[channel]["points_gained"] += points_gained
            
            log_message = twitch_bot.get_latest_log()
            if log_message:
                timestamp = datetime.now().strftime('%H:%M:%S')
                formatted_log = f"[{timestamp}] {log_message}"
                
                # Store log in memory
                active_bots[channel]["logs"].append(formatted_log)
                
                # Keep only last 100 messages
                if len(active_bots[channel]["logs"]) > 100:
                    active_bots[channel]["logs"] = active_bots[channel]["logs"][-100:]
                
                # Notify user if important message
                if any(keyword in log_message.lower() for keyword in ["error", "claimed", "points", "offline"]):
                    asyncio.run_coroutine_threadsafe(
                        send_status_message(user_id, f"**{channel}**: {formatted_log}"),
                        bot.loop
                    )
            
            # Sleep for a bit
            time.sleep(30)
        except Exception as e:
            print(f"Error in bot worker: {str(e)}")
            break

async def send_status_message(user_id, message):
    """Send a message to a user"""
    try:
        user = await bot.fetch_user(user_id)
        await user.send(message)
    except Exception as e:
        print(f"Failed to send message to user {user_id}: {str(e)}")

# Start farming on a channel
async def start_farming_channel(interaction, channel, username, password):
    """Start farming points on a specific channel"""
    user_id = interaction.user.id
    
    # Check if already farming this channel
    if channel in active_bots and active_bots[channel]["running"]:
        await interaction.followup.send(f"Already farming on channel: {channel}")
        return False
    
    # Create new bot instance
    try:
        twitch_bot = TwitchBot(username, password)
        login_success = twitch_bot.login()
        
        if not login_success:
            await interaction.followup.send("Failed to login to Twitch. Please check your credentials.")
            return False
        
        # Initialize bot data
        active_bots[channel] = {
            "bot": twitch_bot,
            "running": True,
            "start_time": datetime.now(),
            "points_gained": 0,
            "logs": [],
            "user_id": user_id
        }
        
        # Start the actual farming process
        twitch_bot.start_farming(channel)
        
        # Record session start in data manager
        data_manager.start_session(channel)
        
        # Start worker thread
        worker_thread = threading.Thread(
            target=bot_worker,
            args=(channel, user_id)
        )
        worker_thread.daemon = True
        worker_thread.start()
        
        return True
    
    except Exception as e:
        await interaction.followup.send(f"Error starting farming on {channel}: {str(e)}")
        return False

# Stop farming on a channel
async def stop_farming_channel(interaction, channel):
    """Stop farming points on a specific channel"""
    if channel not in active_bots or not active_bots[channel]["running"]:
        await interaction.followup.send(f"Not currently farming on channel: {channel}")
        return False
    
    try:
        # Mark as not running first to stop worker thread
        active_bots[channel]["running"] = False
        
        # Stop the bot
        twitch_bot = active_bots[channel]["bot"]
        twitch_bot.stop_farming()
        
        # Calculate stats
        duration = (datetime.now() - active_bots[channel]["start_time"]).total_seconds() / 60
        points_gained = active_bots[channel]["points_gained"]
        
        # Record session end in data manager
        data_manager.end_session(channel, duration, points_gained)
        
        # Generate summary
        elapsed_time = format_time(duration * 60)
        summary = (
            f"**Farming Summary for {channel}**\n"
            f"Duration: {elapsed_time}\n"
            f"Points Gained: {points_gained}\n"
        )
        
        # Clean up
        del active_bots[channel]
        
        return summary
    
    except Exception as e:
        await interaction.followup.send(f"Error stopping farming on {channel}: {str(e)}")
        return False

# Load bot token from config.json
def load_config():
    global TOKEN, GUILD_ID
    try:
        if os.path.exists("bot_config.json"):
            with open("bot_config.json", "r") as f:
                config = json.load(f)
                TOKEN = config.get("token", "")
                GUILD_ID = config.get("guild_id")
    except Exception as e:
        print(f"Error loading config: {str(e)}")

# Save config
def save_config(token, guild_id=None):
    try:
        config = {
            "token": token,
            "guild_id": guild_id
        }
        with open("bot_config.json", "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {str(e)}")
        return False

#
# Discord Slash Commands
#

@bot.tree.command(name="setup", description="Set up the Discord bot with your token")
@app_commands.describe(token="Your Discord bot token")
@app_commands.describe(guild_id="Optional: Restrict commands to a specific server ID")
async def setup_command(interaction: discord.Interaction, token: str, guild_id: str = None):
    """Set up the Discord bot with your token"""
    await interaction.response.defer(ephemeral=True)
    
    # Convert guild_id to int if provided
    guild_id_int = None
    if guild_id:
        try:
            guild_id_int = int(guild_id)
        except ValueError:
            await interaction.followup.send("Invalid guild ID. Please provide a valid number.")
            return
    
    # Save config
    if save_config(token, guild_id_int):
        await interaction.followup.send("Bot configuration saved. Please restart the bot to apply changes.")
    else:
        await interaction.followup.send("Failed to save configuration.")

@bot.tree.command(name="start", description="Start farming on a Twitch channel")
@app_commands.describe(channel="Twitch channel name")
@app_commands.describe(username="Your Twitch username")
@app_commands.describe(password="Your Twitch password")
async def start_command(interaction: discord.Interaction, channel: str, username: str, password: str):
    """Start farming points on a Twitch channel"""
    # Always defer to avoid timeout, and make it ephemeral to hide user credentials
    await interaction.response.defer(ephemeral=True)
    
    # Clean channel name
    channel = channel.strip().lower()
    
    # Start farming process
    success = await start_farming_channel(interaction, channel, username, password)
    
    if success:
        await interaction.followup.send(f"Started farming on channel: {channel}")
        
        # Send a public confirmation (without credentials)
        if not interaction.response.is_done():
            await interaction.followup.send(
                f"{interaction.user.mention} started farming on {channel}",
                ephemeral=False
            )

@bot.tree.command(name="stop", description="Stop farming on a Twitch channel")
@app_commands.describe(channel="Twitch channel name (or 'all' to stop all)")
async def stop_command(interaction: discord.Interaction, channel: str):
    """Stop farming points on a Twitch channel"""
    await interaction.response.defer()
    
    if channel.lower() == "all":
        if not active_bots:
            await interaction.followup.send("No active farming sessions to stop.")
            return
        
        summaries = []
        channels_to_stop = list(active_bots.keys())
        
        for ch in channels_to_stop:
            summary = await stop_farming_channel(interaction, ch)
            if summary:
                summaries.append(summary)
        
        if summaries:
            await interaction.followup.send("\n\n".join(summaries))
        else:
            await interaction.followup.send("Failed to stop farming sessions.")
    else:
        # Clean channel name
        channel = channel.strip().lower()
        
        # Stop the specific channel
        summary = await stop_farming_channel(interaction, channel)
        
        if summary:
            await interaction.followup.send(summary)

@bot.tree.command(name="status", description="Check farming status")
async def status_command(interaction: discord.Interaction):
    """Check the status of all farming sessions"""
    await interaction.response.defer()
    
    if not active_bots:
        await interaction.followup.send("No active farming sessions.")
        return
    
    status_msg = "**Current Farming Sessions:**\n\n"
    
    for channel, data in active_bots.items():
        duration = (datetime.now() - data["start_time"]).total_seconds()
        duration_formatted = format_time(duration)
        
        status_msg += (
            f"**Channel:** {channel}\n"
            f"**Duration:** {duration_formatted}\n"
            f"**Points gained:** {data['points_gained']}\n"
            f"**Started by:** <@{data['user_id']}>\n\n"
        )
    
    await interaction.followup.send(status_msg)

@bot.tree.command(name="logs", description="Get recent logs for a channel")
@app_commands.describe(channel="Twitch channel name")
@app_commands.describe(count="Number of log entries to show (max 50)")
async def logs_command(interaction: discord.Interaction, channel: str, count: int = 10):
    """Get recent logs for a farming session"""
    await interaction.response.defer()
    
    # Clean channel name
    channel = channel.strip().lower()
    
    # Check if farming this channel
    if channel not in active_bots:
        await interaction.followup.send(f"Not farming on channel: {channel}")
        return
    
    # Limit count
    count = min(count, 50)
    
    # Get logs
    logs = active_bots[channel]["logs"][-count:] if active_bots[channel]["logs"] else []
    
    if not logs:
        await interaction.followup.send(f"No logs available for channel: {channel}")
        return
    
    # Format logs
    logs_text = f"**Recent logs for {channel}:**\n```\n"
    logs_text += "\n".join(logs)
    logs_text += "\n```"
    
    await interaction.followup.send(logs_text)

@bot.tree.command(name="stats", description="View your farming statistics")
async def stats_command(interaction: discord.Interaction):
    """View farming statistics"""
    await interaction.response.defer()
    
    if not data_manager.has_data():
        await interaction.followup.send("No farming data available yet.")
        return
    
    # Get statistics
    total_time = data_manager.get_total_watchtime()
    total_points = data_manager.get_total_points()
    total_sessions = data_manager.get_total_sessions()
    
    # Format time
    time_formatted = format_time(total_time * 60)
    
    # Generate stats message
    stats_msg = (
        "**Twitch Farming Statistics**\n\n"
        f"**Total Watchtime:** {time_formatted}\n"
        f"**Total Points Earned:** {total_points:,}\n"
        f"**Total Sessions:** {total_sessions}\n\n"
    )
    
    # Add channel-specific stats
    channel_stats = data_manager.get_channel_stats()
    if channel_stats:
        stats_msg += "**Points by Channel:**\n"
        for stat in channel_stats:
            channel_time = format_time(stat["watchtime"] * 3600)  # Convert hours to seconds
            stats_msg += f"• **{stat['channel']}**: {stat['points']:,} points ({channel_time})\n"
    
    await interaction.followup.send(stats_msg)

@bot.tree.command(name="help", description="Show bot commands and help")
async def help_command(interaction: discord.Interaction):
    """Show help information about the bot"""
    await interaction.response.defer()
    
    help_text = """
**Twitch Auto-Farmer Discord Bot**

This bot allows you to automatically farm Twitch channel points from Discord.

**Commands:**
• `/setup <token> [guild_id]` - Set up the bot with your Discord token
• `/start <channel> <username> <password>` - Start farming on a channel
• `/stop <channel>` - Stop farming on a channel (use 'all' to stop all)
• `/status` - Check current farming sessions
• `/logs <channel> [count]` - View recent logs for a channel
• `/stats` - View your farming statistics
• `/help` - Show this help message

**Notes:**
• Your Twitch credentials are used only for the login process and are not stored.
• For security, use the commands in a private channel or DM.
"""
    
    await interaction.followup.send(help_text)

# Run the bot if this file is executed directly
if __name__ == "__main__":
    import time
    
    # Load config
    load_config()
    
    if not TOKEN:
        print("No Discord bot token found.")
        print("Please set up the bot with a token first by running:")
        print("  1. Start the bot (it will run with limited functionality)")
        print("  2. Use the /setup command with your bot token")
        print("  3. Restart the bot")
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("Invalid Discord token. Please use /setup to configure the bot.")
    except Exception as e:
        print(f"Error starting bot: {str(e)}")