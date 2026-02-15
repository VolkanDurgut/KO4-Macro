# modules/components/toast.py
import tkinter as tk
from ..constants import COLORS, FONT_FAMILY

class ToastNotification(tk.Toplevel):
    """
    Ekranın sağ alt köşesinde beliren geçici bildirim penceresi.
    """
    def __init__(self, parent, title, message, color_key="green_neon", duration=4000):
        super().__init__(parent)
        self.overrideredirect(True) # Çerçevesiz pencere
        self.attributes("-topmost", True) # Her zaman en üstte
        self.attributes("-alpha", 0.0)    # Başlangıçta görünmez
        
        self.duration = duration
        # Renk anahtarı yoksa varsayılan olarak yeşili kullan
        self.color = COLORS.get(color_key, COLORS["green_neon"])
        
        self.configure(bg=COLORS["bg_card"])
        
        # --- TASARIM ---
        # Dış Kutu (Sol tarafında renkli çizgi olan kart yapısı)
        container = tk.Frame(self, bg=COLORS["bg_card"], highlightbackground=self.color, highlightthickness=1)
        container.pack(fill="both", expand=True)
        
        # Sol Renkli Şerit
        bar = tk.Frame(container, bg=self.color, width=5)
        bar.pack(side="left", fill="y")
        
        # İçerik Alanı
        content = tk.Frame(container, bg=COLORS["bg_card"])
        content.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Başlık
        tk.Label(
            content, text=title, font=(FONT_FAMILY[0], 10, "bold"),
            bg=COLORS["bg_card"], fg=self.color, anchor="w"
        ).pack(fill="x")
        
        # Mesaj
        tk.Label(
            content, text=message, font=(FONT_FAMILY[0], 9),
            bg=COLORS["bg_card"], fg=COLORS["text_main"], anchor="w"
        ).pack(fill="x")
        
        # --- KONUMLANDIRMA ---
        self.update_idletasks() # Boyutları hesaplamak için zorla güncelle
        width = 320
        height = self.winfo_reqheight()
        
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # Sağ alt köşe (Taskbar'ın biraz üstü)
        x_pos = screen_w - width - 20
        y_pos = screen_h - height - 50 
        self.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        
        # Animasyonu Başlat
        self.after(50, self.fade_in)

    def fade_in(self):
        """Pencereyi yavaşça görünür yapar."""
        try:
            # KRİTİK KONTROL: Pencere kapatıldıysa işlemi durdur
            if not self.winfo_exists(): return
            
            alpha = self.attributes("-alpha")
            if alpha < 0.95:
                alpha += 0.1
                self.attributes("-alpha", alpha)
                self.after(20, self.fade_in)
            else:
                # Görünür oldu, bekleme süresini başlat
                self.after(self.duration, self.fade_out)
        except Exception:
            pass # Uygulama kapanırken hata verirse yoksay

    def fade_out(self):
        """Pencereyi yavaşça kaybeder ve yok eder."""
        try:
            if not self.winfo_exists(): return

            alpha = self.attributes("-alpha")
            if alpha > 0.05:
                alpha -= 0.1
                self.attributes("-alpha", alpha)
                self.after(20, self.fade_out)
            else:
                self.destroy()
        except Exception:
            self.destroy()