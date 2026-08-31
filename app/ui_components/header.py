"""
Moduli i Shiritit të Kokës (header.py).
Përmban logon, titullin e aplikacionit, badge të modelit AI,
matësin e latencës në sekonda, dhe butonat e kontrollit të pamjes (Split View dhe Historiku).
"""

from typing import Callable, Optional
import customtkinter as ctk

from app.config import APP_NAME, APP_VERSION, AI_MODEL
from app.ui_components.theme import Theme


class HeaderBar(ctk.CTkFrame):
    """
    Paneli i sipërm i stilizuar me estetikë moderne obsidian/glassmorphism.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_toggle_split_view: Callable[[], None],
        on_toggle_history: Callable[[], None],
        on_hide_window: Callable[[], None],
        **kwargs
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.on_toggle_split_view = on_toggle_split_view
        self.on_toggle_history = on_toggle_history
        self.on_hide_window = on_hide_window

        self._build_header()

    def _build_header(self) -> None:
        # Majtas: Logo dhe Titulli
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(
            self.left_container,
            text=f"⚡ {APP_NAME.upper()}",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY,
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.left_container,
            text=f"v{APP_VERSION} • Ultra-Responsive AI • Ctrl+Shift+V për thirrje",
            font=Theme.font_subtitle(),
            text_color=Theme.TEXT_SECONDARY,
        )
        self.subtitle_label.pack(anchor="w")

        # Djathtas: Controls, Badges & Toggles
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="right", fill="y")

        # Butoni Fsheh (Close / Hide)
        self.hide_btn = ctk.CTkButton(
            self.right_container,
            text="✕",
            font=Theme.font_button_sm(),
            width=28,
            height=28,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.DANGER,
            corner_radius=Theme.RADIUS_SM,
            command=self.on_hide_window,
        )
        self.hide_btn.pack(side="right", padx=(6, 0))

        # Butoni i Historikut
        self.history_btn = ctk.CTkButton(
            self.right_container,
            text="📜 Historiku",
            font=Theme.font_button_sm(),
            height=28,
            width=90,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.BG_SURFACE_HOVER,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            corner_radius=Theme.RADIUS_SM,
            command=self.on_toggle_history,
        )
        self.history_btn.pack(side="right", padx=(6, 0))

        # Butoni Split View Toggle
        self.split_btn = ctk.CTkButton(
            self.right_container,
            text="🔀 Split View",
            font=Theme.font_button_sm(),
            height=28,
            width=95,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.BG_SURFACE_HOVER,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            corner_radius=Theme.RADIUS_SM,
            command=self.on_toggle_split_view,
        )
        self.split_btn.pack(side="right", padx=(6, 0))

        # Badge e Latencës
        self.latency_badge = ctk.CTkLabel(
            self.right_container,
            text="⚡ Gati",
            font=Theme.font_badge(),
            text_color=Theme.ACCENT_CYAN,
            fg_color=Theme.BG_INPUT,
            corner_radius=Theme.RADIUS_SM,
            padx=8,
            pady=3,
        )
        self.latency_badge.pack(side="right", padx=(6, 0))

        # Badge e Modelit AI
        self.model_badge = ctk.CTkLabel(
            self.right_container,
            text=f"🏷️ {AI_MODEL}",
            font=Theme.font_badge(),
            text_color="#FFFFFF",
            fg_color=Theme.ACCENT_PRIMARY,
            corner_radius=Theme.RADIUS_SM,
            padx=10,
            pady=3,
        )
        self.model_badge.pack(side="right")

    def update_latency(self, seconds: float) -> None:
        """Përditëson kohën e gjenerimit në badge."""
        self.latency_badge.configure(
            text=f"⏱️ {seconds:.2f}s",
            text_color=Theme.SUCCESS if seconds < 1.0 else Theme.ACCENT_CYAN,
        )

    def set_latency_busy(self) -> None:
        """Vendos statusin në gjenerim e sipër."""
        self.latency_badge.configure(
            text="⚡ Duke shkruar...",
            text_color=Theme.WARNING,
        )

    def set_split_active(self, is_split: bool) -> None:
        """Ndryshon pamjen e butonit split view."""
        if is_split:
            self.split_btn.configure(
                text="📄 Single View",
                fg_color=Theme.ACCENT_SECONDARY,
            )
        else:
            self.split_btn.configure(
                text="🔀 Split View",
                fg_color=Theme.BG_SUBTLE,
            )
