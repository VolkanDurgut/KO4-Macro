# modules/components/announcement.py
import customtkinter as ctk
from ..constants import COLORS, FONT_FAMILY

class AnnouncementWindow(ctk.CTkToplevel):
    """
    Sunucudan gelen acil duyuruları gösteren modal pencere.
    """
    def __init__(self, parent, message):
        super().__init__(parent)
        self.title("SİSTEM DUYURUSU")
        self.geometry("500x300")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=COLORS["bg_main"])
        
        # Ortala
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 300) // 2
        self.geometry(f"+{x}+{y}")

        # İkon ve Başlık
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=(20, 10))
        
        ctk.CTkLabel(title_frame, text="📢", font=("Arial", 32)).pack(side="left", padx=10)
        ctk.CTkLabel(title_frame, text="YÖNETİCİ MESAJI", font=(FONT_FAMILY[0], 18, "bold"), text_color=COLORS["yellow_neon"]).pack(side="left")

        # Mesaj İçeriği
        self.textbox = ctk.CTkTextbox(
            self, width=450, height=150, 
            font=(FONT_FAMILY[0], 12),
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_main"],
            border_width=1,
            border_color=COLORS["border_dim"],
            wrap="word"
        )
        self.textbox.pack(padx=20, pady=5)
        self.textbox.insert("0.0", message)
        self.textbox.configure(state="disabled")

        # Tamam Butonu
        ctk.CTkButton(
            self, text="ANLAŞILDI", width=160, height=40,
            font=(FONT_FAMILY[0], 12, "bold"),
            fg_color=COLORS["cyan_neon"], text_color="black", hover_color=COLORS["btn_hover"],
            command=self.destroy
        ).pack(pady=20)
        
        self.grab_set()
        self.focus_force()