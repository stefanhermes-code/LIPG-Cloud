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
        auth_data = _load_json_file(AUTH_FILE)
        for user in auth_data:
            if user.get('username') == username:
                if not user.get('enabled', True):
                    return False, "User account is disabled"
                if user.get('password') == password:
                    return True, "Authentication successful"
                else:
                    return False, "Incorrect password"
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
                # Set default tier if not present (for backward compatibility)
                if 'tier' not in user_info:
                    user_info['tier'] = 'Basic'
                return user_info
        return None
    except Exception as e:
        logging.error(f"Error getting user: {str(e)}")
        return None

def create_user(username, password, enabled=True, email="", tier="Basic"):
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
        
        # Create new user
        new_user = {
            "username": username,
            "password": password,  # In production, hash this
            "enabled": enabled,
            "email": email,
            "tier": tier,
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
        # Remove passwords from response and ensure tier exists (backward compatibility)
        users = []
        for user in auth_data:
            user_info = user.copy()
            user_info.pop('password', None)
            # Set default tier if not present (for backward compatibility)
            if 'tier' not in user_info:
                user_info['tier'] = 'Basic'
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
