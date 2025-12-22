# modules/constants.py

VERSION = "7.5"
GITHUB_USER = "VolkanDurgut"
GITHUB_REPO = "KO4-Macro"
REPO_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
SWORD_IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/sword.png"

CONFIG_FILE = "config.json"
IMAGE_NAME = "sword.png"
LOGO_NAME = "logo.png"  
ICON_NAME = "icon.ico" 

# Varsayılan Ayarlar
DEFAULT_CONFIG = {
    "shield_x": 1574, "shield_y": 507, "shield_key": "v", "shield_delay": 0.0,
    "region_x1": 0, "region_y1": 0, "region_x2": 100, "region_y2": 100,
    "sword_key": "c", "sword_delay": 0.0
}