import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TwitchBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = None
        self.running = False
        self.channel = None
        self.points_before = 0
        self.points_after = 0
        self.gained_points = 0
        self.latest_log = ""
        self.setup_driver()
        
    def setup_driver(self):
        """Set up the Selenium WebDriver with appropriate options."""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--mute-audio")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Add user agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.log("WebDriver initialized successfully")
        except Exception as e:
            self.log(f"Error setting up WebDriver: {str(e)}")
            raise
    
    def login(self):
        """Log in to Twitch account."""
        try:
            self.log("Attempting to log in to Twitch...")
            self.driver.get("https://www.twitch.tv/login")
            
            # Wait for login form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "login-username"))
            )
            
            # Enter username
            username_input = self.driver.find_element(By.ID, "login-username")
            username_input.clear()
            username_input.send_keys(self.username)
            
            # Enter password
            password_input = self.driver.find_element(By.ID, "password-input")
            password_input.clear()
            password_input.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-a-target='passport-login-button']")
            login_button.click()
            
            # Wait for successful login
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver: "login" not in driver.current_url
                )
                
                # Check if we were redirected to the main page
                if self.driver.current_url == "https://www.twitch.tv/":
                    self.log("Successfully logged in to Twitch")
                    return True
                else:
                    self.log(f"Unexpected redirect after login: {self.driver.current_url}")
                    return False
                    
            except TimeoutException:
                # Check if there's an error message
                try:
                    error_message = self.driver.find_element(By.CSS_SELECTOR, ".tw-alert-error")
                    self.log(f"Login error: {error_message.text}")
                except NoSuchElementException:
                    self.log("Login timeout, no error message found")
                
                return False
                
        except Exception as e:
            self.log(f"Login error: {str(e)}")
            return False
            
    def start_farming(self, channel):
        """Start farming points on a specific channel."""
        try:
            self.running = True
            self.channel = channel
            self.points_before = 0
            self.points_after = 0
            self.gained_points = 0
            
            # Navigate to the channel
            self.log(f"Navigating to channel: {channel}")
            self.driver.get(f"https://www.twitch.tv/{channel}")
            
            # Wait for the page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".stream-chat-header"))
            )
            
            # Check and get current points
            self.points_before = self.get_current_points()
            self.log(f"Starting points: {self.points_before}")
            
            # Check for mature content button if present
            try:
                mature_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target='player-overlay-mature-accept']"))
                )
                mature_button.click()
                self.log("Accepted mature content warning")
            except TimeoutException:
                self.log("No mature content warning detected")
            
            # Start watching the stream
            self.enable_autoplay()
            self.log(f"Started watching {channel}")
            
            # Set video quality to low to save bandwidth
            self.set_video_quality("160p")
            
            # Start farming in a loop
            while self.running:
                try:
                    # Click on channel points button if available
                    self.claim_bonus()
                    
                    # Update current points count
                    new_points = self.get_current_points()
                    if new_points > self.points_after:
                        self.points_after = new_points
                        self.gained_points += (self.points_after - self.points_before)
                        self.points_before = self.points_after
                        self.log(f"Points updated: {self.points_after}")
                    
                    # Check if stream is still live
                    if self.is_stream_offline():
                        self.log(f"Stream appears to be offline. Refreshing...")
                        self.driver.refresh()
                        time.sleep(5)
                    
                    # Move mouse and perform random actions to appear active
                    self.simulate_activity()
                    
                    # Sleep for a while
                    time.sleep(random.randint(30, 60))
                    
                except Exception as e:
                    self.log(f"Error during farming loop: {str(e)}")
                    time.sleep(10)
            
        except Exception as e:
            self.log(f"Error starting farming: {str(e)}")
            self.running = False
    
    def stop_farming(self):
        """Stop the farming process."""
        self.log("Stopping farming process...")
        self.running = False
        
        # Get final points count
        self.points_after = self.get_current_points()
        self.gained_points = self.points_after - self.points_before
        self.log(f"Farming stopped. Gained {self.gained_points} points")
        
        # Close the WebDriver
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def get_current_points(self):
        """Get the current channel points balance."""
        try:
            # Try to find the points indicator
            points_element = self.driver.find_element(
                By.CSS_SELECTOR, 
                ".community-points-summary .tw-animated-number"
            )
            
            # Get the text content and parse as integer
            points_text = points_element.text.replace(",", "")
            return int(points_text) if points_text.isdigit() else 0
            
        except NoSuchElementException:
            self.log("Could not find points counter")
            return 0
        except Exception as e:
            self.log(f"Error getting current points: {str(e)}")
            return 0
    
    def claim_bonus(self):
        """Click on the bonus points button if available."""
        try:
            # Look for the claim button
            bonus_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                "button[data-test-selector='community-points-claim-button']"
            )
            
            if bonus_button and bonus_button.is_displayed():
                bonus_button.click()
                self.log("Claimed bonus points!")
                return True
                
        except NoSuchElementException:
            # No bonus available, this is normal
            pass
        except Exception as e:
            self.log(f"Error claiming bonus: {str(e)}")
        
        return False
    
    def set_video_quality(self, quality="160p"):
        """Set the video quality to save bandwidth."""
        try:
            # Click settings button
            settings_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                "button[data-a-target='player-settings-button']"
            )
            settings_button.click()
            time.sleep(1)
            
            # Click quality option
            quality_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                "button[data-a-target='player-settings-menu-item-quality']"
            )
            quality_button.click()
            time.sleep(1)
            
            # Select the lowest quality
            quality_options = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".tw-radio input"
            )
            
            if quality_options:
                # Click the last option (lowest quality)
                quality_options[-1].click()
                self.log(f"Set video quality to lowest available")
            
            # Click away from the menu
            self.driver.find_element(By.CSS_SELECTOR, ".video-player__container").click()
            
        except Exception as e:
            self.log(f"Error setting video quality: {str(e)}")
    
    def enable_autoplay(self):
        """Ensure autoplay is enabled."""
        try:
            # Check if autoplay button exists and is needed
            autoplay_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-a-target='player-play-pause-button']")
            
            if autoplay_buttons and len(autoplay_buttons) > 0:
                # Check if stream is paused
                play_button = autoplay_buttons[0]
                if "pause" not in play_button.get_attribute("aria-label").lower():
                    play_button.click()
                    self.log("Enabled autoplay")
        except Exception as e:
            self.log(f"Error enabling autoplay: {str(e)}")
    
    def is_stream_offline(self):
        """Check if the stream is offline."""
        try:
            # Look for offline indicators
            offline_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".channel-status-info--offline, .offline-embeds"
            )
            
            return len(offline_elements) > 0
        except Exception:
            return False
    
    def simulate_activity(self):
        """Simulate user activity to appear active."""
        try:
            # Random actions to simulate real user
            action = random.choice([
                "scroll",
                "move_mouse",
                "click_player",
                "do_nothing"
            ])
            
            if action == "scroll":
                # Scroll down a bit and then back up
                self.driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(1)
                self.driver.execute_script("window.scrollBy(0, -300);")
                
            elif action == "move_mouse":
                # Move mouse to random coordinates in the player
                player = self.driver.find_element(By.CSS_SELECTOR, ".video-player__container")
                action_chain = webdriver.ActionChains(self.driver)
                action_chain.move_to_element_with_offset(
                    player, 
                    random.randint(10, 100), 
                    random.randint(10, 100)
                ).perform()
                
            elif action == "click_player":
                # Click on the player to show controls
                player = self.driver.find_element(By.CSS_SELECTOR, ".video-player__container")
                player.click()
                time.sleep(0.5)
                player.click()  # Click again to hide controls
                
        except Exception as e:
            self.log(f"Error simulating activity: {str(e)}")
    
    def log(self, message):
        """Log a message."""
        self.latest_log = message
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
    
    def get_latest_log(self):
        """Return the latest log message and clear it."""
        message = self.latest_log
        self.latest_log = ""
        return message
    
    def get_gained_points(self):
        """Return and reset the gained points."""
        points = self.gained_points
        self.gained_points = 0
        return points
