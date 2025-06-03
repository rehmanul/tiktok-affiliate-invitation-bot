
# TikTok Search Configuration
TIKTOK_FILTERS = {
    'MIN_FOLLOWERS': 10000,  # Minimum follower count
    'CATEGORIES': [
        'tech',
        'repair',
        'electronics',
        'mobile_repair',
        'gadget_repair'
    ],
    'PROMOTION_TYPES': ['Video', 'Live']
}

# Business Configuration
BUSINESS_NAME = "Digi4u Repair UK"
BUSINESS_WEBSITE = "https://www.digi4u.co.uk/"
TARGET_GMV_THRESHOLD = 5000  # Minimum GMV value to consider an affiliate
DEFAULT_INVITE_COUNT = 100   # Default number of invites to generate

# Selenium Configuration
SELENIUM_TIMEOUT = 30  # seconds
TIKTOK_BASE_URL = "https://www.tiktok.com"
TIKTOK_SEARCH_URL = f"{TIKTOK_BASE_URL}/search"

# Logging Configuration
import logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO
LOG_FILE = 'affiliate_bot.log'

# Database Configuration (for tracking invited affiliates)
INVITED_AFFILIATES_FILE = 'invited_affiliates.csv'
