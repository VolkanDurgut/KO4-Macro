# modules/login.py
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image # Görselleri güvenli yüklemek için eklendi
import webbrowser
import os
import threading
import subprocess 
from .keyauth import api
from .constants import COLORS, LOGO_NAME, ICON_NAME, VERSION, LICENSE_FILE

# --- KEYAUTH AYARLARI ---
# DİKKAT: Bu bilgiler KeyAuth panelinizdekiyle BİREBİR aynı olmalı.
APP_NAME = "ScuderiaFerrari" # Paneldeki Application Name
OWNER_ID = "tFrtYO894n"      # Paneldeki Owner ID
SECRET = "8bf72b6bc09a90ced8c1b942b8139a7a1e0cccb0eedfab1eff8c852c8a102897" # Paneldeki Secret
KEYAUTH_VERSION = f"v{VERSION}" 

SHOPIER_URL = "https://www.shopier.com/SeninMagazan" 

# --- HWID ALMA FONKSİYONU (GÜVENLİ) ---
def get_hwid():
    """
    Bilgisayarın benzersiz donanım kimliğini alır.
    Hata durumunda programı çökertmez, 'Unknown' döner.
    """
    try:
        if os.name == 'nt':
            cmd = 'wmic csproduct get uuid'
            # creationflags=0x08000000 -> Konsol penceresi açılmasını engeller
            output = subprocess.check_output(cmd, shell=True, creationflags=0x08000000).decode()
            
            # Gelen veriyi satır satır ayır ve temizle
            lines = [line.strip() for line in output.split('\n') if line.strip()]
            
            # Genelde 2. satır UUID olur (1. satır başlıktır)
            if len(lines) > 1:
                return lines[1]
            return "Unknown-UUID-Format"
        else:
            return "Non-Windows-HWID"
    except Exception as e:
        print(f"HWID Okuma Hatası: {e}")
        return "Unknown-HWID-Error"

class LoginApp(ctk.CTk):
    def __init__(self, on_success_callback):
        super().__init__()
        self.on_success = on_success_callback
        
        # Pencere Ayarları
        self.title(f"KO4 TAKTİKSEL ERİŞİM - v{VERSION}")
        self.geometry("400x550")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=COLORS["bg_main"]) 
        
        # Pencere İkonu (Varsa)
        if os.path.exists(ICON_NAME): 
            try: self.iconbitmap(ICON_NAME)
            except: pass
            
        # KeyAuth Başlatma (Güvenli Blok)
        try:
            self.auth = api(APP_NAME, OWNER_ID, SECRET, KEYAUTH_VERSION, "")
        except Exception as e:
            # keyauth.py içindeki hatayı yakalar ve kullanıcıya gösterir
            messagebox.showerror("Sunucu Hatası", f"Güvenlik sunucusuna bağlanılamadı.\nDetay: {e}")
            self.destroy()
            return

        self.create_widgets()
        self.load_saved_key()

    def create_widgets(self):
        # --- HEADER ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(40, 20))

        # Logo Yükleme (EXE Uyumlu - PIL ile)
        if os.path.exists(LOGO_NAME):
            try:
                # GÜNCELLEME: Image.open kullanımı (PyInstaller dostu)
                pil_img = Image.open(LOGO_NAME)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(60, 60))
                ctk.CTkLabel(header_frame, text="", image=ctk_img).pack(pady=(0, 10))
            except Exception as e:
                print(f"Login logo hatası: {e}")

        ctk.CTkLabel(
            header_frame, 
            text="KO4 TACTICAL", 
            font=("Arial Black", 20), 
            text_color=COLORS["text_main"]
        ).pack()
        
        ctk.CTkLabel(
            header_frame, 
            text="YETKİLİ GİRİŞİ", 
            font=("Arial", 10, "bold"), 
            text_color=COLORS["accent_primary"]
        ).pack(pady=(2, 0))

        # --- GİRİŞ KARTI ---
        card = ctk.CTkFrame(self, fg_color=COLORS["bg_panel"], corner_radius=6, border_width=1, border_color=COLORS["border_main"])
        card.pack(pady=10, padx=30, fill="x")

        # Key Input
        ctk.CTkLabel(card, text="LİSANS ANAHTARI", font=("Arial", 9, "bold"), text_color=COLORS["text_dim"]).pack(pady=(20, 5), anchor="w", padx=20)
        
        self.entry_key = ctk.CTkEntry(
            card, 
            placeholder_text="XXXX-XXXX-XXXX-XXXX", 
            font=("Consolas", 12), 
            height=45, 
            fg_color=COLORS["bg_input"], 
            text_color=COLORS["text_main"], 
            border_width=1,
            border_color=COLORS["border_main"]
        )
        self.entry_key.pack(fill="x", padx=20, pady=(0, 20))

        # Login Button
        self.btn_login = ctk.CTkButton(
            card, 
            text="GİRİŞ YAP", 
            font=("Arial", 12, "bold"), 
            height=45, 
            fg_color=COLORS["accent_primary"], 
            hover_color=COLORS["accent_hover"], 
            text_color="white", 
            corner_radius=4,
            command=self.start_login
        )
        self.btn_login.pack(fill="x", padx=20, pady=(0, 25))

        # --- FOOTER LINKLERI ---
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(pady=20)

        ctk.CTkButton(
            footer_frame, 
            text="Ücretsiz Deneme Al", 
            font=("Arial", 11), 
            fg_color="transparent", 
            text_color=COLORS["text_dim"], 
            hover_color=COLORS["bg_panel"], 
            width=140, 
            height=30,
            command=self.start_trial
        ).pack()
        
        ctk.CTkButton(
            footer_frame, 
            text="Lisans Satın Al", 
            font=("Arial", 11), 
            fg_color="transparent", 
            text_color=COLORS["accent_primary"], 
            hover_color=COLORS["bg_panel"], 
            width=140, 
            height=30,
            command=lambda: webbrowser.open(SHOPIER_URL)
        ).pack(pady=2)

        # Durum Mesajı
        self.status = ctk.CTkLabel(self, text="", text_color=COLORS["danger"], font=("Arial", 10))
        self.status.pack(side="bottom", pady=15)

    def load_saved_key(self):
        """Kaydedilmiş lisansı AppData klasöründen yükler."""
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE, "r") as f: self.entry_key.insert(0, f.read().strip())
            except: pass

    def start_login(self):
        key = self.entry_key.get().strip()
        if not key: 
            self.status.configure(text="ANAHTAR GEREKLİ", text_color=COLORS["warning"])
            return
            
        self.btn_login.configure(state="disabled", text="DOĞRULANIYOR...")
        # Arayüz donmasın diye işlemi thread'e alıyoruz
        threading.Thread(target=self.process_login, args=(key,), daemon=True).start()

    def process_login(self, key):
        hwid = get_hwid()
        
        # Sunucu Sorgusu
        result = self.auth.license(key, hwid=hwid)
        
        if result["success"]:
            # Başarılı ise anahtarı kaydet
            try:
                with open(LICENSE_FILE, "w") as f: f.write(key)
            except Exception as e:
                print(f"Lisans kaydetme hatası: {e}")

            self.status.configure(text="ERİŞİM ONAYLANDI", text_color=COLORS["success"])
            # 1 saniye sonra ana uygulamayı aç
            self.after(1000, self.finish)
        else:
            self.btn_login.configure(state="normal", text="GİRİŞ YAP")
            
            # Hata mesajını analiz et ve Türkçeleştir
            msg = result.get("message", "Bilinmeyen Hata")
            if "hwid" in msg.lower(): msg = "GÜVENLİK UYARISI: DONANIM UYUŞMAZLIĞI"
            elif "invalid" in msg.lower(): msg = "HATA: GEÇERSİZ LİSANS ANAHTARI"
            elif "expired" in msg.lower(): msg = "HATA: LİSANS SÜRESİ DOLMUŞ"
            elif "used" in msg.lower(): msg = "HATA: LİSANS BAŞKA CİHAZDA AKTİF"
            elif "not found" in msg.lower(): msg = f"SÜRÜM HATASI: Güncelleme Gerekli (v{VERSION})"
            
            self.status.configure(text=msg, text_color=COLORS["danger"])

    def start_trial(self):
        messagebox.showinfo("Deneme Erişimi", "Deneme talep sayfasına yönlendiriliyorsunuz...")
        webbrowser.open(SHOPIER_URL)
    
    def finish(self):
        self.destroy() # Login penceresini yok et
        self.on_success(self.auth) # Main.py içindeki callback'i tetikle