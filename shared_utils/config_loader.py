"""
Configuration Loader Module
Handles loading and saving customer configuration
"""

import json
import os
from pathlib import Path
import logging

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

def load_customer_config():
    """Load customer configuration from file"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**DEFAULT_CONFIG, **config}
        else:
            # Create default config if it doesn't exist
            save_customer_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
    except Exception as e:
        logging.error(f"Error loading customer configuration: {str(e)}")
        return DEFAULT_CONFIG

def save_customer_config(config):
    """Save customer configuration to file"""
    try:
        # Merge with defaults to ensure all keys exist
        full_config = {**DEFAULT_CONFIG, **config}
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(full_config, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        logging.error(f"Error saving customer configuration: {str(e)}")
        return False

