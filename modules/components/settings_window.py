# modules/components/settings_window.py
import customtkinter as ctk
import logging
from ..constants import COLORS, FONT_FAMILY

logger = logging.getLogger(__name__)

class SettingsWindow(ctk.CTkToplevel):
    """
    Kullanıcının Config dosyasını manuel düzenlemeden,
    Loop Rate, Input Pause ve Tema gibi ayarları yapmasını sağlar.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # --- PENCERE AYARLARI ---
        self.title("SİSTEM AYARLARI")
        self.geometry("400x480") # Yükseklik biraz artırıldı
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=COLORS["bg_main"])
        
        # Pencereyi Ana Ekranın Ortasına Hizala
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 240
            self.geometry(f"+{x}+{y}")
        except:
            self.geometry("400x480")

        # Başlık
        ctk.CTkLabel(self, text="YAPILANDIRMA", font=(FONT_FAMILY[0], 16, "bold"), text_color=COLORS["text_main"]).pack(pady=20)
        
        # --- BÖLÜM 1: PERFORMANS (TPS) ---
        f1 = ctk.CTkFrame(self, fg_color=COLORS["bg_card"])
        f1.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(f1, text="TICK RATE (Hız)", font=(FONT_FAMILY[0], 12, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        current_tps = self.parent.cfg.get("loop_rate", 60)
        self.lbl_tps = ctk.CTkLabel(f1, text=f"{current_tps} TPS", font=(FONT_FAMILY[0], 11), text_color=COLORS["cyan_neon"])
        self.lbl_tps.pack(anchor="e", padx=10, pady=(0,0))
        
        self.slider_tps = ctk.CTkSlider(
            f1, from_=30, to=120, number_of_steps=90, 
            fg_color=COLORS["bg_input"], progress_color=COLORS["cyan_neon"],
            command=self.update_tps_label
        )
        self.slider_tps.set(current_tps)
        self.slider_tps.pack(fill="x", padx=10, pady=(5,15))

        # --- BÖLÜM 2: GECİKME (INPUT LATENCY) ---
        f2 = ctk.CTkFrame(self, fg_color=COLORS["bg_card"])
        f2.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(f2, text="INPUT PAUSE (Gecikme)", font=(FONT_FAMILY[0], 12, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        current_pause = self.parent.cfg.get("input_pause", 0.001)
        current_pause_ms = int(current_pause * 1000)
        self.lbl_pause = ctk.CTkLabel(f2, text=f"{current_pause_ms} ms", font=(FONT_FAMILY[0], 11), text_color=COLORS["yellow_neon"])
        self.lbl_pause.pack(anchor="e", padx=10, pady=(0,0))

        self.slider_pause = ctk.CTkSlider(
            f2, from_=1, to=50, number_of_steps=49,
            fg_color=COLORS["bg_input"], progress_color=COLORS["yellow_neon"],
            command=self.update_pause_label
        )
        self.slider_pause.set(current_pause_ms)
        self.slider_pause.pack(fill="x", padx=10, pady=(5,15))

        # --- BÖLÜM 3: TEMA (GÖRSEL) ---
        f3 = ctk.CTkFrame(self, fg_color=COLORS["bg_card"])
        f3.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(f3, text="TEMA SEÇİMİ (Yeniden Başlatma Gerekir)", font=(FONT_FAMILY[0], 12, "bold")).pack(anchor="w", padx=10, pady=(10,5))
        
        # Mevcut temayı config'den oku
        current_theme = self.parent.cfg.get("app_theme", "Neon Cyan")
        
        self.seg_theme = ctk.CTkSegmentedButton(
            f3, values=["Neon Cyan", "Toxic Green"],
            selected_color=COLORS["green_neon"], selected_hover_color=COLORS["btn_hover"],
            font=(FONT_FAMILY[0], 11, "bold")
        )
        self.seg_theme.set(current_theme) 
        self.seg_theme.pack(fill="x", padx=10, pady=(0, 15))

        # KAYDET BUTONU
        ctk.CTkButton(
            self, text="AYARLARI KAYDET", height=40, font=(FONT_FAMILY[0], 12, "bold"),
            fg_color=COLORS["green_neon"], hover_color=COLORS["btn_hover"], text_color="black",
            command=self.save_settings
        ).pack(side="bottom", fill="x", padx=20, pady=20)
        
        # Modality (Arka planı kilitle)
        self.grab_set()
        self.focus_force()

    def update_tps_label(self, value):
        self.lbl_tps.configure(text=f"{int(value)} TPS")

    def update_pause_label(self, value):
        self.lbl_pause.configure(text=f"{int(value)} ms")

    def save_settings(self):
        # Değerleri Al
        new_tps = int(self.slider_tps.get())
        new_pause_ms = int(self.slider_pause.get())
        new_pause_sec = new_pause_ms / 1000.0
        new_theme = self.seg_theme.get() # Artık tema değerini de alıyoruz
        
        # Config'e Yaz
        self.parent.cfg.set("loop_rate", new_tps, save_now=False)
        self.parent.cfg.set("input_pause", new_pause_sec, save_now=False)
        
        # Tema değiştiyse kullanıcıyı uyaracağız
        old_theme = self.parent.cfg.get("app_theme", "Neon Cyan")
        self.parent.cfg.set("app_theme", new_theme, save_now=True) # Hepsini tek seferde kaydet
        
        if old_theme != new_theme:
            self.parent.show_toast("TEMA DEĞİŞTİ", "Değişikliklerin görünmesi için uygulamayı yeniden başlatın.", type="warning")
        else:
            self.parent.show_toast("BAŞARILI", "Ayarlar başarıyla güncellendi.", type="success")
            
        logger.info(f"Ayarlar güncellendi: TPS={new_tps}, Pause={new_pause_sec}s, Theme={new_theme}")
        self.destroy()