# modules/features/combo.py
import keyboard
import logging
import time
from ..core import execute_combo_sequence

logger = logging.getLogger(__name__)

# Durum Değişkenleri
_combo_running = False
_last_key_state = False

def run_combo_module(cfg):
    """
    Profesyonel Kombo Modülü.
    Toggle mantığı ve Anlık Kesme (Interrupt) özelliği ile çalışır.
    """
    global _combo_running, _last_key_state

    # 1. Modül Kapalıysa işlem yapma
    if not cfg.get("combo_active", False):
        _combo_running = False
        return

    # 2. Tuş Kontrolü
    trigger_key = cfg.get("combo_key")
    if not trigger_key: return

    try:
        is_pressed = keyboard.is_pressed(trigger_key)
    except:
        is_pressed = False

    # --- TOGGLE MANTIĞI (Bas-Çek) ---
    # Tuşa basıldığı an (Rising Edge)
    if is_pressed and not _last_key_state:
        _combo_running = not _combo_running
        status = "BAŞLATILDI" if _combo_running else "DURDURULDU"
        logger.info(f"KOMBAT MODU: {status}")
        
        # KRİTİK DÜZELTME: Kullanıcı elini tuştan çekene kadar bekle.
        # Bu yapılmazsa, stop_checker hemen devreye girip "Tuş basılı, durmalıyım" sanar.
        start_wait = time.time()
        while keyboard.is_pressed(trigger_key):
            time.sleep(0.01)
            # Güvenlik: Tuş takılı kalırsa 2 saniye sonra zorla çık
            if time.time() - start_wait > 2.0: break
            
        time.sleep(0.1) # Ekstra güvenlik payı

    _last_key_state = is_pressed

    # 3. ÇALIŞTIRMA
    if _combo_running:
        try:
            sequence = cfg.get("combo_sequence", "R-R-2")
            
            # Hız hesaplama (Milisaniye -> Saniye)
            ms_val = cfg.get("combo_delay_ms", 5.0)
            delay_sec = float(ms_val) / 1000.0
            
            # --- STOP CALLBACK ---
            def stop_checker():
                # 1. Kullanıcı tuşa tekrar basarsa dur
                if keyboard.is_pressed(trigger_key):
                    return True
                # 2. Modül arayüzden kapatılırsa dur
                if not cfg.get("combo_active", False):
                    return True
                return False

            # Core fonksiyonu çağır (Kesilebilir Mod)
            aborted = execute_combo_sequence(sequence, delay_sec, stop_callback=stop_checker)
            
            if aborted:
                _combo_running = False
                # Durdurulduğunda tuşun bırakılmasını bekle (Tekrar başlamasın diye)
                while keyboard.is_pressed(trigger_key): time.sleep(0.01)
                
                _last_key_state = False 
                logger.info("KOMBAT MODU: KESİLDİ (Manuel)")
                time.sleep(0.2)

        except Exception as e:
            logger.error(f"Combo Hatası: {e}")
            _combo_running = False