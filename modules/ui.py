# modules/ui.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import time
import keyboard
import pydirectinput
import json
import os
import sys
import math 

from .constants import VERSION, CONFIG_FILE, LOGO_NAME, ICON_NAME, DEFAULT_CONFIG, COLORS
from .core import perform_shield_macro, perform_sword_scan_macro, check_and_download_assets
from .updater import AutoUpdater

# Profesyonel Ayrıştırma: Diğer modülleri çağırıyoruz
from .snipping import SnippingTool


# --- RENK MATEMATİĞİ ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

def interpolate_color(start_hex, end_hex, factor):
    c1 = hex_to_rgb(start_hex)
    c2 = hex_to_rgb(end_hex)
    new_rgb = tuple(int(c1[i] + (c2[i] - c1[i]) * factor) for i in range(3))
    return rgb_to_hex(new_rgb)

# --- ANA ARAYÜZ ---
class MacroApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if os.path.exists(ICON_NAME):
            try: self.iconbitmap(ICON_NAME)
            except: pass
        if os.path.exists(LOGO_NAME):
            try:
                icon_img = ImageTk.PhotoImage(file=LOGO_NAME)
                self.iconphoto(False, icon_img)
            except: pass

        threading.Thread(target=check_and_download_assets, daemon=True).start()
        
        self.updater = AutoUpdater(VERSION, self)
        self.updater.check_for_updates()

        self.title(f"SCUDERIA FERRARI v{VERSION}")
        self.geometry("450x630")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=COLORS["bg_main"])

        self.is_running = False
        self.listening_key_shield = False
        self.listening_key_sword = False
        
        self.config = self.load_config()
        self.create_widgets()
        
        self.pulse_step = 0
        self.animate_heartbeat()

    def create_widgets(self):
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["bg_main"])
        self.header_frame.pack(fill="x")
        
        header_text = "   SCUDERIA FERRARI"
        self.header_label = ctk.CTkLabel(self.header_frame, text=header_text, font=("Montserrat", 26, "bold"), text_color=COLORS["ferrari_red"])
        
        if os.path.exists(LOGO_NAME):
            try:
                pil_img = Image.open(LOGO_NAME)
                head_img = ctk.CTkImage(pil_img, size=(40, 40))
                self.header_label.configure(image=head_img, compound="left")
            except: pass
            
        self.header_label.pack(pady=20)

        self.tabview = ctk.CTkTabview(
            self, 
            width=420, 
            height=380,
            fg_color=COLORS["bg_main"],
            segmented_button_fg_color=COLORS["bg_card"],
            segmented_button_selected_color=COLORS["ferrari_red"],
            segmented_button_selected_hover_color=COLORS["ferrari_dark"],
            segmented_button_unselected_color=COLORS["bg_card"],
            segmented_button_unselected_hover_color=COLORS["border_grey"],
            text_color=COLORS["text_white"]
        )
        self.tabview._segmented_button.configure(font=("Roboto Medium", 13))
        self.tabview.pack(pady=10)
        
        self.tab_shield = self.tabview.add("🛡️ KALKAN")
        self.tab_sword = self.tabview.add("👁️ KILIÇ SİL")

        self.build_shield_tab()
        self.build_sword_tab()

        self.status_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border_grey"])
        self.status_card.pack(fill="x", padx=20, pady=5)
        self.status_label = ctk.CTkLabel(self.status_card, text="SİSTEM HAZIR", font=("Roboto Medium", 14), text_color=COLORS["text_grey"])
        self.status_label.pack(pady=10)

        self.btn_toggle = ctk.CTkButton(
            self, 
            text="ENGINE START",
            font=("Montserrat", 18, "bold"),
            height=55, 
            corner_radius=12,
            fg_color=COLORS["ferrari_red"],
            hover_color=COLORS["ferrari_glow"],
            text_color="white",
            command=self.toggle_macro
        )
        self.btn_toggle.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(self, text=f"v{VERSION} Auto-Update", text_color=COLORS["text_grey"], font=("Arial", 10)).pack(side="bottom", pady=5)

    def build_shield_tab(self):
        parent = self.tab_shield
        ctk.CTkLabel(parent, text="ENVANTER KOORDİNATI", font=("Roboto Medium", 12), text_color=COLORS["text_white"]).pack(pady=(10, 5))
        
        coord_frame = ctk.CTkFrame(parent, fg_color="transparent")
        coord_frame.pack()
        
        self.entry_shield_x = ctk.CTkEntry(coord_frame, width=65, justify="center", font=("Consolas", 12), fg_color=COLORS["bg_input"], border_color=COLORS["border_grey"], text_color="white")
        self.entry_shield_x.pack(side="left", padx=5)
        self.entry_shield_x.insert(0, self.config["shield_x"])
        
        self.entry_shield_y = ctk.CTkEntry(coord_frame, width=65, justify="center", font=("Consolas", 12), fg_color=COLORS["bg_input"], border_color=COLORS["border_grey"], text_color="white")
        self.entry_shield_y.pack(side="left", padx=5)
        self.entry_shield_y.insert(0, self.config["shield_y"])
        
        ctk.CTkButton(
            coord_frame, 
            text="BUL (F10)", 
            width=85,
            font=("Roboto Medium", 12),
            fg_color=COLORS["ferrari_yellow"], 
            text_color=COLORS["text_black"],
            hover_color=COLORS["ferrari_yellow_hover"], 
            command=lambda: self.pick_coord("shield")
        ).pack(side="left", padx=5)
        
        self.build_common_settings(parent, "shield")

    def build_sword_tab(self):
        parent = self.tab_sword
        ctk.CTkLabel(parent, text="KILIÇ BÖLGESİ", font=("Roboto Medium", 12), text_color=COLORS["text_white"]).pack(pady=(10, 5))
        ctk.CTkLabel(parent, text="Debuff kutusunu seçin.", font=("Arial", 10), text_color=COLORS["text_grey"]).pack()
        
        ctk.CTkButton(
            parent, 
            text="🖱️ DEBUFF ALANINI TANIMLA", 
            fg_color=COLORS["bg_card"],
            font=("Roboto Medium", 12),
            border_width=2,
            border_color=COLORS["ferrari_red"],
            hover_color=COLORS["border_grey"],
            height=40, 
            command=self.open_snipping_tool
        ).pack(pady=15)
        
        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.pack()
        self.lbl_region_info = ctk.CTkLabel(info_frame, text=f"[{self.config['region_x1']},{self.config['region_y1']}] - [{self.config['region_x2']},{self.config['region_y2']}]", text_color=COLORS["ferrari_red"], font=("Consolas", 11, "bold"))
        self.lbl_region_info.pack(side="left", padx=5)

        self.build_common_settings(parent, "sword")

    def build_common_settings(self, parent, prefix):
        set_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border_grey"])
        set_frame.pack(pady=25, padx=10, fill="x")
        inner_frame = ctk.CTkFrame(set_frame, fg_color="transparent")
        inner_frame.pack(pady=15)
        
        font_label = ("Roboto Medium", 12)
        
        ctk.CTkLabel(inner_frame, text="ATANAN TUŞ:", font=font_label, text_color=COLORS["text_grey"]).pack(side="left", padx=(0, 10))

        btn_key = ctk.CTkButton(
            inner_frame, 
            text=self.config[f"{prefix}_key"].upper(), 
            width=70, height=35,
            font=("Roboto Medium", 14), 
            fg_color=COLORS["bg_input"],
            border_width=1,
            border_color=COLORS["border_grey"],
            hover_color=COLORS["border_grey"],
            corner_radius=8,
            command=lambda: self.listen_for_key(prefix)
        )
        btn_key.pack(side="left", padx=(0, 25))
        setattr(self, f"btn_{prefix}_key", btn_key)

        ctk.CTkLabel(inner_frame, text="GECİKME (SN):", font=font_label, text_color=COLORS["text_grey"]).pack(side="left", padx=(10, 10))

        entry_delay = ctk.CTkEntry(
            inner_frame, width=70, height=35,
            font=("Consolas", 13), justify="center",
            corner_radius=8, 
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border_grey"],
            text_color="white"
        )
        entry_delay.insert(0, self.config[f"{prefix}_delay"])
        entry_delay.pack(side="left")
        setattr(self, f"entry_{prefix}_delay", entry_delay)

    def animate_heartbeat(self):
        if not self.is_running:
            pulse = (math.sin(self.pulse_step / 10) + 1) / 2 
            current_color = interpolate_color(COLORS["ferrari_dark"], COLORS["ferrari_red"], pulse)
            self.btn_toggle.configure(fg_color=current_color)
            self.pulse_step += 1
        self.after(50, self.animate_heartbeat)

    def load_config(self):
        final = DEFAULT_CONFIG.copy()
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
        self.status_label.configure(text="MOUSE'U GÖTÜR (3 sn)", text_color=COLORS["ferrari_yellow"])
        self.update()
        time.sleep(3)
        x, y = pydirectinput.position()
        if target == "shield":
            self.entry_shield_x.delete(0, tk.END); self.entry_shield_x.insert(0, x)
            self.entry_shield_y.delete(0, tk.END); self.entry_shield_y.insert(0, y)
        self.status_label.configure(text="KOORDİNAT KAYDEDİLDİ", text_color=COLORS["ferrari_red"])
        self.after(1500, lambda: self.status_label.configure(text="SİSTEM HAZIR", text_color=COLORS["text_grey"]))

    def listen_for_key(self, target):
        getattr(self, f"btn_{target}_key").configure(text="...", fg_color=COLORS["ferrari_red"])
        if target == "shield": self.listening_key_shield = True
        else: self.listening_key_sword = True
        threading.Thread(target=self._wait_key, args=(target,), daemon=True).start()

    def _wait_key(self, target):
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN and event.name not in ['esc', 'enter']:
            self.config[f"{target}_key"] = event.name
            getattr(self, f"btn_{target}_key").configure(text=event.name.upper(), fg_color=COLORS["bg_input"])
            if target == "shield": self.listening_key_shield = False
            else: self.listening_key_sword = False

    def toggle_macro(self):
        if self.is_running:
            self.is_running = False
            self.btn_toggle.configure(text="ENGINE START", fg_color=COLORS["ferrari_red"])
            self.status_label.configure(text="SİSTEM DURDURULDU", text_color=COLORS["text_grey"])
        else:
            self.save_config()
            self.is_running = True
            self.btn_toggle.configure(text="STOP ENGINE", fg_color=COLORS["stop_red"])
            self.status_label.configure(text="SİSTEM AKTİF (RACE MODE)", text_color=COLORS["ferrari_glow"])
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