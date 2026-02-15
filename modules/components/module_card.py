# modules/components/module_card.py
import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os
import logging
from ..constants import COLORS, FONT_FAMILY

logger = logging.getLogger(__name__)

# --- TOOLTIP CLASS (İPUCU BALONCUĞU) ---
class CTkToolTip:
    """Mouse üzerine gelince açıklama gösteren yardımcı sınıf."""
    def __init__(self, widget, text, delay=300):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)

    def schedule(self, event=None):
        self.id = self.widget.after(self.delay, self.show)

    def show(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True) 
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip_window, text=self.text, justify='left',
            background="#222", foreground="white",
            relief='solid', borderwidth=0, font=("Arial", 9)
        )
        label.pack(ipadx=8, ipady=4)

    def hide(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# --- MODULE CARD CLASS (NEXT-GEN TASARIM) ---
class ModuleCard(ctk.CTkFrame):
    def __init__(self, parent, app, module_key, title, icon_path, fallback_txt, extra_widget_callback=None, col_index=0, **kwargs):
        super().__init__(
            parent, fg_color=COLORS["bg_card"], corner_radius=12, 
            border_width=1, border_color=COLORS["border"], **kwargs
        )
        self.app = app
        self.module_key = module_key
        self.title = title
        self.icon_path = icon_path
        self.fallback_txt = fallback_txt
        
        self.grid(row=0, column=col_index, padx=12, pady=10, sticky="nsew")
        self._build_ui(extra_widget_callback)
        self._load_state() 

    def _build_ui(self, extra_callback):
        # 1. Üst Başlık ve Toggle Alanı
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        # Başlık ve İkon
        self._load_icon(header_frame)
        
        # Toggle Switch
        self.switch_var = ctk.StringVar(value="off")
        self.switch = ctk.CTkSwitch(
            header_frame, text="", command=self._toggle_action,
            variable=self.switch_var, 
            onvalue="on", offvalue="off", 
            progress_color=COLORS["green_neon"], button_color="white",
            button_hover_color="#EEEEEE", width=45, height=24,
            fg_color=COLORS["bg_input"]
        )
        self.switch.pack(side="right", anchor="ne")

        # Ayırıcı Çizgi
        ctk.CTkFrame(self, height=2, fg_color=COLORS["bg_input"]).pack(fill="x", padx=15, pady=5)

        # 2. Orta Alan: Ekstra Widgetlar
        if extra_callback:
            content_frame = ctk.CTkFrame(self, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=15, pady=5)
            extra_callback(content_frame)

        # 3. Alt Kısım: SADECE TUŞ BUTONU (Gecikme kaldırıldı)
        if self.module_key != "combo":
            self._build_footer_controls()

    def _load_icon(self, parent):
        left_box = ctk.CTkFrame(parent, fg_color="transparent")
        left_box.pack(side="left")

        if os.path.exists(self.icon_path):
            try:
                pil_img = Image.open(self.icon_path).convert("RGBA")
                self.icon_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(28, 28))
                ctk.CTkLabel(left_box, text="", image=self.icon_image).pack(side="left", padx=(0, 8))
            except: pass
        else:
            ctk.CTkLabel(left_box, text=self.fallback_txt[:1], font=(FONT_FAMILY[1], 20, "bold"), text_color=COLORS["accent"]).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(left_box, text=self.title, font=("Segoe UI", 12, "bold"), text_color=COLORS["text_main"]).pack(side="left")

    def _build_footer_controls(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=15, pady=15)

        # Tuş Butonu (Tam Genişlik)
        key_val = self.app.cfg.get(f"{self.module_key}_key", "").upper()
        self.key_btn = ctk.CTkButton(
            footer, text=f"[{key_val}]" if key_val else "[YOK]", 
            height=32, font=("Consolas", 11, "bold"),
            fg_color=COLORS["bg_input"], hover_color=COLORS["bg_main"],
            border_width=1, border_color=COLORS["border"], 
            text_color=COLORS["text_dim"],
            command=self._listen_key
        )
        # fill="x", expand=True ile butonu tüm footer'a yayıyoruz
        self.key_btn.pack(side="left", fill="x", expand=True) 
        CTkToolTip(self.key_btn, text="Kısayol tuşu atamak için tıkla")
        
        # Referans Kaydı
        setattr(self.app, f"btn_{self.module_key}_key", self.key_btn)

        # GECİKME KUTUSU (ENTRY) KALDIRILDI

    def _load_state(self):
        active_key = f"{self.module_key}_active"
        is_active = self.app.cfg.get(active_key, False)
        self.switch_var.set("on" if is_active else "off")
        self.configure(border_color=COLORS["accent"] if is_active else COLORS["border"])

    def _toggle_action(self):
        state = (self.switch_var.get() == "on")
        active_key = f"{self.module_key}_active"
        self.app.cfg.set(active_key, state)
        self.configure(border_color=COLORS["accent"] if state else COLORS["border"])
        try:
            self.app.log_to_console(f"{self.title} modülü {'AKTİF' if state else 'PASİF'} duruma getirildi.")
        except: pass

    def _listen_key(self):
        self.key_btn.configure(text="...", border_color=COLORS["accent"])
        self.app.listen_for_key(self.module_key)