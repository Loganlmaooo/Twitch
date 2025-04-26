import streamlit as st
import pandas as pd
import plotly.express as px
import time
import threading
import os
from datetime import datetime, timedelta

from twitch_bot import TwitchBot
from data_manager import DataManager
from utils import format_time, get_emoji_status, send_discord_webhook

# Page configuration
st.set_page_config(
    page_title="Twitch Auto-Farmer",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'active_bot' not in st.session_state:
    st.session_state.active_bot = None
if 'farming_thread' not in st.session_state:
    st.session_state.farming_thread = None
if 'channels' not in st.session_state:
    st.session_state.channels = []
if 'selected_channel' not in st.session_state:
    st.session_state.selected_channel = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'points_gained' not in st.session_state:
    st.session_state.points_gained = 0
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'discord_webhook_url' not in st.session_state:
    st.session_state.discord_webhook_url = "https://discord.com/api/webhooks/1365508833815953518/i6QoxKXSD75Yp-F1zmeVEga1K_DKt3J4xAOdMe_TGWXjWPmBkAbhCB9l4dyfoQtC7Yl8"
if 'enable_discord_logging' not in st.session_state:
    st.session_state.enable_discord_logging = False

# Custom function to update the UI while bot is running
def bot_worker():
    while st.session_state.bot_running:
        # Update the UI periodically
        time.sleep(10)
        st.session_state.points_gained += st.session_state.active_bot.get_gained_points()
        log_message = st.session_state.active_bot.get_latest_log()
        if log_message:
            timestamp = datetime.now().strftime('%H:%M:%S')
            formatted_log = f"[{timestamp}] {log_message}"
            
            # Add to local log messages
            st.session_state.log_messages.append(formatted_log)
            
            # Keep only the most recent 100 messages
            if len(st.session_state.log_messages) > 100:
                st.session_state.log_messages = st.session_state.log_messages[-100:]
            
            # Send to Discord webhook if enabled
            if st.session_state.enable_discord_logging and st.session_state.discord_webhook_url:
                send_discord_webhook(
                    message=formatted_log,
                    webhook_url=st.session_state.discord_webhook_url
                )

# Function to start farming
def start_farming():
    if not st.session_state.selected_channel:
        st.error("Please select a channel to farm first.")
        return
        
    if st.session_state.bot_running:
        st.error("Bot is already running!")
        return

    try:
        username = st.session_state.twitch_username
        password = st.session_state.twitch_password
        
        if not username or not password:
            st.error("Please enter your Twitch credentials.")
            return
        
        st.session_state.active_bot = TwitchBot(username, password)
        success = st.session_state.active_bot.login()
        
        if not success:
            st.error("Failed to login to Twitch. Check your credentials.")
            return
            
        st.session_state.bot_running = True
        st.session_state.start_time = datetime.now()
        st.session_state.points_gained = 0
        
        # Add log message
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] Started farming on channel: {st.session_state.selected_channel}"
        st.session_state.log_messages.append(log_message)
        
        # Send to Discord webhook if enabled
        if st.session_state.enable_discord_logging and st.session_state.discord_webhook_url:
            send_discord_webhook(
                message=log_message,
                webhook_url=st.session_state.discord_webhook_url
            )
        
        # Start the bot in a separate thread
        st.session_state.active_bot.start_farming(st.session_state.selected_channel)
        
        # Start worker thread to update UI
        st.session_state.farming_thread = threading.Thread(target=bot_worker)
        st.session_state.farming_thread.daemon = True
        st.session_state.farming_thread.start()
        
        # Record session start in data manager
        st.session_state.data_manager.start_session(st.session_state.selected_channel)
        
        st.success(f"Started farming on {st.session_state.selected_channel}")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Error starting the bot: {str(e)}")

# Function to stop farming
def stop_farming():
    if not st.session_state.bot_running:
        st.error("Bot is not running!")
        return
        
    try:
        st.session_state.bot_running = False
        
        if st.session_state.active_bot:
            st.session_state.active_bot.stop_farming()
            
        # Record session end with statistics
        duration = (datetime.now() - st.session_state.start_time).total_seconds() / 60
        st.session_state.data_manager.end_session(
            st.session_state.selected_channel,
            duration,
            st.session_state.points_gained
        )
        
        # Add log message
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] Stopped farming on channel: {st.session_state.selected_channel}"
        st.session_state.log_messages.append(log_message)
        
        # Send to Discord webhook if enabled
        if st.session_state.enable_discord_logging and st.session_state.discord_webhook_url:
            send_discord_webhook(
                message=log_message,
                webhook_url=st.session_state.discord_webhook_url
            )
        
        st.success(f"Stopped farming on {st.session_state.selected_channel}")
        
        # Reset active bot
        st.session_state.active_bot = None
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Error stopping the bot: {str(e)}")

def add_channel():
    new_channel = st.session_state.new_channel.strip().lower()
    if new_channel and new_channel not in st.session_state.channels:
        st.session_state.channels.append(new_channel)
        st.session_state.new_channel = ""
        st.rerun()

# Main layout
st.markdown("""
<div style='text-align: center'>
    <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M2.149 0L0.642 4.04V20.96H6.655V24H10.693L13.733 20.96H18.761L23.775 15.946V0H2.149ZM21.269 14.692L17.507 18.454H11.493L8.453 21.494V18.454H3.4V2.506H21.269V14.692Z" fill="#9146FF"/>
        <path d="M10.231 5.764H12.734V12.783H10.231V5.764Z" fill="#9146FF"/>
        <path d="M16.772 5.764H19.276V12.783H16.772V5.764Z" fill="#9146FF"/>
    </svg>
    <h1>Twitch Auto-Farmer</h1>
</div>
""", unsafe_allow_html=True)

# Create three columns for the main content
col1, col2 = st.columns([1, 2])

# Column 1: Control Panel
with col1:
    st.subheader("Control Panel")
    
    # Twitch credentials
    with st.expander("Twitch Login", expanded=True):
        if 'twitch_username' not in st.session_state:
            st.session_state.twitch_username = ""
        if 'twitch_password' not in st.session_state:
            st.session_state.twitch_password = ""
            
        st.text_input("Username", key="twitch_username")
        st.text_input("Password", type="password", key="twitch_password")
    
    # Channel management
    with st.expander("Channel Management", expanded=True):
        # Add new channel
        st.text_input("Add Channel", key="new_channel", on_change=add_channel)
        
        # Channel selection
        if st.session_state.channels:
            st.selectbox(
                "Select Channel to Farm",
                options=st.session_state.channels,
                key="selected_channel"
            )
        else:
            st.info("Add channels to begin farming")
        
        # List of channels with delete buttons
        if st.session_state.channels:
            st.subheader("Your Channels")
            for idx, channel in enumerate(st.session_state.channels):
                cols = st.columns([4, 1])
                cols[0].write(channel)
                if cols[1].button("❌", key=f"delete_{idx}"):
                    st.session_state.channels.remove(channel)
                    st.rerun()
    
    # Bot controls
    if st.session_state.bot_running:
        st.error("Bot Status: Running")
        st.button("Stop Farming", on_click=stop_farming)
    else:
        st.success("Bot Status: Ready")
        st.button("Start Farming", on_click=start_farming)
    
    # Current session stats
    if st.session_state.bot_running:
        st.subheader("Current Session")
        
        elapsed_time = datetime.now() - st.session_state.start_time
        elapsed_formatted = format_time(elapsed_time.total_seconds())
        
        st.metric("Channel", st.session_state.selected_channel)
        st.metric("Duration", elapsed_formatted)
        st.metric("Points Gained", st.session_state.points_gained)

# Column 2: Dashboard
with col2:
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Activity Log", "Statistics"])
    
    # Tab 1: Dashboard Overview
    with tab1:
        st.subheader("Farming Dashboard")
        
        # Status cards
        status_cols = st.columns(3)
        
        # Card 1: Bot Status
        with status_cols[0]:
            status = "Online" if st.session_state.bot_running else "Offline"
            emoji = get_emoji_status(st.session_state.bot_running)
            st.info(f"Bot Status: {emoji} {status}")
        
        # Card 2: Active Channel
        with status_cols[1]:
            channel = st.session_state.selected_channel if st.session_state.selected_channel else "None"
            st.info(f"Active Channel: {channel}")
        
        # Card 3: Session Duration
        with status_cols[2]:
            if st.session_state.start_time:
                elapsed_time = datetime.now() - st.session_state.start_time
                elapsed_formatted = format_time(elapsed_time.total_seconds())
                st.info(f"Session Duration: {elapsed_formatted}")
            else:
                st.info("Session Duration: 00:00:00")
        
        # Session Statistics
        if st.session_state.data_manager.has_data():
            st.subheader("Your Farming Statistics")
            
            stats_cols = st.columns(3)
            
            total_time = st.session_state.data_manager.get_total_watchtime()
            total_points = st.session_state.data_manager.get_total_points()
            total_sessions = st.session_state.data_manager.get_total_sessions()
            
            stats_cols[0].metric("Total Watchtime", format_time(total_time * 60))
            stats_cols[1].metric("Total Points", f"{total_points:,}")
            stats_cols[2].metric("Total Sessions", total_sessions)
            
            # Watchtime chart
            st.subheader("Watchtime by Channel")
            
            channel_stats = st.session_state.data_manager.get_channel_stats()
            if channel_stats:
                df = pd.DataFrame(channel_stats)
                
                # Create watchtime chart
                fig = px.bar(
                    df, 
                    x='channel', 
                    y='watchtime', 
                    title='Total Watchtime by Channel (hours)',
                    labels={'channel': 'Channel', 'watchtime': 'Hours Watched'},
                    color_discrete_sequence=['#9146FF']
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Create points chart
                fig2 = px.bar(
                    df, 
                    x='channel', 
                    y='points', 
                    title='Total Points by Channel',
                    labels={'channel': 'Channel', 'points': 'Points Earned'},
                    color_discrete_sequence=['#9146FF']
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Start farming to see your statistics here!")
            
    # Tab 2: Activity Log
    with tab2:
        st.subheader("Activity Log")
        
        if st.session_state.log_messages:
            for msg in reversed(st.session_state.log_messages):
                st.text(msg)
        else:
            st.info("No activity logged yet.")
        
        if st.button("Clear Log"):
            st.session_state.log_messages = []
            st.rerun()
    
    # Tab 3: Detailed Statistics
    with tab3:
        st.subheader("Detailed Farming Statistics")
        
        if st.session_state.data_manager.has_data():
            # Show session history
            sessions = st.session_state.data_manager.get_all_sessions()
            if sessions:
                session_df = pd.DataFrame(sessions)
                session_df['end_time'] = pd.to_datetime(session_df['end_time'])
                session_df['start_time'] = pd.to_datetime(session_df['start_time'])
                session_df = session_df.sort_values('end_time', ascending=False)
                
                st.dataframe(
                    session_df[['channel', 'start_time', 'end_time', 'duration', 'points']],
                    use_container_width=True
                )
                
                # Show points gained over time
                st.subheader("Points Gained Over Time")
                
                # Prepare data for time series
                time_df = session_df.copy()
                time_df['date'] = time_df['end_time'].dt.date
                time_series = time_df.groupby('date')['points'].sum().reset_index()
                time_series['cumulative_points'] = time_series['points'].cumsum()
                
                # Create time series chart
                fig3 = px.line(
                    time_series,
                    x='date',
                    y='cumulative_points',
                    title='Cumulative Points Over Time',
                    labels={'date': 'Date', 'cumulative_points': 'Total Points'},
                    markers=True,
                    color_discrete_sequence=['#9146FF']
                )
                st.plotly_chart(fig3, use_container_width=True)
                
                # Show daily farming chart
                st.subheader("Daily Farming Activity")
                
                daily_df = time_df.groupby('date')['duration'].sum().reset_index()
                daily_df['duration_hours'] = daily_df['duration'] / 60  # Convert to hours
                
                fig4 = px.bar(
                    daily_df,
                    x='date',
                    y='duration_hours',
                    title='Daily Farming Hours',
                    labels={'date': 'Date', 'duration_hours': 'Hours Farmed'},
                    color_discrete_sequence=['#9146FF']
                )
                st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Start farming to see your detailed statistics!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Twitch Auto-Farmer | Made with ❤️ for streamers</p>
        <p><small>This tool is for educational purposes only.</small></p>
    </div>
    """, 
    unsafe_allow_html=True
)
