"""
Moduli i Sirtarit të Historikut (history_drawer.py).
Ofron panel anësor të integruar me kërkim të shpejtë, shënim të preferuarave (⭐),
kopjim të drejtpërdrejtë dhe ngarkim të teksteve të mëparshme në redaktor.
"""

from typing import Callable, List, Dict, Any, Optional
import customtkinter as ctk

from app.storage.history_store import HistoryStore
from app.ui_components.theme import Theme


class HistoryDrawer(ctk.CTkFrame):
    """
    Paneli anësor i historikut të transformimeve.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        history_store: HistoryStore,
        on_load_text: Callable[[str, str], None],
        on_copy_text: Callable[[str], None],
        on_close: Callable[[], None],
        **kwargs
    ) -> None:
        super().__init__(
            master,
            fg_color=Theme.BG_SURFACE,
            corner_radius=Theme.RADIUS_LG,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
            width=320,
            **kwargs
        )

        self.history_store = history_store
        self.on_load_text = on_load_text
        self.on_copy_text = on_copy_text
        self.on_close = on_close

        self.favorites_only: bool = False
        self.search_query: str = ""
        self.card_widgets: List[ctk.CTkFrame] = []

        self._build_ui()

    def _build_ui(self) -> None:
        # 1. Koka e Sirtarit
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=12, pady=(10, 6))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="📜 Historiku",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY,
        )
        self.title_label.pack(side="left")

        self.close_btn = ctk.CTkButton(
            self.header_frame,
            text="✕",
            font=Theme.font_button_sm(),
            width=26,
            height=26,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.DANGER,
            corner_radius=Theme.RADIUS_SM,
            command=self.on_close,
        )
        self.close_btn.pack(side="right")

        # 2. Fusha e Kërkimit
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="🔍 Kërko në historik...",
            font=Theme.font_subtitle(),
            height=30,
            corner_radius=Theme.RADIUS_MD,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_MAIN,
        )
        self.search_entry.pack(fill="x", padx=12, pady=(0, 6))
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())

        # 3. Filtrat (Të gjitha / Vetëm të Preferuarat)
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", padx=12, pady=(0, 6))

        self.all_btn = ctk.CTkButton(
            self.filter_frame,
            text="Të Gjitha",
            font=Theme.font_chip(),
            height=24,
            corner_radius=Theme.RADIUS_SM,
            fg_color=Theme.ACCENT_PRIMARY,
            command=self._show_all,
        )
        self.all_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))

        self.fav_btn = ctk.CTkButton(
            self.filter_frame,
            text="⭐ Të Preferuarat",
            font=Theme.font_chip(),
            height=24,
            corner_radius=Theme.RADIUS_SM,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.BG_SURFACE_HOVER,
            command=self._show_favorites,
        )
        self.fav_btn.pack(side="right", fill="x", expand=True, padx=(3, 0))

        # 4. Lista e Rrotullueshme e Kartave të Historikut
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=Theme.BG_INPUT,
            corner_radius=Theme.RADIUS_MD,
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        # 5. Shiriti i Poshtëm (Pastro Gjithçka)
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=12, pady=(0, 10))

        self.clear_all_btn = ctk.CTkButton(
            self.bottom_frame,
            text="🧹 Pastro Historikun",
            font=Theme.font_button_sm(),
            height=28,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.DANGER,
            corner_radius=Theme.RADIUS_MD,
            command=self._clear_all_history,
        )
        self.clear_all_btn.pack(fill="x")

    def refresh_history(self) -> None:
        """Rifreskon listën e kartave nga baza e të dhënave SQLite."""
        # Pastro kartat ekzistuese
        for card in self.card_widgets:
            card.destroy()
        self.card_widgets.clear()

        entries = self.history_store.get_entries(
            limit=50,
            search_query=self.search_query,
            favorites_only=self.favorites_only,
        )

        if not entries:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="Nuk ka regjistrime në historik.",
                font=Theme.font_subtitle(),
                text_color=Theme.TEXT_MUTED,
            )
            empty_lbl.pack(pady=20)
            self.card_widgets.append(empty_lbl)
            return

        for entry in entries:
            card = self._create_entry_card(entry)
            card.pack(fill="x", pady=4, padx=2)
            self.card_widgets.append(card)

    def _create_entry_card(self, entry: Dict[str, Any]) -> ctk.CTkFrame:
        """Ndërton një kartë vizuale për një transformim të historikut."""
        entry_id = entry["id"]
        action_name = entry["action_name"]
        timestamp = entry["timestamp"]
        original = entry["original_text"]
        transformed = entry["transformed_text"]
        is_fav = entry["is_favorite"]

        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=Theme.BG_SURFACE,
            corner_radius=Theme.RADIUS_MD,
            border_width=1,
            border_color=Theme.BORDER_MAIN,
        )

        # Rreshti 1: Action Badge + Timestamp + Favorite button
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=8, pady=(6, 2))

        badge = ctk.CTkLabel(
            top_row,
            text=action_name[:20],
            font=Theme.font_badge(),
            text_color=Theme.ACCENT_CYAN,
            fg_color=Theme.BG_SUBTLE,
            corner_radius=Theme.RADIUS_SM,
            padx=6,
            pady=2,
        )
        badge.pack(side="left")

        # Koha (ora e ditës)
        time_part = timestamp.split(" ")[1] if " " in timestamp else timestamp
        time_lbl = ctk.CTkLabel(
            top_row,
            text=time_part,
            font=Theme.font_subtitle(),
            text_color=Theme.TEXT_MUTED,
        )
        time_lbl.pack(side="left", padx=6)

        # Butoni Favorite ⭐
        fav_icon = "⭐" if is_fav else "☆"
        fav_color = Theme.WARNING if is_fav else Theme.TEXT_MUTED
        fav_btn = ctk.CTkButton(
            top_row,
            text=fav_icon,
            font=Theme.font_chip(),
            width=24,
            height=22,
            fg_color="transparent",
            hover_color=Theme.BG_SUBTLE,
            text_color=fav_color,
            command=lambda eid=entry_id: self._toggle_fav(eid),
        )
        fav_btn.pack(side="right")

        # Butoni Fshij 🗑️
        del_btn = ctk.CTkButton(
            top_row,
            text="🗑️",
            font=Theme.font_chip(),
            width=22,
            height=22,
            fg_color="transparent",
            hover_color=Theme.DANGER,
            command=lambda eid=entry_id: self._delete_entry(eid),
        )
        del_btn.pack(side="right", padx=(0, 2))

        # Rreshti 2: Parashikim i tekstit të transformuar
        preview_text = transformed[:120] + ("..." if len(transformed) > 120 else "")
        preview_lbl = ctk.CTkLabel(
            card,
            text=preview_text,
            font=Theme.font_subtitle(),
            text_color=Theme.TEXT_PRIMARY,
            wraplength=260,
            justify="left",
        )
        preview_lbl.pack(fill="x", padx=8, pady=4)

        # Rreshti 3: Butonat e veprimit (Kopjo dhe Ngarko)
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=(2, 6))

        load_btn = ctk.CTkButton(
            btn_row,
            text="↩️ Ngarko",
            font=Theme.font_button_sm(),
            height=24,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.ACCENT_PRIMARY,
            corner_radius=Theme.RADIUS_SM,
            command=lambda o=original, t=transformed: self.on_load_text(o, t),
        )
        load_btn.pack(side="left", expand=True, fill="x", padx=(0, 3))

        copy_btn = ctk.CTkButton(
            btn_row,
            text="📋 Kopjo",
            font=Theme.font_button_sm(),
            height=24,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.SUCCESS,
            corner_radius=Theme.RADIUS_SM,
            command=lambda t=transformed: self.on_copy_text(t),
        )
        copy_btn.pack(side="right", expand=True, fill="x", padx=(3, 0))

        return card

    def _toggle_fav(self, entry_id: int) -> None:
        self.history_store.toggle_favorite(entry_id)
        self.refresh_history()

    def _delete_entry(self, entry_id: int) -> None:
        self.history_store.delete_entry(entry_id)
        self.refresh_history()

    def _clear_all_history(self) -> None:
        self.history_store.clear_all()
        self.refresh_history()

    def _show_all(self) -> None:
        self.favorites_only = False
        self.all_btn.configure(fg_color=Theme.ACCENT_PRIMARY)
        self.fav_btn.configure(fg_color=Theme.BG_SUBTLE)
        self.refresh_history()

    def _show_favorites(self) -> None:
        self.favorites_only = True
        self.fav_btn.configure(fg_color=Theme.ACCENT_PRIMARY)
        self.all_btn.configure(fg_color=Theme.BG_SUBTLE)
        self.refresh_history()

    def _on_search_change(self) -> None:
        self.search_query = self.search_entry.get().strip()
        self.refresh_history()
