# main.py
from modules.splash import SplashScreen
from modules.ui import MacroApp

def launch_main_app():
    app = MacroApp()
    app.mainloop()

if __name__ == "__main__":
    # Önce Splash Screen, callback olarak ana uygulamayı alır
    splash = SplashScreen(main_app_callback=launch_main_app)
    splash.mainloop()