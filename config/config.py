import json
import os
from logger import log
from gui.constants import Constants


class Config:
    MEDIA_DIR = ""
    THUMBNAILS_DIR = ""
    S3_BUCKET_NAME = ""
    LOCAL_STORAGE_ENABLED = True
    DATABASE_DIR = ""
    CLOUDFRONT_KEY_PATH = ""
    CLOUDFRONT_DOMAIN = ""
    CLOUDFRONT_KEY_ID = ""
    THEME = Constants.SETTINGS_THEME_LIGHT
    MEDIA_PRIVACY_LEVEL = 0
    LATEST_DURATION_DAYS = 7
    DELETE_ORIGINAL_AFTER_UPLOAD = False
    INITIAL_MEDIA_INDEX = Constants.SETTINGS_INITIAL_END

    CONFIG_FILE_PATH = "res/config.json"

    @staticmethod
    def read_config():
        """Read configuration from config.json file and update Config class attributes"""
        try:
            if os.path.exists(Config.CONFIG_FILE_PATH):
                with open(Config.CONFIG_FILE_PATH, "r") as f:
                    config = json.load(f)

                for key, value in config.items():
                    if hasattr(Config, key) and not key.startswith('__') and not callable(getattr(Config, key)):
                        setattr(Config, key, value)
                    else:
                        log("Config.read_config", f"Unexpected config key: {key}", level="warning")
        except Exception as e:
            log("Config.read_config", f"Error reading config file: {e}", level="error")

    @staticmethod
    def save_config():
        """Save current Config class attributes to config.json file"""
        config_data = {}
        
        # Get all attributes from Config class that are not methods or private
        for attr in dir(Config):
            if not attr.startswith('__') and not callable(getattr(Config, attr)) and attr != 'CONFIG_FILE_PATH':
                config_data[attr] = getattr(Config, attr)
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(Config.CONFIG_FILE_PATH), exist_ok=True)
            
            with open(Config.CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
            log("Config.save_config", f"Configuration saved to {Config.CONFIG_FILE_PATH}", level="info")
            return True
        except Exception as e:
            log("Config.save_config", f"Error saving config file: {e}", level="error")
            return False
    
    @staticmethod
    def get_all_settings():
        """Get all settings as a dictionary"""
        settings = {}
        
        for attr in dir(Config):
            if not attr.startswith('__') and not callable(getattr(Config, attr)) and attr != 'CONFIG_FILE_PATH':
                settings[attr] = getattr(Config, attr)
                
        return settings
    
    @staticmethod
    def update_settings(settings_dict):
        """Update multiple settings at once and save to config file
        
        Args:
            settings_dict (dict): Dictionary of settings to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        for key, value in settings_dict.items():
            if hasattr(Config, key) and not key.startswith('__') and not callable(getattr(Config, key)) and key != 'CONFIG_FILE_PATH':
                setattr(Config, key, value)
        
        return Config.save_config()
