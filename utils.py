
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1365508833815953518/i6QoxKXSD75Yp-F1zmeVEga1K_DKt3J4xAOdMe_TGWXjWPmBkAbhCB9l4dyfoQtC7Yl8"

def format_time(seconds):
    """Format seconds into HH:MM:SS format."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_emoji_status(is_running):
    """Get an emoji representing the bot status."""
    return "🟢" if is_running else "🔴"

def send_webhook_log(message):
    """Send a log message to Discord webhook."""
    try:
        est_time = datetime.now(ZoneInfo("America/New_York"))
        formatted_time = est_time.strftime("%I:%M:%S %p EST")
        
        data = {
            "username": "Twitch Channel Points Pro",
            "avatar_url": "https://static-cdn.jtvnw.net/points-packages/points-500.png",
            "embeds": [{
                "title": "📊 Channel Points Analytics",
                "description": f"```diff\n+ {formatted_time}\n{message}```",
                "color": 0xF0C43F,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "footer": {
                    "text": "Twitch Channel Points Pro™ Enterprise Edition",
                    "icon_url": "https://static-cdn.jtvnw.net/custom-reward-images/default-4.png"
                },
                "thumbnail": {
                    "url": "https://static-cdn.jtvnw.net/points-packages/points-100000.png"
                }
            }]
        }
        
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Error sending webhook: {str(e)}")
