# modules/features/shield.py
import keyboard
import logging
import time
from ..core import perform_shield_macro

logger = logging.getLogger(__name__)

def run_shield_module(cfg):
    """
    Kalkan takma işlemini tetikler.
    Tekil çalışır: Tuşa basıldığı sürece tekrar tetiklemez.
    """
    # Modül aktif mi kontrol et
    if not cfg.get("shield_active", True):
        return

    shield_key = cfg.get("shield_key")
    
    # Tuş basılı mı?
    if shield_key and keyboard.is_pressed(shield_key):
        try:
            # 1. İşlemi gerçekleştir
            perform_shield_macro(
                cfg.get("shield_x", 0),
                cfg.get("shield_y", 0),
                cfg.get("shield_delay", 0.0)
            )
            
            # 2. KRİTİK DÜZELTME: Tuş bırakılana kadar bekle
            # Bu döngü, parmağınızı tuştan çekene kadar programı bu satırda tutar.
            # Böylece motor bir sonraki tura geçtiğinde tuş hala basılıysa tekrar işlem yapmaz.
            start_wait = time.time()
            while keyboard.is_pressed(shield_key):
                time.sleep(0.01)
                # Güvenlik önlemi: Tuş takılı kalırsa 2 saniye sonra döngüyü kır
                if time.time() - start_wait > 2.0:
                    break
                    
        except Exception as e:
            logger.error(f"Shield Modül Hatası: {e}")