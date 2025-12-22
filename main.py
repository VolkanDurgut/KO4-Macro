import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
import keyboard
import pydirectinput
import json
import os
import sys
import requests
import webbrowser
import ctypes
import pyautogui

# --- PROJE AYARLARI (v7.0 AUTO-UPDATER ENGINE) ---
VERSION = "7.2"
GITHUB_USER = "VolkanDurgut"
GITHUB_REPO = "KO4-Macro"
REPO_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
SWORD_IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/sword.png"

CONFIG_FILE = "config.json"
IMAGE_NAME = "sword.png"

pydirectinput.PAUSE = 0.001

# --- GHOST MODE ---
def block_input(block=True):
    try:
        ctypes.windll.user32.BlockInput(block)
    except:
        pass

# --- DONANIM KONTROL ---
def is_key_held(hex_code):
    return ctypes.windll.user32.GetAsyncKeyState(hex_code) & 0x8000 != 0

# --- KALKAN FONKSİYONU ---
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

# --- KILIÇ TARAMA FONKSİYONU ---
def perform_sword_scan_macro(region, delay):
    try:
        # Varlık kontrolü
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

# --- ASSET YÖNETİCİSİ ---
def check_and_download_assets():
    if not os.path.exists(IMAGE_NAME):
        try:
            r = requests.get(SWORD_IMAGE_URL)
            if r.status_code == 200:
                with open(IMAGE_NAME, 'wb') as f:
                    f.write(r.content)
        except: pass

# ==========================================
# 🔄 OTO-GÜNCELLEME MOTORU (YENİ)
# ==========================================
class AutoUpdater:
    def __init__(self, current_version, root_window):
        self.current_version = current_version
        self.root = root_window

    def check_for_updates(self):
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            # 1. GitHub API'sine sor
            response = requests.get(REPO_API_URL)
            if response.status_code == 200:
                data = response.json()
                latest_tag = data['tag_name'] # Örn: "v7.1"
                
                # Sürüm Karşılaştırma (v'yi atıyoruz)
                clean_latest = latest_tag.replace("v", "").strip()
                clean_current = self.current_version.replace("v", "").strip()

                if clean_latest != clean_current:
                    # Güncelleme bulundu, asset linkini al
                    assets = data.get('assets', [])
                    if assets:
                        download_url = assets[0]['browser_download_url']
                        self.root.after(0, lambda: self.prompt_update(latest_tag, download_url))
        except Exception as e:
            print(f"Update Check Error: {e}")

    def prompt_update(self, version, url):
        msg = f"YENİ SÜRÜM MEVCUT: {version}\n\nProgramı şimdi otomatik güncelleyip yeniden başlatmak ister misiniz?"
        if messagebox.askyesno("Güncelleme", msg):
            self.perform_update(url)

    def perform_update(self, url):
        # Eğer EXE değilse (Geliştirici modundaysan) sadece uyar
        if not getattr(sys, 'frozen', False):
            messagebox.showinfo("Bilgi", "Python script modunda otomatik güncelleme yapılamaz.\nLütfen GitHub'dan indiriniz.")
            webbrowser.open(f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases")
            return

        # 1. Yeni EXE'yi indir (Geçici isimle)
        try:
            temp_exe = "new_version_temp.exe"
            r = requests.get(url, stream=True)
            with open(temp_exe, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    f.write(chunk)
            
            # 2. BAT Dosyası Oluştur (Eski sil -> Yeni isim değiştir -> Başlat)
            current_exe = sys.executable
            exe_name = os.path.basename(current_exe)
            
            bat_script = f"""
            @echo off
            echo Guncelleniyor... Lutfen bekleyin...
            timeout /t 3 /nobreak > NUL
            move /Y "{temp_exe}" "{exe_name}"
            start "" "{exe_name}"
            del "%~f0"
            """
            
            with open("updater.bat", "w") as f:
                f.write(bat_script)
            
            # 3. Bat dosyasını çalıştır ve programı kapat
            os.startfile("updater.bat")
            sys.exit()

        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme başarısız: {e}")

# ==========================================
# GÖRSEL SEÇİM ARACI
# ==========================================
class SnippingTool(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.attributes('-fullscreen', True)
        self.attributes('-alpha', 0.3)
        self.configure(bg='black')
        self.cursor_start_x = 0; self.cursor_start_y = 0; self.rect = None
        self.canvas = tk.Canvas(self, cursor="cross", bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Escape>", lambda e: self.destroy())

    def on_press(self, event):
        self.cursor_start_x = event.x; self.cursor_start_y = event.y
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red', width=3, fill="white", stipple="gray12")

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.cursor_start_x, self.cursor_start_y, event.x, event.y)

    def on_release(self, event):
        x1 = min(self.cursor_start_x, event.x); y1 = min(self.cursor_start_y, event.y)
        x2 = max(self.cursor_start_x, event.x); y2 = max(self.cursor_start_y, event.y)
        self.callback(x1, y1, x2, y2)
        self.destroy()

# ==========================================
# ANA ARAYÜZ
# ==========================================
class MacroApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Varlık ve Güncelleme Kontrolü
        threading.Thread(target=check_and_download_assets, daemon=True).start()
        
        self.updater = AutoUpdater(VERSION, self)
        self.updater.check_for_updates()

        self.title(f"KO4 ELITE MACRO v{VERSION}")
        self.geometry("450x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.is_running = False
        self.listening_key_shield = False
        self.listening_key_sword = False
        
        self.default_config = {
            "shield_x": 1574, "shield_y": 507, "shield_key": "v", "shield_delay": 0.0,
            "region_x1": 0, "region_y1": 0, "region_x2": 100, "region_y2": 100,
            "sword_key": "c", "sword_delay": 0.0
        }
        
        self.config = self.load_config()
        self.create_widgets()

    def create_widgets(self):
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a")
        self.header_frame.pack(fill="x")
        ctk.CTkLabel(self.header_frame, text="🛡️ KO4 DOSTLARA ÖZEL", font=("Roboto Medium", 20), text_color="#e74c3c").pack(pady=15)

        self.tabview = ctk.CTkTabview(self, width=400, height=350)
        self.tabview.pack(pady=10)
        
        self.tab_shield = self.tabview.add("🛡️ KALKAN")
        self.tab_sword = self.tabview.add("👁️ KILIÇ SİL")

        self.build_shield_tab()
        self.build_sword_tab()

        self.status_card = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.status_card.pack(fill="x", padx=20, pady=5)
        self.status_label = ctk.CTkLabel(self.status_card, text="SİSTEM HAZIR", font=("Roboto", 14, "bold"), text_color="#95a5a6")
        self.status_label.pack(pady=10)

        self.btn_toggle = ctk.CTkButton(self, text="SİSTEMİ BAŞLAT", font=("Roboto", 16, "bold"), height=50, fg_color="#27ae60", hover_color="#2ecc71", command=self.toggle_macro)
        self.btn_toggle.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self, text=f"v{VERSION} Auto-Update", text_color="gray", font=("Arial", 10)).pack(side="bottom", pady=5)

    def build_shield_tab(self):
        parent = self.tab_shield
        ctk.CTkLabel(parent, text="ENVANTER KOORDİNATI", font=("Roboto", 10, "bold")).pack(pady=5)
        
        coord_frame = ctk.CTkFrame(parent, fg_color="transparent")
        coord_frame.pack()
        
        self.entry_shield_x = ctk.CTkEntry(coord_frame, width=60); self.entry_shield_x.pack(side="left", padx=5)
        self.entry_shield_x.insert(0, self.config["shield_x"])
        self.entry_shield_y = ctk.CTkEntry(coord_frame, width=60); self.entry_shield_y.pack(side="left", padx=5)
        self.entry_shield_y.insert(0, self.config["shield_y"])
        
        ctk.CTkButton(coord_frame, text="BUL (F10)", width=80, fg_color="#e67e22", command=lambda: self.pick_coord("shield")).pack(side="left", padx=5)
        self.build_common_settings(parent, "shield")

    def build_sword_tab(self):
        parent = self.tab_sword
        ctk.CTkLabel(parent, text="KILIÇ BÖLGESİ", font=("Roboto", 10, "bold")).pack(pady=5)
        ctk.CTkLabel(parent, text="Debuff kutusunu seçin.", font=("Arial", 10), text_color="gray").pack()
        
        ctk.CTkButton(parent, text="🖱️ DEBUFF ALANINI TANIMLA", fg_color="#3498db", hover_color="#2980b9", height=40, command=self.open_snipping_tool).pack(pady=15)
        
        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.pack()
        self.lbl_region_info = ctk.CTkLabel(info_frame, text=f"[{self.config['region_x1']},{self.config['region_y1']}] - [{self.config['region_x2']},{self.config['region_y2']}]", text_color="#e74c3c", font=("Arial", 10, "bold"))
        self.lbl_region_info.pack(side="left", padx=5)

        self.build_common_settings(parent, "sword")

    def open_snipping_tool(self):
        self.withdraw()
        time.sleep(0.2)
        SnippingTool(self, self.on_snip_finished)

    def on_snip_finished(self, x1, y1, x2, y2):
        self.deiconify()
        self.config["region_x1"] = int(x1); self.config["region_y1"] = int(y1)
        self.config["region_x2"] = int(x2); self.config["region_y2"] = int(y2)
        self.lbl_region_info.configure(text=f"[{x1},{y1}] - [{x2},{y2}]")
        self.save_config()
        messagebox.showinfo("Başarılı", "Tarama alanı kaydedildi!")

    def build_common_settings(self, parent, prefix):
        set_frame = ctk.CTkFrame(parent, fg_color="transparent")
        set_frame.pack(pady=20)
        ctk.CTkLabel(set_frame, text="Tuş:").pack(side="left")
        btn_key = ctk.CTkButton(set_frame, text=self.config[f"{prefix}_key"].upper(), width=50, fg_color="#34495e", command=lambda: self.listen_for_key(prefix))
        btn_key.pack(side="left", padx=5)
        setattr(self, f"btn_{prefix}_key", btn_key)
        ctk.CTkLabel(set_frame, text="Gecikme:").pack(side="left", padx=(10,5))
        entry_delay = ctk.CTkEntry(set_frame, width=50)
        entry_delay.insert(0, self.config[f"{prefix}_delay"])
        entry_delay.pack(side="left")
        setattr(self, f"entry_{prefix}_delay", entry_delay)

    def load_config(self):
        final = self.default_config.copy()
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: final.update(json.load(f))
            except: pass
        return final

    def save_config(self):
        try:
            self.config["shield_x"] = int(self.entry_shield_x.get())
            self.config["shield_y"] = int(self.entry_shield_y.get())
            self.config["shield_delay"] = float(self.entry_shield_delay.get())
            self.config["sword_delay"] = float(self.entry_sword_delay.get())
            with open(CONFIG_FILE, "w") as f: json.dump(self.config, f)
        except: pass

    def pick_coord(self, target):
        self.status_label.configure(text="MOUSE'U GÖTÜR (3 sn)", text_color="#e67e22")
        self.update()
        time.sleep(3)
        x, y = pydirectinput.position()
        if target == "shield":
            self.entry_shield_x.delete(0, tk.END); self.entry_shield_x.insert(0, x)
            self.entry_shield_y.delete(0, tk.END); self.entry_shield_y.insert(0, y)
        self.status_label.configure(text="KOORDİNAT KAYDEDİLDİ", text_color="#3498db")
        self.after(1500, lambda: self.status_label.configure(text="SİSTEM HAZIR", text_color="#95a5a6"))

    def listen_for_key(self, target):
        getattr(self, f"btn_{target}_key").configure(text="...")
        if target == "shield": self.listening_key_shield = True
        else: self.listening_key_sword = True
        threading.Thread(target=self._wait_key, args=(target,), daemon=True).start()

    def _wait_key(self, target):
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN and event.name not in ['esc', 'enter']:
            self.config[f"{target}_key"] = event.name
            getattr(self, f"btn_{target}_key").configure(text=event.name.upper())
            if target == "shield": self.listening_key_shield = False
            else: self.listening_key_sword = False

    def toggle_macro(self):
        if self.is_running:
            self.is_running = False
            self.btn_toggle.configure(text="SİSTEMİ BAŞLAT", fg_color="#27ae60")
            self.status_label.configure(text="SİSTEM DURDURULDU", text_color="#95a5a6")
        else:
            self.save_config()
            self.is_running = True
            self.btn_toggle.configure(text="SİSTEMİ DURDUR", fg_color="#c0392b")
            self.status_label.configure(text="SİSTEM AKTİF", text_color="#2ecc71")
            threading.Thread(target=self.macro_loop, daemon=True).start()

    def macro_loop(self):
        while self.is_running:
            if keyboard.is_pressed(self.config["shield_key"]):
                try: perform_shield_macro(int(self.entry_shield_x.get()), int(self.entry_shield_y.get()), float(self.entry_shield_delay.get()))
                except: pass
            
            if keyboard.is_pressed(self.config["sword_key"]):
                try:
                    x1, y1 = self.config["region_x1"], self.config["region_y1"]
                    x2, y2 = self.config["region_x2"], self.config["region_y2"]
                    w, h = x2 - x1, y2 - y1
                    if w > 0 and h > 0:
                        perform_sword_scan_macro((x1, y1, w, h), float(self.entry_sword_delay.get()))
                except: pass
            time.sleep(0.001)

if __name__ == "__main__":
    app = MacroApp()
    app.mainloop()