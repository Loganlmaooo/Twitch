#!/usr/bin/env python3

"""
Twitch Auto-Farmer Discord Bot
Run this script to start the Discord bot for controlling Twitch auto-farming.
"""

import os
import sys
import time
import json
from discord_bot import bot, load_config, TOKEN

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
        # Wait for a bit before checking again
        time.sleep(30)

if __name__ == "__main__":
    print("Starting Discord bot worker...")
    
    # Wait for token to be available (either from file or environment variable)
    token = check_token_file()
    
    # Run the bot with the token
    try:
        print("Starting Discord bot with the provided token...")
        bot.run(token)
    except Exception as e:
        print(f"Error starting Discord bot: {str(e)}")
        
        # If the token is invalid, clear it from memory and wait for a new one
        print("Token appears to be invalid. Waiting for a new token...")
        
        # Continuously retry with new tokens
        while True:
            try:
                # Wait 60 seconds before checking for a new token
                time.sleep(60)
                token = check_token_file()
                print("Attempting to start bot with new token...")
                bot.run(token)
                break  # If successful, exit the loop
            except Exception as e:
                print(f"Error starting Discord bot: {str(e)}")
                print("Waiting for a valid token...")