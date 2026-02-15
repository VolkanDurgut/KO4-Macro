# modules/keyauth.py
import requests
import json
import time
import hashlib
import logging

# Logger entegrasyonu (Print yerine log dosyasına yazar)
logger = logging.getLogger(__name__)

class api:
    def __init__(self, name, ownerid, secret, version, hash_to_check):
        self.name = name
        self.ownerid = ownerid
        self.secret = secret
        self.version = version
        self.hash_to_check = hash_to_check
        self.sessionid = None
        self.init()

    def init(self):
        """
        KeyAuth sunucusu ile ilk el sıkışmayı (Handshake) yapar.
        Hata durumunda programı kapatmaz, Login ekranının yakalaması için hata fırlatır.
        """
        logger.info("KeyAuth başlatılıyor...")
        
        try:
            self.sessionid = hashlib.md5(str(time.time()).encode()).hexdigest()
            init_iv = "SHA256" + self.secret + self.hash_to_check + self.sessionid + self.name + self.ownerid
            self.init_iv = hashlib.sha256(init_iv.encode()).hexdigest()
            
            post_data = {
                "type": "init",
                "ver": self.version,
                "hash": self.hash_to_check,
                "name": self.name,
                "ownerid": self.ownerid,
                "init_iv": self.init_iv
            }
            
            response = self.__do_request(post_data)
            
            if response == "KeyAuth_Invalid":
                raise ConnectionError("Sunucuya erişilemiyor veya SSL hatası.")

            json_data = json.loads(response)

            if json_data.get("success"):
                self.sessionid = json_data["sessionid"]
                logger.info("KeyAuth oturumu başarıyla oluşturuldu.")
            elif json_data.get("message") == "invalidver":
                raise ValueError(f"Sürüm Uyuşmazlığı: Lütfen güncelleyin.")
            else:
                raise PermissionError(f"Başlatma Hatası: {json_data.get('message')}")
                
        except Exception as e:
            logger.critical(f"KeyAuth Init Hatası: {e}")
            raise e # Hatayı yukarı fırlat (Login ekranı yakalayacak)

    def license(self, key, hwid=None):
        """Lisans anahtarı ile giriş yapar."""
        return self.__simple_request("license", {"key": key, "hwid": hwid})

    def login(self, user, password, hwid=None):
        """Kullanıcı adı/şifre ile giriş yapar (Opsiyonel)."""
        return self.__simple_request("login", {"username": user, "pass": password, "hwid": hwid})

    def check(self):
        """Oturumun hala geçerli olup olmadığını kontrol eder."""
        return self.__simple_request("check", {})

    def var(self, name):
        """Sunucudan uzaktan değişken okur (Duyurular için)."""
        return self.__simple_request("var", {"varid": name})

    def __simple_request(self, type_str, extra_data):
        """Tekrarlanan istek kodlarını azaltmak için yardımcı fonksiyon."""
        if not self.sessionid:
            return {"success": False, "message": "Oturum başlatılmamış."}

        post_data = {
            "type": type_str, 
            "sessionid": self.sessionid, 
            "name": self.name, 
            "ownerid": self.ownerid
        }
        post_data.update(extra_data)
        
        response = self.__do_request(post_data)
        try: 
            return json.loads(response)
        except: 
            return {"success": False, "message": "Sunucudan bozuk yanıt geldi."}

    def __do_request(self, post_data):
        """Raw HTTP isteği atar."""
        try:
            req = requests.post(
                "https://keyauth.win/api/1.2/", 
                data=post_data, 
                timeout=15 # Timeout artırıldı (Yavaş internetler için)
            )
            return req.text
        except requests.exceptions.Timeout:
            logger.error("KeyAuth sunucusu zaman aşımına uğradı.")
            return "KeyAuth_Invalid"
        except requests.exceptions.ConnectionError:
            logger.error("İnternet bağlantısı yok.")
            return "KeyAuth_Invalid"
        except Exception as e:
            logger.error(f"Bilinmeyen İstek Hatası: {e}")
            return "KeyAuth_Invalid"