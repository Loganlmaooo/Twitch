
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
