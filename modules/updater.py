# modules/updater.py
import sys
import os
import requests
import threading
from tkinter import messagebox
import webbrowser
from .constants import REPO_API_URL

class AutoUpdater:
    def __init__(self, current_version, root_window):
        self.current_version = current_version
        self.root = root_window

    def check_for_updates(self):
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            response = requests.get(REPO_API_URL)
            if response.status_code == 200:
                data = response.json()
                latest_tag = data['tag_name']
                clean_latest = latest_tag.replace("v", "").strip()
                clean_current = self.current_version.replace("v", "").strip()

                if clean_latest != clean_current:
                    assets = data.get('assets', [])
                    if assets:
                        download_url = assets[0]['browser_download_url']
                        self.root.after(0, lambda: self.prompt_update(latest_tag, download_url))
        except: pass

    def prompt_update(self, version, url):
        msg = f"YENİ SÜRÜM MEVCUT: {version}\n\nProgramı şimdi otomatik güncelleyip yeniden başlatmak ister misiniz?"
        if messagebox.askyesno("Güncelleme", msg):
            self.perform_update(url)

    def perform_update(self, url):
        if not getattr(sys, 'frozen', False):
            messagebox.showinfo("Bilgi", "Python script modunda güncelleme yapılamaz.")
            return

        try:
            temp_exe = "new_version_temp.exe"
            r = requests.get(url, stream=True)
            with open(temp_exe, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    f.write(chunk)
            
            current_exe = sys.executable
            exe_name = os.path.basename(current_exe)
            
            bat_script = f"""
            @echo off
            echo Guncelleniyor... Lutfen bekleyin...
            timeout /t 3 /nobreak > NUL
            move /Y "{temp_exe}" "{exe_name}"
            start "" "{exe_name}"
            del "%~f0"
            """
            with open("updater.bat", "w") as f:
                f.write(bat_script)
            os.startfile("updater.bat")
            sys.exit()
        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme başarısız: {e}")