import requests
from datetime import datetime

def format_time(seconds):
    """Format seconds into HH:MM:SS format."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_emoji_status(is_running):
    """Get an emoji representing the bot status."""
    return "🟢" if is_running else "🔴"

def send_discord_webhook(message, webhook_url, username="Twitch Auto-Farmer", color=0x9146FF):
    """Send a message to a Discord webhook."""
    try:
        data = {
            "username": username,
            "embeds": [
                {
                    "title": "Twitch Auto-Farmer Log",
                    "description": message,
                    "color": color,
                    "timestamp": datetime.now().isoformat(),
                    "footer": {
                        "text": "Twitch Auto-Farmer Bot"
                    }
                }
            ]
        }
        
        response = requests.post(webhook_url, json=data)
        
        if response.status_code == 204:
            return True
        else:
            print(f"Failed to send Discord webhook: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error sending Discord webhook: {str(e)}")
        return False
