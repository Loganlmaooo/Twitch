"""
Onboarding Tutorial for the Twitch Auto-Farmer
Provides an interactive tutorial to help new users get started
"""

import streamlit as st
import time
import base64
from io import BytesIO

# Tutorial steps
TUTORIAL_STEPS = [
    {
        "title": "Welcome to Twitch Auto-Farmer!",
        "content": """
        Thank you for using Twitch Auto-Farmer! This tutorial will guide you through the main features.
        
        The app automatically collects Twitch channel points while you're away, allowing you to:
        
        • Earn channel points without watching streams
        • Track your earnings and watchtime
        • Manage multiple channels at once
        • Control everything through Discord
        
        Let's get started!
        """,
        "image": None,
        "animation": "welcome"
    },
    {
        "title": "Step 1: Add Your Twitch Account",
        "content": """
        First, you need to add your Twitch account credentials. These are used to log in to Twitch and collect points.
        
        Your credentials are stored locally and never shared with anyone.
        
        Go to the **Control Center** tab and enter your Twitch username and password.
        """,
        "image": None,
        "animation": "login"
    },
    {
        "title": "Step 2: Start Farming",
        "content": """
        To start farming points, enter a channel name in the **Control Center** tab and click **Start Farming**.
        
        The bot will:
        1. Log in to your Twitch account
        2. Navigate to the channel
        3. Set quality to lowest setting to save bandwidth
        4. Start collecting points automatically
        
        You can add multiple channels to farm simultaneously.
        """,
        "image": None,
        "animation": "farming"
    },
    {
        "title": "Step 3: Monitor Progress",
        "content": """
        In the **Activity Log** tab, you can see real-time updates from your farming sessions.
        
        The log shows:
        • When points are earned
        • When bonus points are claimed
        • When channels go offline
        • Any errors that occur
        
        You'll also see notifications for important events.
        """,
        "image": None,
        "animation": "monitoring"
    },
    {
        "title": "Step 4: View Statistics",
        "content": """
        The **Statistics** tab shows your farming performance.
        
        You can see:
        • Total points earned
        • Total watchtime
        • Points per channel
        • Points over time
        
        Stats are updated in real-time as you collect points.
        """,
        "image": None,
        "animation": "statistics"
    },
    {
        "title": "Step 5: Discord Integration",
        "content": """
        The **Discord Bot** tab allows you to control farming from Discord.
        
        Set up the bot by:
        1. Creating a Discord bot on the Discord Developer Portal
        2. Adding your bot token
        3. Inviting the bot to your server
        
        You can then use slash commands like `/start`, `/stop`, and `/status` to control farming from Discord.
        """,
        "image": None,
        "animation": "discord"
    },
    {
        "title": "Bonus Features",
        "content": """
        Check out these additional features:
        
        • **Notifications**: Get SMS and in-app alerts for important events
        • **Themes**: Customize the dashboard appearance
        • **Channel Management**: Organize channels with drag and drop
        • **Scheduling**: Set up automatic farming schedules
        • **Achievements**: Earn badges as you reach milestones
        
        Explore these features in the settings!
        """,
        "image": None,
        "animation": "features"
    },
    {
        "title": "You're All Set!",
        "content": """
        Congratulations! You're ready to start farming Twitch points.
        
        Remember:
        • The app needs to be running to collect points
        • Your computer must remain on (consider cloud deployment)
        • Check the activity log regularly
        
        Happy farming!
        """,
        "image": None,
        "animation": "complete"
    }
]

# Animation frames for simple ASCII animations
ANIMATIONS = {
    "welcome": [
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃                          ┃
        ┃   Twitch Auto-Farmer!    ┃
        ┃                          ┃
        ┃         Welcome!         ┃
        ┃                          ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃                          ┃
        ┃   Twitch Auto-Farmer!    ┃
        ┃                          ┃
        ┃       * Welcome! *       ┃
        ┃                          ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃                          ┃
        ┃   Twitch Auto-Farmer!    ┃
        ┃                          ┃
        ┃     ** Welcome! **       ┃
        ┃                          ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
    ],
    "login": [
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃   Login to Twitch        ┃
        ┃                          ┃
        ┃   Username: [          ] ┃
        ┃   Password: [          ] ┃
        ┃                          ┃
        ┃   [ Login ]              ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃   Login to Twitch        ┃
        ┃                          ┃
        ┃   Username: [user123   ] ┃
        ┃   Password: [*********] ┃
        ┃                          ┃
        ┃   [ Login ]              ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃   Login to Twitch        ┃
        ┃                          ┃
        ┃   Username: [user123   ] ┃
        ┃   Password: [*********] ┃
        ┃                          ┃
        ┃   [ Logging in... ]      ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃   Login to Twitch        ┃
        ┃                          ┃
        ┃                          ┃
        ┃      Login Success!      ┃
        ┃                          ┃
        ┃                          ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
    ],
    "farming": [
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃   Channel: ninja         ┃
        ┃                          ┃
        ┃   Points: 2,345          ┃
        ┃   [■□□□□□□□□□]          ┃
        ┃                          ┃
        ┃   Waiting for bonus...   ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃   Channel: ninja         ┃
        ┃                          ┃
        ┃   Points: 2,345          ┃
        ┃   [■■□□□□□□□□]          ┃
        ┃                          ┃
        ┃   Waiting for bonus...   ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃   Channel: ninja         ┃
        ┃                          ┃
        ┃   Points: 2,345          ┃
        ┃   [■■■□□□□□□□]          ┃
        ┃                          ┃
        ┃   Bonus available!       ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃   Channel: ninja         ┃
        ┃                          ┃
        ┃   Points: 2,395 (+50)    ┃
        ┃   [□□□□□□□□□□]          ┃
        ┃                          ┃
        ┃   Claimed bonus points!  ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
    ],
    "monitoring": [
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ Activity Log                                  ┃
        ┃------------------------------------------------┃
        ┃ [12:30] Started farming on channel: ninja     ┃
        ┃ [12:35] Current points: 2,345                 ┃
        ┃ [12:40] Claimed 50 bonus points!              ┃
        ┃ [12:45] Current points: 2,395                 ┃
        ┃                                               ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ Activity Log                                  ┃
        ┃------------------------------------------------┃
        ┃ [12:30] Started farming on channel: ninja     ┃
        ┃ [12:35] Current points: 2,345                 ┃
        ┃ [12:40] Claimed 50 bonus points!              ┃
        ┃ [12:45] Current points: 2,395                 ┃
        ┃ [12:50] Claimed 50 bonus points!              ┃
        ┃                                               ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ Activity Log                                  ┃
        ┃------------------------------------------------┃
        ┃ [12:35] Current points: 2,345                 ┃
        ┃ [12:40] Claimed 50 bonus points!              ┃
        ┃ [12:45] Current points: 2,395                 ┃
        ┃ [12:50] Claimed 50 bonus points!              ┃
        ┃ [12:55] Current points: 2,445                 ┃
        ┃                                               ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
    ],
    "statistics": [
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ Statistics               ┃
        ┃-------------------------┃
        ┃ Total Points: 12,345    ┃
        ┃ Total Hours: 24.5       ┃
        ┃ Channels: 3             ┃
        ┃                         ┃
        ┃ [Chart placeholder]     ┃
        ┃                         ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ Statistics               ┃
        ┃-------------------------┃
        ┃ Total Points: 12,395    ┃
        ┃ Total Hours: 24.8       ┃
        ┃ Channels: 3             ┃
        ┃                         ┃
        ┃ [Chart placeholder]     ┃
        ┃                         ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ Statistics               ┃
        ┃-------------------------┃
        ┃ Total Points: 12,445    ┃
        ┃ Total Hours: 25.2       ┃
        ┃ Channels: 3             ┃
        ┃                         ┃
        ┃ [Chart placeholder]     ┃
        ┃                         ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
    ],
    "discord": [
        """
        [Discord]
        
        You: /start ninja
        
        Bot: Starting to farm points on 
        channel: ninja
        
        You: /status
        
        Bot: Currently farming on:
        - ninja (2,345 points)
        """,
        """
        [Discord]
        
        You: /start ninja
        
        Bot: Starting to farm points on 
        channel: ninja
        
        You: /status
        
        Bot: Currently farming on:
        - ninja (2,395 points)
        """,
        """
        [Discord]
        
        You: /start ninja
        
        Bot: Starting to farm points on 
        channel: ninja
        
        You: /status
        
        Bot: Currently farming on:
        - ninja (2,445 points)
        
        You: /stats
        """
    ],
    "features": [
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ [1] Notifications        ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ [2] Custom Themes        ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ [3] Channel Management   ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ [4] Scheduling           ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃ [5] Achievements         ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
    ],
    "complete": [
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃                          ┃
        ┃                          ┃
        ┃   Tutorial Complete!     ┃
        ┃                          ┃
        ┃                          ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃                          ┃
        ┃         🎉 🎉 🎉         ┃
        ┃   Tutorial Complete!     ┃
        ┃         🎉 🎉 🎉         ┃
        ┃                          ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """,
        """
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃         🎉 🎉 🎉         ┃
        ┃                          ┃
        ┃   Tutorial Complete!     ┃
        ┃                          ┃
        ┃         🎉 🎉 🎉         ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
    ]
}

class TutorialManager:
    def __init__(self):
        """Initialize the tutorial manager"""
        if 'tutorial_step' not in st.session_state:
            st.session_state.tutorial_step = 0
        if 'tutorial_completed' not in st.session_state:
            st.session_state.tutorial_completed = False
    
    def next_step(self):
        """Move to the next tutorial step"""
        if st.session_state.tutorial_step < len(TUTORIAL_STEPS) - 1:
            st.session_state.tutorial_step += 1
        else:
            st.session_state.tutorial_completed = True
    
    def previous_step(self):
        """Move to the previous tutorial step"""
        if st.session_state.tutorial_step > 0:
            st.session_state.tutorial_step -= 1
    
    def restart_tutorial(self):
        """Restart the tutorial from the beginning"""
        st.session_state.tutorial_step = 0
        st.session_state.tutorial_completed = False
    
    def render_animation(self, animation_key):
        """Render ASCII animation for tutorial step"""
        if animation_key and animation_key in ANIMATIONS:
            frames = ANIMATIONS[animation_key]
            
            # Display animation container
            animation_container = st.empty()
            
            # Function to create the animation with white space preserved
            def show_frame(frame):
                animation_container.markdown(f"```{frame}```")
            
            # Show first frame immediately
            show_frame(frames[0])
            
            # Don't actually animate in this version since we can't use JavaScript
            # Just show the last frame after a brief delay
            time.sleep(0.5)
            show_frame(frames[-1])
    
    def render_tutorial(self):
        """Render the tutorial UI in Streamlit"""
        current_step = TUTORIAL_STEPS[st.session_state.tutorial_step]
        
        # Display progress
        progress = (st.session_state.tutorial_step + 1) / len(TUTORIAL_STEPS)
        st.progress(progress)
        
        # Step title
        st.subheader(current_step["title"])
        
        # Animation
        if current_step["animation"]:
            self.render_animation(current_step["animation"])
        
        # Content
        st.markdown(current_step["content"])
        
        # Navigation buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        # Previous button
        if col1.button("← Previous", disabled=(st.session_state.tutorial_step == 0)):
            self.previous_step()
            st.rerun()
        
        # Next button
        if col2.button("Next →", disabled=(st.session_state.tutorial_step == len(TUTORIAL_STEPS) - 1)):
            self.next_step()
            st.rerun()
        
        # Skip button
        if col3.button("Skip Tutorial"):
            st.session_state.tutorial_completed = True
            st.rerun()
        
        # Restart button (only show if not on first step)
        if st.session_state.tutorial_step > 0:
            if col4.button("Restart"):
                self.restart_tutorial()
                st.rerun()
    
    def show_tutorial_button(self):
        """Show a button to open the tutorial"""
        if st.button("Show Tutorial"):
            st.session_state.tutorial_completed = False
            st.rerun()

# Global instance
tutorial_manager = TutorialManager()