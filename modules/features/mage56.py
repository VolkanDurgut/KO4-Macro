# modules/features/mage56.py
import keyboard
import logging
import time
from ..core import perform_mage56_logic

logger = logging.getLogger(__name__)

# Durum Değişkenleri
_mage56_running = False
_last_key_state = False

def run_mage56_module(cfg):
    """
    Mage 56 (Skill + Staff) Makrosu.
    AMC Dosyası referans alınarak 'Toggle' (Bas-Başlat / Bas-Durdur) mantığıyla çalışır.
    
    Çalışma Prensibi:
    1. Skill Tuşu (Ayarlanabilir) -> Bas-Çek
    2. W (Sabit) -> İptal
    3. Staff Tuşu (Ayarlanabilir) -> 1.1 Saniye Basılı Tut (HOLD)
    4. W (Sabit) -> İptal
    """
    global _mage56_running, _last_key_state

    # 1. Modül Aktif mi? (UI Switch Kontrolü)
    if not cfg.get("mage56_active", False):
        _mage56_running = False
        return

    # 2. Tetikleyici Tuş (Örn: F)
    trigger_key = cfg.get("mage56_key")
    if not trigger_key: return

    try:
        is_pressed = keyboard.is_pressed(trigger_key)
    except:
        is_pressed = False

    # --- TOGGLE MANTIĞI (Başlat/Durdur) ---
    if is_pressed and not _last_key_state:
        _mage56_running = not _mage56_running
        status = "BAŞLATILDI" if _mage56_running else "DURDURULDU"
        logger.info(f"MAGE 56 MODU: {status}")
        
        # Tuş çakışmasını önlemek için parmağın çekilmesini bekle
        start_wait = time.time()
        while keyboard.is_pressed(trigger_key):
            time.sleep(0.01)
            if time.time() - start_wait > 2.0: break 
        
        time.sleep(0.1)

    _last_key_state = is_pressed

    # 3. ÇALIŞTIRMA (AMC Mantığı)
    if _mage56_running:
        # Arayüzden girilen tuşları al (Yoksa varsayılanları kullan)
        skill_key = cfg.get("mage56_skill_key", "2") 
        r_key = cfg.get("mage56_r_key", "r")         

        # --- ANLIK DURDURMA KONTROLÜ ---
        # Staff vuruşu (1.1sn) sırasında kullanıcı makroyu kapatırsa anında durmalı.
        def stop_checker():
            # Kullanıcı F tuşuna tekrar bastıysa DUR
            if keyboard.is_pressed(trigger_key):
                return True
            # Arayüzden kapatıldıysa DUR
            if not cfg.get("mage56_active", False):
                return True
            return False

        # Core modülündeki AMC motorunu çalıştır
        perform_mage56_logic(skill_key, r_key, stop_callback=stop_checker)
        
        # Eğer işlem sırasında durdurma emri geldiyse durumu güncelle
        if stop_checker():
            _mage56_running = False
            # Tuşun bırakılmasını bekle
            while keyboard.is_pressed(trigger_key): time.sleep(0.01)
            _last_key_state = False
            logger.info("MAGE 56 MODU: KESİLDİ (Manuel)")
            time.sleep(0.2)