# modules/splash.py
import customtkinter as ctk
from PIL import Image, ImageSequence
import os
from .constants import SPLASH_GIF, LOGO_NAME

class SplashScreen(ctk.CTk):
    def __init__(self, main_app_callback):
        super().__init__()
        self.main_app_callback = main_app_callback
        
        # Çerçevesiz Pencere
        self.overrideredirect(True)
        
        # --- ŞEFFAFLIK AYARLARI ---
        # Bu renk (neredeyse siyah) pencerede görünmez olur.
        transparent_bg_key = "#000001" 
        self.configure(fg_color=transparent_bg_key)
        self.attributes("-transparentcolor", transparent_bg_key)
        self.attributes("-topmost", True)

        # Pencere Boyutu
        window_width = 500
        window_height = 400 # Yazı kalktığı için boyutu GIF'e odakladık
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Görsel Alanı (Arka planı şeffaf anahtarı ile aynı yapıyoruz)
        self.label_anim = ctk.CTkLabel(self, text="", fg_color=transparent_bg_key)
        self.label_anim.pack(expand=True, fill="both")

        # --- GIF YÜKLEME MOTORU (V2 - Speed Boost) ---
        self.frames = []
        
        if os.path.exists(SPLASH_GIF):
            try:
                pil_gif = Image.open(SPLASH_GIF)
                
                frame_idx = 0
                while True:
                    try:
                        pil_gif.seek(frame_idx)
                        
                        # Her karenin kendi süresini al (Milisaniye)
                        duration = pil_gif.info.get('duration', 30)
                        
                        # HIZ AYARI: Eğer GIF yavaş tanımlanmışsa (örn: >35ms), 
                        # onu zorla 30ms'ye çekerek akıcılık sağlıyoruz.
                        if duration > 35 or duration == 0:
                            duration = 30
                        
                        # Kareyi işle
                        frame = pil_gif.copy().convert("RGBA").resize((450, 350), Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=frame, dark_image=frame, size=(450, 350))
                        
                        # Listeye (Resim, Süre) ikilisi olarak ekle
                        self.frames.append((ctk_img, duration))
                        frame_idx += 1
                    except EOFError:
                        break
            except Exception as e:
                print(f"GIF Error: {e}")

        # Yedek Logo (GIF yoksa)
        if not self.frames and os.path.exists(LOGO_NAME):
            try:
                img = ctk.CTkImage(Image.open(LOGO_NAME), size=(200, 200))
                self.frames.append((img, 2000)) # 2 saniye bekle
            except: pass

        self.frame_index = 0
        
        # Başlat
        if len(self.frames) > 1:
            self.animate_gif()
        else:
            if self.frames:
                self.label_anim.configure(image=self.frames[0][0])
                self.after(2000, self.finish)
            else:
                # Ne GIF ne Logo varsa direkt aç
                self.finish()

    def animate_gif(self):
        """Kare kare değişken hızlı GIF oynatıcı"""
        if self.frames:
            image, duration = self.frames[self.frame_index]
            self.label_anim.configure(image=image)
            
            self.frame_index += 1
            
            # Son kareye gelince bitir
            if self.frame_index >= len(self.frames):
                # Son kareyi süresi kadar gösterip kapat
                self.after(duration, self.finish)
                return
            
            # Bir sonraki kare için bekle
            self.after(duration, self.animate_gif)

    def finish(self):
        self.destroy()
        if self.main_app_callback:
            self.main_app_callback()