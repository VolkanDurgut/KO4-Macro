# modules/constants.py
import sys
import os

# --- MARKA KİMLİĞİ ---
APP_TITLE = "VOBERIX"
APP_SUBTITLE = "NEXUS COMMAND CENTER"
VERSION = "v9.4" 

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
ATTACK_IMAGE_NAME = resource_path("attack.png") 
LOGO_NAME = resource_path("logo.png")
ICON_NAME = resource_path("icon.ico")

# --- FONT AYARLARI (GÜVENLİ) ---
FONT_FAMILY = ("Segoe UI", "Consolas", "Arial")

# --- RENK PALETİ (PREMIUM DARK GAMER TEMA) ---
COLORS = {
    # -- YENİ MODERN TASARIM (OLED BLACK & NEON) --
    "bg_dark": "#050507",       # Ultra Derin Siyah (Ana Arka Plan)
    "bg_card": "#0A0A0F",       # Premium Kart Rengi (Çok koyu füme/siyah)
    "bg_input": "#101015",      # Zifiri Input Rengi
    "accent": "#00F0FF",        # Neon Cyan (Ana Vurgu - Lazer Mavi)
    "accent_dim": "#005560",    # Sönük Vurgu
    "border": "#15151A",        # Çok İnce ve Karanlık Çerçeve Rengi
    
    # -- GERİYE DÖNÜK UYUMLULUK --
    "bg_main": "#050507",       
    "bg_sidebar": "#07070A",    # Sidebar bir tık daha farklı siyah
    "bg_panel": "#0A0A0F",
    
    "text_main": "#F0F0F5",     # Parlak ve Keskin Beyaz
    "text_dim": "#6E6E7A",      # Soluk Gri/Mavi (Daha az dikkat çeken metinler için)
    "text_dark": "#000000",
    
    "border_main": "#15151A",
    "border_dim": "#15151A",
    "border_focus": "#00F0FF",
    "border_highlight": "#00F0FF",

    "accent_primary": "#00F0FF",
    "accent_hover": "#00D6E6",  # Hover durumunda biraz daha koyu Neon
    "accent_glow": "#00FFFF",
    
    "cyan_neon": "#00F0FF",
    "green_neon": "#00FFA3",    # Hacker Yeşili
    "yellow_neon": "#FFD300",   
    "pink_neon": "#FF0055",     # Lazer Pembesi/Kırmızısı
    "red_error": "#FF003C",     # Agresif Hata Kırmızısı
    
    "btn_hover": "#14141A",
    "toggle_active": "#00F0FF",
    "toggle_passive": "#15151A",
    
    "success": "#00FFA3",
    "warning": "#FFD300",
    "danger": "#FF003C"
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

    # --- OKÇU 3-5 MODÜLÜ ---
    "archer35_active": False,
    "archer35_key": "g",         
    "archer35_skill1_key": "3",  
    "archer35_skill2_key": "4",  
    "archer35_skill3_key": "5"
}