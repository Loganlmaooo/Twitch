"""
Channel Manager for the Twitch Auto-Farmer
Handles channel recommendations, scheduling, and advanced channel management
"""

import os
import json
import random
from datetime import datetime, time, timedelta
import streamlit as st
import pandas as pd
import requests

# Channel data file
CHANNEL_DATA_FILE = "channel_data.json"

class ChannelManager:
    def __init__(self):
        """Initialize the channel manager"""
        self.channel_data = self.load_channel_data()
        
    def load_channel_data(self):
        """Load channel data from file"""
        if os.path.exists(CHANNEL_DATA_FILE):
            try:
                with open(CHANNEL_DATA_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading channel data: {str(e)}")
        
        # Default data
        return {
            "channels": {},
            "recommendations": [],
            "schedules": {},
            "last_update": None
        }
    
    def save_channel_data(self):
        """Save channel data to file"""
        try:
            with open(CHANNEL_DATA_FILE, "w") as f:
                json.dump(self.channel_data, f, indent=4)
        except Exception as e:
            print(f"Error saving channel data: {str(e)}")
    
    def update_channel_stats(self, channel, points_earned=0, online=False):
        """Update stats for a channel"""
        if channel not in self.channel_data["channels"]:
            # Initialize new channel
            self.channel_data["channels"][channel] = {
                "points_earned": 0,
                "sessions": 0,
                "online_history": [],
                "point_rate": 0,
                "last_online": None,
                "tags": [],
                "schedule": {}
            }
        
        # Update stats
        if points_earned > 0:
            self.channel_data["channels"][channel]["points_earned"] += points_earned
            self.channel_data["channels"][channel]["sessions"] += 1
        
        # Update online status
        current_time = datetime.now().isoformat()
        
        if online:
            self.channel_data["channels"][channel]["last_online"] = current_time
            
            # Add to online history (max 24 hours)
            self.channel_data["channels"][channel]["online_history"].append({
                "timestamp": current_time,
                "online": True
            })
        else:
            # Add to online history
            self.channel_data["channels"][channel]["online_history"].append({
                "timestamp": current_time,
                "online": False
            })
        
        # Limit history to 100 entries
        if len(self.channel_data["channels"][channel]["online_history"]) > 100:
            self.channel_data["channels"][channel]["online_history"] = \
                self.channel_data["channels"][channel]["online_history"][-100:]
        
        # Calculate point rate (points per hour)
        if self.channel_data["channels"][channel]["sessions"] > 0:
            total_points = self.channel_data["channels"][channel]["points_earned"]
            total_sessions = self.channel_data["channels"][channel]["sessions"]
            
            # Estimate 50 points per hour on average if we don't have enough data
            estimated_hours = total_sessions * 0.5  # Assume average session is 30 minutes
            point_rate = total_points / max(estimated_hours, 1)
            
            self.channel_data["channels"][channel]["point_rate"] = point_rate
        
        # Save updated data
        self.channel_data["last_update"] = current_time
        self.save_channel_data()
    
    def get_channel_recommendations(self, count=3):
        """Get recommended channels based on potential point earnings"""
        # Update recommendations if it's been a while
        should_update = True
        if self.channel_data["last_update"]:
            last_update = datetime.fromisoformat(self.channel_data["last_update"])
            if (datetime.now() - last_update).total_seconds() < 3600:  # 1 hour
                should_update = False
        
        if should_update or not self.channel_data["recommendations"]:
            self._update_recommendations()
        
        # Return top recommendations
        return self.channel_data["recommendations"][:count]
    
    def _update_recommendations(self):
        """Update channel recommendations using Twitch API or top streamers list"""
        try:
            # In a real implementation, this would use the Twitch API
            # For now, we'll use a list of popular channels as a fallback
            popular_channels = [
                "xQc", "Ninja", "pokimane", "shroud", "NICKMERCS",
                "TimTheTatman", "DrLupo", "summit1g", "Myth", "DrDisrespect",
                "sodapoppin", "Tfue", "Asmongold", "HasanAbi", "Ludwig",
                "moistcr1tikal", "Mizkif", "loltyler1", "Sykkuno", "Valkyrae"
            ]
            
            # Filter out channels we're already farming
            existing_channels = list(self.channel_data["channels"].keys())
            available_channels = [c for c in popular_channels if c not in existing_channels]
            
            # Randomly select channels and assign estimated point rates
            recommendations = []
            for channel in random.sample(available_channels, min(10, len(available_channels))):
                point_rate = random.randint(60, 120)  # Random estimate between 60-120 points/hour
                recommendations.append({
                    "channel": channel,
                    "estimated_point_rate": point_rate,
                    "reason": "Popular streamer with active chat"
                })
            
            # Sort by point rate
            recommendations.sort(key=lambda x: x["estimated_point_rate"], reverse=True)
            
            # Save recommendations
            self.channel_data["recommendations"] = recommendations
            self.save_channel_data()
        except Exception as e:
            print(f"Error updating recommendations: {str(e)}")
    
    def set_channel_schedule(self, channel, schedule):
        """Set a farming schedule for a channel"""
        if channel not in self.channel_data["channels"]:
            self.update_channel_stats(channel)  # Initialize channel
        
        # Save schedule
        self.channel_data["channels"][channel]["schedule"] = schedule
        self.channel_data["schedules"][channel] = schedule
        self.save_channel_data()
    
    def get_channels_to_farm_now(self):
        """Get channels that should be farmed now based on schedules"""
        current_time = datetime.now()
        current_weekday = current_time.strftime("%A").lower()
        current_hour = current_time.hour
        
        channels_to_farm = []
        for channel, schedule in self.channel_data.get("schedules", {}).items():
            # Check if channel should be farmed on this day
            if schedule.get(current_weekday, False):
                # Check if channel should be farmed at this hour
                start_hour = schedule.get("start_hour", 0)
                end_hour = schedule.get("end_hour", 23)
                
                if start_hour <= current_hour <= end_hour:
                    channels_to_farm.append(channel)
        
        return channels_to_farm
    
    def add_channel_tag(self, channel, tag):
        """Add a tag to a channel"""
        if channel not in self.channel_data["channels"]:
            self.update_channel_stats(channel)  # Initialize channel
        
        if tag not in self.channel_data["channels"][channel]["tags"]:
            self.channel_data["channels"][channel]["tags"].append(tag)
            self.save_channel_data()
    
    def remove_channel_tag(self, channel, tag):
        """Remove a tag from a channel"""
        if channel in self.channel_data["channels"]:
            if tag in self.channel_data["channels"][channel]["tags"]:
                self.channel_data["channels"][channel]["tags"].remove(tag)
                self.save_channel_data()
    
    def render_channel_recommendations(self):
        """Render channel recommendations in Streamlit"""
        st.subheader("Recommended Channels")
        
        recommendations = self.get_channel_recommendations(count=5)
        
        if not recommendations:
            st.info("No channel recommendations available.")
            return
        
        # Display recommendations
        for i, rec in enumerate(recommendations):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            col1.write(f"**{rec['channel']}**")
            col2.write(f"~{rec['estimated_point_rate']} points/hour")
            
            if col3.button("Start Farming", key=f"rec_start_{i}"):
                # Set values in session state for the main app to use
                st.session_state.new_channel = rec['channel']
                st.session_state.start_recommended = True
                st.rerun()
            
            # Show reason as a tooltip/info
            st.caption(f"💡 {rec['reason']}")
            
            if i < len(recommendations) - 1:
                st.markdown("---")
    
    def render_channel_scheduling(self):
        """Render channel scheduling UI in Streamlit"""
        st.subheader("Advanced Scheduling")
        
        # Get existing channels
        existing_channels = list(self.channel_data["channels"].keys())
        if not existing_channels:
            existing_channels = [""]
        
        # Select channel
        selected_channel = st.selectbox("Select Channel", 
                                      options=existing_channels,
                                      index=0,
                                      help="Select a channel to schedule")
        
        if not selected_channel:
            st.info("Please add channels to use scheduling.")
            return
        
        # Get current schedule
        current_schedule = {}
        if selected_channel in self.channel_data.get("schedules", {}):
            current_schedule = self.channel_data["schedules"][selected_channel]
        
        # Days of week
        st.write("Farm on these days:")
        
        days_cols = st.columns(7)
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_selected = {}
        
        for i, day in enumerate(days):
            day_selected[day] = days_cols[i].checkbox(
                day.capitalize()[:3], 
                value=current_schedule.get(day, True),
                key=f"day_{day}"
            )
        
        # Time range
        st.write("Farm during these hours:")
        
        time_cols = st.columns(2)
        with time_cols[0]:
            start_hour = st.slider(
                "Start Hour", 
                min_value=0, 
                max_value=23, 
                value=current_schedule.get("start_hour", 0),
                help="Hour to start farming (24-hour format)"
            )
        
        with time_cols[1]:
            end_hour = st.slider(
                "End Hour", 
                min_value=0, 
                max_value=23, 
                value=current_schedule.get("end_hour", 23),
                help="Hour to stop farming (24-hour format)"
            )
        
        # Save schedule button
        if st.button("Save Schedule"):
            # Create schedule dictionary
            schedule = {
                "monday": day_selected["monday"],
                "tuesday": day_selected["tuesday"],
                "wednesday": day_selected["wednesday"],
                "thursday": day_selected["thursday"],
                "friday": day_selected["friday"],
                "saturday": day_selected["saturday"],
                "sunday": day_selected["sunday"],
                "start_hour": start_hour,
                "end_hour": end_hour
            }
            
            # Save schedule
            self.set_channel_schedule(selected_channel, schedule)
            
            st.success(f"Schedule saved for {selected_channel}")
    
    def render_drag_drop_channels(self, active_channels):
        """Render drag and drop channel management UI in Streamlit"""
        st.subheader("Channel Management")
        
        # This is just a mockup since actual drag and drop requires JavaScript
        # which is out of scope for this implementation
        
        if not active_channels:
            st.info("No active channels to manage.")
            return
        
        st.write("Drag and drop channels to reorder them:")
        
        # Create a list view with up/down arrows as a simulation
        for i, channel in enumerate(active_channels):
            col1, col2, col3 = st.columns([5, 1, 1])
            
            # Channel info
            col1.write(f"**{i+1}. {channel}**")
            
            # Move up button (disabled for first item)
            up_disabled = (i == 0)
            if col2.button("⬆️", disabled=up_disabled, key=f"up_{i}"):
                # Swap with previous item
                if i > 0:
                    active_channels[i], active_channels[i-1] = active_channels[i-1], active_channels[i]
                    # In a real app, you would save this order
                    st.rerun()
            
            # Move down button (disabled for last item)
            down_disabled = (i == len(active_channels) - 1)
            if col3.button("⬇️", disabled=down_disabled, key=f"down_{i}"):
                # Swap with next item
                if i < len(active_channels) - 1:
                    active_channels[i], active_channels[i+1] = active_channels[i+1], active_channels[i]
                    # In a real app, you would save this order
                    st.rerun()
            
            # Channel tags
            if channel in self.channel_data["channels"]:
                tags = self.channel_data["channels"][channel].get("tags", [])
                if tags:
                    tags_html = ""
                    for tag in tags:
                        tags_html += f'<span style="background-color:#9146FF; color:white; padding:2px 8px; border-radius:10px; margin-right:5px; font-size:0.8em;">{tag}</span>'
                    st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tag management
        st.subheader("Channel Tags")
        
        selected_channel = st.selectbox("Select Channel for Tags", 
                                      options=active_channels,
                                      index=0,
                                      help="Select a channel to manage tags")
        
        # Current tags
        current_tags = []
        if selected_channel in self.channel_data["channels"]:
            current_tags = self.channel_data["channels"][selected_channel].get("tags", [])
        
        st.write("Current tags:")
        if current_tags:
            tags_cols = st.columns(3)
            for i, tag in enumerate(current_tags):
                col = tags_cols[i % 3]
                if col.button(f"❌ {tag}", key=f"remove_tag_{i}"):
                    self.remove_channel_tag(selected_channel, tag)
                    st.rerun()
        else:
            st.write("No tags")
        
        # Add new tag
        new_tag = st.text_input("Add a new tag", key="new_tag")
        
        if st.button("Add Tag"):
            if new_tag:
                self.add_channel_tag(selected_channel, new_tag)
                st.session_state.new_tag = ""
                st.rerun()
            else:
                st.error("Please enter a tag name")

# Global instance
channel_manager = ChannelManager()