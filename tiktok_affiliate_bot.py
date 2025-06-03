from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import json
import logging
from datetime import datetime
import os
import tempfile
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TikTokAffiliateBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def start_browser(self):
        """Initialize Chrome browser with anti-detection measures using Xvfb"""
        try:
            # Create a unique temporary directory
            self.temp_dir = tempfile.mkdtemp()
            unique_dir = f"{self.temp_dir}/chrome-{uuid.uuid4()}"
            
            chrome_options = Options()
            
            # Add Chrome arguments for headless mode and stability
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Add random user agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
            ]
            chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')
            
            # Set up ChromeDriver service with specific path
            chromedriver_path = "/root/.wdm/drivers/chromedriver/linux64/137.0.7151.68/chromedriver-linux64/chromedriver"
            service = Service(executable_path=chromedriver_path)
            chrome_options.binary_location = "/usr/bin/google-chrome-stable"
            
            # Initialize Chrome browser
            self.driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            
            # Set up wait and disable webdriver flag
            self.wait = WebDriverWait(self.driver, 20)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Browser started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            return False


    def login(self):
        """Handle TikTok Shop login process"""
        try:
            # Check for existing session
            if os.path.exists('session.json'):
                logger.info("Found existing session, attempting to restore...")
                with open('session.json', 'r') as f:
                    session_data = json.load(f)
                
                # Set environment variables from saved credentials if available
                if session_data.get('credentials'):
                    os.environ['TIKTOK_EMAIL'] = session_data['credentials'].get('email', '')
                    os.environ['TIKTOK_PASSWORD'] = session_data['credentials'].get('password', '')
                
                # First navigate to TikTok Shop domain to set cookies
                self.driver.get('https://seller.tiktok.com')
                
                # Add cookies from session
                if session_data.get('cookies'):
                    for cookie in session_data['cookies']:
                        try:
                            self.driver.add_cookie(cookie)
                        except Exception as e:
                            logger.warning(f"Failed to add cookie: {str(e)}")
                            
                # Add localStorage items
                if session_data.get('localStorage'):
                    for key, value in session_data['localStorage'].items():
                        if key not in ['clear', 'getItem', 'key', 'length', 'removeItem', 'setItem']:
                            try:
                                self.driver.execute_script(f"window.localStorage.setItem('{key}', '{value}')")
                            except Exception as e:
                                logger.warning(f"Failed to set localStorage item: {str(e)}")
                            
                # Add sessionStorage items
                if session_data.get('sessionStorage'):
                    for key, value in session_data['sessionStorage'].items():
                        if key not in ['clear', 'getItem', 'key', 'length', 'removeItem', 'setItem']:
                            try:
                                self.driver.execute_script(f"window.sessionStorage.setItem('{key}', '{value}')")
                            except Exception as e:
                                logger.warning(f"Failed to set sessionStorage item: {str(e)}")
                
                # Navigate to seller page
                self.driver.get('https://seller.tiktok.com')
                time.sleep(3)
                
                # Check if session is valid
                if "login" not in self.driver.current_url.lower():
                    logger.info("Session restored successfully")
                    return True
                else:
                    logger.warning("Session expired, proceeding with normal login")
            
            # Normal login process if no session or session expired
            self.driver.get('https://seller-uk-accounts.tiktok.com/account/login')
            
            # Wait for login form to be visible
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form")))
            
            # Enter credentials (from environment variables)
            email_input = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_input.send_keys(os.getenv('TIKTOK_EMAIL'))
            
            password_input = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_input.send_keys(os.getenv('TIKTOK_PASSWORD'))
            
            # Click login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            login_button.click()
            
            # Wait for login to complete and verify
            time.sleep(5)
            if "seller.tiktok.com" in self.driver.current_url:
                # Save session after successful login
                session_data = {
                    'cookies': self.driver.get_cookies(),
                    'localStorage': {},
                    'sessionStorage': {},
                    'timestamp': datetime.now().isoformat(),
                    'credentials': {
                        'email': os.getenv('TIKTOK_EMAIL'),
                        'password': os.getenv('TIKTOK_PASSWORD')
                    }
                }
                
                # Get localStorage items
                local_storage = self.driver.execute_script(
                    "return Object.keys(window.localStorage).reduce((obj, k) => { obj[k] = window.localStorage.getItem(k); return obj; }, {});"
                )
                session_data['localStorage'].update(local_storage)
                
                # Get sessionStorage items
                session_storage = self.driver.execute_script(
                    "return Object.keys(window.sessionStorage).reduce((obj, k) => { obj[k] = window.sessionStorage.getItem(k); return obj; }, {});"
                )
                session_data['sessionStorage'].update(session_storage)
                
                # Save session data
                with open('session.json', 'w') as f:
                    json.dump(session_data, f)
                logger.info(f"Login successful and session saved for user: {os.getenv('TIKTOK_EMAIL')}")
                return True
            else:
                logger.error("Login failed - Incorrect URL after login")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def navigate_to_affiliate_page(self):
        """Navigate to the affiliate creator page"""
        try:
            self.driver.get('https://affiliate.tiktok.com/connection/creator?shop_region=GB')
            time.sleep(3)
            
            if "affiliate.tiktok.com" in self.driver.current_url:
                logger.info("Successfully navigated to affiliate page")
                return True
            else:
                logger.error("Failed to navigate to affiliate page")
                return False
                
        except Exception as e:
            logger.error(f"Failed to navigate to affiliate page: {str(e)}")
            return False

    def apply_filters(self, min_followers=1000, max_followers=None, min_gmv=1000, categories=None):
        """Apply filters to creator list"""
        try:
            # Wait for page to load completely
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)  # Additional wait for dynamic content
            
            # Try different selectors for filter button
            filter_selectors = [
                "[data-testid='filter-button']",
                "button[aria-label='Filter']",
                "//button[contains(text(), 'Filter')]",
                ".filter-button",
                "#filter-button",
                "button:contains('Filter')",
                "button[title='Filter']",
                "button[aria-label*='filter']",
                "button[role='button']",
                "button[data-test='filter']"
            ]
            
            filter_button = None
            for selector in filter_selectors:
                try:
                    if selector.startswith("//"):
                        filter_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    elif selector.startswith("."):
                        filter_button = self.wait.until(
                            EC.element_to_be_clickable((By.CLASS_NAME, selector.replace(".", "")))
                        )
                    elif selector.startswith("#"):
                        filter_button = self.wait.until(
                            EC.element_to_be_clickable((By.ID, selector.replace("#", "")))
                        )
                    else:
                        try:
                            filter_button = self.wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        except Exception:
                            # Try using jQuery-like :contains selector fallback
                            elements = self.driver.find_elements(By.CSS_SELECTOR, "button")
                            for el in elements:
                                if 'filter' in el.text.lower():
                                    filter_button = el
                                    break
                    if filter_button:
                        break
                except Exception as e:
                    logger.warning(f"Filter button selector '{selector}' failed: {str(e)}")
                    continue
            
            if not filter_button:
                logger.error("Could not find filter button with any selector")
                # Save page source for debugging
                with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                raise Exception("Could not find filter button")
            
            # Click filter button and wait for modal
            filter_button.click()
            time.sleep(3)
            
            # Set follower range with retry logic
            input_fields = {
                'min_followers': ('Min Followers', 1000),
                'max_followers': ('Max Followers', 2000),
                'min_gmv': ('Min GMV', 1000)
            }
            
            for field, (label, value) in input_fields.items():
                retries = 3
                while retries > 0:
                    try:
                        # Try different selectors for input fields
                        selectors = [
                            f"input[placeholder*='{label}']",
                            f"input[aria-label*='{label}']",
                            f"//input[contains(@placeholder, '{label}')]",
                            f"//label[contains(text(), '{label}')]/..//input"
                        ]
                        
                        input_field = None
                        for selector in selectors:
                            try:
                                if selector.startswith("//"):
                                    input_field = self.wait.until(
                                        EC.presence_of_element_located((By.XPATH, selector))
                                    )
                                else:
                                    input_field = self.wait.until(
                                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                    )
                                break
                            except Exception:
                                continue
                        
                        if input_field:
                            input_field.clear()
                            input_field.send_keys(str(value))
                            logger.info(f"Set {field} to {value}")
                            break
                        else:
                            raise Exception(f"Could not find input field for {label}")
                            
                    except Exception as e:
                        logger.warning(f"Failed to set {field} (attempt {4-retries}): {str(e)}")
                        retries -= 1
                        time.sleep(1)
            
            # Select categories if provided
            if categories:
                try:
                    # Try different selectors for category dropdown
                    dropdown_selectors = [
                        "[data-testid='category-dropdown']",
                        "button[aria-label*='Category']",
                        "//button[contains(., 'Category')]",
                        ".category-dropdown"
                    ]
                    
                    for selector in dropdown_selectors:
                        try:
                            if selector.startswith("//"):
                                category_dropdown = self.wait.until(
                                    EC.element_to_be_clickable((By.XPATH, selector))
                                )
                            else:
                                category_dropdown = self.wait.until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                )
                            category_dropdown.click()
                            break
                        except Exception:
                            continue
                    
                    # Select categories
                    for category in categories:
                        try:
                            # Try different ways to find category options
                            selectors = [
                                f"//div[contains(text(), '{category}')]",
                                f"//label[contains(., '{category}')]",
                                f"[data-value='{category}']",
                                f"input[value='{category}']"
                            ]
                            
                            for selector in selectors:
                                try:
                                    if selector.startswith("//"):
                                        option = self.wait.until(
                                            EC.element_to_be_clickable((By.XPATH, selector))
                                        )
                                    else:
                                        option = self.wait.until(
                                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                        )
                                    option.click()
                                    time.sleep(1)
                                    break
                                except Exception:
                                    continue
                        except Exception as e:
                            logger.warning(f"Failed to select category {category}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Failed to handle categories: {str(e)}")
            
            # Try to find and click apply button
            apply_selectors = [
                "[data-testid='apply-filters']",
                "button[type='submit']",
                "//button[contains(., 'Apply')]",
                ".apply-button",
                "#apply-button"
            ]
            
            for selector in apply_selectors:
                try:
                    if selector.startswith("//"):
                        apply_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    elif selector.startswith("."):
                        apply_button = self.wait.until(
                            EC.element_to_be_clickable((By.CLASS_NAME, selector.replace(".", "")))
                        )
                    elif selector.startswith("#"):
                        apply_button = self.wait.until(
                            EC.element_to_be_clickable((By.ID, selector.replace("#", "")))
                        )
                    else:
                        apply_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    apply_button.click()
                    break
                except Exception:
                    continue
            
            # Wait for filters to be applied
            time.sleep(5)
            
            logger.info("Filters applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply filters: {str(e)}")
            return False

    def send_invitations(self, max_invites=50, campaign_id=None, db_session=None):
        """Send invitations to filtered creators and update campaign progress"""
        invites_sent = 0
        try:
            while invites_sent < max_invites:
                # Find all invite buttons that haven't been clicked
                invite_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='invite-button']:not([disabled])")
                
                if not invite_buttons:
                    logger.info("No more invite buttons found")
                    break
                    
                for button in invite_buttons:
                    if invites_sent >= max_invites:
                        break
                        
                    try:
                        # Scroll button into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(random.uniform(1, 2))
                        
                        # Click invite button
                        button.click()
                        time.sleep(random.uniform(2, 3))
                        
                        # Confirm invitation if needed
                        try:
                            confirm_button = self.wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='confirm-invite']"))
                            )
                            confirm_button.click()
                            time.sleep(random.uniform(1, 2))
                        except TimeoutException:
                            pass  # No confirmation needed
                            
                        invites_sent += 1
                        logger.info(f"Invitation sent successfully ({invites_sent}/{max_invites})")
                        
                        # Update campaign progress in DB
                        if campaign_id and db_session:
                            from src.models import Invitation, CreatorProfile
                            # Here you would get creator info from the page or button context
                            # For now, assume creator_id is retrievable (placeholder)
                            creator_id = None
                            try:
                                # Example: extract creator id from button attribute or nearby element
                                creator_id = button.get_attribute('data-creator-id')
                                if creator_id:
                                    creator_id = int(creator_id)
                            except Exception as e:
                                logger.warning(f"Failed to get creator id: {str(e)}")
                            
                            if creator_id:
                                invitation = Invitation(
                                    campaign_id=campaign_id,
                                    creator_id=creator_id,
                                    status='sent',
                                    sent_at=datetime.now()
                                )
                                db_session.add(invitation)
                                db_session.commit()
                                
                                # Update invites_sent count in campaign
                                campaign = db_session.query(Campaign).filter(Campaign.id == campaign_id).first()
                                if campaign:
                                    campaign.invites_sent = invites_sent
                                    db_session.commit()
                        
                        # Add random delay between invites
                        time.sleep(random.uniform(3, 5))
                        
                    except Exception as e:
                        logger.warning(f"Failed to send individual invitation: {str(e)}")
                        continue
                        
                # Scroll down to load more creators
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 3))
                
            logger.info(f"Finished sending invitations. Total sent: {invites_sent}")
            return invites_sent
            
        except Exception as e:
            logger.error(f"Failed to send invitations: {str(e)}")
            return invites_sent

    def close(self):
        """Clean up and close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed successfully")
            
            # Clean up temporary directory
            if hasattr(self, 'temp_dir') and self.temp_dir:
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                logger.info("Temporary directory cleaned up")
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")

def main():
    bot = TikTokAffiliateBot()
    
    try:
        # Start browser
        if not bot.start_browser():
            raise Exception("Failed to start browser")
            
        # Login directly
        if not bot.login():
            raise Exception("Failed to login")
            
        # Navigate to affiliate page
        if not bot.navigate_to_affiliate_page():
            raise Exception("Failed to navigate to affiliate page")
            
        # Apply filters
        filters = {
            'min_followers': 5000,
            'max_followers': 100000,
            'categories': ['Fashion', 'Beauty']
        }
        if not bot.apply_filters(**filters):
            raise Exception("Failed to apply filters")
            
        # Send invitations
        invites_sent = bot.send_invitations(max_invites=50)
        logger.info(f"Successfully sent {invites_sent} invitations")
        
    except Exception as e:
        logger.error(f"Bot execution failed: {str(e)}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
