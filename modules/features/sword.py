# modules/features/sword.py
import keyboard
import logging
from ..core import perform_sword_scan_macro

logger = logging.getLogger(__name__)

def run_sword_module(cfg, region):
    """
    Atak (Minor/Sword) taramasını tetikler.
    """
    if cfg.get("sword_active", True):
        s_key = cfg.get("sword_key")
        
        if s_key and keyboard.is_pressed(s_key):
            try:
                perform_sword_scan_macro(region, cfg.get("sword_delay", 0.0))
            except Exception as e:
                logger.error(f"Sword Modül Hatası: {e}")