
import argparse
import logging
from .affiliate_inviter import AffiliateInviter
from .invitation_link_generator import InvitationLinkGenerator
from .config import *

def setup_logger():
    logger = logging.getLogger('main')
    logger.setLevel(LOG_LEVEL)
    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger

def run_affiliate_inviter(invite_count=None):
    logger = setup_logger()
    logger.info("Starting affiliate invitation process")
    
    # Initialize the link generator and create required links
    link_generator = InvitationLinkGenerator()
    if invite_count:
        links = link_generator.run_invite_link_generator(invite_count)
    else:
        links = link_generator.run_invite_link_generator()
    
    if not links:
        logger.error("Failed to generate invitation links")
        return False
    
    # Initialize the affiliate inviter
    inviter = AffiliateInviter()
    
    try:
        # For each generated link, run the invitation process
        for link in links:
            inviter.run_invitation_process(link)
            link_generator.mark_link_as_used(link)
            
        logger.info("Completed affiliate invitation process")
        return True
    except Exception as e:
        logger.error(f"Error in affiliate invitation process: {str(e)}")
        return False
    finally:
        inviter.close()

def main():
    parser = argparse.ArgumentParser(description='TikTok Affiliate Invitation Bot')
    parser.add_argument(
        '--invite-count',
        type=int,
        help='Number of invitation links to generate'
    )
    parser.add_argument(
        '--min-followers',
        type=int,
        help='Minimum number of followers required'
    )
    parser.add_argument(
        '--min-gmv',
        type=float,
        help='Minimum GMV threshold'
    )
    
    args = parser.parse_args()
    
    # Update configuration if command line arguments are provided
    if args.min_followers:
        TIKTOK_FILTERS['MIN_FOLLOWERS'] = args.min_followers
    if args.min_gmv:
        TARGET_GMV_THRESHOLD = args.min_gmv
    
    # Run the invitation process
    success = run_affiliate_inviter(args.invite_count)
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
