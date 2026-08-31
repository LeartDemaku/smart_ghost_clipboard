"""
Moduli i Shiritit të Statusit dhe Veprimeve Kryesore (status_bar.py).
Shfaq statistikat e tekstit (fjalë, shkronja, kohë leximi), statusin e sistemit,
dhe butonat e shpejtë të veprimit: Pastro, Rifresko, Kopjo dhe Auto-Paste.
"""

from typing import Callable, Optional
import customtkinter as ctk

from app.ui_components.theme import Theme


class StatusBar(ctk.CTkFrame):
    """
    Shiriti i poshtëm i integruar me telemetri dhe butonat kryesorë.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_clear: Callable[[], None],
        on_reload: Callable[[], None],
        on_copy: Callable[[], None],
        on_paste_replace: Callable[[], None],
        on_quit: Callable[[], None],
        **kwargs
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.on_clear = on_clear
        self.on_reload = on_reload
        self.on_copy = on_copy
        self.on_paste_replace = on_paste_replace
        self.on_quit = on_quit

        self._build_ui()

    def _build_ui(self) -> None:
        # Majtas: Statistikat & Statusi
        self.left_box = ctk.CTkFrame(self, fg_color="transparent")
        self.left_box.pack(side="left", fill="y")

        self.stats_label = ctk.CTkLabel(
            self.left_box,
            text="📊 0 fjalë | 0 shkronja | ~0s lexim",
            font=Theme.font_status(),
            text_color=Theme.TEXT_SECONDARY,
        )
        self.stats_label.pack(anchor="w")

        self.status_label = ctk.CTkLabel(
            self.left_box,
            text="Gati.",
            font=Theme.font_status(),
            text_color=Theme.TEXT_MUTED,
        )
        self.status_label.pack(anchor="w")

        # Djathtas: Butonat e Veprimit
        self.right_box = ctk.CTkFrame(self, fg_color="transparent")
        self.right_box.pack(side="right", fill="y")

        # Butoni Dil
        self.quit_btn = ctk.CTkButton(
            self.right_box,
            text="🚪",
            font=Theme.font_button_sm(),
            width=32,
            height=32,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.DANGER,
            corner_radius=Theme.RADIUS_MD,
            command=self.on_quit,
        )
        self.quit_btn.pack(side="right", padx=(4, 0))

        # Butoni Auto-Paste (Kopjo & Zëvendëso)
        self.paste_replace_btn = ctk.CTkButton(
            self.right_box,
            text="🚀 Kopjo & Zëvendëso (↵)",
            font=Theme.font_button(),
            height=32,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            corner_radius=Theme.RADIUS_MD,
            command=self.on_paste_replace,
        )
        self.paste_replace_btn.pack(side="right", padx=(4, 0))

        # Butoni Kopjo
        self.copy_btn = ctk.CTkButton(
            self.right_box,
            text="📋 Kopjo (Ctrl+Shift+C)",
            font=Theme.font_button(),
            height=32,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            corner_radius=Theme.RADIUS_MD,
            command=self.on_copy,
        )
        self.copy_btn.pack(side="right", padx=(4, 0))

        # Butoni Rifresko
        self.reload_btn = ctk.CTkButton(
            self.right_box,
            text="🔄 Rifresko (F5)",
            font=Theme.font_button_sm(),
            height=32,
            width=100,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.BG_SURFACE_HOVER,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            corner_radius=Theme.RADIUS_MD,
            command=self.on_reload,
        )
        self.reload_btn.pack(side="right", padx=(4, 0))

        # Butoni Pastro
        self.clear_btn = ctk.CTkButton(
            self.right_box,
            text="🧹 Pastro (Ctrl+L)",
            font=Theme.font_button_sm(),
            height=32,
            width=100,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.BG_SURFACE_HOVER,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            corner_radius=Theme.RADIUS_MD,
            command=self.on_clear,
        )
        self.clear_btn.pack(side="right")

    def update_stats(self, text: str) -> None:
        """Llogarit dhe shfaq numrin e fjalëve, shkronjave dhe kohën e leximit."""
        chars = len(text)
        words = len(text.split()) if text.strip() else 0
        # Supozojmë 200 fjalë në minutë për lexim mesatar
        reading_seconds = max(1, int((words / 200) * 60)) if words > 0 else 0

        if reading_seconds > 60:
            time_str = f"~{reading_seconds // 60}m {reading_seconds % 60}s lexim"
        else:
            time_str = f"~{reading_seconds}s lexim"

        self.stats_label.configure(
            text=f"📊 {words} fjalë | {chars} shkronja | {time_str}"
        )

    def set_status(self, message: str, text_color: str = Theme.TEXT_SECONDARY) -> None:
        """Përditëson mesazhin e statusit."""
        self.status_label.configure(text=message, text_color=text_color)

    def show_copy_feedback(self) -> None:
        """Shfaq animacion / ndryshim të tekstit të butonit gjatë kopjimit me sukses."""
        orig_text = "📋 Kopjo (Ctrl+Shift+C)"
        self.copy_btn.configure(text="✅ U Kopjua!", fg_color="#059669")
        self.set_status("Teksti u kopjua me sukses në Clipboard!", Theme.SUCCESS)
        self.after(1500, lambda: self.copy_btn.configure(text=orig_text, fg_color=Theme.SUCCESS))

    def set_enabled(self, enabled: bool) -> None:
        """Aktivizon ose çaktivizon butonat gjatë përpunimit."""
        state = "normal" if enabled else "disabled"
        self.copy_btn.configure(state=state)
        self.paste_replace_btn.configure(state=state)
        self.reload_btn.configure(state=state)
        self.clear_btn.configure(state=state)
