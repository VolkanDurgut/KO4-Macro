# main.py
import logging
import sys
import os
import ctypes
import traceback
from logging.handlers import RotatingFileHandler

from modules.constants import LOG_FILE, VERSION

# --- LOGLAMA YAPILANDIRMASI ---
try:
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            RotatingFileHandler(
                LOG_FILE,             
                maxBytes=5*1024*1024, 
                backupCount=3,        
                encoding='utf-8'
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )
except OSError:
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger("Main")

# --- GLOBAL HATA YAKALAYICI ---
def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Görseldeki "_tkinter.TclError" hatasını yutan filtre
    error_msg = str(exc_value).lower()
    if any(keyword in error_msg for keyword in ["destroyed", "invoke", "focus", "invalid command"]):
        logger.info("Uygulama kapatıldı (Normal Çıkış).")
        return 

    error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.critical(f"SİSTEM ÇÖKME RAPORU: \n{error_details}")

    try:
        from modules.components.error_window import GlobalErrorWindow
        GlobalErrorWindow("Beklenmedik Uygulama Hatası", error_details)
    except Exception:
        try:
            ctypes.windll.user32.MessageBoxW(0, f"Kritik Hata:\n{exc_value}", "Voberix Fatal Error", 16)
        except: pass
    
    sys.exit(1)

sys.excepthook = global_exception_handler

# --- MODÜL YÜKLEME ---
try:
    from modules.splash import SplashScreen
    from modules.ui import MacroApp 
    # Login ekranını import etmemize gerek yok, kullanmayacağız.
except ImportError as e:
    logger.critical(f"Modül import hatası: {e}")
    ctypes.windll.user32.MessageBoxW(0, f"Eksik Dosya Hatası:\n{e}", "Başlatılamadı", 16)
    sys.exit(1)

# --- UYGULAMA AKIŞI ---

def start_macro_system_bypassed(): 
    """
    Login ekranını atlayarak doğrudan Dashboard'u başlatır.
    auth_api=None gönderildiği için ui.py içindeki lisans kontrolleri çalışmaz.
    """
    try:
        logger.info("Sistem başlatılıyor (Keyless Mode)...")
        # auth_api=None göndererek güvenliği pas geçiyoruz
        app = MacroApp(auth_api=None) 
        app.mainloop()
    except Exception as e:
        global_exception_handler(type(e), e, e.__traceback__)

if __name__ == "__main__":
    # 1. YÖNETİCİ İZNİ
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    except Exception as e:
        logger.error(f"Yönetici izni hatası: {e}")

    # 2. GÖREV ÇUBUĞU İKONU
    try:
        myappid = f'voberix.system.macro.v{VERSION}'
        ctypes.windll.user32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        logger.warning(f"AppID Hatası: {e}")

    # 3. BAŞLATMA
    try:
        logger.info(f">>> VOBERIX v{VERSION} BAŞLATILIYOR <<<")
        
        # Splash ekranı kapandığında doğrudan bypass fonksiyonunu çağırır.
        splash = SplashScreen(main_app_callback=start_macro_system_bypassed)
        splash.mainloop()
        
    except Exception as e:
        global_exception_handler(type(e), e, e.__traceback__)
    finally:
        logger.info("Sistem kapatıldı.")