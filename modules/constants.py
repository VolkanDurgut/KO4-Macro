# modules/constants.py
import sys
import os

# --- MARKA KİMLİĞİ ---
APP_TITLE = "VOBERIX"
APP_SUBTITLE = "NEXUS COMMAND CENTER"
VERSION = "9.1" 

# --- GITHUB UPDATER ---
GITHUB_USER = "VolkanDurgut"
GITHUB_REPO = "KO4-Macro"
REPO_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    data_dir = os.path.join(os.getenv('LOCALAPPDATA', os.path.expanduser("~")), "Voberix_Suite")
    if not os.path.exists(data_dir): os.makedirs(data_dir, exist_ok=True)
    return data_dir

DATA_DIR = get_user_data_dir()
CONFIG_FILE = os.path.join(DATA_DIR, "config.vbx")
LOG_FILE = os.path.join(DATA_DIR, "nexus.log")
LICENSE_FILE = os.path.join(DATA_DIR, "license.vbx") 

# --- VARLIKLAR ---
IMAGE_NAME = resource_path("sword.png")
RESTORE_IMAGE_NAME = resource_path("restore.png")
SHIELD_IMAGE_NAME = resource_path("shield.png")
ARROWS_IMAGE_NAME = resource_path("arrows.png") 
ATTACK_IMAGE_NAME = resource_path("attack.png") # YENİ EKLENDİ (Kombo Görseli)
LOGO_NAME = resource_path("logo.png")
ICON_NAME = resource_path("icon.ico")

# --- FONT AYARLARI (GÜVENLİ) ---
FONT_FAMILY = ("Segoe UI", "Consolas", "Arial")

# --- RENK PALETİ (HİBRİT) ---
COLORS = {
    # -- YENİ MODERN TASARIM (NEXUS) --
    "bg_dark": "#0B0B0E",       # Ana Arka Plan
    "bg_card": "#141417",       # Kart Rengi
    "bg_input": "#1C1C21",      # Input Rengi
    "accent": "#00F0FF",        # Neon Cyan (Ana Vurgu)
    "accent_dim": "#006670",    # Sönük Vurgu
    "border": "#222226",        # İnce Çerçeve Rengi
    
    # -- GERİYE DÖNÜK UYUMLULUK --
    "bg_main": "#0B0B0E",       
    "bg_sidebar": "#0F0F12",
    "bg_panel": "#141417",
    
    "text_main": "#E1E1E6",     
    "text_dim": "#82828F", 
    "text_dark": "#000000",
    
    "border_main": "#222226",
    "border_dim": "#27272A",
    "border_focus": "#00F0FF",
    "border_highlight": "#00F0FF",

    "accent_primary": "#00F0FF",
    "accent_hover": "#00B8C4",
    "accent_glow": "#00FFFF",
    
    "cyan_neon": "#00F0FF",
    "green_neon": "#10B981",    # Aktif Yeşil
    "yellow_neon": "#F59E0B",   
    "pink_neon": "#D946EF",     
    "red_error": "#FF4B4B",     # Hata Kırmızı
    
    "btn_hover": "#2A2A30",
    "toggle_active": "#00F0FF",
    "toggle_passive": "#27272A",
    
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#FF4B4B"
}

# --- VARSAYILAN AYARLAR (GÜNCEL) ---
DEFAULT_CONFIG = {
    # Eski Modüller
    "shield_x": 0, "shield_y": 0, "shield_key": "v", "shield_delay": 0.0, "shield_active": False,
    "region_x1": 0, "region_y1": 0, "region_x2": 100, "region_y2": 100,
    "sword_key": "c", "sword_delay": 0.0, "sword_active": False,
    "restore_key": "x", "restore_delay": 0.0, "restore_active": False,
    "input_pause": 0.001, "loop_rate": 60,
    
    # Kombo Modülü
    "combo_active": False, "combo_key": "caps lock", "combo_sequence": "1-6-7-8",
    "combo_delay_ms": 1.0, "combo_time_unit": "MS",
    
    # Tema
    "app_theme": "Neon Cyan",

    # --- MAGE 56 MODÜLÜ ---
    "mage56_active": False,
    "mage56_key": "f",       
    "mage56_skill_key": "2", 
    "mage56_r_key": "r",      

    # --- YENİ: OKÇU 3-5 MODÜLÜ ---
    "archer35_active": False,
    "archer35_key": "g",         # Başlatma tuşu (Örn: G)
    "archer35_skill1_key": "3",  # 1. Skill (Örn: 3)
    "archer35_skill2_key": "4",  # 2. Skill (Örn: 4)
    "archer35_skill3_key": "5"   # 3. Skill (Örn: 5)
}