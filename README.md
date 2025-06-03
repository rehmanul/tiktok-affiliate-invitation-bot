<<<<<<< HEAD

# Digi4u Repair UK - TikTok Affiliate Invitation Bot

An automated bot for inviting TikTok creators to promote Digi4u Repair UK services through collaborations.

## Features

- Automated TikTok creator search and filtering
- Customizable filters for:
  - Follower count
  - Category
  - Promotion type (Video/Live)
- GMV-based targeting (highest to lowest)
- Automatic invitation link generation
- Detailed logging and tracking of invited affiliates

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rehmanul/Digi4u-Repair-Bot.git
cd Digi4u-Repair-Bot
```

2. Install dependencies:
=======
# TikTok Affiliate Bot

A production-ready automated system for managing TikTok Shop affiliate invitations. Built with Python, Selenium, and Flask.

## Features

- 🤖 Automated TikTok Shop login with session management
- 👥 Smart creator discovery and filtering
- 📊 Real-time dashboard for monitoring
- 🔄 Rate limiting and human-like behavior
- 🛡️ Anti-detection measures
- 🚀 Production-ready with Docker support
- ☁️ Easy deployment to Render.com

## Prerequisites

- Python 3.9+
- Google Chrome
- Docker (for containerized deployment)

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tiktok-affiliate-bot.git
cd tiktok-affiliate-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
>>>>>>> 0f14b6f (Initial commit of relevant project files)
```bash
pip install -r requirements.txt
```

<<<<<<< HEAD
## Usage

### Basic Usage
```bash
python -m src.main
```

### With Custom Parameters
```bash
python -m src.main --invite-count 50 --min-followers 20000 --min-gmv 10000
```

### Command Line Arguments

- `--invite-count`: Number of invitation links to generate
- `--min-followers`: Minimum number of followers required
- `--min-gmv`: Minimum GMV threshold for creators

## Configuration

Edit `src/config.py` to customize:
- TikTok search filters
- Business information
- GMV thresholds
- Logging settings

## Logging

Logs are stored in `affiliate_bot.log`. Invited affiliates are tracked in `invited_affiliates.csv`.

## Business Information

- Website: https://www.digi4u.co.uk/
- Services: Mobile and electronics repair
- Location: UK

## Safety Features

- Automatic stop when GMV threshold is reached
- Tracking of invited creators to prevent duplicates
- Error handling and logging
- Rate limiting to comply with TikTok's policies

## Note

This bot is designed for use with TikTok's platform. Please ensure compliance with TikTok's terms of service and API usage policies.
=======
4. Create a .env file:
```bash
FLASK_SECRET_KEY=your-secret-key
TIKTOK_EMAIL=your-tiktok-email
TIKTOK_PASSWORD=your-tiktok-password
```

5. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:8000`

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t tiktok-affiliate-bot .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 \
  -e FLASK_SECRET_KEY=your-secret-key \
  -e TIKTOK_EMAIL=your-tiktok-email \
  -e TIKTOK_PASSWORD=your-tiktok-password \
  tiktok-affiliate-bot
```

## Render.com Deployment

1. Fork this repository to your GitHub account

2. Connect your GitHub repository to Render.com

3. Create a new Web Service and select the repository

4. Render will automatically detect the `render.yaml` configuration

5. Set the following environment variables in the Render dashboard:
   - `FLASK_SECRET_KEY`
   - `TIKTOK_EMAIL`
   - `TIKTOK_PASSWORD`

6. Deploy! Render will automatically build and deploy your application

## Usage

1. Access the dashboard at your deployed URL or localhost:8000

2. Configure your bot settings:
   - Set minimum and maximum follower counts
   - Select product categories
   - Set maximum number of invitations to send

3. Click "Start Bot" to begin the automation

4. Monitor progress in real-time through the dashboard

5. Use the "Stop Bot" button to safely stop the automation at any time

## Safety Features

- Session management to prevent repeated logins
- Random delays between actions to mimic human behavior
- Anti-detection measures for browser automation
- Rate limiting to prevent account flags
- Error handling and automatic retries
- Secure credential management

## Monitoring and Logs

- Real-time status updates in the dashboard
- Detailed logging to `bot.log` and `webapp.log`
- Error tracking and reporting
- Campaign statistics and success rates

## Best Practices

1. Start with small batches to test the system
2. Monitor the first few invitations closely
3. Use reasonable delays between actions
4. Keep your TikTok credentials secure
5. Regularly check TikTok's terms of service for any changes

## Troubleshooting

### Common Issues

1. **Login Failures**
   - Check your TikTok credentials
   - Ensure no active sessions elsewhere
   - Verify network connectivity

2. **Browser Automation Issues**
   - Update Chrome and ChromeDriver
   - Check system resources
   - Verify proper permissions

3. **Rate Limiting**
   - Reduce invitation frequency
   - Increase delays between actions
   - Split campaigns into smaller batches

### Support

For issues and feature requests, please create an issue in the GitHub repository.

## License

MIT License - See LICENSE file for details

## Security

- Never commit credentials to version control
- Use environment variables for sensitive data
- Regularly update dependencies
- Monitor for suspicious activity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Disclaimer

This tool is for educational purposes only. Use responsibly and in accordance with TikTok's terms of service.
>>>>>>> 0f14b6f (Initial commit of relevant project files)
