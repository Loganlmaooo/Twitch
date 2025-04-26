
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def format_time(seconds):
    """Format seconds into HH:MM:SS format."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_emoji_status(is_running):
    """Get an emoji representing the bot status."""
    return "🟢" if is_running else "🔴"

def send_discord_webhook(message, webhook_url, username="Twitch Channel Points Pro", color=0xF0C43F):
    """Send a message to a Discord webhook with luxury formatting."""
    try:
        est_time = datetime.now(ZoneInfo("America/New_York"))
        formatted_time = est_time.strftime("%I:%M:%S %p EST")
        
        data = {
            "username": username,
            "avatar_url": "https://static-cdn.jtvnw.net/points-packages/points-500.png",
            "embeds": [
                {
                    "title": "📊 Channel Points Analytics",
                    "description": f"```diff\n+ {formatted_time}\n{message}```",
                    "color": color,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "footer": {
                        "text": "Twitch Channel Points Pro™ Enterprise Edition",
                        "icon_url": "https://static-cdn.jtvnw.net/custom-reward-images/default-4.png"
                    },
                    "thumbnail": {
                        "url": "https://static-cdn.jtvnw.net/points-packages/points-100000.png"
                    }
                }
            ]
        }
        
        response = requests.post(webhook_url, json=data)
        return response.status_code == 204
        
    except Exception as e:
        print(f"Error sending Discord webhook: {str(e)}")
        return False
