# modules/features/restore.py
import keyboard
import logging
from ..core import perform_restore_scan_macro

logger = logging.getLogger(__name__)

def run_restore_module(cfg, region):
    """
    Restore taramasını tetikler.
    """
    if cfg.get("restore_active", False):
        r_key = cfg.get("restore_key")
        
        if r_key and keyboard.is_pressed(r_key):
            try:
                perform_restore_scan_macro(region, cfg.get("restore_delay", 0.0))
            except Exception as e:
                logger.error(f"Restore Modül Hatası: {e}")