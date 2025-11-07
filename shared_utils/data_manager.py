"""
Data Manager Module
Handles database operations for posts and users
"""

import json
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Data directory - relative to LIPG Cloud folder
_base_dir = Path(__file__).parent.parent  # Go up from shared_utils to LIPG Cloud
DATA_DIR = _base_dir / "data"
POSTS_FILE = DATA_DIR / "posts.json"
USERS_FILE = DATA_DIR / "users.json"
AUTH_FILE = DATA_DIR / "auth.json"  # User authentication data
COMPANIES_FILE = DATA_DIR / "companies.json"  # Company data with subscriptions

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

def _load_json_file(filepath):
    """Load JSON data from file"""
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading {filepath}: {str(e)}")
            return []
    return []

def _save_json_file(filepath, data):
    """Save JSON data to file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error saving {filepath}: {str(e)}")
        return False

def save_post_to_database(user_id, topic, purpose, audience, message, tone_intensity, 
                          language_style, post_length, formatting, cta, post_goal, generated_post):
    """Save a generated post to the database"""
    try:
        posts = _load_json_file(POSTS_FILE)
        
        post_data = {
            "id": len(posts) + 1,
            "user_id": user_id,
            "date": datetime.now().isoformat(),
            "topic": topic,
            "purpose": purpose,
            "audience": audience,
            "message": message,
            "tone_intensity": tone_intensity,
            "language_style": language_style,
            "post_length": post_length,
            "formatting": formatting,
            "cta": cta,
            "post_goal": post_goal,
            "generated_post": generated_post
        }
        
        posts.append(post_data)
        _save_json_file(POSTS_FILE, posts)
        
        # Update user stats
        users = _load_json_file(USERS_FILE)
        user_found = False
        for user in users:
            if user.get('user_id') == user_id:
                user['post_count'] = user.get('post_count', 0) + 1
                user['last_post_date'] = datetime.now().isoformat()
                user_found = True
                break
        
        if not user_found:
            users.append({
                "user_id": user_id,
                "post_count": 1,
                "created_date": datetime.now().isoformat(),
                "last_post_date": datetime.now().isoformat()
            })
        
        _save_json_file(USERS_FILE, users)
        
        return True
    except Exception as e:
        logging.error(f"Error saving post to database: {str(e)}")
        return False

def get_user_post_history(user_id, limit=None):
    """Get post history for a specific user"""
    try:
        posts = _load_json_file(POSTS_FILE)
        user_posts = [p for p in posts if p.get('user_id') == user_id]
        user_posts.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        if limit:
            user_posts = user_posts[:limit]
        
        return user_posts
    except Exception as e:
        logging.error(f"Error getting user post history: {str(e)}")
        return []

def get_all_posts(limit=None):
    """Get all posts"""
    try:
        posts = _load_json_file(POSTS_FILE)
        posts.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        if limit:
            posts = posts[:limit]
        
        return posts
    except Exception as e:
        logging.error(f"Error getting all posts: {str(e)}")
        return []

def get_all_users():
    """Get all users with their stats"""
    try:
        users = _load_json_file(USERS_FILE)
        posts = _load_json_file(POSTS_FILE)
        
        # Calculate post counts
        for user in users:
            user_id = user.get('user_id')
            user['post_count'] = len([p for p in posts if p.get('user_id') == user_id])
        
        return users
    except Exception as e:
        logging.error(f"Error getting all users: {str(e)}")
        return []

def get_user_stats(user_id=None):
    """Get statistics for a user or overall"""
    try:
        posts = _load_json_file(POSTS_FILE)
        users = _load_json_file(USERS_FILE)
        
        if user_id:
            # User-specific stats
            user_posts = [p for p in posts if p.get('user_id') == user_id]
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            return {
                'total_posts': len(user_posts),
                'posts_today': len([p for p in user_posts if datetime.fromisoformat(p.get('date', '2000-01-01')).date() == today]),
                'posts_week': len([p for p in user_posts if datetime.fromisoformat(p.get('date', '2000-01-01')).date() >= week_ago]),
            }
        else:
            # Overall stats
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            return {
                'total_users': len(users),
                'total_posts': len(posts),
                'posts_today': len([p for p in posts if datetime.fromisoformat(p.get('date', '2000-01-01')).date() == today]),
                'posts_week': len([p for p in posts if datetime.fromisoformat(p.get('date', '2000-01-01')).date() >= week_ago]),
            }
    except Exception as e:
        logging.error(f"Error getting user stats: {str(e)}")
        return {}

def delete_post(post_id):
    """Delete a post by ID"""
    try:
        posts = _load_json_file(POSTS_FILE)
        posts = [p for p in posts if p.get('id') != post_id]
        return _save_json_file(POSTS_FILE, posts)
    except Exception as e:
        logging.error(f"Error deleting post: {str(e)}")
        return False

def get_analytics_data():
    """Get analytics data for dashboard"""
    try:
        posts = _load_json_file(POSTS_FILE)
        
        # Posts by goal
        posts_by_goal = {}
        posts_by_length = {}
        template_usage = {}
        
        for post in posts:
            goal = post.get('post_goal', 'Unknown')
            posts_by_goal[goal] = posts_by_goal.get(goal, 0) + 1
            
            length = post.get('post_length', 'Unknown')
            posts_by_length[length] = posts_by_length.get(length, 0) + 1
        
        return {
            'posts_by_goal': posts_by_goal,
            'posts_by_length': posts_by_length,
            'template_usage': template_usage,
            'all_posts': posts
        }
    except Exception as e:
        logging.error(f"Error getting analytics data: {str(e)}")
        return {}

# User Authentication Functions
def authenticate_user(username, password):
    """Authenticate a user with username and password"""
    try:
        # Normalize username (strip whitespace, case-insensitive comparison)
        username = username.strip() if username else ""
        password = password.strip() if password else ""
        
        if not username or not password:
            return False, "Username and password are required"
        
        auth_data = _load_json_file(AUTH_FILE)
        
        # Debug: log file path and data count
        logging.info(f"Authenticating user. Auth file: {AUTH_FILE}, exists: {AUTH_FILE.exists()}, users count: {len(auth_data)}")
        
        if not auth_data:
            logging.warning(f"Auth file is empty or doesn't exist: {AUTH_FILE}")
            return False, "No users found in system. Please contact administrator."
        
        for user in auth_data:
            # Case-insensitive username comparison with whitespace stripped
            stored_username = user.get('username', '').strip() if user.get('username') else ""
            if stored_username.lower() == username.lower():
                if not user.get('enabled', True):
                    return False, "User account is disabled"
                if user.get('password') == password:
                    return True, "Authentication successful"
                else:
                    return False, "Incorrect password"
        
        # Log available usernames for debugging (without passwords)
        available_users = [u.get('username', 'N/A') for u in auth_data]
        logging.warning(f"User '{username}' not found. Available users: {available_users}")
        return False, "User not found"
    except Exception as e:
        logging.error(f"Error authenticating user: {str(e)}")
        return False, f"Authentication error: {str(e)}"

def get_user(username):
    """Get user information by username"""
    try:
        auth_data = _load_json_file(AUTH_FILE)
        for user in auth_data:
            if user.get('username') == username:
                # Don't return password
                user_info = user.copy()
                user_info.pop('password', None)
                # Set defaults if not present (for backward compatibility)
                if 'tier' not in user_info:
                    user_info['tier'] = 'Basic'
                if 'company_id' not in user_info:
                    user_info['company_id'] = None
                if 'role' not in user_info:
                    user_info['role'] = 'User'
                return user_info
        return None
    except Exception as e:
        logging.error(f"Error getting user: {str(e)}")
        return None

def create_user(username, password, enabled=True, email="", tier="Basic", company_id=None, role="User"):
    """Create a new user account"""
    try:
        auth_data = _load_json_file(AUTH_FILE)
        
        # Check if user already exists
        for user in auth_data:
            if user.get('username') == username:
                return False, "Username already exists"
        
        # Validate tier
        valid_tiers = ["Basic", "Standard", "Premium"]
        if tier not in valid_tiers:
            tier = "Basic"
        
        # Validate role
        valid_roles = ["Admin", "User", "Viewer"]
        if role not in valid_roles:
            role = "User"
        
        # If company_id provided, verify company exists
        if company_id:
            companies = _load_json_file(COMPANIES_FILE)
            company_exists = any(c.get('id') == company_id for c in companies)
            if not company_exists:
                return False, f"Company with ID {company_id} not found"
        
        # Create new user
        new_user = {
            "username": username,
            "password": password,  # In production, hash this
            "enabled": enabled,
            "email": email,
            "tier": tier,
            "company_id": company_id,
            "role": role,
            "created_date": datetime.now().isoformat(),
            "last_login": None
        }
        
        auth_data.append(new_user)
        _save_json_file(AUTH_FILE, auth_data)
        return True, "User created successfully"
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        return False, f"Error creating user: {str(e)}"

def update_user_password(username, new_password):
    """Update user password"""
    try:
        auth_data = _load_json_file(AUTH_FILE)
        for user in auth_data:
            if user.get('username') == username:
                user['password'] = new_password  # In production, hash this
                _save_json_file(AUTH_FILE, auth_data)
                return True, "Password updated successfully"
        return False, "User not found"
    except Exception as e:
        logging.error(f"Error updating password: {str(e)}")
        return False, f"Error updating password: {str(e)}"

def enable_disable_user(username, enabled):
    """Enable or disable a user account"""
    try:
        auth_data = _load_json_file(AUTH_FILE)
        for user in auth_data:
            if user.get('username') == username:
                user['enabled'] = enabled
                _save_json_file(AUTH_FILE, auth_data)
                return True, f"User {'enabled' if enabled else 'disabled'} successfully"
        return False, "User not found"
    except Exception as e:
        logging.error(f"Error updating user status: {str(e)}")
        return False, f"Error updating user status: {str(e)}"

def delete_user(username):
    """Delete a user account"""
    try:
        auth_data = _load_json_file(AUTH_FILE)
        auth_data = [u for u in auth_data if u.get('username') != username]
        _save_json_file(AUTH_FILE, auth_data)
        return True, "User deleted successfully"
    except Exception as e:
        logging.error(f"Error deleting user: {str(e)}")
        return False, f"Error deleting user: {str(e)}"

def get_all_auth_users():
    """Get all authenticated users (without passwords)"""
    try:
        auth_data = _load_json_file(AUTH_FILE)
        # Remove passwords from response and ensure defaults exist (backward compatibility)
        users = []
        for user in auth_data:
            user_info = user.copy()
            user_info.pop('password', None)
            # Set defaults if not present (for backward compatibility)
            if 'tier' not in user_info:
                user_info['tier'] = 'Basic'
            if 'company_id' not in user_info:
                user_info['company_id'] = None
            if 'role' not in user_info:
                user_info['role'] = 'User'
            users.append(user_info)
        return users
    except Exception as e:
        logging.error(f"Error getting auth users: {str(e)}")
        return []

def update_last_login(username):
    """Update user's last login timestamp"""
    try:
        auth_data = _load_json_file(AUTH_FILE)
        for user in auth_data:
            if user.get('username') == username:
                user['last_login'] = datetime.now().isoformat()
                _save_json_file(AUTH_FILE, auth_data)
                return True
        return False
    except Exception as e:
        logging.error(f"Error updating last login: {str(e)}")
        return False

def update_user_tier(username, tier):
    """Update user tier"""
    try:
        valid_tiers = ["Basic", "Standard", "Premium"]
        if tier not in valid_tiers:
            return False, f"Invalid tier. Must be one of: {', '.join(valid_tiers)}"
        
        auth_data = _load_json_file(AUTH_FILE)
        for user in auth_data:
            if user.get('username') == username:
                user['tier'] = tier
                _save_json_file(AUTH_FILE, auth_data)
                return True, f"User tier updated to {tier} successfully"
        return False, "User not found"
    except Exception as e:
        logging.error(f"Error updating user tier: {str(e)}")
        return False, f"Error updating user tier: {str(e)}"

def update_user_role(username, role):
    """Update user role"""
    try:
        valid_roles = ["Admin", "User", "Viewer"]
        if role not in valid_roles:
            return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        
        auth_data = _load_json_file(AUTH_FILE)
        for user in auth_data:
            if user.get('username') == username:
                user['role'] = role
                _save_json_file(AUTH_FILE, auth_data)
                return True, f"User role updated to {role} successfully"
        return False, "User not found"
    except Exception as e:
        logging.error(f"Error updating user role: {str(e)}")
        return False, f"Error updating user role: {str(e)}"

def update_user_company(username, company_id):
    """Update user's company"""
    try:
        auth_data = _load_json_file(AUTH_FILE)
        companies = _load_json_file(COMPANIES_FILE)
        
        # If company_id provided, verify company exists
        if company_id:
            company_exists = any(c.get('id') == company_id for c in companies)
            if not company_exists:
                return False, f"Company with ID {company_id} not found"
        
        for user in auth_data:
            if user.get('username') == username:
                user['company_id'] = company_id
                _save_json_file(AUTH_FILE, auth_data)
                return True, f"User company updated successfully"
        return False, "User not found"
    except Exception as e:
        logging.error(f"Error updating user company: {str(e)}")
        return False, f"Error updating user company: {str(e)}"

# Company Management Functions
def create_company(name, subscription_type="monthly", start_date=None, expiration_date=None):
    """Create a new company with subscription"""
    try:
        companies = _load_json_file(COMPANIES_FILE)
        
        # Check if company already exists
        for company in companies:
            if company.get('name', '').lower() == name.lower():
                return False, "Company name already exists"
        
        # Generate company ID
        company_id = len(companies) + 1
        
        # Set default dates if not provided
        if not start_date:
            start_date = datetime.now().isoformat()
        if not expiration_date:
            if subscription_type == "monthly":
                expiration_date = (datetime.now() + timedelta(days=30)).isoformat()
            else:  # annual
                expiration_date = (datetime.now() + timedelta(days=365)).isoformat()
        
        # Validate subscription type
        if subscription_type not in ["monthly", "annual"]:
            subscription_type = "monthly"
        
        new_company = {
            "id": company_id,
            "name": name,
            "subscription_type": subscription_type,
            "start_date": start_date,
            "expiration_date": expiration_date,
            "created_date": datetime.now().isoformat(),
            "enabled": True
        }
        
        companies.append(new_company)
        _save_json_file(COMPANIES_FILE, companies)
        return True, company_id
    except Exception as e:
        logging.error(f"Error creating company: {str(e)}")
        return False, None

def get_company(company_id):
    """Get company information by ID"""
    try:
        companies = _load_json_file(COMPANIES_FILE)
        for company in companies:
            if company.get('id') == company_id:
                return company
        return None
    except Exception as e:
        logging.error(f"Error getting company: {str(e)}")
        return None

def get_all_companies():
    """Get all companies"""
    try:
        companies = _load_json_file(COMPANIES_FILE)
        return companies
    except Exception as e:
        logging.error(f"Error getting companies: {str(e)}")
        return []

def update_company_subscription(company_id, subscription_type=None, start_date=None, expiration_date=None):
    """Update company subscription dates and type"""
    try:
        companies = _load_json_file(COMPANIES_FILE)
        for company in companies:
            if company.get('id') == company_id:
                if subscription_type:
                    if subscription_type not in ["monthly", "annual"]:
                        return False, "Invalid subscription type. Must be 'monthly' or 'annual'"
                    company['subscription_type'] = subscription_type
                if start_date:
                    company['start_date'] = start_date
                if expiration_date:
                    company['expiration_date'] = expiration_date
                _save_json_file(COMPANIES_FILE, companies)
                return True, "Company subscription updated successfully"
        return False, "Company not found"
    except Exception as e:
        logging.error(f"Error updating company subscription: {str(e)}")
        return False, f"Error updating company subscription: {str(e)}"

def enable_disable_company(company_id, enabled):
    """Enable or disable a company"""
    try:
        companies = _load_json_file(COMPANIES_FILE)
        for company in companies:
            if company.get('id') == company_id:
                company['enabled'] = enabled
                _save_json_file(COMPANIES_FILE, companies)
                return True, f"Company {'enabled' if enabled else 'disabled'} successfully"
        return False, "Company not found"
    except Exception as e:
        logging.error(f"Error updating company status: {str(e)}")
        return False, f"Error updating company status: {str(e)}"

def delete_company(company_id):
    """Delete a company"""
    try:
        companies = _load_json_file(COMPANIES_FILE)
        companies = [c for c in companies if c.get('id') != company_id]
        _save_json_file(COMPANIES_FILE, companies)
        
        # Also remove company_id from users
        auth_data = _load_json_file(AUTH_FILE)
        for user in auth_data:
            if user.get('company_id') == company_id:
                user['company_id'] = None
        _save_json_file(AUTH_FILE, auth_data)
        
        return True, "Company deleted successfully"
    except Exception as e:
        logging.error(f"Error deleting company: {str(e)}")
        return False, f"Error deleting company: {str(e)}"

def get_company_users(company_id):
    """Get all users belonging to a company"""
    try:
        auth_data = _load_json_file(AUTH_FILE)
        company_users = [u for u in auth_data if u.get('company_id') == company_id]
        # Remove passwords and ensure default fields exist (backward compatibility)
        for user in company_users:
            user.pop('password', None)
            if 'tier' not in user:
                user['tier'] = 'Basic'
            if 'role' not in user:
                user['role'] = 'User'
        return company_users
    except Exception as e:
        logging.error(f"Error getting company users: {str(e)}")
        return []

def is_subscription_active(company_id):
    """Check if company subscription is active"""
    try:
        company = get_company(company_id)
        if not company or not company.get('enabled', True):
            return False
        
        expiration_date_str = company.get('expiration_date')
        if not expiration_date_str:
            return False
        
        expiration_date = datetime.fromisoformat(expiration_date_str.replace('Z', '+00:00'))
        return datetime.now() < expiration_date
    except Exception as e:
        logging.error(f"Error checking subscription status: {str(e)}")
        return False
