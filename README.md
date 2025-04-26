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
- `RENDER`: Set to `true` to show deployment info in the UI

**Note about Discord token:**
- You do NOT need to set the Discord token as an environment variable
- The token should be configured through the web interface
- The Discord bot worker will automatically wait for the token to be configured

### Deployment Steps

1. Use Blueprint Deployment (Recommended)
   - Connect your repository to Render.com
   - The `render.yaml` file will automatically configure all services
   - Add your Discord bot token in the environment variables

2. Manual Deployment (Alternative)

   **Web Service**:
   - Connect your repository
   - Set environment to "Python"
   - Set the build command to `chmod +x render-build.sh && ./render-build.sh && poetry install`
   - Set the start command to `poetry run streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - Add the necessary environment variables

   **Background Worker**:
   - Connect the same repository
   - Set environment to "Python"
   - Set the build command to `chmod +x render-build.sh && ./render-build.sh && poetry install`
   - Set the start command to `poetry run python run_discord_bot.py`
   - Add the same environment variables

For more detailed instructions, see the [Render.com documentation](https://render.com/docs).

## Security Considerations

- Store your Twitch credentials securely
- Use Discord's slash commands in private channels or DMs for security
- Be aware that automation may violate Twitch's terms of service

## Disclaimer

This tool is for educational purposes only. Use at your own risk.