# modules/ui.py
import customtkinter as ctk
import tkinter as tk
from PIL import Image
import threading
import time
import keyboard
import pydirectinput
import os
import sys
import math
import logging
import ctypes 
from datetime import datetime

# Bileşenler
from .components.toast import ToastNotification
from .components.announcement import AnnouncementWindow
from .components.module_card import ModuleCard, CTkToolTip
from .components.settings_window import SettingsWindow

from .constants import *
from .engine import AutomationEngine
from .updater import AutoUpdater
from .snipping import SnippingTool
from .config_manager import ConfigManager 

logger = logging.getLogger(__name__)

# --- WINDOWS API FARE KONTROLÜ ---
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_mouse_pos():
    """Windows API kullanarak farenin anlık X,Y koordinatlarını okur."""
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

class SidebarButton(ctk.CTkButton):
    """Sol menü için özel stil butonu"""
    def __init__(self, parent, text, icon, cmd, active=False):
        fg = COLORS["bg_input"] if active else "transparent"
        txt_col = "white" if active else COLORS["text_dim"]
        border_c = COLORS["accent_primary"] if active else "transparent"
        
        super().__init__(
            parent, text=f"  {icon}   {text}", anchor="w", 
            height=45, corner_radius=6, border_width=1 if active else 0,
            fg_color=fg, text_color=txt_col, border_color=border_c,
            hover_color=COLORS["bg_input"], font=("Segoe UI", 12, "bold" if active else "normal"),
            command=cmd
        )

class MacroApp(ctk.CTk):
    def __init__(self, auth_api=None): 
        super().__init__()
        self.alive = True
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.cfg = ConfigManager()
        self.auth_api = auth_api 
        self.engine = AutomationEngine(self.cfg)
        
        self._init_window()
        self._init_system_threads()
        
        self.create_layout()
        
        self.pulse_step = 0
        self.animate_heartbeat()
        self.log_to_console("Nexus Core initialized.")

    def _init_window(self):
        if os.path.exists(ICON_NAME): 
            try: self.iconbitmap(ICON_NAME)
            except: pass
            
        self.title(f"{APP_TITLE} | COMMAND CENTER")
        self.geometry("1280x800")
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=COLORS["bg_main"])
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _init_system_threads(self):
        if self.auth_api:
            threading.Thread(target=self._security_watchdog, daemon=True).start()
            threading.Thread(target=self.check_server_announcement, daemon=True).start()
        
        self.updater = AutoUpdater(VERSION, self)
        self.updater.check_for_updates()
        
        self.listening_key_shield = False
        self.listening_key_sword = False
        self.listening_key_restore = False
        self.listening_key_combo = False 
        self.listening_key_mage56 = False
        self.listening_key_archer35 = False

    def create_layout(self):
        # --- SOL SIDEBAR ---
        sidebar = ctk.CTkFrame(self, fg_color=COLORS["bg_sidebar"], width=240, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(4, weight=1)

        if os.path.exists(LOGO_NAME):
            try:
                pil_img = Image.open(LOGO_NAME)
                logo_img = ctk.CTkImage(pil_img, size=(180, 55))
                ctk.CTkLabel(sidebar, text="", image=logo_img).pack(pady=(40, 30))
            except: pass
        else:
            ctk.CTkLabel(sidebar, text=APP_TITLE, font=("Arial Black", 24), text_color="white").pack(pady=(40, 30))

        SidebarButton(sidebar, "KONTROL PANELİ", "⚡", lambda: None, True).pack(fill="x", padx=15, pady=5)
        
        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.pack(side="bottom", pady=20, padx=20, fill="x")
        ctk.CTkLabel(footer, text=f"CORE: v{VERSION}", font=("Consolas", 10), text_color=COLORS["text_dim"]).pack(anchor="w")
        
        status_row = ctk.CTkFrame(footer, fg_color="transparent")
        status_row.pack(anchor="w", pady=(2,0))
        ctk.CTkLabel(status_row, text="●", font=("Arial", 10), text_color=COLORS["green_neon"]).pack(side="left")
        ctk.CTkLabel(status_row, text=" SYSTEM READY", font=("Consolas", 10, "bold"), text_color=COLORS["accent_primary"]).pack(side="left", padx=5)

        # --- SAĞ İÇERİK ---
        main = ctk.CTkFrame(self, fg_color=COLORS["bg_main"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        
        container = ctk.CTkFrame(main, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="OPERASYON MERKEZİ", font=("Arial", 24, "bold"), text_color="white").pack(side="left")
        
        self.status_badge = ctk.CTkButton(
            header, text="BEKLEMEDE", font=("Consolas", 11, "bold"),
            fg_color="transparent", text_color=COLORS["text_dim"], hover=False,
            border_width=1, border_color=COLORS["border_dim"], height=32, corner_radius=16
        )
        self.status_badge.pack(side="right")

        row1_frame = ctk.CTkFrame(container, fg_color="transparent")
        row1_frame.pack(fill="x", pady=(0, 15))
        row1_frame.grid_columnconfigure((0,1,2), weight=1)

        ModuleCard(row1_frame, self, "sword", "ATAK", IMAGE_NAME, "⚔", self._setup_sword_extras, 0)
        ModuleCard(row1_frame, self, "shield", "KALKAN", SHIELD_IMAGE_NAME, "🛡", self._setup_shield_extras, 1)
        ModuleCard(row1_frame, self, "restore", "YAŞAM", RESTORE_IMAGE_NAME, "❤️", self._setup_restore_extras, 2)

        row2_frame = ctk.CTkFrame(container, fg_color="transparent")
        row2_frame.pack(fill="x")
        row2_frame.grid_columnconfigure((0,1,2), weight=1)

        ModuleCard(row2_frame, self, "mage56", "MAGE 56", "", "🔥", self._setup_mage56_extras, 0)
        ModuleCard(row2_frame, self, "archer35", "OKÇU 3-5", ARROWS_IMAGE_NAME, "🏹", self._setup_archer35_extras, 1)
        ModuleCard(row2_frame, self, "combo", "KOMBO", ATTACK_IMAGE_NAME, "⚡", self._setup_combo_extras, 2)

        bottom_panel = ctk.CTkFrame(container, fg_color="transparent")
        bottom_panel.pack(fill="x", side="bottom", pady=20) 

        self.btn_toggle = ctk.CTkButton(
            bottom_panel, text="SAVAŞ MOTORUNU BAŞLAT", font=("Consolas", 14, "bold"), 
            width=280, height=45, corner_radius=4,
            fg_color="transparent", border_width=1, border_color=COLORS["accent_dim"],
            text_color=COLORS["text_main"], hover_color=COLORS["bg_panel"],
            command=self.toggle_macro
        )
        self.btn_toggle.pack(pady=10)

    def log_to_console(self, message):
        pass

    def toggle_macro(self):
        if self.engine.is_running:
            self.engine.stop()
            self.log_to_console("Motor durduruldu.")
        else:
            if not self.run_preflight_checks(): return
            self.sync_ui_state() 
            self.engine.start()
            self.log_to_console("Motor başlatıldı. Protokoller aktif.")
            self.show_toast("AKTİF", "Voberix devrede.", type="success")

    def animate_heartbeat(self):
        if not self.alive: return
        if self.engine.is_running:
            pulse = (math.sin(self.pulse_step / 5.0) + 1) / 2 
            color = self.interpolate_color(COLORS["bg_main"], COLORS["green_neon"], pulse)
            
            self.btn_toggle.configure(
                border_color=color, 
                text="MOTOR DEVREDE (DURDUR)", 
                text_color=COLORS["green_neon"],
                fg_color="transparent"
            )
            self.status_badge.configure(text="SİSTEM AKTİF", text_color=COLORS["cyan_neon"], border_color=COLORS["cyan_neon"])
            self.pulse_step += 1
        else:
            self.btn_toggle.configure(
                border_color=COLORS["accent_dim"], 
                text="SAVAŞ MOTORUNU BAŞLAT", 
                text_color=COLORS["text_main"],
                fg_color="transparent"
            )
            if self.pulse_step != 0: 
                 self.status_badge.configure(text="SİSTEM HAZIR", text_color=COLORS["text_dim"], border_color=COLORS["border_dim"])
        self.after(50, self.animate_heartbeat)

    def _setup_combo_extras(self, parent):
        ctk.CTkLabel(parent, text="Sıralama:", font=("Arial", 10, "bold"), text_color=COLORS["text_dim"]).pack(pady=(5,0))
        
        seq_frame = ctk.CTkFrame(parent, fg_color="transparent")
        seq_frame.pack(pady=2, fill="x")
        
        self.entry_combo_seq = ctk.CTkEntry(seq_frame, width=90, height=26, font=("Consolas", 11), fg_color=COLORS["bg_input"], border_width=1, border_color=COLORS["border_dim"])
        self.entry_combo_seq.pack(side="left", padx=(0,5))
        self.entry_combo_seq.insert(0, self.cfg.get("combo_sequence", "R-R-2"))
        
        ctk.CTkButton(
            seq_frame, text="Kaydet", width=40, height=26,
            fg_color=COLORS["bg_input"], hover_color=COLORS["btn_hover"], border_width=1, border_color=COLORS["border_dim"],
            command=lambda: [self.cfg.set("combo_sequence", self.entry_combo_seq.get()), self.focus()]
        ).pack(side="left")

        ctk.CTkLabel(parent, text="Hız:", font=("Arial", 10, "bold"), text_color=COLORS["text_dim"]).pack(pady=(8,0))
        self.entry_combo_val = ctk.CTkEntry(parent, width=140, height=26, font=("Consolas", 11), fg_color=COLORS["bg_input"], border_width=1, border_color=COLORS["border_dim"])
        self.entry_combo_val.pack(pady=2)
        
        self.seg_unit = ctk.CTkSegmentedButton(
            parent, values=["MS", "SN", "DK"], width=140, height=22,
            selected_color=COLORS["accent_primary"], selected_hover_color=COLORS["accent_hover"],
            font=("Arial", 9, "bold"), command=self._on_combo_unit_change
        )
        self.seg_unit.pack(pady=5)
        
        ms = self.cfg.get("combo_delay_ms", 5.0)
        unit = self.cfg.get("combo_time_unit", "MS")
        self.seg_unit.set(unit)
        
        disp_val = ms
        if unit == "SN": disp_val = ms / 1000.0
        elif unit == "DK": disp_val = ms / 60000.0
        
        if float(disp_val).is_integer(): disp_val = int(disp_val)
        self.entry_combo_val.insert(0, str(disp_val))
        self.entry_combo_val.bind("<KeyRelease>", self._on_combo_val_change)

    def _on_combo_val_change(self, e): self._recalc_combo()
    def _on_combo_unit_change(self, v): self.cfg.set("combo_time_unit", v); self._recalc_combo()
    
    def _recalc_combo(self):
        try:
            val = float(self.entry_combo_val.get().replace(",", "."))
            unit = self.seg_unit.get()
            final_ms = val * (1000 if unit == "SN" else 60000 if unit == "DK" else 1)
            self.cfg.set("combo_delay_ms", final_ms)
        except: pass

    def _setup_mage56_extras(self, parent):
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", pady=(5, 5))
        ctk.CTkLabel(row1, text="Skill Tuşu (Örn: 2):", font=("Arial", 10, "bold"), text_color=COLORS["text_dim"]).pack(side="left")
        self.entry_mage56_skill = ctk.CTkEntry(row1, width=60, height=26, font=("Consolas", 12), fg_color=COLORS["bg_input"], border_width=1, border_color=COLORS["border_dim"], justify="center")
        self.entry_mage56_skill.pack(side="right")
        self.entry_mage56_skill.insert(0, self.cfg.get("mage56_skill_key", "2"))
        self.entry_mage56_skill.bind("<KeyRelease>", lambda e: self.cfg.set("mage56_skill_key", self.entry_mage56_skill.get()))

        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(row2, text="Staff (R) Tuşu:", font=("Arial", 10, "bold"), text_color=COLORS["text_dim"]).pack(side="left")
        self.entry_mage56_r = ctk.CTkEntry(row2, width=60, height=26, font=("Consolas", 12), fg_color=COLORS["bg_input"], border_width=1, border_color=COLORS["border_dim"], justify="center")
        self.entry_mage56_r.pack(side="right")
        self.entry_mage56_r.insert(0, self.cfg.get("mage56_r_key", "r"))
        self.entry_mage56_r.bind("<KeyRelease>", lambda e: self.cfg.set("mage56_r_key", self.entry_mage56_r.get()))

    def _setup_archer35_extras(self, parent):
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", pady=(5, 5))
        ctk.CTkLabel(row1, text="5'li OK (Örn: 3):", font=("Arial", 10, "bold"), text_color=COLORS["text_dim"]).pack(side="left")
        self.entry_arch35_s1 = ctk.CTkEntry(row1, width=60, height=26, font=("Consolas", 12), fg_color=COLORS["bg_input"], border_width=1, border_color=COLORS["border_dim"], justify="center")
        self.entry_arch35_s1.pack(side="right")
        self.entry_arch35_s1.insert(0, self.cfg.get("archer35_skill1_key", "3"))
        self.entry_arch35_s1.bind("<KeyRelease>", lambda e: self.cfg.set("archer35_skill1_key", self.entry_arch35_s1.get()))

        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(row2, text="3'lü OK (Örn: 4):", font=("Arial", 10, "bold"), text_color=COLORS["text_dim"]).pack(side="left")
        self.entry_arch35_s2 = ctk.CTkEntry(row2, width=60, height=26, font=("Consolas", 12), fg_color=COLORS["bg_input"], border_width=1, border_color=COLORS["border_dim"], justify="center")
        self.entry_arch35_s2.pack(side="right")
        self.entry_arch35_s2.insert(0, self.cfg.get("archer35_skill2_key", "4"))
        self.entry_arch35_s2.bind("<KeyRelease>", lambda e: self.cfg.set("archer35_skill2_key", self.entry_arch35_s2.get()))
        
    def _setup_sword_extras(self, p):
        ctk.CTkButton(p, text="ALAN SEÇ", height=25, fg_color=COLORS["bg_input"], hover_color=COLORS["btn_hover"], 
                      border_width=1, border_color=COLORS["border_dim"], command=self.open_snipping_tool).pack(pady=10)
    
    def _setup_shield_extras(self, p):
        self.btn_shield_learn = ctk.CTkButton(p, text="KONUM ÖĞRET", height=25, fg_color=COLORS["bg_input"], hover_color=COLORS["btn_hover"], 
                      border_width=1, border_color=COLORS["border_dim"], command=lambda: self.pick_coord("shield"))
        self.btn_shield_learn.pack(pady=10)
        self.entry_shield_x = ctk.CTkEntry(p, width=0, height=0); self.entry_shield_x.insert(0, self.cfg.get("shield_x"))
        self.entry_shield_y = ctk.CTkEntry(p, width=0, height=0); self.entry_shield_y.insert(0, self.cfg.get("shield_y"))

    def _setup_restore_extras(self, p): 
        ctk.CTkButton(p, text="ALAN SEÇ", height=25, fg_color=COLORS["bg_input"], hover_color=COLORS["btn_hover"], 
                      border_width=1, border_color=COLORS["border_dim"], command=self.open_snipping_tool).pack(pady=10)

    def sync_ui_state(self):
        try:
            if hasattr(self, 'entry_shield_x'):
                self.cfg.set("shield_x", int(self.entry_shield_x.get()), save_now=False)
                self.cfg.set("shield_y", int(self.entry_shield_y.get()), save_now=True)
        except: pass 

    def open_snipping_tool(self):
        self.withdraw(); time.sleep(0.2)
        SnippingTool(self, self.on_snip_finished)

    def on_snip_finished(self, x1, y1, x2, y2):
        self.deiconify()
        self.cfg.set("region_x1", x1, False); self.cfg.set("region_y1", y1, False)
        self.cfg.set("region_x2", x2, False); self.cfg.set("region_y2", y2, True) 
        self.show_toast("BAŞARILI", "Tarama alanı güncellendi.", "success")

    def pick_coord(self, target):
        if target == "shield":
            self.show_toast("BİLGİ", "Fareyi kalkanın üzerine götür ve klavyeden CTRL tuşuna bas.", "warning")
            self.status_badge.configure(text="MOD: ÖĞRENME", text_color=COLORS["yellow_neon"], border_color=COLORS["yellow_neon"])
            self.btn_shield_learn.configure(text="CTRL BEKLENİYOR...", fg_color=COLORS["yellow_neon"], text_color="black")
            
            def wait_for_key():
                time.sleep(0.3)
                while getattr(self, "alive", True):
                    if keyboard.is_pressed('ctrl'):
                        break
                    time.sleep(0.01)
                
                x, y = get_mouse_pos()
                
                def update_ui():
                    self.entry_shield_x.delete(0, tk.END); self.entry_shield_x.insert(0, x)
                    self.entry_shield_y.delete(0, tk.END); self.entry_shield_y.insert(0, y)
                    self.cfg.set("shield_x", x, False); self.cfg.set("shield_y", y, True)
                    
                    self.btn_shield_learn.configure(text="KONUM ÖĞRET", fg_color=COLORS["bg_input"], text_color=COLORS["text_main"])
                    self.show_toast("KAYDEDİLDİ", f"Kalkan Koordinatı: {x}x{y}", "success")
                    self.status_badge.configure(text="SİSTEM HAZIR", text_color=COLORS["text_dim"], border_color=COLORS["border_dim"])
                
                self.after(0, update_ui)
                
            threading.Thread(target=wait_for_key, daemon=True).start()

    def listen_for_key(self, target):
        btn = getattr(self, f"btn_{target}_key")
        btn.configure(text="Dinleniyor...", fg_color=COLORS["bg_input"], border_color=COLORS["border_focus"])
        threading.Thread(target=self._wait_key, args=(target,), daemon=True).start()

    def _wait_key(self, target):
        try:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN and event.name not in ['esc', 'enter']:
                self.cfg.set(f"{target}_key", event.name)
                getattr(self, f"btn_{target}_key").configure(
                    text=f"Buton Seç ({event.name.upper()})", 
                    fg_color=COLORS["bg_input"], 
                    border_color=COLORS["border_dim"]
                )
        except: pass

    def run_preflight_checks(self):
        if self.auth_api:
            try:
                res = self.auth_api.check()
                if not res.get("success", False): return False
            except: return False
        return True

    def _security_watchdog(self):
        while self.alive:
            time.sleep(30) 
            if not self.alive: break
            try:
                res = self.auth_api.check()
                if not res.get("success", False):
                    msg = res.get("message", "Lisans süresi doldu veya oturum sonlandı.")
                    self.after(0, lambda m=msg: self.trigger_security_lockdown(m))
                    break
            except Exception as e:
                pass

    def check_server_announcement(self):
        try:
            data = self.auth_api.var("GlobalDuyuru")
            if data.get("success") and data.get("message") and data["message"].lower() != "yok":
                self.after(0, lambda: AnnouncementWindow(self, data["message"]))
        except: pass

    # --- EKSİK OLAN BİLDİRİM FONKSİYONU GERİ EKLENDİ ---
    def show_toast(self, title, message, type="success"):
        """Ekranda sağ alt köşede şık bildirimler (toast) gösterir."""
        if type == "error": color_key = "red_error"
        elif type == "warning": color_key = "yellow_neon"
        else: color_key = "cyan_neon" 
        ToastNotification(self, title, message, color_key)

    def trigger_security_lockdown(self, reason):
        self.engine.stop() 
        
        try:
            if os.path.exists(LICENSE_FILE):
                os.remove(LICENSE_FILE)
        except: pass

        self.show_toast("GÜVENLİK UYARISI", reason, type="error") 
        self.after(3000, self.on_closing) 
    
    def open_settings(self): SettingsWindow(self)

    def on_closing(self):
        self.alive = False
        if hasattr(self, 'engine'): self.engine.stop()
        if hasattr(self, 'updater'): 
            try: self.updater.stop()
            except: pass
        self.destroy()
        sys.exit(0)

    def interpolate_color(self, start_hex, end_hex, factor):
        def hex_to_rgb(hex_color): return tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        def rgb_to_hex(rgb_color): return '#%02x%02x%02x' % tuple(int(x) for x in rgb_color)
        c1 = hex_to_rgb(start_hex); c2 = hex_to_rgb(end_hex)
        new_rgb = tuple(c1[i] + (c2[i] - c1[i]) * factor for i in range(3))
        return rgb_to_hex(new_rgb)