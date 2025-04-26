#!/usr/bin/env python3

"""
Twitch Auto-Farmer Discord Bot
Run this script to start the Discord bot for controlling Twitch auto-farming.
"""

import os
import json
import time
from discord_bot import bot, load_config

def check_token_file():
    """Check for a valid Discord token."""
    # Load the bot configuration
    load_config()
    
    # First check environment variable
    env_token = os.environ.get("DISCORD_TOKEN", "").strip()
    if env_token:
        print("Using Discord token from environment variables")
        return env_token
        
    # Fallback to config file
    if os.path.exists("bot_config.json"):
        try:
            with open("bot_config.json", "r") as f:
                config = json.load(f)
                token = config.get("token", "").strip()
                if token:
                    print("Using Discord token from config file")
                    return token
        except Exception as e:
            print(f"Error reading config file: {str(e)}")
    
    print("No valid Discord token found!")
    print("Please set the DISCORD_TOKEN environment variable")
    return None

if __name__ == "__main__":
    token = check_token_file()
    if not token:
        print("Exiting due to missing Discord token")
        exit(1)
        
    print("Starting Discord bot...")
    try:
        bot.run(token)
    except Exception as e:
        print(f"Fatal error running Discord bot: {str(e)}")
        exit(1)