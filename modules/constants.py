# modules/constants.py

VERSION = "8.2"
GITHUB_USER = "VolkanDurgut"
GITHUB_REPO = "KO4-Macro"
REPO_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
SWORD_IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/sword.png"

CONFIG_FILE = "config.json"
IMAGE_NAME = "sword.png"
LOGO_NAME = "logo.png"
ICON_NAME = "icon.ico"
SPLASH_GIF = "splash.gif"

# --- SCUDERIA FERRARI RENK PALETİ ---
COLORS = {
    "bg_main": "#121212",
    "bg_card": "#1e1e1e",
    "bg_input": "#2d2d2d",
    "border_grey": "#333333",
    "ferrari_red": "#FF2800",
    "ferrari_dark": "#CC0000",
    "ferrari_glow": "#FF4500",
    "stop_red": "#8B0000",
    "ferrari_yellow": "#FFF200", 
    "ferrari_yellow_hover": "#E6D900",
    "text_white": "#FFFFFF",
    "text_grey": "#B0B0B0",
    "text_black": "#000000"
}

# Varsayılan Ayarlar
DEFAULT_CONFIG = {
    "shield_x": 1574, "shield_y": 507, "shield_key": "v", "shield_delay": 0.0,
    "region_x1": 0, "region_y1": 0, "region_x2": 100, "region_y2": 100,
    "sword_key": "c", "sword_delay": 0.0
}