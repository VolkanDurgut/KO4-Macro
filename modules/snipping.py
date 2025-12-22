# modules/snipping.py
import tkinter as tk
from .constants import COLORS

class SnippingTool(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.attributes('-fullscreen', True)
        self.attributes('-alpha', 0.3)
        self.configure(bg='black')
        self.cursor_start_x = 0; self.cursor_start_y = 0; self.rect = None
        
        self.canvas = tk.Canvas(self, cursor="cross", bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Escape>", lambda e: self.destroy())

    def on_press(self, event):
        self.cursor_start_x = event.x; self.cursor_start_y = event.y
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline=COLORS["ferrari_red"], width=3, fill="white", stipple="gray12")

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.cursor_start_x, self.cursor_start_y, event.x, event.y)

    def on_release(self, event):
        x1 = min(self.cursor_start_x, event.x); y1 = min(self.cursor_start_y, event.y)
        x2 = max(self.cursor_start_x, event.x); y2 = max(self.cursor_start_y, event.y)
        self.callback(x1, y1, x2, y2)
        self.destroy()