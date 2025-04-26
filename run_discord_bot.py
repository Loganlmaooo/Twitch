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
    """Continuously check for a token file and return the token when available."""
    while True:
        # Load the bot configuration
        load_config()

        # Check for token in bot_config.json
        if os.path.exists("bot_config.json"):
            try:
                with open("bot_config.json", "r") as f:
                    config = json.load(f)
                    token = config.get("token", "")
                    if token and token.strip():
                        print("Discord bot token found in configuration file.")
                        return token
            except Exception as e:
                print(f"Error reading token file: {str(e)}")

        # Check for environment variable as fallback
        env_token = os.environ.get("DISCORD_TOKEN", "")
        if env_token and env_token.strip():
            print("Discord bot token found in environment variables.")
            return env_token

        print("Discord bot token not found. Waiting for token to be configured...")
        print("Please use the Streamlit dashboard to set up your Discord bot token.")
        print("The bot will automatically start once a token is provided.")
        time.sleep(30)

if __name__ == "__main__":
    while True:
        try:
            # Get token
            token = check_token_file()

            if token:
                print("Starting Discord bot...")
                bot.run(token)
            else:
                print("No token available, waiting...")
                time.sleep(30)

        except Exception as e:
            print(f"Error running Discord bot: {str(e)}")
            print("Restarting in 30 seconds...")
            time.sleep(30)