"""
Moduli i Theksimit të Ndryshimeve (diff_highlighter.py).
Krahason tekstin origjinal me rezultatin e AI dhe thekson ndryshimet
(fjalët e reja në jeshile, fjalët e hequra në të kuqe) duke përdorur SequenceMatcher.
"""

import difflib
import logging
from typing import List, Tuple
import customtkinter as ctk
from app.ui_components.theme import Theme

logger: logging.Logger = logging.getLogger(__name__)


class DiffHighlighter:
    """
    Klasë ndihmëse për konfigurimin dhe ngjyrosjen e diferencave në fushën e tekstit.
    """

    @staticmethod
    def setup_tags(textbox: ctk.CTkTextbox) -> None:
        """
        Konfiguron tag-et e ngjyrave në widget-in e brendshëm Tkinter Text.
        """
        try:
            tk_text = textbox._textbox
            tk_text.tag_configure(
                "diff_added",
                background=Theme.DIFF_ADDED_BG,
                foreground=Theme.DIFF_ADDED_FG,
            )
            tk_text.tag_configure(
                "diff_removed",
                background=Theme.DIFF_REMOVED_BG,
                foreground=Theme.DIFF_REMOVED_FG,
            )
            tk_text.tag_configure(
                "diff_normal",
                foreground=Theme.TEXT_PRIMARY,
            )
        except Exception as error:
            logger.debug("Nuk u arrit konfigurimi i tag-eve të diff: %s", error)

    @classmethod
    def apply_diff(
        cls,
        textbox: ctk.CTkTextbox,
        original_text: str,
        transformed_text: str,
    ) -> None:
        """
        Krahason fjalë për fjalë tekstin origjinal me tekstin e transformuar
        dhe e vendos në textbox me theksim vizual.
        """
        cls.setup_tags(textbox)

        orig_words = original_text.split()
        trans_words = transformed_text.split()

        if not orig_words or not trans_words:
            textbox.delete("1.0", "end")
            textbox.insert("1.0", transformed_text)
            return

        matcher = difflib.SequenceMatcher(None, orig_words, trans_words)
        
        textbox.delete("1.0", "end")
        tk_text = textbox._textbox

        try:
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    chunk = " ".join(trans_words[j1:j2]) + " "
                    tk_text.insert("end", chunk, "diff_normal")
                elif tag == "insert":
                    chunk = " ".join(trans_words[j1:j2]) + " "
                    tk_text.insert("end", chunk, "diff_added")
                elif tag == "replace":
                    # Shfaq fjalën e re të theksuar me jeshile
                    chunk = " ".join(trans_words[j1:j2]) + " "
                    tk_text.insert("end", chunk, "diff_added")
                elif tag == "delete":
                    pass  # Mos e ngarko tekstin e hequr në rezultatin përfundimtar
        except Exception as error:
            logger.error("Gabim gjatë aplikimit të diff: %s", error)
            textbox.delete("1.0", "end")
            textbox.insert("1.0", transformed_text)
