#!/usr/bin/env python3

"""
Twitch Auto-Farmer Discord Bot
Run this script to start the Discord bot for controlling Twitch auto-farming.
"""

import os
import sys
from discord_bot import bot, load_config, TOKEN

if __name__ == "__main__":
    # Load the bot configuration
    load_config()
    
    # Check if token is available
    if not TOKEN:
        print("Discord bot token not found.")
        print("Please set up the bot with a valid token first.")
        print("After starting the bot, use the /setup command to configure it.")
    
    # Run the bot
    try:
        print("Starting Discord bot...")
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error starting Discord bot: {str(e)}")
        sys.exit(1)