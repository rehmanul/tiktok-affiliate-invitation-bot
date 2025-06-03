<<<<<<< HEAD

from flask import Flask, render_template, jsonify, request
from tiktok_bot import TikTokAffiliateBot
import threading
import json
import os

app = Flask(__name__)
bot = None
campaign_thread = None

# Get port from environment variable (Render.com sets this)
port = int(os.environ.get('PORT', 5000))

# Get Chrome profile path from environment variable
default_chrome_profile = os.environ.get('CHROME_PROFILE_PATH', '/chrome-profile')

@app.route('/')
def index():
    return render_template('index.html', 
                         default_profile=default_chrome_profile)

@app.route('/api/start', methods=['POST'])
def start_campaign():
    global bot, campaign_thread
    
    config = request.json
    chrome_profile = config.get('chrome_profile', default_chrome_profile)
    
    if bot and bot.status['running']:
        return jsonify({
            'success': False,
            'error': 'Campaign already running'
        })
    
    bot = TikTokAffiliateBot(chrome_profile)
    campaign_thread = threading.Thread(
        target=bot.run_campaign,
        args=(config,)
    )
    campaign_thread.start()
    
    return jsonify({'success': True})

@app.route('/api/stop')
def stop_campaign():
    if bot:
        bot.stop_campaign()
        return jsonify({'success': True})
    return jsonify({
        'success': False,
        'error': 'No campaign running'
    })

@app.route('/api/status')
def get_status():
    if bot:
        return jsonify(bot.get_status())
    return jsonify({
        'running': False,
        'invites_sent': 0,
        'creators_found': 0,
        'current_creator': '',
        'last_error': None,
        'invite_links': []
    })

if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible externally
=======
from flask import Flask, render_template, request, jsonify, session, make_response
from tiktok_affiliate_bot import TikTokAffiliateBot
import os
from dotenv import load_dotenv
import logging
import threading
import time
from datetime import datetime

# Database imports and setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Campaign

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///tiktok_affiliate_bot.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route('/campaigns', methods=['POST'])
def create_campaign():
    """Create a new campaign"""
    try:
        data = request.json
        db = next(get_db())
        campaign = Campaign(
            name=data.get('name', f"Campaign {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
            min_followers=data.get('min_followers', 1000),
            max_followers=data.get('max_followers', 100000),
            min_gmv=data.get('min_gmv', 0),
            categories=','.join(data.get('categories', [])),
            promotion_types=','.join(data.get('promotion_types', [])),
            region=data.get('region', 'UK'),
            max_invites=data.get('max_invites', 50),
            status='pending'
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return jsonify({'message': 'Campaign created', 'campaign_id': campaign.id})
    except Exception as e:
        logging.error(f"Failed to create campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/campaigns', methods=['GET'])
def list_campaigns():
    """List all campaigns"""
    try:
        db = next(get_db())
        campaigns = db.query(Campaign).all()
        result = []
        for c in campaigns:
            result.append({
                'id': c.id,
                'name': c.name,
                'min_followers': c.min_followers,
                'max_followers': c.max_followers,
                'min_gmv': c.min_gmv,
                'categories': c.categories.split(',') if c.categories else [],
                'promotion_types': c.promotion_types.split(',') if c.promotion_types else [],
                'region': c.region,
                'max_invites': c.max_invites,
                'invites_sent': c.invites_sent,
                'status': c.status,
                'created_at': c.created_at.isoformat(),
                'updated_at': c.updated_at.isoformat() if c.updated_at else None
            })
        return jsonify(result)
    except Exception as e:
        logging.error(f"Failed to list campaigns: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/campaigns/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get campaign details"""
    try:
        db = next(get_db())
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        result = {
            'id': campaign.id,
            'name': campaign.name,
            'min_followers': campaign.min_followers,
            'max_followers': campaign.max_followers,
            'min_gmv': campaign.min_gmv,
            'categories': campaign.categories.split(',') if campaign.categories else [],
            'promotion_types': campaign.promotion_types.split(',') if campaign.promotion_types else [],
            'region': campaign.region,
            'max_invites': campaign.max_invites,
            'invites_sent': campaign.invites_sent,
            'status': campaign.status,
            'created_at': campaign.created_at.isoformat(),
            'updated_at': campaign.updated_at.isoformat() if campaign.updated_at else None
        }
        return jsonify(result)
    except Exception as e:
        logging.error(f"Failed to get campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Register after_request handler
@app.after_request
def after_request(response):
    return add_cors_headers(response)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webapp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global bot instance and status
bot_instance = None
bot_status = {
    'is_running': False,
    'total_invites': 0,
    'last_update': None,
    'current_status': 'Idle',
    'error': None
}

def update_status(status, error=None):
    """Update bot status"""
    bot_status['current_status'] = status
    bot_status['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if error:
        bot_status['error'] = str(error)
        logger.error(f"Bot error: {error}")
    else:
        bot_status['error'] = None

def check_status():
    """Check current bot status"""
    global bot_status
    
    # Get the last 100 lines from the log file
    log_messages = []
    try:
        with open('bot.log', 'r') as f:
            log_messages = f.readlines()[-100:]
    except Exception as e:
        logger.error(f"Failed to read log file: {str(e)}")
    
    # Add account info and logs to status
    status = bot_status.copy()
    status['log_messages'] = log_messages
    
    # Add account email from session if available
    if os.path.exists('session.json'):
        try:
            with open('session.json', 'r') as f:
                session_data = json.load(f)
                if session_data.get('credentials', {}).get('email'):
                    status['account_email'] = session_data['credentials']['email']
        except Exception as e:
            logger.error(f"Failed to read session file: {str(e)}")
    
    return status

def bot_worker(filters, max_invites, campaign_id=None):
    """Background worker for bot operations"""
    global bot_instance, bot_status
    
    from sqlalchemy.orm import sessionmaker
    from src.models import Campaign
    from src.creator_sync import sync_creators
    db = None
    
    try:
        bot_status['is_running'] = True
        update_status('Starting bot...')
        
        # Initialize bot
        bot_instance = TikTokAffiliateBot()
        
        # Start browser
        update_status('Starting browser...')
        if not bot_instance.start_browser():
            raise Exception("Failed to start browser")
            
        # Login
        update_status('Logging in...')
        if not bot_instance.login():
            raise Exception("Failed to login")
            
        # Navigate to affiliate page
        update_status('Navigating to affiliate page...')
        if not bot_instance.navigate_to_affiliate_page():
            raise Exception("Failed to navigate to affiliate page")
        
        # Create DB session
        from sqlalchemy import create_engine
        engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///tiktok_affiliate_bot.db'), connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Sync creators before applying filters
        update_status('Syncing creators...')
        sync_creators(bot_instance.driver, db)
        
        # Apply filters
        update_status('Applying filters...')
        if not bot_instance.apply_filters(**filters):
            raise Exception("Failed to apply filters")
            
        # Send invitations with campaign tracking
        update_status('Sending invitations...')
        
        invites_sent = bot_instance.send_invitations(max_invites=max_invites, campaign_id=campaign_id, db_session=db)
        bot_status['total_invites'] = invites_sent
        
        # Update campaign status
        if campaign_id:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if campaign:
                campaign.status = 'completed'
                campaign.invites_sent = invites_sent
                db.commit()
        
        update_status(f'Completed! Sent {invites_sent} invitations')
        
    except Exception as e:
        update_status('Error occurred', error=str(e))
    finally:
        if bot_instance:
            bot_instance.close()
        if db:
            db.close()
        bot_status['is_running'] = False

@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html', status=bot_status)

@app.route('/connect', methods=['POST'])
def connect_tiktok():
    """Test TikTok Shop connection"""
    global bot_instance, bot_status
    
    try:
        temp_bot = TikTokAffiliateBot()
        if not temp_bot.start_browser():
            raise Exception("Failed to start browser")
            
        # Test login
        if temp_bot.login():
            update_status('Connected to TikTok Shop')
            return jsonify({'message': 'Connected successfully'})
        else:
            raise Exception("Failed to connect to TikTok Shop")
            
    except Exception as e:
        update_status('Connection failed', error=str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        if temp_bot:
            temp_bot.close()

@app.route('/start', methods=['POST'])
def start_bot():
    """Start bot with specified parameters"""
    if bot_status['is_running']:
        return jsonify({'error': 'Bot is already running'}), 400
        
    try:
        data = request.json
        filters = {
            'min_followers': int(data.get('min_followers', 1000)),
            'max_followers': int(data.get('max_followers', 2000)),
            'min_gmv': int(data.get('min_gmv', 1000)),
            'categories': data.get('categories', ['Phone & Electronics', 'Computer and office equipment'])
        }
        max_invites = int(data.get('max_invites', 50))
        campaign_id = data.get('campaign_id')
        
        # Start bot in background thread
        thread = threading.Thread(
            target=bot_worker,
            args=(filters, max_invites, campaign_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': 'Bot started successfully'})
        
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop_bot():
    """Stop the running bot"""
    global bot_instance, bot_status
    
    if not bot_status['is_running']:
        return jsonify({'error': 'Bot is not running'}), 400
        
    try:
        if bot_instance:
            bot_instance.close()
            bot_instance = None
            
        bot_status['is_running'] = False
        update_status('Stopped by user')
        
        return jsonify({'message': 'Bot stopped successfully'})
        
    except Exception as e:
        logger.error(f"Failed to stop bot: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def get_status():
    """Get current bot status"""
    response = make_response(jsonify(bot_status))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/user_email')
def get_user_email():
    """Get logged-in user email from session"""
    try:
        if os.path.exists('session.json'):
            with open('session.json', 'r') as f:
                session_data = json.load(f)
                email = session_data.get('credentials', {}).get('email', None)
                if email:
                    return jsonify({'email': email})
        return jsonify({'email': None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # For production, use gunicorn or similar WSGI server
    port = int(os.getenv('PORT', 8000))
>>>>>>> 0f14b6f (Initial commit of relevant project files)
    app.run(host='0.0.0.0', port=port)
