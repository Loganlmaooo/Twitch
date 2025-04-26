"""
Notification Manager for the Twitch Auto-Farmer
Handles SMS notifications through Twilio and in-app notifications
"""

import os
import json
from datetime import datetime
from twilio.rest import Client
import streamlit as st

# Notification settings file
NOTIFICATION_SETTINGS_FILE = "notification_settings.json"

class NotificationManager:
    def __init__(self):
        """Initialize the notification manager"""
        self.twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.twilio_phone = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Debug logging for credential detection
        print("Twilio Credentials Status:")
        print(f"Account SID present: {bool(self.twilio_sid)}")
        print(f"Auth Token present: {bool(self.twilio_token)}")
        print(f"Phone Number present: {bool(self.twilio_phone)}")
        
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Load notification settings from file"""
        if os.path.exists(NOTIFICATION_SETTINGS_FILE):
            try:
                with open(NOTIFICATION_SETTINGS_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading notification settings: {str(e)}")
        
        # Default settings
        return {
            "enabled": False,
            "phone_number": "",
            "notify_on_milestone": True,
            "notify_on_offline": True,
            "notify_on_bonus": True,
            "milestone_interval": 1000,  # Points
            "last_milestone": {},  # Per channel milestone tracking
            "in_app_notifications": True,
            "notification_history": []
        }
    
    def save_settings(self):
        """Save notification settings to file"""
        try:
            with open(NOTIFICATION_SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving notification settings: {str(e)}")
    
    def send_sms(self, message):
        """Send an SMS notification using Twilio"""
        if not self.settings.get("enabled", False) or not self.settings.get("phone_number"):
            return False
        
        if not all([self.twilio_sid, self.twilio_token, self.twilio_phone]):
            print("Twilio credentials not configured")
            return False
        
        try:
            client = Client(self.twilio_sid, self.twilio_token)
            message = client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=self.settings["phone_number"]
            )
            print(f"SMS sent with SID: {message.sid}")
            
            # Add to notification history
            self.add_to_history("sms", message)
            
            return True
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            return False
    
    def send_in_app(self, message, level="info"):
        """Send an in-app notification (will be shown in the UI)"""
        if not self.settings.get("in_app_notifications", True):
            return
        
        # Add to notification history
        self.add_to_history("in_app", message, level)
    
    def add_to_history(self, type, message, level="info"):
        """Add a notification to the history"""
        notification = {
            "type": type,
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to beginning of list (newest first)
        self.settings["notification_history"].insert(0, notification)
        
        # Limit history to 100 items
        if len(self.settings["notification_history"]) > 100:
            self.settings["notification_history"] = self.settings["notification_history"][:100]
        
        # Save updated settings
        self.save_settings()
    
    def check_milestone(self, channel, current_points):
        """Check if a point milestone has been reached and send notification if needed"""
        if not self.settings.get("notify_on_milestone", True):
            return
        
        # Initialize channel tracking if not exists
        if channel not in self.settings["last_milestone"]:
            self.settings["last_milestone"][channel] = 0
        
        # Get last milestone for this channel
        last_milestone = self.settings["last_milestone"][channel]
        milestone_interval = self.settings.get("milestone_interval", 1000)
        
        # Check if milestone reached
        current_milestone = (current_points // milestone_interval) * milestone_interval
        if current_milestone > last_milestone:
            # Update last milestone
            self.settings["last_milestone"][channel] = current_milestone
            self.save_settings()
            
            # Send notifications
            message = f"🎉 Milestone reached! You've earned {current_milestone} points on {channel}!"
            
            # Send SMS if enabled
            if self.settings.get("enabled", False):
                self.send_sms(message)
            
            # Send in-app notification
            self.send_in_app(message, "success")
            
            return True
        
        return False
    
    def notify_stream_offline(self, channel):
        """Send notification when a stream goes offline"""
        if not self.settings.get("notify_on_offline", True):
            return
        
        message = f"📴 The stream for {channel} has gone offline."
        
        # Send SMS if enabled
        if self.settings.get("enabled", False):
            self.send_sms(message)
        
        # Send in-app notification
        self.send_in_app(message, "warning")
    
    def notify_bonus_claimed(self, channel, points):
        """Send notification when bonus points are claimed"""
        if not self.settings.get("notify_on_bonus", True):
            return
        
        message = f"💰 Claimed {points} bonus points on {channel}!"
        
        # Only send as in-app notification to avoid SMS spam
        self.send_in_app(message, "info")
    
    def render_settings_ui(self):
        """Render the notification settings UI in Streamlit"""
        st.subheader("Notification Settings")
        
        # Show SMS configuration status
        if all([self.twilio_sid, self.twilio_token, self.twilio_phone]):
            st.success("SMS notifications are available")
        else:
            st.error("SMS notifications are not configured")
            
        # Enable/disable notifications
        enabled = st.toggle("Enable SMS Notifications", 
                          value=self.settings.get("enabled", True),
                          help="Enable SMS notifications for important events")
        
        # Phone number input
        phone = st.text_input("Your Phone Number", 
                            value=self.settings.get("phone_number", ""),
                            help="Enter your phone number with country code (e.g., +1234567890)")
        
        # Notification preferences
        col1, col2 = st.columns(2)
        with col1:
            notify_milestone = st.checkbox("Notify on Point Milestones", 
                                        value=self.settings.get("notify_on_milestone", True))
            notify_offline = st.checkbox("Notify when Stream Offline", 
                                        value=self.settings.get("notify_on_offline", True))
        
        with col2:
            notify_bonus = st.checkbox("Notify on Bonus Points (In-app only)", 
                                     value=self.settings.get("notify_on_bonus", True))
            in_app = st.checkbox("Enable In-app Notifications", 
                               value=self.settings.get("in_app_notifications", True))
        
        # Milestone interval
        milestone_interval = st.number_input("Point Milestone Interval",
                                           min_value=100,
                                           max_value=10000,
                                           value=self.settings.get("milestone_interval", 1000),
                                           step=100,
                                           help="You'll receive notifications when your points reach multiples of this value")
        
        # Save button
        if st.button("Save Notification Settings"):
            # Update settings
            self.settings["enabled"] = enabled
            self.settings["phone_number"] = phone
            self.settings["notify_on_milestone"] = notify_milestone
            self.settings["notify_on_offline"] = notify_offline
            self.settings["notify_on_bonus"] = notify_bonus
            self.settings["in_app_notifications"] = in_app
            self.settings["milestone_interval"] = milestone_interval
            
            # Save settings
            self.save_settings()
            
            # Show success message
            st.success("Notification settings saved!")
            
            # Test notification
            if enabled and phone:
                if st.button("Send Test SMS"):
                    success = self.send_sms("This is a test notification from your Twitch Auto-Farmer!")
                    if success:
                        st.success("Test SMS sent successfully!")
                    else:
                        st.error("Failed to send test SMS. Please check your credentials and phone number.")
    
    def render_notification_history(self):
        """Render the notification history in Streamlit"""
        st.subheader("Notification History")
        
        # Check if there are any notifications
        if not self.settings.get("notification_history", []):
            st.info("No notifications yet.")
            return
        
        # Display notifications
        for notification in self.settings.get("notification_history", [])[:10]:  # Show last 10
            timestamp = datetime.fromisoformat(notification["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            message = notification["message"]
            level = notification["level"]
            type_icon = "📱" if notification["type"] == "sms" else "💬"
            
            # Format based on level
            if level == "success":
                st.success(f"{type_icon} {timestamp}: {message}")
            elif level == "warning":
                st.warning(f"{type_icon} {timestamp}: {message}")
            elif level == "error":
                st.error(f"{type_icon} {timestamp}: {message}")
            else:
                st.info(f"{type_icon} {timestamp}: {message}")
        
        # Show button to clear history
        if st.button("Clear Notification History"):
            self.settings["notification_history"] = []
            self.save_settings()
            st.success("Notification history cleared!")
            st.rerun()

# Global instance
notification_manager = NotificationManager()