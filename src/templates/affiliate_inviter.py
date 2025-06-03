
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
import csv
from datetime import datetime
from .config import *

class AffiliateInviter:
    def __init__(self):
        self.logger = self._setup_logger()
        self.driver = self._setup_webdriver()
        self.invited_affiliates = self._load_invited_affiliates()

    def _setup_logger(self):
        logger = logging.getLogger('AffiliateInviter')
        logger.setLevel(LOG_LEVEL)
        handler = logging.FileHandler(LOG_FILE)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
        return logger

    def _setup_webdriver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=options)

    def _load_invited_affiliates(self):
        try:
            with open(INVITED_AFFILIATES_FILE, 'r') as f:
                reader = csv.DictReader(f)
                return {row['username'] for row in reader}
        except FileNotFoundError:
            with open(INVITED_AFFILIATES_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'gmv', 'followers', 'invite_date'])
            return set()

    def search_tiktok(self, category):
        """Search TikTok for creators in a specific category"""
        try:
            self.driver.get(TIKTOK_SEARCH_URL)
            search_box = WebDriverWait(self.driver, SELENIUM_TIMEOUT).until(
                EC.presence_of_element_located((By.NAME, 'q'))
            )
            search_box.send_keys(f"{category} creator")
            search_box.submit()
            return True
        except TimeoutException:
            self.logger.error(f"Timeout while searching for category: {category}")
            return False

    def filter_creators(self):
        """Apply filters for followers and promotion type"""
        creators = []
        try:
            # Wait for creator list to load
            creator_elements = WebDriverWait(self.driver, SELENIUM_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'creator-card'))
            )
            
            for element in creator_elements:
                creator_info = self._extract_creator_info(element)
                if self._meets_criteria(creator_info):
                    creators.append(creator_info)
            
            # Sort by GMV (highest to lowest)
            creators.sort(key=lambda x: x['gmv'], reverse=True)
            return creators
        except TimeoutException:
            self.logger.error("Timeout while filtering creators")
            return []

    def _extract_creator_info(self, element):
        """Extract creator information from element"""
        try:
            return {
                'username': element.find_element(By.CLASS_NAME, 'username').text,
                'gmv': float(element.find_element(By.CLASS_NAME, 'gmv').text.replace('$', '').replace(',', '')),
                'followers': int(element.find_element(By.CLASS_NAME, 'followers').text.replace('K', '000').replace('M', '000000')),
                'promotion_type': element.find_element(By.CLASS_NAME, 'promotion-type').text
            }
        except Exception as e:
            self.logger.error(f"Error extracting creator info: {str(e)}")
            return None

    def _meets_criteria(self, creator_info):
        """Check if creator meets the filtering criteria"""
        if not creator_info:
            return False
            
        return (
            creator_info['followers'] >= TIKTOK_FILTERS['MIN_FOLLOWERS'] and
            creator_info['promotion_type'] in TIKTOK_FILTERS['PROMOTION_TYPES'] and
            creator_info['username'] not in self.invited_affiliates
        )

    def invite_creator(self, creator_info, invite_link):
        """Send invitation to creator"""
        try:
            # Implementation of actual invitation mechanism would go here
            # This is a placeholder for the actual TikTok API integration
            
            # Record the invitation
            self._record_invitation(creator_info)
            self.logger.info(f"Invited creator: {creator_info['username']}")
            return True
        except Exception as e:
            self.logger.error(f"Error inviting creator {creator_info['username']}: {str(e)}")
            return False

    def _record_invitation(self, creator_info):
        """Record the invitation in CSV file"""
        with open(INVITED_AFFILIATES_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                creator_info['username'],
                creator_info['gmv'],
                creator_info['followers'],
                datetime.now().isoformat()
            ])
        self.invited_affiliates.add(creator_info['username'])

    def run_invitation_process(self, invite_link):
        """Run the complete invitation process"""
        for category in TIKTOK_FILTERS['CATEGORIES']:
            if not self.search_tiktok(category):
                continue
                
            creators = self.filter_creators()
            for creator in creators:
                if creator['gmv'] < TARGET_GMV_THRESHOLD:
                    self.logger.info(f"Stopping invitations for category {category} - GMV threshold reached")
                    break
                    
                self.invite_creator(creator, invite_link)

    def close(self):
        """Clean up resources"""
        self.driver.quit()
