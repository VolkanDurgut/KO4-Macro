# modules/engine.py
import threading
import time
import pydirectinput
import logging
from .core import session_stats

# --- MODÜLER İMPORTLAR ---
from .features.shield import run_shield_module
from .features.sword import run_sword_module
from .features.restore import run_restore_module
from .features.combo import run_combo_module
from .features.mage56 import run_mage56_module
from .features.archer35 import run_archer35_module

# Logger
logger = logging.getLogger(__name__)

class AutomationEngine:
    """
    Otomasyon mantığını ve thread yönetimini üstlenen sınıf.
    UI'dan bağımsız çalışır, özellikleri 'features' klasöründen çağırır.
    """
    def __init__(self, config_manager):
        self.cfg = config_manager
        self.stop_event = threading.Event()
        self.thread = None
        self.is_running = False

    def start(self):
        """Otomasyon döngüsünü yeni bir thread üzerinde başlatır."""
        if self.is_running:
            return

        logger.info("Motor başlatılıyor...")
        self.stop_event.clear()
        self.is_running = True
        
        # İstatistikleri sıfırla
        try:
            session_stats.reset_session()
        except Exception as e:
            logger.error(f"İstatistik reset hatası: {e}")
        
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Çalışan döngüyü güvenli bir şekilde durdurur."""
        if not self.is_running:
            return

        logger.info("Motor durduruluyor...")
        self.is_running = False
        self.stop_event.set()

    def get_report(self):
        return session_stats.get_report()

    def _loop(self):
        """
        Ana otomasyon döngüsü.
        Modüler yapıyı kullanır.
        """
        logger.info("Motor döngüsü (Modular Loop) aktif.")
        
        while self.is_running and not self.stop_event.is_set():
            start_time = time.perf_counter()

            # --- 1. AYARLARI OKU ---
            try:
                loop_rate = self.cfg.get("loop_rate", 60)
                target_tps = max(30, loop_rate)
                tick_duration = 1.0 / target_tps
                pydirectinput.PAUSE = self.cfg.get("input_pause", 0.001)
            except:
                tick_duration = 0.016

            # --- 2. MODÜLLERİ ÇALIŞTIR ---
            
            # A) Kalkan Modülü
            run_shield_module(self.cfg)

            # B) Kombo Modülü
            run_combo_module(self.cfg)

            # C) Mage 56 Modülü
            run_mage56_module(self.cfg)

            # D) Okçu 3-5 Modülü
            run_archer35_module(self.cfg)

            # E) Görüntü İşleme Modülleri (Sword & Restore)
            # --- KRİTİK DÜZELTME: Ters seçimlerde ve Float durumlarında çökme engellendi ---
            region = None
            x1 = self.cfg.get("region_x1")
            y1 = self.cfg.get("region_y1")
            x2 = self.cfg.get("region_x2")
            y2 = self.cfg.get("region_y2")
            
            if x1 is not None and x2 is not None and y1 is not None and y2 is not None:
                try:
                    # Değerleri tam sayıya çevir
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Kullanıcı ters çizse bile sol üst noktayı otomatik bul (min)
                    left = min(x1, x2)
                    top = min(y1, y2)
                    
                    # Mutlak değer ile (abs) genişlik ve yüksekliği daima pozitif al
                    w = abs(x2 - x1)
                    h = abs(y2 - y1)
                    
                    # Yanlışlıkla tıklama (1-2 piksellik alanlar) ihtimaline karşı ufak bir sınır
                    if w > 5 and h > 5:
                        region = (left, top, w, h)
                except Exception as e:
                    logger.error(f"Region Parse Hatası: {e}")

            if region:
                run_sword_module(self.cfg, region)
                run_restore_module(self.cfg, region)

            # --- 3. AKILLI BEKLEME ---
            elapsed = time.perf_counter() - start_time
            sleep_time = tick_duration - elapsed
            
            if sleep_time > 0:
                self.stop_event.wait(timeout=sleep_time)
            else:
                time.sleep(0.001) 
        
        logger.info("Motor döngüsü sona erdi.")