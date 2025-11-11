"""
Configuration Loader Module
Handles loading and saving customer configuration
"""

import json
import os
from pathlib import Path
import logging
from time import time

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configuration file path - relative to LIPG Cloud folder
_base_dir = Path(__file__).parent.parent  # Go up from shared_utils to LIPG Cloud
CONFIG_FILE = _base_dir / "data" / "customer_config.json"

# Ensure data directory exists
CONFIG_FILE.parent.mkdir(exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "customer_name": "LinkedIn Post Generator",
    "background_color": "#E9F7EF",
    "button_color": "#17A2B8"
}

# Cache for config file
_config_cache = None
_config_cache_time = 0
_config_cache_mtime = 0
_cache_ttl = 60  # Cache config for 60 seconds

def load_customer_config():
    """Load customer configuration from file with caching"""
    global _config_cache, _config_cache_time, _config_cache_mtime
    
    try:
        # Check cache validity
        current_mtime = CONFIG_FILE.stat().st_mtime if CONFIG_FILE.exists() else 0
        current_time = time()
        
        if (_config_cache is not None and 
            _config_cache_mtime == current_mtime and
            current_time - _config_cache_time < _cache_ttl):
            return _config_cache
        
        # Load from file
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = {**DEFAULT_CONFIG, **config}
                # Update cache
                _config_cache = merged_config
                _config_cache_time = current_time
                _config_cache_mtime = current_mtime
                return merged_config
        else:
            # Create default config if it doesn't exist
            save_customer_config(DEFAULT_CONFIG)
            _config_cache = DEFAULT_CONFIG
            _config_cache_time = current_time
            _config_cache_mtime = 0
            return DEFAULT_CONFIG
    except Exception as e:
        logging.error(f"Error loading customer configuration: {str(e)}")
        return DEFAULT_CONFIG

def save_customer_config(config):
    """Save customer configuration to file and invalidate cache"""
    global _config_cache, _config_cache_time, _config_cache_mtime
    
    try:
        # Merge with defaults to ensure all keys exist
        full_config = {**DEFAULT_CONFIG, **config}
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(full_config, f, indent=2, ensure_ascii=False)
        
        # Update cache with new data
        _config_cache = full_config
        _config_cache_time = time()
        _config_cache_mtime = CONFIG_FILE.stat().st_mtime if CONFIG_FILE.exists() else 0
        
        return True
    except Exception as e:
        logging.error(f"Error saving customer configuration: {str(e)}")
        return False

