# modules/core.py
import ctypes
import time
import os
import pydirectinput
import pyautogui
import logging
import re
from PIL import Image 
from contextlib import contextmanager
from .constants import (
    IMAGE_NAME, 
    RESTORE_IMAGE_NAME, 
    SHIELD_IMAGE_NAME
)

logger = logging.getLogger(__name__)
pydirectinput.PAUSE = 0

# --- DPI ve API AYARLARI ---
try:
    ctypes.windll.user32.SetProcessDPIAware()
except: pass

PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_ABSOLUTE = 0x8000 
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002

DI_KEYS = {
    'esc': 0x01, '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06, 
    '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B, '-': 0x0C, 
    '=': 0x0D, 'backspace': 0x0E, 'tab': 0x0F, 'q': 0x10, 'w': 0x11, 
    'e': 0x12, 'r': 0x13, 't': 0x14, 'y': 0x15, 'u': 0x16, 'i': 0x17, 
    'o': 0x18, 'p': 0x19, '[': 0x1A, ']': 0x1B, 'enter': 0x1C, 
    'ctrl': 0x1D, 'a': 0x1E, 's': 0x1F, 'd': 0x20, 'f': 0x21, 'g': 0x22, 
    'h': 0x23, 'j': 0x24, 'k': 0x25, 'l': 0x26, ';': 0x27, "'": 0x28, 
    'shift': 0x2A, '\\': 0x2B, 'z': 0x2C, 'x': 0x2D, 'c': 0x2E, 'v': 0x2F, 
    'b': 0x30, 'n': 0x31, 'm': 0x32, ',': 0x33, '.': 0x34, '/': 0x35, 
    'space': 0x39, 'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E, 
    'f5': 0x3F, 'f6': 0x40, 'f7': 0x41, 'f8': 0x42
}

def _block_input(enable):
    try: ctypes.windll.user32.BlockInput(enable)
    except: pass

def _send_input(input_structure):
    ctypes.windll.user32.SendInput(1, ctypes.pointer(input_structure), ctypes.sizeof(input_structure))

def _press_scancode(hexKeyCode):
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, KEYEVENTF_SCANCODE, 0, None)
    x = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_)
    _send_input(x)

def _release_scancode(hexKeyCode):
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, None)
    x = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_)
    _send_input(x)

def precise_wait(duration, stop_callback=None):
    if duration <= 0: return False
    start = time.perf_counter()
    end = start + duration
    while True:
        if stop_callback and stop_callback(): return True 
        current = time.perf_counter()
        remaining = end - current
        if remaining <= 0: return False 
        if remaining > 0.002: time.sleep(0.001)
        else: pass 

def game_key_press(key_char, hold_time=0.03):
    try:
        key = key_char.lower()
        if key in DI_KEYS:
            scancode = DI_KEYS[key]
            _press_scancode(scancode)
            precise_wait(hold_time) 
            _release_scancode(scancode)
        else:
            pydirectinput.press(key)
    except Exception as e:
        logger.error(f"Tuş hatası ({key_char}): {e}")

def execute_combo_sequence(sequence_str, delay_between, stop_callback=None):
    if not sequence_str: return False
    raw_parts = re.split(r'[\s,\-]+', sequence_str)
    final_keys = []
    for part in raw_parts:
        if not part: continue
        lower_part = part.lower()
        if lower_part in DI_KEYS: final_keys.append(part)
        else:
            if len(part) > 1:
                for char in part: final_keys.append(char)
            else: final_keys.append(part)
    
    for k in final_keys:
        if stop_callback and stop_callback(): return True 
        game_key_press(k)
        if delay_between > 0:
            aborted = precise_wait(delay_between, stop_callback)
            if aborted: return True
    return False

# --- MAGE 56 ÖZEL MOTORU ---
def perform_mage56_logic(skill_key, r_key, stop_callback=None):
    try:
        s_code = DI_KEYS.get(skill_key.lower())
        r_code = DI_KEYS.get(r_key.lower())
        w_code = DI_KEYS.get('w')

        if not (s_code and r_code and w_code): return

        # 1. Skill Vur
        _press_scancode(s_code)
        if precise_wait(0.005, stop_callback): 
            _release_scancode(s_code); return
        _release_scancode(s_code)
        if precise_wait(0.005, stop_callback): return

        # 2. W Bas
        _press_scancode(w_code)
        if precise_wait(0.02, stop_callback):
            _release_scancode(w_code); return
        _release_scancode(w_code)
        if precise_wait(0.02, stop_callback): return

        # 3. R Basılı Tut
        _press_scancode(r_code)
        if precise_wait(1.1, stop_callback):
            _release_scancode(r_code); return
        _release_scancode(r_code)

        # 4. W Bas
        _press_scancode(w_code)
        if precise_wait(0.02, stop_callback):
            _release_scancode(w_code); return
        _release_scancode(w_code)

    except Exception as e:
        logger.error(f"Mage56 Core Error: {e}")

# --- ARCHER 3-5 ÖZEL MOTORU ---
def perform_archer35_logic(skill1_key, skill2_key, skill3_key, stop_callback=None):
    try:
        s1 = DI_KEYS.get(skill1_key.lower())
        s2 = DI_KEYS.get(skill2_key.lower())
        s3 = DI_KEYS.get(skill3_key.lower()) if skill3_key and skill3_key.strip() else None
        w_code = DI_KEYS.get('w')

        if not (s1 and s2 and w_code): return

        # --- Skill 1 ---
        _press_scancode(s1)
        if precise_wait(0.22, stop_callback): _release_scancode(s1); return
        _release_scancode(s1)
        if precise_wait(0.27, stop_callback): return

        # Cancel
        _press_scancode(w_code)
        if precise_wait(0.015, stop_callback): _release_scancode(w_code); return
        _release_scancode(w_code)

        # --- Skill 2 ---
        _press_scancode(s2)
        if precise_wait(0.22, stop_callback): _release_scancode(s2); return
        _release_scancode(s2)
        if precise_wait(0.22, stop_callback): return

        # Cancel
        _press_scancode(w_code)
        if precise_wait(0.015, stop_callback): _release_scancode(w_code); return
        _release_scancode(w_code)

        # --- Skill 3 ---
        if s3:
            _press_scancode(s3)
            if precise_wait(0.015, stop_callback): _release_scancode(s3); return
            _release_scancode(s3)
            _press_scancode(w_code)
            if precise_wait(0.015, stop_callback): _release_scancode(w_code); return
            _release_scancode(w_code)

        precise_wait(0.05, stop_callback)

    except Exception as e:
        logger.error(f"Archer35 Core Error: {e}")

# --- YARDIMCI FONKSİYONLAR ---
def get_cursor_pos():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def hardware_move(x, y):
    screen_w = ctypes.windll.user32.GetSystemMetrics(0)
    screen_h = ctypes.windll.user32.GetSystemMetrics(1)
    abs_x = int(x * 65535 / screen_w)
    abs_y = int(y * 65535 / screen_h)
    ii_ = Input_I()
    ii_.mi = MouseInput(abs_x, abs_y, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, 0, None)
    _send_input(Input(ctypes.c_ulong(INPUT_MOUSE), ii_))

def _mouse_click(flags):
    ii_ = Input_I()
    ii_.mi = MouseInput(0, 0, 0, flags, 0, None)
    _send_input(Input(ctypes.c_ulong(INPUT_MOUSE), ii_))

def is_key_held(hex_code):
    return ctypes.windll.user32.GetAsyncKeyState(hex_code) & 0x8000 != 0

@contextmanager
def ghost_mode_action():
    """
    Mouse'u geçici olarak hedefe götürür, işlemi yapar ve geri getirir.
    Geri dönmeden önce bekleme süresi eklendi (Stabilizasyon).
    """
    orig_x, orig_y = get_cursor_pos()
    held_left = is_key_held(0x01) 
    try:
        _block_input(True)
        if held_left: _mouse_click(MOUSEEVENTF_LEFTUP)
        yield 
    finally:
        # ÖNEMLİ DEĞİŞİKLİK:
        # İşlem bittiğinde (yield bittiğinde), mouse hemen geri kaçmasın.
        # Bu context manager'ı kullanan fonksiyonun içinde 'precise_wait' olsa bile,
        # buradaki move işlemi çok kritik.
        hardware_move(orig_x, orig_y)
        if held_left: _mouse_click(MOUSEEVENTF_LEFTDOWN)
        _block_input(False)

def perform_shield_macro(x, y, user_delay):
    try:
        with ghost_mode_action():
            hardware_move(x, y)
            precise_wait(0.02) # Hızlandırıldı
            _mouse_click(MOUSEEVENTF_RIGHTDOWN)
            precise_wait(0.02) # Hızlandırıldı
            _mouse_click(MOUSEEVENTF_RIGHTUP)
            precise_wait(0.01) # Hızlandırıldı
            session_stats.increment_shield()
    except: pass

def _perform_scan_logic(region, user_delay, image_target_path, log_tag):
    try:
        if not os.path.exists(image_target_path): return
        needle_image = Image.open(image_target_path)
        # confidence değerini biraz daha toleranslı yaptım (0.7 -> 0.75 veya sabit)
        found_pos = pyautogui.locateOnScreen(needle_image, region=region, confidence=0.7, grayscale=True)
        if found_pos:
            target_x, target_y = pyautogui.center(found_pos)
            
            with ghost_mode_action():
                hardware_move(int(target_x), int(target_y))
                
                # Hareket sonrası stabilizasyon (Süper Hızlı)
                precise_wait(0.01)
                
                # --- 1. TIK (SOL) ---
                _mouse_click(MOUSEEVENTF_LEFTDOWN)
                precise_wait(0.02) 
                _mouse_click(MOUSEEVENTF_LEFTUP)
                
                # İki tık arası (Optimize)
                precise_wait(0.03) # 40ms -> 30ms'ye çekildi
                
                # --- 2. TIK (SOL) ---
                _mouse_click(MOUSEEVENTF_LEFTDOWN)
                precise_wait(0.02)
                _mouse_click(MOUSEEVENTF_LEFTUP)
                
                # İstatistik
                if log_tag == "SWORD": session_stats.increment_sword()
                elif log_tag == "RESTORE": session_stats.increment_restore()
                
                # Mouse geri dönmeden önce oyunun algılaması için bekleme
                # 0.05 -> 0.02 (Oyunun algılayabileceği en alt sınıra çekildi)
                # Bu sayede mouse ikon üzerinde "asılı" kalmayacak.
                precise_wait(0.02) 
                
    except: pass

def perform_sword_scan_macro(region, user_delay):
    _perform_scan_logic(region, user_delay, IMAGE_NAME, "SWORD")

def perform_restore_scan_macro(region, user_delay):
    _perform_scan_logic(region, user_delay, RESTORE_IMAGE_NAME, "RESTORE")

class SessionManager:
    def __init__(self): self.reset_session()
    def reset_session(self):
        self.stats = {"shield": 0, "sword": 0, "restore": 0}
        self.start_time = time.time()
    def increment_shield(self): self.stats["shield"] += 1
    def increment_sword(self): self.stats["sword"] += 1
    def increment_restore(self): self.stats["restore"] += 1
    def get_report(self):
        elapsed = int(time.time() - self.start_time)
        return (f"Süre: {elapsed//60}dk {elapsed%60}sn | 🛡️:{self.stats['shield']} ⚔️:{self.stats['sword']} ❤️:{self.stats['restore']}")

session_stats = SessionManager()