import json
import os

CONFIG_FILE = "ditom_config.json"

# 10 Professionelle Themes
THEMES = {
    "Bio-Neural (Original)": {
        "bg": "#050705", "card": "#141b16", "accent": "#00ff66", 
        "text": "#e0eadd", "text_dim": "#6b7a6d", "border": "#3a4d3f", "error": "#ff3333"
    },
    "Corporate Dark": {
        "bg": "#1e1e1e", "card": "#252526", "accent": "#007acc", 
        "text": "#ffffff", "text_dim": "#cccccc", "border": "#3e3e42", "error": "#f44336"
    },
    "Clean Light": {
        "bg": "#f3f3f3", "card": "#ffffff", "accent": "#0066cc", 
        "text": "#333333", "text_dim": "#666666", "border": "#d1d1d1", "error": "#d32f2f"
    },
    "Midnight Blue": {
        "bg": "#0f172a", "card": "#1e293b", "accent": "#38bdf8", 
        "text": "#f1f5f9", "text_dim": "#94a3b8", "border": "#334155", "error": "#ef4444"
    },
    "Deep Ocean": {
        "bg": "#001f3f", "card": "#003366", "accent": "#0074D9", 
        "text": "#7FDBFF", "text_dim": "#39CCCC", "border": "#001f3f", "error": "#FF4136"
    },
    "Mars Mission": {
        "bg": "#2b1b1b", "card": "#3f2828", "accent": "#ff5733", 
        "text": "#ffdcd6", "text_dim": "#bcaaa4", "border": "#5d4037", "error": "#d32f2f"
    },
    "Industrial Yellow": {
        "bg": "#222222", "card": "#333333", "accent": "#ffcc00", 
        "text": "#eeeeee", "text_dim": "#aaaaaa", "border": "#444444", "error": "#ff4444"
    },
    "Forest Green": {
        "bg": "#1a2f1a", "card": "#264226", "accent": "#4caf50", 
        "text": "#e8f5e9", "text_dim": "#a5d6a7", "border": "#2e7d32", "error": "#e53935"
    },
    "Royal Purple": {
        "bg": "#240046", "card": "#3c096c", "accent": "#9d4edd", 
        "text": "#e0aaff", "text_dim": "#c77dff", "border": "#5a189a", "error": "#ff006e"
    },
    "Slate Grey": {
        "bg": "#202225", "card": "#2f3136", "accent": "#7289da", 
        "text": "#dcddde", "text_dim": "#b9bbbe", "border": "#40444b", "error": "#ed4245"
    }
}

DEFAULT_CONFIG = {
    "system_name": "Roboter 1",
    "github_token": "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",
    "repo_owner": "katimur94",
    "repo_name": "katiproplan-live",
    "repo_path": "index.html",
    
    "theme": "Bio-Neural (Original)",
    "base_path": "",
    "folder_structure": "KW Jahr (z.B. KW2 2026)",
    "admin_password": "1234"
}

class ConfigManager:
    def __init__(self):
        self.data = self.load_config()
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    for key, val in DEFAULT_CONFIG.items():
                        if key not in loaded: loaded[key] = val
                    return loaded
            except: return DEFAULT_CONFIG
        self.save_defaults()
        return DEFAULT_CONFIG

    def save_defaults(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        except: pass

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e: print(f"Fehler: {e}")

    def get_colors(self):
        theme_name = self.data.get("theme", "Bio-Neural (Original)")
        return THEMES.get(theme_name, THEMES["Bio-Neural (Original)"])