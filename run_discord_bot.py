#!/usr/bin/env python3

"""
Twitch Auto-Farmer Discord Bot
Run this script to start the Discord bot for controlling Twitch auto-farming.
"""

import os
import sys
from discord_bot import bot, load_config, TOKEN

if __name__ == "__main__":
    # Load the bot configuration from file (config overrides environment variables if file exists)
    load_config()
    
    # Check for environment variable if no file config
    discord_token = os.environ.get("DISCORD_TOKEN", TOKEN)
    
    # Check if token is available
    if not discord_token:
        print("Discord bot token not found.")
        print("Please set up the bot with a valid token first.")
        print("After starting the bot, use the /setup command to configure it.")
        print("For hosting on Render.com, set the DISCORD_TOKEN environment variable.")
    
    # Run the bot
    try:
        print("Starting Discord bot...")
        bot.run(discord_token)
    except Exception as e:
        print(f"Error starting Discord bot: {str(e)}")
        sys.exit(1)