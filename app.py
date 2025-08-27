import os
import json
import time
import uuid
import random
import requests
import base64
from utils import *
from auth import * 
from models import *
from io import BytesIO
from datetime import datetime, timedelta

# Import Flask first
from flask import Flask, request, redirect, url_for, session, jsonify, render_template_string, send_file
from werkzeug.security import generate_password_hash, check_password_hash

# Create the Flask app
app = Flask(__name__)

# Import our modules
from config import SECRET_KEY, PERMANENT_SESSION_LIFETIME_DAYS, FIREBASE_CONFIG, CONFIG, APIS_CONFIG
from models import db, init_db
from utils import (
    login_required, admin_required, check_credits, deduct_credits, rate_limit_check,
    update_user_activity, is_user_online, clean_api_response, api_protect, api_disabled_resp, cost_banner
)
from auth import login_user, register_user
from templates import get_base_template, COMPLETE_STYLE, GLOBAL_SCRIPT  # Fixed typo here

# Configure the app
app.secret_key = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=PERMANENT_SESSION_LIFETIME_DAYS)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Firebase (for auth only)
try:
    import pyrebase
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    auth = firebase.auth()
except ImportError:
    # Fallback if pyrebase is not available
    auth = None

# Import and register routes after app is created
from routes import register_routes
register_routes(app)

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('username', '').strip()  # Can be username or email
        password = request.form.get('password', '')
        
        success, message = login_user(login_input, password)
        
        if success:
            return redirect(url_for('dashboard'))
        else:
            content = (
                '<div class="verification-container">'
                '<div style="text-align: center; margin-bottom: 30px;">'
                '<h1 style="font-size: 2.5rem; font-weight: 900; background: linear-gradient(135deg, var(--primary-red), var(--accent-red)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">OSINT Tool</h1>'
                '<p style="color: var(--text-gray);">Secure Intelligence Dashboard</p></div>'
                '<form method="POST">'
                '<div class="form-group"><label>Username or Email</label><input type="text" name="username" required></div>'
                '<div class="form-group"><label>Password</label><input type="password" name="password" required></div>'
                '<button type="submit" class="btn" style="width: 100%;">Login</button></form>'
                '<div style="text-align: center; margin-top: 20px;"><a href="/register" style="color: var(--primary-red);">Create Account</a></div>'
                '<div style="background: rgba(220, 38, 38, 0.1); padding: 15px; border-radius: 10px; margin-top: 20px; color: var(--primary-red);">' + message + '</div>'
                '</div>'
            )
            return get_base_template('Login - OSINT Tool', content)
    
    content = '''
    <div class="verification-container">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-size: 2.5rem; font-weight: 900; background: linear-gradient(135deg, var(--primary-red), var(--accent-red)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">OSINT Tool</h1>
            <p style="color: var(--text-gray);">Secure Intelligence Dashboard</p>
        </div>
        <form method="POST">
            <div class="form-group"><label>Username or Email</label><input type="text" name="username" required></div>
            <div class="form-group"><label>Password</label><input type="password" name="password" required></div>
            <button type="submit" class="btn" style="width: 100%;">Login</button>
        </form>
        <div style="text-align: center; margin-top: 20px;"><a href="/register" style="color: var(--primary-red);">Create Account</a></div>
    </div>
    '''
    return get_base_template('Login - OSINT Tool', content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        ip_address = request.remote_addr
        
        success, message = register_user(username, email, password, ip_address)
        
        if success:
            if auth:
                content = '''
                <div class="firebase-verification">
                    <div style="text-align: center;">
                        <h2 style="color: var(--success-green);">Registration Successful!</h2>
                        <p style="color: var(--text-gray); margin: 20px 0;">A verification email has been sent to your email address.</p>
                        <div class="email-display" style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59,130,246,0.3); padding: 12px; border-radius: 10px; color: var(--info-blue);">''' + email + '''</div>
                        <p style="color: var(--text-gray); margin: 20px 0;">Please click the verification link, then return to login.</p>
                        <p style="color: var(--warning-yellow); margin: 20px 0;">If you don\'t receive the email within a few minutes, please check your spam folder.</p>
                        <a href="/login" class="btn">Go to Login</a>
                    </div>
                </div>
                '''
            else:
                content = '''
                <div class="firebase-verification">
                    <div style="text-align: center;">
                        <h2 style="color: var(--success-green);">Registration Successful!</h2>
                        <p style="color: var(--text-gray); margin: 20px 0;">Your account has been created successfully.</p>
                        <a href="/login" class="btn">Go to Login</a>
                    </div>
                </div>
                '''
            return get_base_template('Registration Successful - OSINT Tool', content)
        else:
            content = (
                '<div class="verification-container">'
                '<div style="text-align: center; margin-bottom: 30px;"><h1 style="font-size: 2.2rem; font-weight: 900; background: linear-gradient(135deg, var(--primary-red), var(--accent-red)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Register</h1></div>'
                '<form method="POST">'
                '<div class="form-group"><label>Username</label><input type="text" name="username" value="' + username + '" required></div>'
                '<div class="form-group"><label>Email</label><input type="email" name="email" value="' + email + '" required></div>'
                '<div class="form-group"><label>Password (min 6 chars)</label><input type="password" name="password" minlength="6" required></div>'
                '<button type="submit" class="btn" style="width: 100%;">Register</button></form>'
                '<div style="background: rgba(220, 38, 38, 0.1); padding: 15px; border-radius: 10px; margin-top: 20px; color: var(--primary-red);">' + message + '</div>'
                '<div style="text-align: center; margin-top: 20px;"><a href="/login" style="color: var(--primary-red);">Already have account?</a></div>'
                '</div>'
            )
            return get_base_template('Register - OSINT Tool', content)
    
    content = '''
    <div class="verification-container">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-size: 2.2rem; font-weight: 900; background: linear-gradient(135deg, var(--primary-red), var(--accent-red)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Register</h1>
        </div>
        <form method="POST">
            <div class="form-group"><label>Username</label><input type="text" name="username" pattern="[a-zA-Z0-9_]{3,20}" required></div>
            <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
            <div class="form-group"><label>Password (min 6 chars)</label><input type="password" name="password" minlength="6" required></div>
            <button type="submit" class="btn" style="width: 100%;">Register</button>
        </form>
        <div style="text-align: center; margin-top: 20px;"><a href="/login" style="color: var(--primary-red);">Already have account?</a></div>
    </div>
    '''
    return get_base_template('Register - OSINT Tool', content)

@app.route('/logout')
def logout():
    if 'username' in session:
        activity_data = db.get_user_activity()
        if session['username'] in activity_data:
            del activity_data[session['username']]
            db.save_user_activity(session['username'], activity_data)
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = db.get_user(session['username'])
    check_credits_expiry(session['username'])
    credits_expiry = ''
    if user.get('credits_expiry'):
        try:
            expiry = datetime.fromisoformat(user['credits_expiry'])
            credits_expiry = "<div style='font-size: 0.8rem; color: var(--warning-yellow);'>Expires: " + expiry.strftime('%Y-%m-%d') + "</div>"
        except Exception:
            pass
    
    content = (
        '<div class="credits-display"><div>Credits: <span style="color: var(--success-green); font-size: 1.2rem; font-weight: 700;">'
        + str(user.get('credits', 0)) + '</span></div>' + credits_expiry + '<div style="font-size:.8rem;color:var(--text-gray);margin-top:6px;">Per search: ' + str(CONFIG['search_cost']) + ' credits</div></div>'
        '<div class="user-info">'
        '<span>Welcome, ' + session['username'] + '</span>'
        '<a href="/profile" style="padding: 8px 15px; background: rgba(220, 38, 38, 0.2); border-radius: 8px; color: white; text-decoration: none;">Profile</a>'
        '<a href="/pricing" style="padding: 8px 15px; background: rgba(220, 38, 38, 0.2); border-radius: 8px; color: white; text-decoration: none;">Pricing</a>'
        '<a href="/tickets" style="padding: 8px 15px; background: rgba(220, 38, 38, 0.2); border-radius: 8px; color: white; text-decoration: none;">Support</a>'
        + ('<a href="/admin" style="padding: 8px 15px; background: rgba(168, 85, 247, 0.3); border-radius: 8px; color: white; text-decoration: none;">Admin</a>' if user.get('role') == 'admin' else '')
        + '<a href="/logout" style="padding: 8px 15px; background: linear-gradient(135deg, var(--primary-red), var(--secondary-red)); border-radius: 8px; color: white; text-decoration: none;">Logout</a>'
        '</div>'
        '<div style="margin-top: 80px;"><div class="header"><h1>OSINT Tool</h1>'
        '<p style="color: var(--text-gray);">Advanced Information Gathering Platform</p></div>'
        '<div class="tools-grid">'
        '<a href="/vehicle-info" class="tool-card" onclick="playSound(\'click\')"><i class="fas fa-car" style="font-size: 3rem; color: var(--primary-red); margin-bottom: 20px;"></i><h3 style="color: white; margin-bottom: 10px;">Vehicle Information</h3><p style="color: var(--text-gray);">Get vehicle details using registration number</p></a>'
        '<a href="/ifsc-info" class="tool-card" onclick="playSound(\'click\')"><i class="fas fa-university" style="font-size: 3rem; color: var(--primary-red); margin-bottom: 20px;"></i><h3 style="color: white; margin-bottom: 10px;">IFSC Lookup</h3><p style="color: var(--text-gray);">Find bank branch details using IFSC code</p></a>'
        '<a href="/pincode-info" class="tool-card" onclick="playSound(\'click\')"><i class="fas fa-map-marker-alt" style="font-size: 3rem; color: var(--primary-red); margin-bottom: 20px;"></i><h3 style="color: white; margin-bottom: 10px;">PIN Code Info</h3><p style="color: var(--text-gray);">Get location details from PIN code</p></a>'
        '<a href="/ip-info" class="tool-card" onclick="playSound(\'click\')"><i class="fas fa-globe" style="font-size: 3rem; color: var(--primary-red); margin-bottom: 20px;"></i><h3 style="color: white; margin-bottom: 10px;">IP Information</h3><p style="color: var(--text-gray);">Geolocation and ISP information</p></a>'
        '<a href="/phone-info" class="tool-card" onclick="playSound(\'click\')"><i class="fas fa-phone" style="font-size: 3rem; color: var(--primary-red); margin-bottom: 20px;"></i><h3 style="color: white; margin-bottom: 10px;">Phone Lookup</h3><p style="color: var(--text-gray);">Get phone number information</p></a>'
        '<a href="/freefire-info" class="tool-card" onclick="playSound(\'click\')"><i class="fas fa-gamepad" style="font-size: 3rem; color: var(--primary-red); margin-bottom: 20px;"></i><h3 style="color: white; margin-bottom: 10px;">FreeFire Stats</h3><p style="color: var(--text-gray);">Player statistics and information</p></a>'
        '</div></div>'
    )
    return get_base_template('Dashboard - OSINT Tool', content)

# API Routes
@app.route('/api/vehicle/<vehicle_number>')
@login_required
@api_protect
def api_vehicle(vehicle_number):
    if not rate_limit_check(request.remote_addr, 'api'):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    if not check_credits(session['username']):
        return jsonify({'error': 'Insufficient credits'}), 403
    apis_config_data = db.get_apis_config()
    cfg = apis_config_data.get('vehicle', {})
    if not cfg.get('enabled', True):
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'vehicle',
            'query': vehicle_number,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return api_disabled_resp('vehicle')
    try:
        url = cfg.get('url', 'https://glonova.in/vc.php/?ng={query}').replace('{query}', vehicle_number.upper())
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            text = response.text
            data = {}
            for line in text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip()
            if data and len(data) > 3:
                deduct_credits(session['username'])
                db.add_search_log({
                    'id': str(uuid.uuid4()),
                    'username': session['username'],
                    'type': 'vehicle',
                    'query': vehicle_number,
                    'success': True,
                    'credits': CONFIG['search_cost'],
                    'timestamp': datetime.now().isoformat()
                })
                return jsonify({'d': clean_api_response(data)})
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'vehicle',
            'query': vehicle_number,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return jsonify({'error': 'No data found'}), 404
    except Exception as e:
        app.logger.error(f"Vehicle API error: {str(e)}")
        return jsonify({'error': 'Service error'}), 500

@app.route('/api/ifsc/<ifsc_code>')
@login_required
@api_protect
def api_ifsc(ifsc_code):
    if not rate_limit_check(request.remote_addr, 'api'):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    if not check_credits(session['username']):
        return jsonify({'error': 'Insufficient credits'}), 403
    apis_config_data = db.get_apis_config()
    cfg = apis_config_data.get('ifsc', {})
    if not cfg.get('enabled', True):
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'ifsc',
            'query': ifsc_code,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return api_disabled_resp('ifsc')
    try:
        url = cfg.get('url', 'https://ifsc.razorpay.com/{query}').replace('{query}', ifsc_code.upper())
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            deduct_credits(session['username'])
            db.add_search_log({
                'id': str(uuid.uuid4()),
                'username': session['username'],
                'type': 'ifsc',
                'query': ifsc_code,
                'success': True,
                'credits': CONFIG['search_cost'],
                'timestamp': datetime.now().isoformat()
            })
            return jsonify({'d': clean_api_response(data)})
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'ifsc',
            'query': ifsc_code,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return jsonify({'error': 'Invalid IFSC'}), 404
    except Exception as e:
        app.logger.error(f"IFSC API error: {str(e)}")
        return jsonify({'error': 'Service error'}), 500

@app.route('/api/pincode/<pincode>')
@login_required
@api_protect
def api_pincode(pincode):
    if not rate_limit_check(request.remote_addr, 'api'):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    if not check_credits(session['username']):
        return jsonify({'error': 'Insufficient credits'}), 403
    apis_config_data = db.get_apis_config()
    cfg = apis_config_data.get('pincode', {})
    if not cfg.get('enabled', True):
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'pincode',
            'query': pincode,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return api_disabled_resp('pincode')
    try:
        url = cfg.get('url', 'https://pincode-info-j4tnx.vercel.app/pincode={query}').replace('{query}', pincode)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                result = data[0]
                deduct_credits(session['username'])
                db.add_search_log({
                    'id': str(uuid.uuid4()),
                    'username': session['username'],
                    'type': 'pincode',
                    'query': pincode,
                    'success': True,
                    'credits': CONFIG['search_cost'],
                    'timestamp': datetime.now().isoformat()
                })
                return jsonify({'d': clean_api_response(result)})
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'pincode',
            'query': pincode,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return jsonify({'error': 'Invalid PIN'}), 404
    except Exception as e:
        app.logger.error(f"PIN code API error: {str(e)}")
        return jsonify({'error': 'Service error'}), 500

@app.route('/api/ip/<ip_address>')
@login_required
@api_protect
def api_ip(ip_address):
    if not rate_limit_check(request.remote_addr, 'api'):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    if not check_credits(session['username']):
        return jsonify({'error': 'Insufficient credits'}), 403
    apis_config_data = db.get_apis_config()
    cfg = apis_config_data.get('ip', {})
    if not cfg.get('enabled', True):
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'ip',
            'query': ip_address,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return api_disabled_resp('ip')
    try:
        url = cfg.get('url', 'https://ip-info.bjcoderx.workers.dev/?ip={query}').replace('{query}', ip_address)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            deduct_credits(session['username'])
            db.add_search_log({
                'id': str(uuid.uuid4()),
                'username': session['username'],
                'type': 'ip',
                'query': ip_address,
                'success': True,
                'credits': CONFIG['search_cost'],
                'timestamp': datetime.now().isoformat()
            })
            return jsonify({'d': clean_api_response(data)})
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'ip',
            'query': ip_address,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return jsonify({'error': 'Invalid IP'}), 404
    except Exception as e:
        app.logger.error(f"IP API error: {str(e)}")
        return jsonify({'error': 'Service error'}), 500

@app.route('/api/phone/<phone_number>')
@login_required
@api_protect
def api_phone(phone_number):
    if not rate_limit_check(request.remote_addr, 'api'):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    if not check_credits(session['username']):
        return jsonify({'error': 'Insufficient credits'}), 403
    apis_config_data = db.get_apis_config()
    cfg = apis_config_data.get('phone', {})
    if not cfg.get('enabled', True):
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'phone',
            'query': phone_number,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return api_disabled_resp('phone')
    try:
        url = cfg.get('url', 'http://xploide.site/Api.php?num={query}').replace('{query}', phone_number)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                deduct_credits(session['username'])
                db.add_search_log({
                    'id': str(uuid.uuid4()),
                    'username': session['username'],
                    'type': 'phone',
                    'query': phone_number,
                    'success': True,
                    'credits': CONFIG['search_cost'],
                    'timestamp': datetime.now().isoformat()
                })
                return jsonify({'d': data})
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'phone',
            'query': phone_number,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return jsonify({'error': 'No data found'}), 404
    except Exception as e:
        app.logger.error(f"Phone API error: {str(e)}")
        return jsonify({'error': 'Service error'}), 500

@app.route('/api/freefire/<uid>')
@login_required
@api_protect
def api_freefire(uid):
    if not rate_limit_check(request.remote_addr, 'api'):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    if not check_credits(session['username']):
        return jsonify({'error': 'Insufficient credits'}), 403
    apis_config_data = db.get_apis_config()
    cfg = apis_config_data.get('freefire', {})
    if not cfg.get('enabled', True):
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'freefire',
            'query': uid,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return api_disabled_resp('freefire')
    try:
        url = cfg.get('url', 'http://raw.thug4ff.com/info?uid={query}').replace('{query}', uid)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and 'basicInfo' in data:
                deduct_credits(session['username'])
                db.add_search_log({
                    'id': str(uuid.uuid4()),
                    'username': session['username'],
                    'type': 'freefire',
                    'query': uid,
                    'success': True,
                    'credits': CONFIG['search_cost'],
                    'timestamp': datetime.now().isoformat()
                })
                return jsonify({'d': clean_api_response(data)})
        db.add_search_log({
            'id': str(uuid.uuid4()),
            'username': session['username'],
            'type': 'freefire',
            'query': uid,
            'success': False,
            'credits': 0,
            'timestamp': datetime.now().isoformat()
        })
        return jsonify({'error': 'Player not found'}), 404
    except Exception as e:
        app.logger.error(f"FreeFire API error: {str(e)}")
        return jsonify({'error': 'Service error'}), 500

@app.route('/api/redeem-key', methods=['POST'])
@login_required
def api_redeem_key():
    key = request.json.get('key', '').upper()
    key_data = db.get_key(key)
    if key_data and key_data['status'] == 'unused':
        credits = key_data['credits']
        user = db.get_user(session['username'])
        user['credits'] += credits
        if key_data.get('expiry_days'):
            user['credits_expiry'] = (datetime.now() + timedelta(days=key_data['expiry_days'])).isoformat()
        db.save_user(session['username'], user)
        key_data['status'] = 'used'
        key_data['used_by'] = session['username']
        db.save_key(key, key_data)
        return jsonify({'success': True, 'credits': credits})
    return jsonify({'error': 'Invalid or used key'}), 400

@app.route('/api/delete-account', methods=['POST'])
@login_required
def api_delete_account():
    try:
        username = session['username']
        
        # Delete user from database
        if db.delete_user(username):
            # Clear session
            session.clear()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete account'}), 400
    except Exception as e:
        app.logger.error(f"Error deleting account: {str(e)}")
        return jsonify({'error': 'An error occurred while deleting your account'}), 500

@app.route('/api/create-ticket', methods=['POST'])
@login_required
def api_create_ticket():
    user = db.get_user(session['username'])
    ticket_id = str(uuid.uuid4())
    ticket_data = {
        'user_id': user['id'],
        'username': session['username'],
        'subject': request.json.get('subject'),
        'message': request.json.get('message'),
        'status': 'OPEN',
        'created_at': datetime.now().isoformat()
    }
    db.save_ticket(ticket_id, ticket_data)
    return jsonify({'success': True, 'ticket_id': ticket_id})

@app.route('/api/reply-ticket', methods=['POST'])
@login_required
def api_reply_ticket():
    ticket_id = request.form.get('ticket_id')
    message = request.form.get('message')
    
    tickets_data = db.get_tickets()
    if ticket_id not in tickets_data:
        return jsonify({'error': 'Ticket not found'}), 404
    
    reply_data = {
        'username': session['username'],
        'message': message,
        'is_admin': db.get_user(session['username']).get('role') == 'admin',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    if 'attachment' in request.files and request.files['attachment']:
        file = request.files['attachment']
        if file.filename != '':
            attachment_id = str(uuid.uuid4())
            file_data = file.read()
            file_base64 = base64.b64encode(file_data).decode('utf-8')
            attachment_data = {
                'filename': file.filename,
                'data': file_base64,
                'content_type': file.content_type or 'application/octet-stream',
                'size': len(file_data)
            }
            db.save_ticket_attachment(attachment_id, attachment_data)
            reply_data['attachment_id'] = attachment_id
    
    db.save_ticket_reply(ticket_id, reply_data)
    return jsonify({'success': True})

@app.route('/api/close-ticket', methods=['POST'])
@admin_required
def api_close_ticket():
    ticket_id = request.json.get('ticket_id')
    tickets_data = db.get_tickets()
    if ticket_id in tickets_data:
        tickets_data[ticket_id]['status'] = 'CLOSED'
        db.save_ticket(ticket_id, tickets_data[ticket_id])
        return jsonify({'success': True})
    return jsonify({'error': 'Ticket not found'}), 404

@app.route('/api/attachment/<attachment_id>')
def get_attachment(attachment_id):
    attachment = db.get_ticket_attachment(attachment_id)
    if not attachment:
        return jsonify({'error': 'Attachment not found'}), 404
    file_data = base64.b64decode(attachment['data'])
    return send_file(BytesIO(file_data), mimetype=attachment['content_type'], as_attachment=True, download_name=attachment['filename'])

# Admin API Routes
@app.route('/api/admin/modify-credits', methods=['POST'])
@admin_required
def admin_modify_credits():
    username = request.json.get('username')
    action = request.json.get('action')
    amount = int(request.json.get('amount', 0))
    
    user = db.get_user(username)
    if user:
        if action == 'add':
            user['credits'] += amount
        elif action == 'remove':
            user['credits'] = max(0, user['credits'] - amount)
        db.save_user(username, user)
        return jsonify({'success': True})
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/admin/generate-key', methods=['POST'])
@admin_required
def admin_generate_key():
    from utils import generate_key
    credits = int(request.json.get('credits', 0))
    days = int(request.json.get('days', 0))
    if credits <= 0:
        return jsonify({'error': 'Invalid credits'}), 400
    key = generate_key()
    key_data = {
        'credits': credits,
        'expiry_days': days if days > 0 else None,
        'status': 'unused',
        'created_at': datetime.now().isoformat()
    }
    db.save_key(key, key_data)
    return jsonify({'success': True, 'key': key})

@app.route('/api/admin/config', methods=['POST'])
@admin_required
def admin_config():
    sc = int(request.json.get('search_cost', CONFIG['search_cost']))
    if sc < 1 or sc > 10000:
        return jsonify({'error': 'Invalid search cost'}), 400
    CONFIG['search_cost'] = sc
    db.save_config(CONFIG)
    return jsonify({'success': True, 'search_cost': sc})

@app.route('/api/admin/toggle-status', methods=['POST'])
@admin_required
def admin_toggle_status():
    username = request.json.get('username')
    user = db.get_user(username)
    if user:
        current = user.get('status', 'active')
        user['status'] = 'banned' if current == 'active' else 'active'
        db.save_user(username, user)
        return jsonify({'success': True, 'status': user['status']})
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/admin/toggle-api-protection', methods=['POST'])
@admin_required
def admin_toggle_api_protection():
    CONFIG['api_protection'] = not CONFIG['api_protection']
    db.save_config(CONFIG)
    return jsonify({'success': True, 'api_protection': CONFIG['api_protection']})

@app.route('/api/admin/transfer-admin', methods=['POST'])
@admin_required
def admin_transfer_admin():
    if not CONFIG['admin_transfer_enabled']:
        return jsonify({'error': 'Admin transfer is disabled'}), 400
    username = request.json.get('username')
    user = db.get_user(username)
    if user and user.get('role') == 'admin':
        current_admin = db.get_user(session['username'])
        current_admin['role'] = 'user'
        db.save_user(session['username'], current_admin)
        user['role'] = 'admin'
        db.save_user(username, user)
        return jsonify({'success': True, 'message': f'Admin rights transferred to {username}'})
    return jsonify({'error': 'Invalid user or user is not an admin'}), 400

@app.route('/api/admin/download-data', methods=['GET'])
@admin_required
def admin_download_data():
    try:
        # Get all data from the database
        all_data = db.get_all_data()
        
        # Create a JSON string from the data
        json_data = json.dumps(all_data, indent=2)
        
        # Create a BytesIO object to hold the data
        data_stream = BytesIO(json_data.encode('utf-8'))
        
        # Generate a filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"osint_data_backup_{timestamp}.json"
        
        # Return the file as a download
        return send_file(
            data_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
    except Exception as e:
        app.logger.error(f"Error downloading data: {str(e)}")
        return jsonify({'error': 'Failed to download data'}), 500

@app.route('/api/admin/apis', methods=['GET'])
@admin_required
def admin_get_apis():
    apis_config_data = db.get_apis_config()
    return jsonify({'success': True, 'apis': apis_config_data})

@app.route('/api/admin/apis/toggle', methods=['POST'])
@admin_required
def admin_toggle_api():
    key = request.json.get('key')
    apis_config_data = db.get_apis_config()
    if key not in apis_config_data:
        return jsonify({'error': 'Invalid API key'}), 400
    apis_config_data[key]['enabled'] = not apis_config_data[key]['enabled']
    state = apis_config_data[key]['enabled']
    db.save_apis_config(apis_config_data)
    return jsonify({'success': True, 'enabled': state, 'message': f"{apis_config_data[key]['name']} {'Enabled' if state else 'Disabled'}"})

@app.route('/api/admin/apis/update', methods=['POST'])
@admin_required
def admin_update_api():
    key = request.json.get('key')
    name = request.json.get('name', '').strip()
    url = request.json.get('url', '').strip()
    offline_message = request.json.get('offline_message', '').strip()
    apis_config_data = db.get_apis_config()
    if key not in apis_config_data:
        return jsonify({'error': 'Invalid API key'}), 400
    if not url or '{query}' not in url:
        return jsonify({'error': "URL must include '{query}' placeholder"}), 400
    if name:
        apis_config_data[key]['name'] = name
    apis_config_data[key]['url'] = url
    if offline_message:
        apis_config_data[key]['offline_message'] = offline_message
    db.save_apis_config(apis_config_data)
    return jsonify({'success': True})

@app.route('/api/health')
def health():
    return jsonify({'ok': True, 'time': datetime.now().isoformat(), 'search_cost': CONFIG['search_cost']})

@app.errorhandler(404)
def not_found(e):
    return redirect('/')

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# Initialize the database when the app starts
init_db()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)