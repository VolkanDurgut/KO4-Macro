# modules/config_manager.py
import json
import os
import logging
import threading
import tempfile # EKLENDİ: Güvenli yazma işlemi için
from .constants import CONFIG_FILE, DEFAULT_CONFIG

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Uygulama ayarlarını yöneten Singleton sınıf.
    JSON okuma/yazma, doğrulama ve Atomik Yazma (Data Integrity) işlemlerinden sorumludur.
    """
    _instance = None
    _lock = threading.Lock()
    _io_lock = threading.Lock() # EKLENDİ: Dosya yazma işlemleri için özel kilit

    def __new__(cls):
        # Thread-Safe Singleton Pattern
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        # Sadece ilk oluşumda çalışır
        if self._initialized:
            return
        self._initialized = True
        self.config = {}
        self.load_config()

    def load_config(self):
        """Config dosyasını güvenli yükler, doğrular ve onarır."""
        # Varsayılan konfigürasyonun kopyasını al (Referans hatası olmaması için)
        valid_config = DEFAULT_CONFIG.copy()
        
        if not os.path.exists(CONFIG_FILE):
            logger.info("Config dosyası bulunamadı, varsayılanlar yüklendi.")
            self.config = valid_config
            return

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            # Schema Validation & Repair (Veri Onarımı)
            for key, default_val in DEFAULT_CONFIG.items():
                if key in raw_data:
                    user_val = raw_data[key]
                    
                    # 1. Tip Kontrolü: Bool, Int ve Float ayrımı
                    # Python'da bool, int'in alt sınıfıdır. Bu yüzden isinstance(True, int) True döner.
                    # Bu karışıklığı önlemek için özel kontrol:
                    is_default_bool = isinstance(default_val, bool)
                    is_user_bool = isinstance(user_val, bool)

                    if is_default_bool and is_user_bool:
                        valid_config[key] = user_val
                    elif not is_default_bool and isinstance(default_val, (int, float)) and isinstance(user_val, (int, float)):
                        # Sayısal değerleri onar (Örn: 5.0 gelmesi gerekirken 5 geldiyse)
                        valid_config[key] = int(user_val) if isinstance(default_val, int) else float(user_val)
                    elif isinstance(user_val, type(default_val)):
                        # String vb. diğer tipler
                        valid_config[key] = user_val
                    else:
                        logger.warning(f"Ayar tipi uyuşmazlığı: '{key}'. Varsayılan değer kullanıldı.")
                # Key yoksa zaten valid_config içinde varsayılanı var.
            
            self.config = valid_config
            logger.info("Config başarıyla yüklendi ve doğrulandı.")
            
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Config dosyası bozuk veya okunamadı: {e}")
            self.config = valid_config # Hata durumunda varsayılanlara dön

    def save_config(self):
        """
        Mevcut konfigürasyonu diske yazar.
        GELİŞTİRME: Atomic Write (Atomik Yazma) kullanılır.
        Veri önce geçici dosyaya yazılır, başarılı olursa asıl dosyanın üzerine taşınır.
        Bu sayede yazma sırasında PC kapanırsa veri kaybı olmaz.
        """
        with self._io_lock: # Aynı anda iki thread dosyaya yazmaya çalışmasın
            tmp_name = None
            try:
                # 1. Geçici dosya oluştur
                dir_name = os.path.dirname(CONFIG_FILE)
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)

                # tempfile.NamedTemporaryFile, Windows'ta bazen dosya kilitleme sorunu yaratabilir.
                # Bu yüzden manuel delete=False ile yönetiyoruz.
                with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tmp_file:
                    json.dump(self.config, tmp_file, indent=4)
                    tmp_name = tmp_file.name
                
                # 2. Atomik Değiştirme (Atomic Replace)
                # os.replace atomiktir (ya hep ya hiç).
                os.replace(tmp_name, CONFIG_FILE)
                
            except Exception as e:
                logger.error(f"Config kaydetme hatası (Atomic Save Failed): {e}")
                # Hata olursa geçici dosyayı temizle
                if tmp_name and os.path.exists(tmp_name):
                    try:
                        os.remove(tmp_name)
                    except: pass

    def get(self, key, default=None):
        """İstenilen ayarı döndürür."""
        return self.config.get(key, default)

    def set(self, key, value, save_now=True):
        """Ayarı günceller ve isteğe bağlı olarak anında dosyaya yazar."""
        # Değer gerçekten değiştiyse işlem yap (IO tasarrufu)
        if key in self.config and self.config[key] == value:
            return

        self.config[key] = value
        if save_now:
            self.save_config()