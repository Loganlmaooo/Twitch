import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, data_file="farming_data.json"):
        self.data_file = data_file
        self.current_session = None
        self.data = self.load_data()
    
    def load_data(self):
        """Load data from the JSON file or create default structure."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "sessions": [],
                    "channels": {},
                    "total_points": 0,
                    "total_watchtime": 0  # in minutes
                }
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return {
                "sessions": [],
                "channels": {},
                "total_points": 0,
                "total_watchtime": 0
            }
    
    def save_data(self):
        """Save data to the JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {str(e)}")
    
    def start_session(self, channel):
        """Start a new farming session."""
        self.current_session = {
            "id": len(self.data["sessions"]) + 1,
            "channel": channel,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration": 0,  # in minutes
            "points": 0
        }
        
        # Initialize channel if not exists
        if channel not in self.data["channels"]:
            self.data["channels"][channel] = {
                "watchtime": 0,  # in minutes
                "points": 0,
                "sessions": 0
            }
        
        self.save_data()
    
    def end_session(self, channel, duration, points):
        """End the current farming session and update statistics."""
        if not self.current_session:
            return
        
        # Update current session
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["duration"] = round(duration, 2)
        self.current_session["points"] = points
        
        # Add to sessions list
        self.data["sessions"].append(self.current_session)
        
        # Update channel statistics
        self.data["channels"][channel]["watchtime"] += duration
        self.data["channels"][channel]["points"] += points
        self.data["channels"][channel]["sessions"] += 1
        
        # Update totals
        self.data["total_points"] += points
        self.data["total_watchtime"] += duration
        
        # Save data
        self.save_data()
        
        # Reset current session
        self.current_session = None
    
    def get_channel_stats(self):
        """Get statistics for all channels."""
        result = []
        
        for channel, stats in self.data["channels"].items():
            result.append({
                "channel": channel,
                "watchtime": round(stats["watchtime"] / 60, 2),  # Convert to hours
                "points": stats["points"],
                "sessions": stats["sessions"]
            })
        
        return result
    
    def get_total_points(self):
        """Get the total points earned."""
        return self.data["total_points"]
    
    def get_total_watchtime(self):
        """Get the total watchtime in hours."""
        return round(self.data["total_watchtime"] / 60, 2)  # Convert to hours
    
    def get_total_sessions(self):
        """Get the total number of sessions."""
        return len(self.data["sessions"])
    
    def get_all_sessions(self):
        """Get all farming sessions."""
        return self.data["sessions"]
    
    def has_data(self):
        """Check if there is any farming data."""
        return len(self.data["sessions"]) > 0
