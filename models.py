import os
import json
import threading
import random
from config import *
import uuid
import time
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from config import CONFIG, APIS_CONFIG, ADMIN_USERNAME, ADMIN_PASSWORD

class LocalDB:
    def __init__(self):
        # Use current directory instead of /tmp to avoid read-only file system issues
        self.db_dir = os.path.join(os.getcwd(), 'osint_data')
        self.db_file = os.path.join(self.db_dir, 'osint_db.json')
        self.lock = threading.Lock()
        self.data = self._load_db()
        
    def _load_db(self):
        try:
            # Ensure directory exists
            os.makedirs(self.db_dir, exist_ok=True)
            
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading database: {e}")
        
        # Default database structure
        return {
            "users": {},
            "keys": {},
            "search_logs": [],
            "tickets": {},
            "ticket_replies": {},
            "ticket_attachments": {},
            "api_tokens": {},
            "user_activity": {},
            "apis_config": APIS_CONFIG,
            "config": CONFIG
        }
    
    def _save_db(self):
        try:
            # Ensure directory exists before saving
            os.makedirs(self.db_dir, exist_ok=True)
            
            # Create a deep copy of the data to avoid circular references
            data_to_save = self._deep_copy(self.data)
            
            with open(self.db_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def _deep_copy(self, obj):
        """Create a deep copy of an object, handling circular references"""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
    
    def get_user(self, username):
        with self.lock:
            return self.data["users"].get(username)
    
    def get_user_by_email(self, email):
        with self.lock:
            for username, user in self.data["users"].items():
                if user.get('email') == email:
                    return user
            return None
    
    def save_user(self, username, user_data):
        with self.lock:
            self.data["users"][username] = user_data
            self._save_db()
            return True
    
    def delete_user(self, username):
        with self.lock:
            if username in self.data["users"]:
                del self.data["users"][username]
                self._save_db()
                return True
            return False
    
    def get_key(self, key):
        with self.lock:
            return self.data["keys"].get(key)
    
    def save_key(self, key, key_data):
        with self.lock:
            self.data["keys"][key] = key_data
            self._save_db()
            return True
    
    def add_search_log(self, log_data):
        with self.lock:
            self.data["search_logs"].append(log_data)
            self._save_db()
            return True
    
    def get_search_logs(self, username=None):
        with self.lock:
            if username:
                return [log for log in self.data["search_logs"] if log.get("username") == username]
            return self.data["search_logs"]
    
    def get_tickets(self):
        with self.lock:
            return self.data["tickets"]
    
    def save_ticket(self, ticket_id, ticket_data):
        with self.lock:
            self.data["tickets"][ticket_id] = ticket_data
            self._save_db()
            return True
    
    def get_ticket_replies(self, ticket_id):
        with self.lock:
            return self.data["ticket_replies"].get(ticket_id, [])
    
    def save_ticket_reply(self, ticket_id, reply_data):
        with self.lock:
            if ticket_id not in self.data["ticket_replies"]:
                self.data["ticket_replies"][ticket_id] = []
            self.data["ticket_replies"][ticket_id].append(reply_data)
            self._save_db()
            return True
    
    def get_ticket_attachment(self, attachment_id):
        with self.lock:
            return self.data["ticket_attachments"].get(attachment_id)
    
    def save_ticket_attachment(self, attachment_id, attachment_data):
        with self.lock:
            self.data["ticket_attachments"][attachment_id] = attachment_data
            self._save_db()
            return True
    
    def get_api_tokens(self):
        with self.lock:
            return self.data["api_tokens"]
    
    def save_api_token(self, token_id, token_data):
        with self.lock:
            self.data["api_tokens"][token_id] = token_data
            self._save_db()
            return True
    
    def get_user_activity(self):
        with self.lock:
            return self.data["user_activity"]
    
    def save_user_activity(self, username, activity_data):
        with self.lock:
            # Ensure activity_data is a timestamp (float), not a dict
            if isinstance(activity_data, dict):
                # If it's a dict, extract the timestamp or use current time
                activity_data = activity_data.get('timestamp', time.time())
            
            self.data["user_activity"][username] = activity_data
            self._save_db()
            return True
    
    def get_apis_config(self):
        with self.lock:
            return self.data["apis_config"]
    
    def save_apis_config(self, config_data):
        with self.lock:
            self.data["apis_config"] = config_data
            self._save_db()
            return True
    
    def get_config(self):
        with self.lock:
            return self.data["config"]
    
    def save_config(self, config_data):
        with self.lock:
            self.data["config"] = config_data
            self._save_db()
            return True
    
    def get_all_data(self):
        """Return a deep copy of all data for admin download"""
        with self.lock:
            return self._deep_copy(self.data)

# Initialize database instance
db = LocalDB()

def init_admin_user():
    admin_user = db.get_user(ADMIN_USERNAME)
    if not admin_user:
        admin_user = {
            'id': str(uuid.uuid4()),
            'email': 'admin@osint.com',
            'password': generate_password_hash(ADMIN_PASSWORD),
            'credits': 999999,
            'credits_expiry': None,
            'role': 'admin',
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'last_activity': datetime.now().isoformat(),
            'ip_address': None,
            'status': 'active',
            'email_verified': True  # Admin is pre-verified
        }
        db.save_user(ADMIN_USERNAME, admin_user)

def init_db():
    init_admin_user()
    
    # Initialize config if not exists
    config_data = db.get_config()
    if not config_data:
        db.save_config(CONFIG)
    
    # Initialize APIs config if not exists
    apis_config_data = db.get_apis_config()
    if not apis_config_data:
        db.save_apis_config(APIS_CONFIG)