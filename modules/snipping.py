# modules/snipping.py
import tkinter as tk
from .constants import COLORS

class SnippingTool(tk.Toplevel):
    """
    Ekranın belirli bir bölümünü seçmek için kullanılan araç.
    """
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.parent = parent
        self.callback = callback
        
        # --- PENCERE AYARLARI ---
        self.attributes('-fullscreen', True) # Tam ekran
        self.attributes('-alpha', 0.3)       # Hafif saydamlık (Oyunun görünmesi için)
        self.attributes('-topmost', True)    # Diğer pencerelerin üstünde
        self.configure(bg='black')
        
        # Değişkenler
        self.cursor_start_x = 0
        self.cursor_start_y = 0
        self.rect = None
        
        # --- ÇİZİM ALANI (CANVAS) ---
        self.canvas = tk.Canvas(self, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # --- OLAY DİNLEYİCİLERİ ---
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # İptal Durumu (ESC)
        self.bind("<Escape>", self.on_cancel)
        
        # Pencere açılır açılmaz odağı al (Klavye kısayolları için)
        self.focus_force()

    def on_press(self, event):
        """Tıklama anı: Başlangıç noktasını kaydet."""
        self.cursor_start_x = event.x
        self.cursor_start_y = event.y
        
        # Varsa eski dikdörtgeni sil
        if self.rect:
            self.canvas.delete(self.rect)
            
        # Yeni dikdörtgen oluştur (Voberix Cyan Rengi)
        self.rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, 
            outline=COLORS["cyan_neon"], 
            width=2, 
            # 'stipple' Windows'ta bazen sorunlu olabilir ama şeffaf dolgu efekti verir
            fill=COLORS["cyan_neon"], 
            stipple="gray12" 
        )

    def on_drag(self, event):
        """Sürükleme anı: Dikdörtgeni güncelle."""
        if self.rect:
            self.canvas.coords(self.rect, self.cursor_start_x, self.cursor_start_y, event.x, event.y)

    def on_release(self, event):
        """Bırakma anı: Koordinatları hesapla ve gönder."""
        # Koordinatları sırala (x1 her zaman x2'den küçük olmalı)
        x1 = min(self.cursor_start_x, event.x)
        y1 = min(self.cursor_start_y, event.y)
        x2 = max(self.cursor_start_x, event.x)
        y2 = max(self.cursor_start_y, event.y)
        
        # Çok küçük seçimleri (yanlış tıklamaları) yoksay
        if (x2 - x1) < 5 or (y2 - y1) < 5:
            return

        self.destroy() # Pencereyi kapat
        
        # Ana uygulamadaki callback fonksiyonunu çağır
        if self.callback:
            self.callback(x1, y1, x2, y2)

    def on_cancel(self, event=None):
        """
        Kritik Fix: Kullanıcı ESC'ye basarsa ana pencereyi geri getir.
        Aksi takdirde ana uygulama gizli (withdraw) kalır.
        """
        self.destroy()
        if self.parent:
            self.parent.deiconify() # Ana pencereyi tekrar göster