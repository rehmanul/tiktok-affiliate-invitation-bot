
import uuid
import logging
from datetime import datetime
from .config import *

class InvitationLinkGenerator:
    def __init__(self):
        self.logger = self._setup_logger()
        self.generated_links = []

    def _setup_logger(self):
        logger = logging.getLogger('InvitationLinkGenerator')
        logger.setLevel(LOG_LEVEL)
        handler = logging.FileHandler(LOG_FILE)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
        return logger

    def generate_invite_link(self):
        """Generate a unique invitation link"""
        try:
            # Generate a unique identifier
            unique_id = str(uuid.uuid4())[:8]
            
            # Create the invitation link with the business website as base
            invite_link = f"{BUSINESS_WEBSITE}affiliate/invite/{unique_id}"
            
            # Log the generated link
            self.logger.info(f"Generated new invitation link: {invite_link}")
            self.generated_links.append({
                'link': invite_link,
                'generated_at': datetime.now().isoformat(),
                'used': False
            })
            
            return invite_link
        except Exception as e:
            self.logger.error(f"Error generating invitation link: {str(e)}")
            return None

    def run_invite_link_generator(self, count=DEFAULT_INVITE_COUNT):
        """Generate multiple invitation links"""
        self.logger.info(f"Starting to generate {count} invitation links")
        generated_links = []
        
        for i in range(count):
            link = self.generate_invite_link()
            if link:
                generated_links.append(link)
            else:
                self.logger.error(f"Failed to generate link {i+1}/{count}")
        
        self.logger.info(f"Successfully generated {len(generated_links)} invitation links")
        return generated_links

    def mark_link_as_used(self, link):
        """Mark an invitation link as used"""
        for link_data in self.generated_links:
            if link_data['link'] == link:
                link_data['used'] = True
                link_data['used_at'] = datetime.now().isoformat()
                self.logger.info(f"Marked link as used: {link}")
                return True
        return False

    def get_unused_links(self):
        """Get all unused invitation links"""
        return [link_data['link'] for link_data in self.generated_links if not link_data['used']]
