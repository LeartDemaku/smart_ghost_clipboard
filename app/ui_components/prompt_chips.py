"""
Moduli i Modifikuesve të Shpejtë dhe Inputit të Personalizuar (prompt_chips.py).
Përmban fushën për komanda me tekst të lirë dhe chips (pills) me një klikim.
"""

from typing import Callable, List
import customtkinter as ctk

from app.config import PROMPT_CHIPS
from app.ui_components.theme import Theme


class PromptChipsBar(ctk.CTkFrame):
    """
    Shiriti i modifikuesve të shpejtë me një klikim dhe kërkesave të lira.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_execute_instruction: Callable[[str], None],
        **kwargs
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.on_execute_instruction = on_execute_instruction
        self.chip_buttons: List[ctk.CTkButton] = []

        self._build_ui()

    def _build_ui(self) -> None:
        # 1. Inputi me tekst të lirë (Custom Entry + Run Button)
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.pack(fill="x", pady=(0, 4))

        self.custom_entry = ctk.CTkEntry(
            self.entry_frame,
            placeholder_text="Ose shkruaj një udhëzim të personalizuar... (Shtyp Enter)",
            font=Theme.font_subtitle(),
            height=34,
            corner_radius=Theme.RADIUS_MD,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_LIGHT,
            text_color=Theme.TEXT_PRIMARY,
        )
        self.custom_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.custom_entry.bind("<Return>", lambda e: self._submit_entry())

        self.run_btn = ctk.CTkButton(
            self.entry_frame,
            text="⚡ Ekzekuto",
            font=Theme.font_button(),
            height=34,
            width=100,
            corner_radius=Theme.RADIUS_MD,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            command=self._submit_entry,
        )
        self.run_btn.pack(side="right")

        # 2. Rreshti i Chips (Pills me një klikim)
        self.chips_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chips_frame.pack(fill="x", pady=(2, 2))

        # Etiketa e vogël "Shpejt:"
        self.chips_label = ctk.CTkLabel(
            self.chips_frame,
            text="Modifiko:",
            font=Theme.font_badge(),
            text_color=Theme.TEXT_MUTED,
        )
        self.chips_label.pack(side="left", padx=(0, 6))

        for label, instruction in PROMPT_CHIPS:
            btn = ctk.CTkButton(
                self.chips_frame,
                text=label,
                font=Theme.font_chip(),
                height=26,
                corner_radius=Theme.RADIUS_ROUND,
                fg_color=Theme.BG_SURFACE,
                hover_color=Theme.ACCENT_PURPLE,
                border_width=1,
                border_color=Theme.BORDER_MAIN,
                text_color=Theme.TEXT_PRIMARY,
                command=lambda inst=instruction: self.on_execute_instruction(inst),
            )
            btn.pack(side="left", padx=2)
            self.chip_buttons.append(btn)

    def _submit_entry(self) -> None:
        """Dërgon udhëzimin e shkruar nga fusha e tekstit."""
        instruction = self.custom_entry.get().strip()
        if instruction:
            self.on_execute_instruction(instruction)

    def get_entry_text(self) -> str:
        return self.custom_entry.get().strip()

    def set_entry_text(self, text: str) -> None:
        self.custom_entry.delete(0, "end")
        self.custom_entry.insert(0, text)

    def focus_entry(self) -> None:
        self.custom_entry.focus_set()

    def set_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.custom_entry.configure(state=state)
        self.run_btn.configure(state=state)
        for btn in self.chip_buttons:
            btn.configure(state=state)
