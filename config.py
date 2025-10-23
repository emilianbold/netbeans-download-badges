"""Configuration settings for download counter service"""
import os

# Flask settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
HOST = os.environ.get('HOST', '127.0.0.1')
PORT = int(os.environ.get('PORT', 5000))

# Database settings
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'downloads.db')

# Throttling settings
THROTTLE_HOURS = int(os.environ.get('THROTTLE_HOURS', 24))

# Badge settings
DEFAULT_BADGE_COLOR = '#007ec6'
DEFAULT_BADGE_LABEL = 'downloads'

# Sparkline settings
DEFAULT_SPARKLINE_DAYS = 30
SPARKLINE_WIDTH = 200
SPARKLINE_HEIGHT = 50
SPARKLINE_COLOR = '#007ec6'
