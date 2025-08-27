import time
import functools
import random
import string
import re
from datetime import datetime, timedelta
from flask import session, redirect, url_for, request, jsonify
from config import *
from models import db
from config import CONFIG, REGISTRATION_RATE_LIMIT, REGISTRATION_TIME_WINDOW, API_RATE_LIMIT, API_TIME_WINDOW, USER_ACTIVITY_TIMEOUT

# Rate limiting storage
registration_attempts = {}
api_attempts = {}

def generate_key():
    chars = string.ascii_uppercase + string.digits
    return "OSIT-" + ''.join(random.choices(chars, k=4)) + "-" + ''.join(random.choices(chars, k=4))

def check_credits(username, required=None):
    if required is None:
        required = CONFIG['search_cost']
    user = db.get_user(username)
    if user:
        check_credits_expiry(username)
        return user.get('credits', 0) >= required
    return False

def deduct_credits(username, amount=None):
    if amount is None:
        amount = CONFIG['search_cost']
    user = db.get_user(username)
    if user:
        user['credits'] = max(0, user.get('credits', 0) - amount)
        db.save_user(username, user)
        return True
    return False

def rate_limit_check(ip, limit_type='registration'):
    current_time = time.time()
    
    if limit_type == 'registration':
        if ip not in registration_attempts:
            registration_attempts[ip] = {'count': 0, 'last_attempt': 0}
        attempts = registration_attempts[ip]
        max_attempts = REGISTRATION_RATE_LIMIT
        time_window = REGISTRATION_TIME_WINDOW
    else:
        if ip not in api_attempts:
            api_attempts[ip] = {'count': 0, 'last_attempt': 0}
        attempts = api_attempts[ip]
        max_attempts = API_RATE_LIMIT
        time_window = API_TIME_WINDOW
    
    if current_time - attempts['last_attempt'] > time_window:
        attempts['count'] = 0
    
    if attempts['count'] >= max_attempts:
        return False
    
    attempts['count'] += 1
    attempts['last_attempt'] = current_time
    return True

def check_credits_expiry(username):
    user = db.get_user(username)
    if user:
        if user.get('credits_expiry'):
            try:
                expiry_date = datetime.fromisoformat(user['credits_expiry'])
                if datetime.now() > expiry_date:
                    user['credits'] = 0
                    user['credits_expiry'] = None
                    db.save_user(username, user)
                    return False
            except Exception:
                pass
        return True
    return False

def update_user_activity(username):
    user = db.get_user(username)
    if user:
        user['last_activity'] = datetime.now().isoformat()
        db.save_user(username, user)
        
        # Store activity as a timestamp (float), not a dict
        activity_data = time.time()
        db.save_user_activity(username, activity_data)

def is_user_online(username):
    activity_data = db.get_user_activity()
    if username in activity_data:
        last_activity = activity_data[username]
        # Ensure last_activity is a float (timestamp)
        if isinstance(last_activity, dict):
            # If it's stored as a dict, try to extract timestamp
            last_activity = last_activity.get('timestamp', time.time())
        
        return time.time() - last_activity < USER_ACTIVITY_TIMEOUT
    return False

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        user = db.get_user(session['username'])
        if user and user.get('status') == 'banned':
            session.clear()
            return redirect(url_for('login'))
        update_user_activity(session['username'])
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        user = db.get_user(session['username'])
        if user and user.get('role') != 'admin':
            return redirect(url_for('dashboard'))
        update_user_activity(session['username'])
        return f(*args, **kwargs)
    return decorated_function

def clean_api_response(data):
    if isinstance(data, dict):
        unwanted_keys = ['dev', 'channel', '_resolved_region']
        return {k: v for k, v in data.items() if k.lower() not in unwanted_keys}
    return data

def api_protect(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if CONFIG['api_protection']:
            user_agent = request.headers.get('User-Agent', '')
            if 'curl' in user_agent.lower() or 'wget' in user_agent.lower() or 'python' in user_agent.lower():
                app.logger.warning(f"Suspicious API access attempt from {request.remote_addr}")
                return jsonify({'error': 'Unauthorized access'}), 403
        return f(*args, **kwargs)
    return decorated_function

def api_disabled_resp(key):
    apis_config_data = db.get_apis_config()
    msg = apis_config_data.get(key, {}).get('offline_message', 'This service is temporarily unavailable.')
    return jsonify({'error': 'SERVICE_DISABLED', 'message': msg}), 503

def cost_banner():
    return '<div style="text-align:center; color:var(--text-gray); margin-bottom:10px;">Each search costs <b>' + str(CONFIG['search_cost']) + '</b> credits</div>'