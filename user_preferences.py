"""
User Preferences Manager for the Twitch Auto-Farmer
Handles theme settings, UI preferences, and other user customization options
"""

import os
import json
import streamlit as st

# User preferences file
USER_PREFERENCES_FILE = "user_preferences.json"

# Available themes
AVAILABLE_THEMES = {
    "Default": {
        "primary_color": "#9146FF",  # Twitch purple
        "background_color": "#0E1117",
        "text_color": "#FFFFFF",
        "accent_color": "#FF9900"
    },
    "Dark Mode": {
        "primary_color": "#9146FF",
        "background_color": "#000000",
        "text_color": "#F0F0F0",
        "accent_color": "#FF9900"
    },
    "Light Mode": {
        "primary_color": "#9146FF",
        "background_color": "#F7F7F7",
        "text_color": "#000000",
        "accent_color": "#FF9900"
    },
    "Hacker": {
        "primary_color": "#00FF00",
        "background_color": "#0A0A0A",
        "text_color": "#00FF00",
        "accent_color": "#FF0000"
    },
    "Ocean": {
        "primary_color": "#0077CC",
        "background_color": "#0A2A3F",
        "text_color": "#FFFFFF",
        "accent_color": "#00CCFF"
    },
    "Sunset": {
        "primary_color": "#FF5500",
        "background_color": "#2C1430",
        "text_color": "#FFFFFF",
        "accent_color": "#FFCC00"
    },
    "Custom": {
        "primary_color": "#9146FF",
        "background_color": "#0E1117",
        "text_color": "#FFFFFF",
        "accent_color": "#FF9900"
    }
}

# Achievement badges
ACHIEVEMENT_BADGES = {
    "Point Collector": {
        "description": "Earn your first 5,000 points",
        "requirement": {"type": "total_points", "value": 5000},
        "icon": "🏆",
        "color": "#FFD700"
    },
    "Channel Hopper": {
        "description": "Farm from 3 different channels",
        "requirement": {"type": "unique_channels", "value": 3},
        "icon": "🦘",
        "color": "#4CAF50"
    },
    "Marathon Farmer": {
        "description": "Farm for 24 hours total",
        "requirement": {"type": "total_watchtime", "value": 24},
        "icon": "⏱️",
        "color": "#2196F3"
    },
    "Night Owl": {
        "description": "Farm between midnight and 5am",
        "requirement": {"type": "night_farming", "value": True},
        "icon": "🦉",
        "color": "#673AB7"
    },
    "Bonus Hunter": {
        "description": "Claim 10 bonus point drops",
        "requirement": {"type": "bonus_claims", "value": 10},
        "icon": "💰",
        "color": "#FFC107"
    },
    "Twitch Master": {
        "description": "Earn 100,000 total points",
        "requirement": {"type": "total_points", "value": 100000},
        "icon": "👑",
        "color": "#9C27B0"
    }
}

class UserPreferences:
    def __init__(self):
        """Initialize the user preferences manager"""
        self.preferences = self.load_preferences()
        self.achievements = self.check_achievements()
        
    def load_preferences(self):
        """Load user preferences from file"""
        if os.path.exists(USER_PREFERENCES_FILE):
            try:
                with open(USER_PREFERENCES_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading user preferences: {str(e)}")
        
        # Default preferences
        return {
            "theme": "Default",
            "custom_theme": {
                "primary_color": "#9146FF",
                "background_color": "#0E1117",
                "text_color": "#FFFFFF",
                "accent_color": "#FF9900"
            },
            "show_tutorial": True,
            "tutorial_completed": False,
            "dragdrop_enabled": True,
            "show_recommendations": True,
            "animated_badges": True,
            "achievements": {},
            "multiple_accounts": []
        }
    
    def save_preferences(self):
        """Save user preferences to file"""
        try:
            with open(USER_PREFERENCES_FILE, "w") as f:
                json.dump(self.preferences, f, indent=4)
        except Exception as e:
            print(f"Error saving user preferences: {str(e)}")
    
    def get_theme(self):
        """Get the current theme settings"""
        theme_name = self.preferences.get("theme", "Default")
        
        if theme_name == "Custom":
            return self.preferences.get("custom_theme", AVAILABLE_THEMES["Default"])
        else:
            return AVAILABLE_THEMES.get(theme_name, AVAILABLE_THEMES["Default"])
    
    def apply_theme(self):
        """Apply the current theme to Streamlit"""
        theme = self.get_theme()
        
        # Apply theme using Streamlit's page config and CSS hack
        st.markdown(f"""
        <style>
            :root {{
                --primary-color: {theme['primary_color']};
                --background-color: {theme['background_color']};
                --text-color: {theme['text_color']};
                --accent-color: {theme['accent_color']};
            }}
            .stApp {{
                background-color: var(--background-color);
                color: var(--text-color);
            }}
            .stButton>button {{
                background-color: var(--primary-color);
                color: white;
            }}
            .stProgress .st-bo {{
                background-color: var(--primary-color);
            }}
            .stTabs [data-baseweb="tab-list"] {{
                background-color: var(--background-color);
            }}
            .stTabs [data-baseweb="tab"] {{
                color: var(--text-color);
            }}
            .stTabs [aria-selected="true"] {{
                background-color: var(--primary-color);
                color: white;
            }}
        </style>
        """, unsafe_allow_html=True)
    
    def check_achievements(self):
        """Check which achievements have been unlocked"""
        # This would normally use the data_manager to get stats
        # For now, just return what's in the preferences file
        return self.preferences.get("achievements", {})
    
    def unlock_achievement(self, achievement_id):
        """Unlock a new achievement"""
        if achievement_id not in self.preferences["achievements"]:
            # Mark as newly unlocked
            self.preferences["achievements"][achievement_id] = {
                "unlocked_at": "NOW",  # This would normally be a timestamp
                "new": True
            }
            self.save_preferences()
            return True
        return False
    
    def render_theme_settings(self):
        """Render the theme settings UI in Streamlit"""
        st.subheader("Dashboard Appearance")
        
        # Theme selector
        current_theme = self.preferences.get("theme", "Default")
        theme_names = list(AVAILABLE_THEMES.keys())
        
        selected_theme = st.selectbox("Color Theme", 
                                    options=theme_names,
                                    index=theme_names.index(current_theme),
                                    help="Choose a color theme for your dashboard")
        
        # Custom theme editor
        if selected_theme == "Custom":
            st.write("Customize your theme colors:")
            custom_theme = self.preferences.get("custom_theme", AVAILABLE_THEMES["Default"])
            
            col1, col2 = st.columns(2)
            with col1:
                primary_color = st.color_picker("Primary Color", custom_theme["primary_color"])
                background_color = st.color_picker("Background Color", custom_theme["background_color"])
            
            with col2:
                text_color = st.color_picker("Text Color", custom_theme["text_color"])
                accent_color = st.color_picker("Accent Color", custom_theme["accent_color"])
            
            # Update custom theme
            self.preferences["custom_theme"] = {
                "primary_color": primary_color,
                "background_color": background_color,
                "text_color": text_color,
                "accent_color": accent_color
            }
        
        # Update selected theme
        self.preferences["theme"] = selected_theme
        
        # Preview
        st.subheader("Theme Preview")
        preview_theme = self.get_theme()
        
        # Display color swatches
        cols = st.columns(4)
        cols[0].markdown(f"""
        <div style="background-color: {preview_theme['primary_color']}; 
                    height: 50px; 
                    border-radius: 5px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    color: white;">
            Primary
        </div>
        """, unsafe_allow_html=True)
        
        cols[1].markdown(f"""
        <div style="background-color: {preview_theme['background_color']}; 
                    height: 50px; 
                    border-radius: 5px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    color: {preview_theme['text_color']}; 
                    border: 1px solid #ccc;">
            Background
        </div>
        """, unsafe_allow_html=True)
        
        cols[2].markdown(f"""
        <div style="background-color: {preview_theme['background_color']}; 
                    height: 50px; 
                    border-radius: 5px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    color: {preview_theme['text_color']};">
            Text
        </div>
        """, unsafe_allow_html=True)
        
        cols[3].markdown(f"""
        <div style="background-color: {preview_theme['accent_color']}; 
                    height: 50px; 
                    border-radius: 5px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    color: white;">
            Accent
        </div>
        """, unsafe_allow_html=True)
        
        # UI options
        st.subheader("UI Options")
        
        # Drag and drop channels
        dragdrop_enabled = st.toggle("Enable Drag and Drop Channel Management", 
                                  value=self.preferences.get("dragdrop_enabled", True),
                                  help="Allow dragging and dropping channels to reorder them")
        
        # Show recommendations
        show_recommendations = st.toggle("Show Channel Recommendations", 
                                      value=self.preferences.get("show_recommendations", True),
                                      help="Show channel recommendations based on point earning potential")
        
        # Animated badges
        animated_badges = st.toggle("Animated Achievement Badges", 
                                 value=self.preferences.get("animated_badges", True),
                                 help="Enable animations for achievement badges")
        
        # Tutorial
        show_tutorial = st.toggle("Show Onboarding Tutorial", 
                               value=self.preferences.get("show_tutorial", True),
                               help="Show the onboarding tutorial for new users")
        
        # Save button
        if st.button("Save Appearance Settings"):
            # Update preferences
            self.preferences["dragdrop_enabled"] = dragdrop_enabled
            self.preferences["show_recommendations"] = show_recommendations
            self.preferences["animated_badges"] = animated_badges
            self.preferences["show_tutorial"] = show_tutorial
            
            # Save preferences
            self.save_preferences()
            
            # Show success message
            st.success("Appearance settings saved! Refresh the page to see all changes.")
    
    def render_achievements(self):
        """Render the achievements UI in Streamlit"""
        st.subheader("Achievements")
        
        # Achievement stats
        unlocked = len(self.preferences.get("achievements", {}))
        total = len(ACHIEVEMENT_BADGES)
        
        st.write(f"You've unlocked {unlocked} out of {total} achievements")
        
        # Progress bar
        st.progress(unlocked / total if total > 0 else 0)
        
        # Create a grid layout for badges
        cols = st.columns(3)
        
        # Display all badges
        for i, (badge_id, badge) in enumerate(ACHIEVEMENT_BADGES.items()):
            # Alternate between columns
            col = cols[i % 3]
            
            # Check if unlocked
            is_unlocked = badge_id in self.preferences.get("achievements", {})
            
            # Check if new
            is_new = False
            if is_unlocked:
                is_new = self.preferences["achievements"][badge_id].get("new", False)
                
                # Clear new flag when viewed
                if is_new:
                    self.preferences["achievements"][badge_id]["new"] = False
                    self.save_preferences()
            
            # Create badge UI
            opacity = "1.0" if is_unlocked else "0.4"
            new_badge = "🆕 " if is_new else ""
            
            col.markdown(f"""
            <div style="
                background-color: {badge['color'] if is_unlocked else '#808080'}; 
                opacity: {opacity};
                padding: 10px; 
                border-radius: 10px; 
                margin-bottom: 15px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 2em; margin-bottom: 5px;">{badge['icon']}</div>
                <div style="font-weight: bold;">{new_badge}{badge_id}</div>
                <div style="font-size: 0.9em; margin-top: 5px;">{badge['description']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_multiple_accounts(self):
        """Render the multiple accounts UI in Streamlit"""
        st.subheader("Manage Multiple Accounts")
        
        accounts = self.preferences.get("multiple_accounts", [])
        
        # Show existing accounts
        if accounts:
            st.write("Your saved accounts:")
            
            for i, account in enumerate(accounts):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                # Username
                col1.write(f"👤 **{account['username']}**")
                
                # Use button
                if col2.button("Use", key=f"use_account_{i}"):
                    st.session_state.twitch_username = account["username"]
                    st.session_state.twitch_password = account["password"]
                    st.success(f"Switched to account: {account['username']}")
                    
                # Delete button
                if col3.button("Delete", key=f"delete_account_{i}"):
                    accounts.pop(i)
                    self.preferences["multiple_accounts"] = accounts
                    self.save_preferences()
                    st.success(f"Deleted account: {account['username']}")
                    st.rerun()
            
            st.markdown("---")
        
        # Add new account form
        st.write("Add a new account:")
        
        new_username = st.text_input("Twitch Username", key="new_account_username")
        new_password = st.text_input("Twitch Password", type="password", key="new_account_password")
        
        if st.button("Save Account"):
            if new_username and new_password:
                # Check if account already exists
                exists = any(a["username"] == new_username for a in accounts)
                
                if not exists:
                    # Add new account
                    accounts.append({
                        "username": new_username,
                        "password": new_password
                    })
                    
                    # Save updated accounts
                    self.preferences["multiple_accounts"] = accounts
                    self.save_preferences()
                    
                    st.success(f"Added new account: {new_username}")
                    
                    # Clear form
                    st.session_state.new_account_username = ""
                    st.session_state.new_account_password = ""
                    
                    st.rerun()
                else:
                    st.error(f"Account {new_username} already exists")
            else:
                st.error("Please enter both username and password")

# Global instance
user_preferences = UserPreferences()