# modules/splash.py
import customtkinter as ctk
from PIL import Image
import os
import time
from .constants import (
    COLORS, FONT_FAMILY, LOGO_NAME, ICON_NAME, # ICON_NAME Eklendi
    APP_TITLE, APP_SUBTITLE, VERSION
)

class SplashScreen(ctk.CTk):
    def __init__(self, main_app_callback):
        super().__init__()
        self.main_app_callback = main_app_callback
        
        # --- PENCERE AYARLARI ---
        self.overrideredirect(True) # Çerçevesiz pencere
        self.attributes("-topmost", True) # Her zaman üstte
        self.attributes("-alpha", 0.0) # Başlangıçta görünmez (Fade-in için)
        
        # --- EKLENEN KISIM: GÖREV ÇUBUĞU İKONU ---
        # İlk açılan pencere olduğu için ikonu burada set etmek zorunludur.
        if os.path.exists(ICON_NAME):
            try:
                self.iconbitmap(ICON_NAME)
            except Exception:
                pass
        # -----------------------------------------

        # Voberix Siyahı Arka Plan
        self.configure(fg_color=COLORS["bg_main"])
        
        # Boyut ve Konum (Geniş ve Modern)
        width = 650
        height = 380
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Dış Çerçeve (Accent Rengiyle İnce Bir Çizgi)
        self.border_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=1, border_color=COLORS["border_dim"], corner_radius=0)
        self.border_frame.pack(fill="both", expand=True)

        # UI Bileşenlerini Oluştur
        self.create_widgets()
        
        # Animasyonu Başlat (50ms gecikmeli)
        self.after(50, self.start_sequence)

    def create_widgets(self):
        # İçerik Alanı
        self.content_frame = ctk.CTkFrame(self.border_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # 1. Logo (Varsa)
        if os.path.exists(LOGO_NAME):
            try:
                pil_img = Image.open(LOGO_NAME)
                # Logoyu biraz daha büyük ve net gösteriyoruz
                self.logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(80, 80))
                ctk.CTkLabel(self.content_frame, text="", image=self.logo_img).pack(pady=(10, 15))
            except: pass

        # 2. Marka İsmi (VOBERIX)
        ctk.CTkLabel(
            self.content_frame, 
            text=APP_TITLE, 
            font=(FONT_FAMILY[0], 36, "bold"), 
            text_color="white"
        ).pack(pady=(0, 2))

        # 3. Slogan ve Versiyon
        ctk.CTkLabel(
            self.content_frame, 
            text=f"{APP_SUBTITLE}  |  v{VERSION}", 
            font=("Consolas", 11), 
            text_color=COLORS["accent_primary"],
            height=15
        ).pack(pady=(0, 40))

        # 4. Progress Bar (İnce ve Şık)
        self.progress_bar = ctk.CTkProgressBar(
            self.content_frame, 
            width=400, 
            height=4, 
            corner_radius=2,
            fg_color=COLORS["bg_input"], 
            progress_color=COLORS["cyan_neon"],
            mode="determinate"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(side="bottom", pady=(10, 10))

        # 5. Durum Metni (Loading...)
        self.status_label = ctk.CTkLabel(
            self.content_frame, 
            text="Sistem başlatılıyor...", 
            font=("Consolas", 10), 
            text_color=COLORS["text_dim"]
        )
        self.status_label.pack(side="bottom", pady=(0, 2))

    def start_sequence(self):
        # 1. Adım: Fade In (Görünür Ol)
        self.fade_in()
        
        # 2. Adım: Yükleme Senaryosu
        self.loading_steps = [
            (0.1, "Çekirdek modüller yükleniyor..."),
            (0.25, "Güvenlik protokolleri doğrulanıyor..."),
            (0.40, "Kullanıcı yapılandırması okunuyor..."),
            (0.60, "Grafik arayüz oluşturuluyor..."),
            (0.85, "Voberix Engine başlatılıyor..."),
            (1.0, "Hazır.")
        ]
        self.step_index = 0
        
        # İlerleme çubuğunu çalıştır
        self.after(500, self.run_progress)

    def fade_in(self):
        """Pencerenin opaklığını yavaşça artırır."""
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.08 # Hız ayarı
            self.attributes("-alpha", min(alpha, 1.0))
            self.after(20, self.fade_in)

    def run_progress(self):
        """Yükleme adımlarını simüle eder."""
        if self.step_index < len(self.loading_steps):
            prog_val, text = self.loading_steps[self.step_index]
            
            # Barı ve yazıyı güncelle
            self.progress_bar.set(prog_val)
            self.status_label.configure(text=text)
            
            self.step_index += 1
            
            # Adımlar arası rastgele bir bekleme süresi hissi (Akıcılık için)
            wait_time = 450 if self.step_index < 4 else 800 
            self.after(wait_time, self.run_progress)
        else:
            # Bitti, biraz bekle ve kapat
            self.after(600, self.fade_out)

    def fade_out(self):
        """Pencerenin opaklığını yavaşça azaltır ve kapatır."""
        alpha = self.attributes("-alpha")
        if alpha > 0.0:
            alpha -= 0.1 # Kapanış biraz daha hızlı olsun
            self.attributes("-alpha", max(alpha, 0.0))
            self.after(20, self.fade_out)
        else:
            self.destroy()
            if self.main_app_callback:
                self.main_app_callback()