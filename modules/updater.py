# modules/updater.py
import requests
import os
import sys
import subprocess
import time
import threading
import logging
from tkinter import messagebox
from .constants import REPO_API_URL, VERSION

logger = logging.getLogger(__name__)

class AutoUpdater:
    def __init__(self, current_version, app_instance):
        self.current_version = current_version
        self.app = app_instance
        self.download_url = None
        self.new_version = None

    def check_for_updates(self):
        """GitHub API üzerinden yeni sürüm kontrolü yapar."""
        threading.Thread(target=self._check_update_thread, daemon=True).start()

    def _check_update_thread(self):
        try:
            response = requests.get(REPO_API_URL, timeout=10)
            if response.status_code != 200:
                return

            data = response.json()
            latest_tag = data.get("tag_name", "").strip() 
            
            # Versiyon kontrolü ("v" harfi toleranslı)
            if latest_tag.lower().lstrip('v') != self.current_version.lower().lstrip('v'):
                self.new_version = latest_tag
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        self.download_url = asset["browser_download_url"]
                        break
                
                if self.download_url:
                    self.app.after(0, self._prompt_update)

        except Exception as e:
            logger.error(f"Guncelleme kontrol hatasi: {e}")

    def _prompt_update(self):
        msg = f"Yeni güncelleme mevcut ({self.new_version})!\nŞimdi indirip güncellemek ister misiniz?"
        if messagebox.askyesno("VOBERIX Güncelleme", msg):
            self.app.show_toast("GÜNCELLENİYOR", "İndiriliyor, lütfen kapatmayın...", "warning")
            threading.Thread(target=self._download_and_install, daemon=True).start()

    def _download_and_install(self):
        try:
            current_exe = os.path.abspath(sys.argv[0])
            new_exe = current_exe + ".tmp"      # İndirilen yeni dosya
            old_exe = current_exe + ".old"      # Eski dosyanın yeni adı (Yedek)

            # Dosyayı indir
            response = requests.get(self.download_url, stream=True, timeout=60)
            if response.status_code == 200:
                with open(new_exe, 'wb') as f:
                    for chunk in response.iter_content(4096):
                        f.write(chunk)
                
                updater_bat = "update_installer.bat"
                exe_name = os.path.basename(current_exe)
                
                # --- ONEDRIVE DOSTU GÜNCELLEME SCRIPT'İ ---
                # 1. Eski dosyayı SİLMEK yerine ADINI DEĞİŞTİRİYORUZ (move). Bu işlem kilitleme yapmaz.
                # 2. Yeni dosyayı yerine koyuyoruz.
                # 3. Programı başlatıyoruz.
                # 4. En son temizlik yapıyoruz (Eğer silinemezse de sorun değil, .old olarak kalır).
                
                cmd = f"""
@echo off
@chcp 65001 > nul
echo Guncelleme baslatiliyor... Lutfen bekleyin...

:: 1. Programın kapanması için bekle
timeout /t 3 /nobreak > NUL
taskkill /F /IM "{exe_name}" > NUL 2>&1

:: 2. OneDrive senkronizasyonu için kısa mola
timeout /t 2 /nobreak > NUL

:: 3. Eski dosyanın varsa yedeğini temizle
if exist "{old_exe}" del "{old_exe}"

:: 4. Mevcut dosyayı .old yap (SİLME YOK, SADECE İSİM DEĞİŞTİRME)
move /Y "{current_exe}" "{old_exe}" > NUL

:: 5. Yeni dosyayı asıl yerine koy
move /Y "{new_exe}" "{current_exe}" > NUL

:: 6. Yeni programı başlat (Start komutu ile bağımsız)
start "" "{current_exe}"

:: 7. Scripti temizle
del "%~f0"
"""
                with open(updater_bat, "w", encoding="utf-8") as bat:
                    bat.write(cmd)

                self.app.after(0, lambda: self._finalize_update(updater_bat))

            else:
                self.app.after(0, lambda: self.app.show_toast("HATA", "İndirme başarısız.", "error"))

        except Exception as e:
            logger.error(f"Indirme hatasi: {e}")
            self.app.after(0, lambda: self.app.show_toast("HATA", f"Hata: {e}", "error"))

    def _finalize_update(self, bat_file):
        """Scripti tamamen bağımsız bir süreç olarak başlat."""
        messagebox.showinfo("GÜNCELLEME", "İndirme tamamlandı. Program yeniden başlatılıyor.")
        
        try:
            # CREATE_NEW_CONSOLE | DETACHED_PROCESS benzeri bir yapı
            # Shell=True ve creationflags ile CMD penceresini ana programdan koparıyoruz.
            creation_flags = 0x00000010 # CREATE_NEW_CONSOLE
            subprocess.Popen([bat_file], shell=True, creationflags=creation_flags)
        except Exception:
            os.startfile(bat_file)
            
        # Programı kapat
        self.app.on_closing()