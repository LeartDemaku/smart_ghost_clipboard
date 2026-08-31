"""
Moduli i Pamjes së Redaktorit (editor_view.py).
Ofron mbështetje për Single Mode dhe Dual Split Mode (krah për krah me tekstin origjinal dhe AI),
shkrim Streaming në kohë reale me kursor animimi, dhe integrim me theksimin e ndryshimeve (Diff).
"""

from typing import Callable, Optional
import customtkinter as ctk

from app.ui_components.theme import Theme
from app.ui_components.diff_highlighter import DiffHighlighter


class EditorView(ctk.CTkFrame):
    """
    Komponenti kryesor i redaktimit me mbështetje për Single dhe Split View.
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_text_changed: Optional[Callable[[], None]] = None,
        **kwargs
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.on_text_changed = on_text_changed
        self._is_split: bool = False
        self._is_streaming: bool = False
        self._original_content: str = ""
        self._result_content: str = ""

        self._build_ui()

    def _build_ui(self) -> None:
        # Kontejneri kryesor i redaktimit (Grid layout për të mbështetur 1 ose 2 kolona)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ─── 1. Paneli i Majtë (Origjinali në Split Mode) ───
        self.left_pane = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_SURFACE,
            corner_radius=Theme.RADIUS_LG,
            border_width=1,
            border_color=Theme.BORDER_MAIN,
        )

        self.left_header = ctk.CTkFrame(self.left_pane, fg_color="transparent", height=28)
        self.left_header.pack(fill="x", padx=10, pady=(6, 2))

        self.left_title = ctk.CTkLabel(
            self.left_header,
            text="📋 TEKSTI ORIGJINAL (CLIPBOARD)",
            font=Theme.font_button_sm(),
            text_color=Theme.TEXT_SECONDARY,
        )
        self.left_title.pack(side="left")

        self.original_textbox = ctk.CTkTextbox(
            self.left_pane,
            font=Theme.font_editor(),
            wrap="word",
            fg_color=Theme.BG_INPUT,
            border_width=0,
            text_color=Theme.TEXT_PRIMARY,
        )
        self.original_textbox.pack(fill="both", expand=True, padx=8, pady=(2, 8))
        self.original_textbox.bind("<KeyRelease>", lambda e: self._notify_change())
        self.original_textbox.bind("<ButtonRelease>", lambda e: self._notify_change())

        # ─── 2. Paneli Kryesor / i Djathtë (Rezultati me AI) ───
        self.right_pane = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_SURFACE,
            corner_radius=Theme.RADIUS_LG,
            border_width=1,
            border_color=Theme.BORDER_MAIN,
        )

        self.right_header = ctk.CTkFrame(self.right_pane, fg_color="transparent", height=28)
        self.right_header.pack(fill="x", padx=10, pady=(6, 2))

        self.right_title = ctk.CTkLabel(
            self.right_header,
            text="🤖 REZULTATI I TRANSFORMUAR ME AI",
            font=Theme.font_button_sm(),
            text_color=Theme.TEXT_ACCENT,
        )
        self.right_title.pack(side="left")

        self.diff_btn = ctk.CTkButton(
            self.right_header,
            text="🔍 Thekso Ndryshimet",
            font=Theme.font_chip(),
            height=22,
            width=130,
            fg_color=Theme.BG_SUBTLE,
            hover_color=Theme.BG_SURFACE_HOVER,
            corner_radius=Theme.RADIUS_SM,
            command=self.toggle_diff_highlight,
        )
        # diff_btn do të shfaqet vetëm në Split Mode

        self.main_textbox = ctk.CTkTextbox(
            self.right_pane,
            font=Theme.font_editor(),
            wrap="word",
            fg_color=Theme.BG_INPUT,
            border_width=0,
            text_color=Theme.TEXT_PRIMARY,
        )
        self.main_textbox.pack(fill="both", expand=True, padx=8, pady=(2, 8))
        self.main_textbox.bind("<KeyRelease>", lambda e: self._notify_change())
        self.main_textbox.bind("<ButtonRelease>", lambda e: self._notify_change())

        # Në fillim nis në Single Mode (vetëm main_textbox)
        self._apply_layout()

    def _apply_layout(self) -> None:
        """Vendos pamjen sipas modalitetit Single ose Split."""
        if self._is_split:
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

            self.left_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=0)
            self.right_pane.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=0)

            self.left_title.configure(text="📋 TEKSTI ORIGJINAL")
            self.right_title.configure(text="🤖 REZULTATI ME AI")
            self.diff_btn.pack(side="right")
        else:
            self.left_pane.grid_forget()
            self.grid_columnconfigure(1, weight=0)
            self.grid_columnconfigure(0, weight=1)

            self.right_pane.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            self.right_title.configure(text="📝 REDAKTORI KRYESOR (CLIPBOARD & AI)")
            self.diff_btn.pack_forget()

    def toggle_split_view(self) -> bool:
        """Ndryshon modalitetin mes Single dhe Split View."""
        self._is_split = not self._is_split
        if self._is_split:
            # Sigurohemi që teksti origjinal është i pranishëm në të majtë
            curr_main = self.main_textbox.get("1.0", "end-1c")
            if not self._original_content:
                self._original_content = curr_main
            self.original_textbox.delete("1.0", "end")
            self.original_textbox.insert("1.0", self._original_content)

        self._apply_layout()
        return self._is_split

    def is_split(self) -> bool:
        return self._is_split

    def _notify_change(self) -> None:
        if self.on_text_changed:
            self.on_text_changed()

    def get_active_text(self) -> str:
        """Merr tekstin që duhet përpunuar nga AI ose kopjuar."""
        if self._is_split:
            # Në split mode, nëse fusha origjinale ka tekst, merre nga origjinali
            orig = self.original_textbox.get("1.0", "end-1c").strip()
            if orig:
                return orig
        return self.main_textbox.get("1.0", "end-1c").strip()

    def get_result_text(self) -> str:
        """Merr tekstin e fushës së rezultatit."""
        return self.main_textbox.get("1.0", "end-1c").strip()

    def set_content_from_clipboard(self, text: str) -> None:
        """Ngarkon tekstin e sapomarrë nga clipboard."""
        self._original_content = text
        self._result_content = text

        self.main_textbox.delete("1.0", "end")
        if text:
            self.main_textbox.insert("1.0", text)

        self.original_textbox.delete("1.0", "end")
        if text:
            self.original_textbox.insert("1.0", text)

        self._notify_change()

    def start_streaming(self) -> None:
        """Përgatit fushën për shfaqjen e përgjigjes streaming."""
        # Ruaj tekstin aktual si origjinal para se të rishkruhet rezultati
        curr = self.main_textbox.get("1.0", "end-1c").strip()
        if curr and not self._original_content:
            self._original_content = curr
            self.original_textbox.delete("1.0", "end")
            self.original_textbox.insert("1.0", curr)

        self.main_textbox.delete("1.0", "end")
        self._is_streaming = True

    def append_chunk(self, chunk: str) -> None:
        """Shton një pjesëz teksti në kohë reale me lëvizje automatike në fund."""
        self.main_textbox.insert("end", chunk)
        self.main_textbox.see("end")

    def finish_streaming(self, full_text: str) -> None:
        """Përfundon streaming dhe vendos tekstin përfundimtar."""
        self._is_streaming = False
        self._result_content = full_text
        self.main_textbox.delete("1.0", "end")
        self.main_textbox.insert("1.0", full_text)
        self._notify_change()

    def set_error_message(self, error_message: str) -> None:
        """Shfaq një mesazh gabimi në fushën e tekstit."""
        self._is_streaming = False
        self.main_textbox.delete("1.0", "end")
        self.main_textbox.insert("1.0", error_message)
        self._notify_change()

    def toggle_diff_highlight(self) -> None:
        """Thekson ndryshimet vizuale mes tekstit origjinal dhe rezultatit."""
        orig = self.original_textbox.get("1.0", "end-1c")
        result = self.main_textbox.get("1.0", "end-1c")
        if orig and result:
            DiffHighlighter.apply_diff(self.main_textbox, orig, result)

    def clear(self) -> None:
        """Pastron të gjitha fushat e redaktimit."""
        self._original_content = ""
        self._result_content = ""
        self.main_textbox.delete("1.0", "end")
        self.original_textbox.delete("1.0", "end")
        self._notify_change()

    def focus_editor(self) -> None:
        """Vendos fokusin e kursorit në fushën kryesore."""
        self.main_textbox.focus_set()
