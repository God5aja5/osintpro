import uuid
from datetime import datetime
import random
from flask import session, redirect, url_for, request, jsonify
import re
from config import *
from models import db
from utils import update_user_activity, check_credits_expiry
import time
from config import FIREBASE_CONFIG

# Firebase token verification (placeholder)
def verify_firebase_token(id_token):
    try:
        # In a real implementation, you would verify the token with Firebase
        # For now, we'll just return True
        return True
    except Exception as e:
        app.logger.error(f"Firebase token verification error: {str(e)}")
        return False

def login_user(login_input, password):
    # Try to find user by username first
    user = db.get_user(login_input)
    
    # If not found by username, try by email
    if not user:
        user = db.get_user_by_email(login_input)
    
    if user:
        if user.get('status') == 'banned':
            return False, 'Account banned. Contact support.'
        
        from werkzeug.security import check_password_hash
        if not check_password_hash(user['password'], password):
            return False, 'Invalid password'
        
        # Check Firebase email verification status live
        is_verified = False
        try:
            import pyrebase
            firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
            auth = firebase.auth()
            firebase_user = auth.sign_in_with_email_and_password(user['email'], password)
            account_info = auth.get_account_info(firebase_user['idToken'])
            is_verified = account_info['users'][0].get('emailVerified', False)
        except Exception:
            # Fall back to local flag if Firebase call fails
            is_verified = user.get('email_verified', False)
        
        if is_verified:
            # Update local cache and login
            user['email_verified'] = True
            db.save_user(login_input, user)
            session['username'] = login_input
            session.permanent = True
            user['last_login'] = datetime.now().isoformat()
            user['last_activity'] = datetime.now().isoformat()
            user['ip_address'] = request.remote_addr
            db.save_user(login_input, user)
            update_user_activity(login_input)
            check_credits_expiry(login_input)
            return True, 'Login successful'
        else:
            return False, 'Email not verified. Please check your email for the verification link.'
    else:
        return False, 'User not found'

def register_user(username, email, password, ip_address):
    from utils import rate_limit_check
    from werkzeug.security import generate_password_hash
    
    if not rate_limit_check(ip_address, 'registration'):
        return False, 'Too many attempts. Try again later.'
    
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return False, 'Invalid username (3-20 characters, alphanumeric)'
    
    if db.get_user(username):
        return False, 'Username already exists'
    
    if db.get_user_by_email(email):
        return False, 'Email already registered'
    
    if len(password) < 6:
        return False, 'Password must be at least 6 characters'
    
    try:
        # Try to create user in Firebase
        firebase_user = None
        try:
            import pyrebase
            firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
            auth = firebase.auth()
            firebase_user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(firebase_user['idToken'])
        except Exception as e:
            # Check if the error is due to email already existing in Firebase
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                return False, "Email already exists in Firebase"
            else:
                # If Firebase is not available, continue with local registration
                pass
        
        user_data = {
            'id': str(uuid.uuid4()),
            'email': email,
            'password': generate_password_hash(password),
            'credits': 0,
            'credits_expiry': None,
            'role': 'user',
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'last_activity': datetime.now().isoformat(),
            'ip_address': ip_address,
            'status': 'active',
            'email_verified': False if firebase_user else True  # If no Firebase, mark as verified
        }
        db.save_user(username, user_data)
        
        return True, "Registration successful"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"