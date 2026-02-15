# modules/updater.py
import sys
import os
import requests
import threading
import tempfile
import logging
import urllib3
from tkinter import messagebox

# SSL uyarılarını sustur
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .constants import REPO_API_URL

# Logger Ayarı
logger = logging.getLogger(__name__)

class AutoUpdater:
    def __init__(self, current_version, root_window):
        self.current_version = current_version
        self.root = root_window
        self.running = True 

    def stop(self):
        self.running = False

    def _safe_after(self, func):
        """
        KRİTİK DÜZELTME: Pencere kapandıysa komut göndermeyi engeller.
        Bu fonksiyon 'application has been destroyed' hatasını önler.
        """
        if not self.running: return
        try:
            # Pencere hala hayatta mı kontrol et (Tkinter metodları)
            if hasattr(self.root, 'winfo_exists') and not self.root.winfo_exists():
                return
            
            # Eğer pencere varsa işlemi sıraya koy
            self.root.after(0, func)
        except Exception:
            # Pencere çoktan gitmişse hatayı yut, program çökmesin.
            pass

    def check_for_updates(self):
        if self.running:
            threading.Thread(target=self._worker, daemon=True).start()

    def _parse_version(self, v_str):
        try:
            return [int(x) for x in v_str.replace("v", "").strip().split(".")]
        except ValueError:
            return [0, 0]

    def _worker(self):
        try:
            if not self.running: return

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) VoberixUpdater/1.0'}

            # Bağlantı hatalarını yut (İnternet yoksa program açılmaya devam etsin)
            try:
                response = requests.get(REPO_API_URL, headers=headers, timeout=5, verify=False)
            except Exception:
                return 

            if not self.running: return 

            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get('tag_name', 'v0.0')
                
                v_server = self._parse_version(latest_tag)
                v_local = self._parse_version(self.current_version)

                if v_server > v_local:
                    logger.info(f"GÜNCELLEME: v{v_local} -> v{v_server}")
                    assets = data.get('assets', [])
                    if assets:
                        download_url = assets[0]['browser_download_url']
                        # GÜVENLİ ÇAĞRI: Pencere yoksa hata verme
                        self._safe_after(lambda: self.prompt_update(latest_tag, download_url))
        except Exception as e:
            logger.error(f"Updater hatası: {e}")

    def prompt_update(self, version, url):
        if not self.running: return
        try:
            msg = f"YENİ SÜRÜM: {version}\n\nGüncellemek ister misiniz?"
            # Parent pencere yoksa bile hata vermemesi için try-except
            if messagebox.askyesno("VOBERIX Güncelleme", msg, parent=self.root):
                self.perform_update(url)
        except Exception:
            pass

    def perform_update(self, url):
        if not getattr(sys, 'frozen', False): return

        try:
            # İndirme başladığı bilgisini ver (Güvenli Çağrı)
            self._safe_after(lambda: messagebox.showinfo("İndiriliyor", "Güncelleme iniyor, lütfen bekleyin."))
            
            r = requests.get(url, stream=True, timeout=60, verify=False)
            temp_exe = os.path.join(tempfile.gettempdir(), "voberix_new.exe")
            
            with open(temp_exe, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            current_exe = sys.executable
            bat_path = os.path.join(tempfile.gettempdir(), "update.bat")
            
            # Türkçe karakter sorununu önlemek için basit ASCII bat dosyası
            bat_script = f"""
            @echo off
            timeout /t 2 /nobreak > NUL
            move /Y "{temp_exe}" "{current_exe}"
            start "" "{current_exe}"
            del "%~f0"
            """
            
            with open(bat_path, "w") as f:
                f.write(bat_script)
            
            os.startfile(bat_path)
            self.running = False
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Update başarısız: {e}")