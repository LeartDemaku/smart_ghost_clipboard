"""
Moduli i Menaxhimit të Clipboard-it (clipboard_manager.py).
Ofron funksionalitete të besueshme për leximin, shkrimin dhe zëvendësimin e menjëhershëm (Auto-Paste)
të tekstit në kujtesën e përkohshme (Clipboard) të Windows.
"""

import time
import logging
from typing import Optional

import pyperclip
from pynput.keyboard import Controller, Key

from app.config import CLIPBOARD_MAX_RETRIES, CLIPBOARD_RETRY_DELAY

logger: logging.Logger = logging.getLogger(__name__)


class ClipboardManager:
    """
    Klasë shërbimi për ndërveprimin e sigurt me Windows Clipboard dhe Auto-Paste.
    """

    def __init__(self) -> None:
        self._keyboard: Controller = Controller()

    @staticmethod
    def get_text() -> str:
        """
        Merr tekstin aktual nga clipboard duke tentuar disa herë nëse clipboard-i
        është i bllokuar përkohësisht nga një proces tjetër në Windows.
        """
        for attempt in range(1, CLIPBOARD_MAX_RETRIES + 1):
            try:
                text: Optional[str] = pyperclip.paste()
                if text is not None:
                    cleaned = str(text).replace("\x00", "")
                    return cleaned
                return ""
            except Exception as error:
                logger.warning(
                    "Tentativa %d/%d për lexim nga clipboard dështoi: %s",
                    attempt, CLIPBOARD_MAX_RETRIES, error
                )
                if attempt < CLIPBOARD_MAX_RETRIES:
                    time.sleep(CLIPBOARD_RETRY_DELAY)

        logger.error("Të gjitha tentativat e leximit nga clipboard dështuan.")
        return ""

    @staticmethod
    def set_text(text: str) -> bool:
        """
        Kopjon tekstin e specifikuar në clipboard me pastrim nga karakteret e pavlefshme.
        """
        clean_text = str(text).replace("\x00", "") if text is not None else ""
        for attempt in range(1, CLIPBOARD_MAX_RETRIES + 1):
            try:
                pyperclip.copy(clean_text)
                return True
            except Exception as error:
                logger.warning(
                    "Tentativa %d/%d për shkrim në clipboard dështoi: %s",
                    attempt, CLIPBOARD_MAX_RETRIES, error
                )
                if attempt < CLIPBOARD_MAX_RETRIES:
                    time.sleep(CLIPBOARD_RETRY_DELAY)

        logger.error("Të gjitha tentativat e shkrimit në clipboard dështuan.")
        return False

    def paste_to_active_app(self, text: str) -> bool:
        """
        Kopjon tekstin në clipboard dhe simulon menjëherë 'Ctrl + V' në dritaren aktive.
        """
        copied = self.set_text(text)
        if not copied:
            logger.error("Nuk u arrit vendosja e tekstit para simulimit të paste.")
            return False

        time.sleep(0.08)
        try:
            self._keyboard.press(Key.ctrl)
            self._keyboard.press("v")
            time.sleep(0.02)
            self._keyboard.release("v")
            self._keyboard.release(Key.ctrl)
            logger.info("Simulimi i Ctrl+V u krye me sukses.")
            return True
        except Exception as error:
            logger.error("Gabim gjatë simulimit të Ctrl+V në aplikacion: %s", error)
            return False
