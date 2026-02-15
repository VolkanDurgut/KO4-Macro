# modules/features/archer35.py
import keyboard
import logging
import time
from ..core import perform_archer35_logic

logger = logging.getLogger(__name__)

# Durum Değişkenleri
_archer35_running = False
_last_key_state = False

def run_archer35_module(cfg):
    """
    Okçu 3-5 Kombosu.
    AMC Referanslı: 3 Skill + W (Cancel) döngüsü.
    Toggle Mantığı: Tuşa basınca başlar, tekrar basınca durur.
    Skill 3 (Opsiyonel alan) kaldırıldı, sadece Skill 1 ve 2 çalışır.
    """
    global _archer35_running, _last_key_state

    # 1. Modül Aktif mi? (UI Switch Kontrolü)
    if not cfg.get("archer35_active", False):
        _archer35_running = False
        return

    # 2. Tetikleyici Tuş (Örn: G)
    trigger_key = cfg.get("archer35_key")
    if not trigger_key: return

    try:
        is_pressed = keyboard.is_pressed(trigger_key)
    except:
        is_pressed = False

    # --- TOGGLE MANTIĞI (Başlat/Durdur) ---
    if is_pressed and not _last_key_state:
        _archer35_running = not _archer35_running
        status = "BAŞLATILDI" if _archer35_running else "DURDURULDU"
        logger.info(f"OKÇU 3-5 MODU: {status}")
        
        # Çakışmayı önlemek için tuşun bırakılmasını bekle
        start_wait = time.time()
        while keyboard.is_pressed(trigger_key):
            time.sleep(0.01)
            if time.time() - start_wait > 2.0: break 
        
        time.sleep(0.1)

    _last_key_state = is_pressed

    # 3. ÇALIŞTIRMA
    if _archer35_running:
        # Arayüzden skill tuşlarını al (Yoksa varsayılan: 3, 4)
        s1 = cfg.get("archer35_skill1_key", "3")
        s2 = cfg.get("archer35_skill2_key", "4")
        # Skill 3 kaldırıldı, bu yüzden okuma yapmıyoruz.

        # --- ANLIK DURDURMA KONTROLÜ ---
        # Kombo sırasında (220ms beklerken) durdurma emri gelirse hemen çık.
        def stop_checker():
            # Kullanıcı tuşa tekrar bastıysa DUR
            if keyboard.is_pressed(trigger_key):
                return True
            # Modül arayüzden kapatıldıysa DUR
            if not cfg.get("archer35_active", False):
                return True
            return False

        # Core modülündeki AMC motorunu çalıştır
        # 3. Parametre (Skill 3) artık 'None' olarak gönderiliyor.
        perform_archer35_logic(s1, s2, None, stop_callback=stop_checker)
        
        # Eğer işlem sırasında durdurma emri geldiyse:
        if stop_checker():
            _archer35_running = False
            # Tuşun bırakılmasını bekle
            while keyboard.is_pressed(trigger_key): time.sleep(0.01)
            _last_key_state = False
            logger.info("OKÇU 3-5 MODU: KESİLDİ (Manuel)")
            time.sleep(0.2)