# modules/components/error_window.py
import customtkinter as ctk
import sys
from ..constants import COLORS, FONT_FAMILY

class GlobalErrorWindow(ctk.CTkToplevel):
    """
    Sistem çöktüğünde (Unhandled Exception) devreye giren modern raporlama ekranı.
    """
    def __init__(self, title, error_details):
        super().__init__()
        
        self.title(title)
        self.geometry("650x450")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        # Pencereyi ortala
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 650) // 2
        y = (screen_height - 450) // 2
        self.geometry(f"+{x}+{y}")
        
        self.configure(fg_color=COLORS["bg_main"])
        
        # Başlık ve İkon
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=(20, 10))
        
        ctk.CTkLabel(
            title_frame, text="⚠️", font=("Arial", 32)
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(
            title_frame, text="BEKLENMEDİK BİR HATA OLUŞTU", 
            font=(FONT_FAMILY[0], 18, "bold"), 
            text_color=COLORS["red_error"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            self, text="Uygulama kritik bir sorunla karşılaştı ve kapatılması gerekiyor.\nLütfen aşağıdaki hata raporunu kopyalayıp teknik desteğe iletin.", 
            font=(FONT_FAMILY[0], 12), 
            text_color=COLORS["text_dim"]
        ).pack(pady=(0, 15))

        # Hata Detayı
        self.textbox = ctk.CTkTextbox(
            self, width=600, height=220, 
            font=("Consolas", 10),
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_main"],
            border_width=1,
            border_color=COLORS["border_dim"]
        )
        self.textbox.pack(padx=20, pady=5)
        self.textbox.insert("0.0", error_details)
        self.textbox.configure(state="disabled")
        
        # Butonlar
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        self.btn_copy = ctk.CTkButton(
            btn_frame, text="HATAYI KOPYALA", 
            width=160, height=40,
            font=(FONT_FAMILY[0], 12, "bold"),
            fg_color=COLORS["cyan_neon"], 
            text_color="black",
            hover_color=COLORS["btn_hover"],
            command=self.copy_to_clipboard
        )
        self.btn_copy.pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, text="UYGULAMAYI KAPAT", 
            width=160, height=40,
            font=(FONT_FAMILY[0], 12, "bold"),
            fg_color=COLORS["bg_input"], 
            text_color=COLORS["red_error"],
            border_width=1,
            border_color=COLORS["red_error"],
            hover_color=COLORS["bg_card"],
            command=self.close_app
        ).pack(side="left", padx=10)
        
        self.grab_set()
        self.focus_force()
        self.wait_window()

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.textbox.get("0.0", "end"))
        self.update()
        original_text = self.btn_copy.cget("text")
        self.btn_copy.configure(text="KOPYALANDI! ✓", fg_color=COLORS["green_neon"])
        self.after(2000, lambda: self.btn_copy.configure(text=original_text, fg_color=COLORS["cyan_neon"]))
        
    def close_app(self):
        self.destroy()
        sys.exit(1)