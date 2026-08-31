"""
Moduli i Dëgjuesit të Shkurtoreve Globale (hotkey_listener.py).
Përdor bibliotekën pynput për të monitoruar shtypjen e shkurtoreve të tastierës
(Ctrl + Shift + V dhe variante alternative) në nivel sistemi në Windows.
"""

import threading
import logging
from typing import Callable, Optional
from pynput import keyboard
from app.config import HOTKEY_COMBINATION

logger: logging.Logger = logging.getLogger(__name__)


class HotkeyListener:
    """
    Menaxhon dëgjimin e kombinimeve të tastierës në sfond.
    """

    def __init__(self, callback: Callable[[], None]) -> None:
        """
        Inicimi i dëgjuesit të shkurtoreve.
        """
        self.callback: Callable[[], None] = callback
        self.listener: Optional[keyboard.GlobalHotKeys] = None
        self._thread: Optional[threading.Thread] = None
        self._is_running: bool = False

    def _on_hotkey_triggered(self) -> None:
        """
        Thirret kur shtypet shkurtorja globale.
        """
        logger.info("Shkurtorja globale u shtyp!")
        try:
            if self.callback:
                self.callback()
        except Exception as error:
            logger.error("Gabim gjatë ekzekutimit të callback-ut të shkurtorës: %s", error, exc_info=True)

    def start(self) -> None:
        """
        Nis monitorimin e shkurtoreve globale në daemon thread.
        Regjistron variante të shumta për të garantuar që funksionon në çdo tastierë.
        """
        if self._is_running:
            return

        self._is_running = True

        def run() -> None:
            try:
                hotkey_map = {
                    "<ctrl>+<shift>+v": self._on_hotkey_triggered,
                    "<ctrl>+<shift>+V": self._on_hotkey_triggered,
                    "<ctrl>+<alt>+v": self._on_hotkey_triggered,
                    "<ctrl>+<alt>+V": self._on_hotkey_triggered,
                }
                custom_comb = HOTKEY_COMBINATION.lower()
                if custom_comb not in hotkey_map:
                    hotkey_map[custom_comb] = self._on_hotkey_triggered
                    hotkey_map[HOTKEY_COMBINATION] = self._on_hotkey_triggered

                with keyboard.GlobalHotKeys(hotkey_map) as self.listener:
                    logger.info(
                        "Dëgjuesi i shkurtoreve u nis me sukses (Ctrl+Shift+V / Ctrl+Alt+V / %s).",
                        HOTKEY_COMBINATION,
                    )
                    self.listener.join()
            except Exception as error:
                if self._is_running:
                    logger.error("Gabim gjatë ekzekutimit të dëgjuesit të shkurtoreve: %s", error, exc_info=True)

        self._thread = threading.Thread(
            target=run, daemon=True, name="HotkeyListenerThread"
        )
        self._thread.start()

    def stop(self) -> None:
        """
        Ndalon dëgjuesin e shkurtoreve.
        """
        self._is_running = False
        if self.listener is not None:
            try:
                self.listener.stop()
                logger.info("Dëgjuesi i shkurtoreve u ndalua.")
            except Exception as error:
                logger.warning("Gabim gjatë ndalimit të dëgjuesit: %s", error)
        self.listener = None
