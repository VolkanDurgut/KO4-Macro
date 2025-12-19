import tkinter as tk
from tkinter import messagebox
import threading
import time
import keyboard
import pydirectinput
import json
import os
import requests
import webbrowser

# --- SABİT AYARLAR (Senin GitHub Bilgilerinle Güncellendi) ---
VERSION = "1.0"
# Arkadaşların güncelleme var mı diye tıkladığında gidecekleri yer:
GITHUB_REPO_URL = "https://github.com/VolkanDurgut/KO4-Macro" 
# Programın versiyonu kontrol edeceği ham (raw) dosya adresi:
VERSION_FILE_URL = "https://raw.githubusercontent.com/VolkanDurgut/KO4-Macro/main/version.txt"
CONFIG_FILE = "config.json"

# --- OYUN İÇİ TIKLAMA FONKSİYONU ---
def perform_macro(x, y, delay):
    # Orijinal konumu sakla
    original_x, original_y = pydirectinput.position()
    
    # Kalkan slotuna git
    pydirectinput.moveTo(x, y)
    
    # Sağ tıkla (Kalkanı tak)
    pydirectinput.click(button='right')
    
    # İsteğe bağlı: Mouse'u eski yerine çok hızlı geri çek
    # pydirectinput.moveTo(original_x, original_y) 
    
    time.sleep(delay)

class MacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Clan Shield Macro - v{VERSION}")
        self.root.geometry("350x480")
        self.root.resizable(False, False)
        
        self.is_running = False
        self.listening_key = False
        
        # Varsayılan Değerler
        self.default_config = {
            "x": 1574,
            "y": 507,
            "key": "v",
            "delay": 0.1
        }
        
        self.config = self.load_config()
        self.create_widgets()
        
        # Açılışta güncelleme kontrolü yap
        self.check_updates()

    def create_widgets(self):
        # Başlık
        tk.Label(self.root, text="🛡️ KO4 Kalkan Makrosu", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Durum Göstergesi
        self.status_frame = tk.Frame(self.root, highlightbackground="gray", highlightthickness=1)
        self.status_frame.pack(pady=5, padx=20, fill="x")
        self.status_label = tk.Label(self.status_frame, text="DURUM: KAPALI", fg="red", font=("Segoe UI", 12, "bold"))
        self.status_label.pack(pady=5)

        # Koordinat Ayarları
        frame_coords = tk.LabelFrame(self.root, text="Envanter Koordinatı", padx=10, pady=5)
        frame_coords.pack(pady=10)
        
        tk.Label(frame_coords, text="X:").grid(row=0, column=0)
        self.entry_x = tk.Entry(frame_coords, width=6, justify="center")
        self.entry_x.insert(0, self.config["x"])
        self.entry_x.grid(row=0, column=1, padx=5)

        tk.Label(frame_coords, text="Y:").grid(row=0, column=2)
        self.entry_y = tk.Entry(frame_coords, width=6, justify="center")
        self.entry_y.insert(0, self.config["y"])
        self.entry_y.grid(row=0, column=3, padx=5)
        
        # Koordinat Bulucu
        tk.Button(frame_coords, text="Konumu Seç (3sn)", command=self.start_coord_picker, bg="#f0f0f0", font=("Segoe UI", 8)).grid(row=0, column=4, padx=5)

        # Tuş ve Gecikme Ayarları
        frame_settings = tk.Frame(self.root)
        frame_settings.pack(pady=5)

        # Tuş
        tk.Label(frame_settings, text="Tuş:").grid(row=0, column=0)
        self.btn_key = tk.Button(frame_settings, text=self.config["key"].upper(), command=self.listen_for_key, width=8, bg="white")
        self.btn_key.grid(row=0, column=1, padx=5)

        # Gecikme
        tk.Label(frame_settings, text="Süre (sn):").grid(row=0, column=2)
        self.entry_delay = tk.Entry(frame_settings, width=5, justify="center")
        self.entry_delay.insert(0, self.config["delay"])
        self.entry_delay.grid(row=0, column=3, padx=5)

        # Başlat / Durdur Butonu
        self.btn_toggle = tk.Button(self.root, text="MAKROYU BAŞLAT", bg="#28a745", fg="white", font=("Segoe UI", 12, "bold"), command=self.toggle_macro, height=2, width=25)
        self.btn_toggle.pack(pady=20)

        # GitHub Linki
        lbl_link = tk.Label(self.root, text="GitHub Sayfasına Git", fg="blue", cursor="hand2", font=("Segoe UI", 8, "underline"))
        lbl_link.pack(side=tk.BOTTOM, pady=5)
        lbl_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_REPO_URL))

        tk.Label(self.root, text="Not: Yönetici olarak çalıştırınız.", fg="gray", font=("Segoe UI", 8)).pack(side=tk.BOTTOM, pady=0)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return self.default_config

    def save_config(self):
        try:
            self.config["x"] = int(self.entry_x.get())
            self.config["y"] = int(self.entry_y.get())
            self.config["delay"] = float(self.entry_delay.get())
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f)
        except ValueError:
            messagebox.showerror("Hata", "Lütfen koordinat ve süre için geçerli sayılar girin.")

    def start_coord_picker(self):
        self.status_label.config(text="3 sn içinde slota git!", fg="orange")
        self.root.update()
        time.sleep(3)
        x, y = pydirectinput.position()
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, x)
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, y)
        self.status_label.config(text="Koordinat Alındı!", fg="blue")
        # 1 saniye sonra eski haline dön
        self.root.after(1000, lambda: self.status_label.config(text="DURUM: KAPALI", fg="red"))

    def listen_for_key(self):
        self.btn_key.config(text="Bas...")
        self.listening_key = True
        threading.Thread(target=self._wait_key, daemon=True).start()

    def _wait_key(self):
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            self.config["key"] = event.name
            self.btn_key.config(text=event.name.upper())
            self.listening_key = False

    def toggle_macro(self):
        if self.is_running:
            self.is_running = False
            self.btn_toggle.config(text="MAKROYU BAŞLAT", bg="#28a745")
            self.status_label.config(text="DURUM: KAPALI", fg="red")
        else:
            self.save_config()
            self.is_running = True
            self.btn_toggle.config(text="DURDUR", bg="#dc3545")
            self.status_label.config(text=f"AÇIK: '{self.config['key'].upper()}' bekleniyor...", fg="green")
            threading.Thread(target=self.macro_loop, daemon=True).start()

    def macro_loop(self):
        while self.is_running:
            if keyboard.is_pressed(self.config["key"]):
                try:
                    x = int(self.entry_x.get())
                    y = int(self.entry_y.get())
                    delay = float(self.entry_delay.get())
                    perform_macro(x, y, delay)
                except:
                    pass
            time.sleep(0.01)

    def check_updates(self):
        threading.Thread(target=self._check_update_thread, daemon=True).start()

    def _check_update_thread(self):
        try:
            response = requests.get(VERSION_FILE_URL)
            if response.status_code == 200:
                remote_version = response.text.strip()
                if remote_version != VERSION:
                    self.root.after(0, lambda: self.show_update_dialog(remote_version))
        except Exception as e:
            print(f"Update check failed: {e}")

    def show_update_dialog(self, version):
        if messagebox.askyesno("Güncelleme Mevcut", f"Yeni versiyon ({version}) bulundu. İndirme sayfasına gitmek ister misiniz?"):
            webbrowser.open(GITHUB_REPO_URL)

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroApp(root)
    root.mainloop()