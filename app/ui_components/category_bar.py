"""
Moduli i Shiritit të Kategorive dhe Veprimeve të Shpejta (category_bar.py).
Ofron navigim me tab-e midis kategorive (Shkrim, Biznes, Përkthim, Përmbledhje, Kod)
dhe përditëson në mënyrë reaktive 5 butonat e veprimeve të lidhura me shkurtoret [1..5].
"""

from typing import Callable, Dict, List, Tuple, Any
import customtkinter as ctk

from app.config import ACTION_CATEGORIES
from app.ui_components.theme import Theme


class CategoryBar(ctk.CTkFrame):
    """
    Paneli i kategorive dhe veprimeve të shpejta të AI.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_action_selected: Callable[[str], None],
        **kwargs
    ) -> None:
        super().__init__(
            master,
            fg_color=Theme.BG_SURFACE,
            corner_radius=Theme.RADIUS_LG,
            border_width=1,
            border_color=Theme.BORDER_MAIN,
            **kwargs
        )

        self.on_action_selected = on_action_selected
        self.active_category: str = "writing"
        self.tab_buttons: Dict[str, ctk.CTkButton] = {}
        self.action_buttons: List[ctk.CTkButton] = []
        self.current_action_keys: List[str] = []

        self._build_ui()

    def _build_ui(self) -> None:
        # 1. Rreshti i Tab-eve të Kategorive
        self.tabs_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tabs_container.pack(fill="x", padx=8, pady=(8, 4))

        for cat_key, cat_data in ACTION_CATEGORIES.items():
            tab_btn = ctk.CTkButton(
                self.tabs_container,
                text=cat_data["title"],
                font=Theme.font_tab(),
                height=30,
                corner_radius=Theme.RADIUS_MD,
                fg_color=Theme.ACCENT_PRIMARY if cat_key == self.active_category else Theme.BG_SUBTLE,
                hover_color=Theme.ACCENT_PRIMARY_HOVER if cat_key == self.active_category else Theme.BG_SURFACE_HOVER,
                text_color=Theme.TEXT_PRIMARY,
                command=lambda k=cat_key: self.select_category(k),
            )
            tab_btn.pack(side="left", padx=3, expand=True, fill="x")
            self.tab_buttons[cat_key] = tab_btn

        # 2. Rreshti i Butonave të Veprimit [1..5]
        self.actions_container = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_container.pack(fill="x", padx=8, pady=(2, 8))

        self._render_action_buttons()

    def select_category(self, category_key: str) -> None:
        """Ndryshon kategorinë aktive dhe rifreskon butonat e veprimit."""
        if category_key not in ACTION_CATEGORIES:
            return

        self.active_category = category_key

        # Përditëson ngjyrat e tab-eve
        for key, btn in self.tab_buttons.items():
            if key == category_key:
                btn.configure(
                    fg_color=Theme.ACCENT_PRIMARY,
                    hover_color=Theme.ACCENT_PRIMARY_HOVER,
                )
            else:
                btn.configure(
                    fg_color=Theme.BG_SUBTLE,
                    hover_color=Theme.BG_SURFACE_HOVER,
                )

        self._render_action_buttons()

    def _render_action_buttons(self) -> None:
        """Krijon 5 butonat e veprimit për kategorinë e zgjedhur."""
        # Pastro butonat ekzistues
        for btn in self.action_buttons:
            btn.destroy()
        self.action_buttons.clear()
        self.current_action_keys.clear()

        cat_info = ACTION_CATEGORIES.get(self.active_category, {})
        actions = cat_info.get("actions", [])

        for idx, (label, action_key, tooltip) in enumerate(actions, start=1):
            self.current_action_keys.append(action_key)
            btn = ctk.CTkButton(
                self.actions_container,
                text=label,
                font=Theme.font_button(),
                height=34,
                corner_radius=Theme.RADIUS_MD,
                fg_color=Theme.BG_INPUT,
                hover_color=Theme.ACCENT_SECONDARY,
                border_width=1,
                border_color=Theme.BORDER_LIGHT,
                command=lambda k=action_key: self.on_action_selected(k),
            )
            btn.pack(side="left", padx=3, expand=True, fill="x")
            self.action_buttons.append(btn)

    def trigger_action_by_index(self, index_1_based: int) -> bool:
        """Thërret veprimin e paracaktuar me shkurtoret e tastierës (1..5)."""
        idx = index_1_based - 1
        if 0 <= idx < len(self.current_action_keys):
            action_key = self.current_action_keys[idx]
            self.on_action_selected(action_key)
            return True
        return False

    def set_enabled(self, enabled: bool) -> None:
        """Aktivizon ose çaktivizon të gjithë butonat gjatë përpunimit."""
        state = "normal" if enabled else "disabled"
        for btn in self.tab_buttons.values():
            btn.configure(state=state)
        for btn in self.action_buttons:
            btn.configure(state=state)
