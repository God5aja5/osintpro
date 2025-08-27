import os
import secrets
import random

# Flask Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
PERMANENT_SESSION_LIFETIME_DAYS = 30
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Firebase Configuration (for auth only)
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyBpqelg9CHeZO2Z5yXQAHF1fqMBl3gy0Og",
    "authDomain": "native-igniter.firebaseapp.com",
    "databaseURL": "https://native-igniter-default-rtdb.firebaseio.com",
    "projectId": "native-igniter",
    "storageBucket": "native-igniter.appspot.com",
    "messagingSenderId": "12713798802",
    "appId": "1:12713798802:web:f2114bf79bd281ca524a4b"
}

# Global Configuration
CONFIG = {
    'search_cost': int(os.environ.get('SEARCH_COST', 2)),
    'api_protection': True,  # Enable API protection
    'admin_transfer_enabled': True  # Enable admin transfer functionality
}

# Live API Control config (editable in admin, live effect)
APIS_CONFIG = {
    'vehicle': {
        'name': 'Vehicle Information',
        'enabled': True,
        'url': 'https://glonova.in/vc.php/?ng={query}',
        'offline_message': 'Vehicle search is under maintenance. Please try again soon.'
    },
    'ifsc': {
        'name': 'IFSC Lookup',
        'enabled': True,
        'url': 'https://ifsc.razorpay.com/{query}',
        'offline_message': 'IFSC lookup is temporarily offline. Please try again later.'
    },
    'pincode': {
        'name': 'PIN Code Info',
        'enabled': True,
        'url': 'https://pincode-info-j4tnx.vercel.app/pincode={query}',
        'offline_message': 'Pincode service is under maintenance. Please try later.'
    },
    'ip': {
        'name': 'IP Information',
        'enabled': True,
        'url': 'https://ip-info.bjcoderx.workers.dev/?ip={query}',
        'offline_message': 'IP info is currently disabled. Please try again soon.'
    },
    'phone': {
        'name': 'Phone Lookup',
        'enabled': True,
        'url': 'http://xploide.site/Api.php?num={query}',
        'offline_message': 'Phone lookup is under maintenance. Please try again later.'
    },
    'freefire': {
        'name': 'Free Fire Stats',
        'enabled': True,
        'url': 'http://raw.thug4ff.com/info?uid={query}',
        'offline_message': 'Free Fire stats temporarily offline. Check back soon.'
    }
}

# Admin credentials
ADMIN_USERNAME = "God@Baign"
ADMIN_PASSWORD = "God@111983"

# Rate limiting settings
REGISTRATION_RATE_LIMIT = 3  # attempts
REGISTRATION_TIME_WINDOW = 3600  # seconds
API_RATE_LIMIT = 100  # attempts
API_TIME_WINDOW = 60  # seconds

# User activity timeout (seconds)
USER_ACTIVITY_TIMEOUT = 900  # 15 minutes