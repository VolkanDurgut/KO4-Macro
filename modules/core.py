# modules/core.py
import ctypes
import time
import os
import requests
import pydirectinput
import pyautogui
from .constants import IMAGE_NAME, SWORD_IMAGE_URL

pydirectinput.PAUSE = 0.001

def check_and_download_assets():
    """Gerekli resim dosyalarını indirir."""
    if not os.path.exists(IMAGE_NAME):
        try:
            r = requests.get(SWORD_IMAGE_URL)
            if r.status_code == 200:
                with open(IMAGE_NAME, 'wb') as f:
                    f.write(r.content)
        except: pass

def block_input(block=True):
    """Ghost Mode: Klavye ve mouse girişini kilitler/açar."""
    try:
        ctypes.windll.user32.BlockInput(block)
    except:
        pass

def is_key_held(hex_code):
    """Bir tuşun fiziksel olarak basılı olup olmadığını kontrol eder."""
    return ctypes.windll.user32.GetAsyncKeyState(hex_code) & 0x8000 != 0

def perform_shield_macro(x, y, delay):
    try:
        block_input(True)
        original_x, original_y = pydirectinput.position()
        
        holding_left = is_key_held(0x01)
        holding_right = is_key_held(0x02)
        
        if holding_left: pydirectinput.mouseUp(button='left')
        if holding_right: 
            pydirectinput.mouseUp(button='right')
            time.sleep(0.05)

        pydirectinput.moveTo(x, y)
        time.sleep(0.04)
        pydirectinput.mouseDown(button='right')
        time.sleep(0.10) 
        pydirectinput.mouseUp(button='right')
        
        time.sleep(0.02)
        pydirectinput.moveTo(original_x, original_y)
        
        time.sleep(0.02)
        if holding_left: pydirectinput.mouseDown(button='left')
        if holding_right: pydirectinput.mouseDown(button='right')
        
        if delay > 0: time.sleep(delay)
    except Exception as e:
        print(f"Shield Error: {e}")
    finally:
        block_input(False)

def perform_sword_scan_macro(region, delay):
    try:
        if not os.path.exists(IMAGE_NAME):
            check_and_download_assets()

        # Tarama
        found_pos = pyautogui.locateOnScreen(IMAGE_NAME, region=region, confidence=0.8, grayscale=True)
        
        if found_pos:
            target_x, target_y = pyautogui.center(found_pos)
            
            block_input(True)
            original_x, original_y = pydirectinput.position()
            
            holding_left = is_key_held(0x01)
            holding_right = is_key_held(0x02)
            
            if holding_left: pydirectinput.mouseUp(button='left')
            if holding_right: 
                pydirectinput.mouseUp(button='right')
                time.sleep(0.04)

            pydirectinput.moveTo(int(target_x), int(target_y))
            time.sleep(0.02)
            
            # Çift Tık
            pydirectinput.mouseDown(button='left')
            time.sleep(0.04)
            pydirectinput.mouseUp(button='left')
            time.sleep(0.05)
            pydirectinput.mouseDown(button='left')
            time.sleep(0.04)
            pydirectinput.mouseUp(button='left')
            
            time.sleep(0.02)
            pydirectinput.moveTo(original_x, original_y)
            
            time.sleep(0.02)
            if holding_left: pydirectinput.mouseDown(button='left')
            if holding_right: pydirectinput.mouseDown(button='right')
        
        if delay > 0: time.sleep(delay)

    except Exception as e:
        print(f"Scanner Error: {e}")
    finally:
        block_input(False)