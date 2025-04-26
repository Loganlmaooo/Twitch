# Twitch Auto-Farmer

An automated tool to farm Twitch channel points with a Streamlit dashboard and Discord bot for remote control.

## Features

- Auto-farm Twitch channel points by watching streams
- Monitor multiple channels simultaneously
- Discord bot with slash commands for remote control
- Beautiful Streamlit dashboard with statistics
- Track points earned and watchtime

## Local Development

### Requirements
- Python 3.8 or higher
- Required Python packages: streamlit, pandas, plotly, discord.py, selenium, requests

### Running Locally
1. Clone this repository
2. Install dependencies with `pip install -r packages.txt`
3. Run the Streamlit app with `streamlit run app.py --server.port 5000`
4. Run the Discord bot with `python run_discord_bot.py`

## Deploying to Render.com

This application can be deployed on Render.com as two separate services (web app and worker).

### Environment Variables

Set the following environment variables in your Render.com dashboard:

- `DATA_FILE_PATH`: Path to store farming data (e.g., `/var/data/farming_data.json`)
- `DISCORD_TOKEN`: Your Discord bot token
- `DISCORD_GUILD_ID` (optional): Restrict Discord bot to a specific server

### Deployment Steps

1. Create a new Web Service on Render.com
   - Connect your repository
   - Set the build command to `pip install -r packages.txt`
   - Set the start command to `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - Add the necessary environment variables

2. Create a new Background Worker on Render.com
   - Connect the same repository
   - Set the build command to `pip install -r packages.txt`
   - Set the start command to `python run_discord_bot.py`
   - Add the same environment variables

For more detailed instructions, see the [Render.com documentation](https://render.com/docs).

## Security Considerations

- Store your Twitch credentials securely
- Use Discord's slash commands in private channels or DMs for security
- Be aware that automation may violate Twitch's terms of service

## Disclaimer

This tool is for educational purposes only. Use at your own risk.