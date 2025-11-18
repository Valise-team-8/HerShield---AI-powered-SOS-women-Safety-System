#!/usr/bin/env python3
"""
Custom Keyword Manager
Allows users to set their own secret/safe words for emergency activation
"""

import json
import os

class CustomKeywordManager:
    """
    Manages user's custom emergency keywords
    User can set any word like: "Help", "Red", "Code", "Save me", etc.
    """
    
    def __init__(self, config_file="config/custom_keywords.json"):
        self.config_file = config_file
        self.keywords = []
        self.load_keywords()
    
    def load_keywords(self):
        """Load custom keywords from config"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.keywords = data.get('keywords', [])
            else:
                # Default keywords if no custom ones set
                self.keywords = ["help", "emergency", "save me"]
                self.save_keywords()
        except Exception as e:
            print(f"Error loading keywords: {e}")
            self.keywords = ["help", "emergency", "save me"]
    
    def save_keywords(self):
        """Save keywords to config file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump({'keywords': self.keywords}, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving keywords: {e}")
            return False
    
    def add_keyword(self, keyword):
        """Add a new custom keyword"""
        keyword = keyword.lower().strip()
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.save_keywords()
            return True
        return False
    
    def remove_keyword(self, keyword):
        """Remove a keyword"""
        keyword = keyword.lower().strip()
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            self.save_keywords()
            return True
        return False
    
    def get_keywords(self):
        """Get all custom keywords"""
        return self.keywords.copy()
    
    def set_keywords(self, keywords_list):
        """Set all keywords at once"""
        self.keywords = [kw.lower().strip() for kw in keywords_list if kw.strip()]
        self.save_keywords()
    
    def check_text_for_keywords(self, text):
        """
        Check if text contains any custom keywords
        Returns: (found, matched_keywords)
        """
        text_lower = text.lower()
        matched = [kw for kw in self.keywords if kw in text_lower]
        return len(matched) > 0, matched


# Global instance
keyword_manager = CustomKeywordManager()
