import logging
from sqlalchemy.orm import Session
from src.models import CreatorProfile
from datetime import datetime

logger = logging.getLogger(__name__)

def sync_creators(driver, db: Session):
    """
    Sync creator profiles from TikTok affiliate page into the database.
    Args:
        driver: Selenium webdriver instance
        db: SQLAlchemy session
    """
    try:
        # Navigate to creators page if not already there
        if "affiliate.tiktok.com/connection/creator" not in driver.current_url:
            driver.get("https://affiliate.tiktok.com/connection/creator?shop_region=GB")
        
        # Wait for page to load creators list
        # (Implementation depends on page structure, add waits as needed)
        
        # Example: parse creator elements
        creator_elements = driver.find_elements(By.CSS_SELECTOR, ".creator-card")  # Placeholder selector
        
        for elem in creator_elements:
            try:
                tiktok_id = elem.get_attribute("data-creator-id")
                username = elem.find_element(By.CSS_SELECTOR, ".username").text
                followers_text = elem.find_element(By.CSS_SELECTOR, ".followers").text
                followers = int(followers_text.replace(",", "").replace(" followers", ""))
                category = elem.find_element(By.CSS_SELECTOR, ".category").text
                gmv_text = elem.find_element(By.CSS_SELECTOR, ".gmv").text.replace("$", "").replace(",", "")
                gmv = float(gmv_text)
                promotion_type = elem.find_element(By.CSS_SELECTOR, ".promotion-type").text
                region = "UK"  # Assuming UK region
                
                # Check if creator exists
                creator = db.query(CreatorProfile).filter(CreatorProfile.tiktok_id == tiktok_id).first()
                if creator:
                    # Update existing
                    creator.username = username
                    creator.followers = followers
                    creator.category = category
                    creator.gmv = gmv
                    creator.promotion_type = promotion_type
                    creator.region = region
                    creator.updated_at = datetime.utcnow()
                else:
                    # Add new
                    creator = CreatorProfile(
                        tiktok_id=tiktok_id,
                        username=username,
                        followers=followers,
                        category=category,
                        gmv=gmv,
                        promotion_type=promotion_type,
                        region=region,
                        created_at=datetime.utcnow()
                    )
                    db.add(creator)
                db.commit()
            except Exception as e:
                logger.warning(f"Failed to sync creator: {str(e)}")
        
        logger.info("Creator sync completed successfully")
    except Exception as e:
        logger.error(f"Failed to sync creators: {str(e)}")
