"""
Moduli Kryesor i Ndërfaqes Grafike (ui.py).
Orkestron të gjithë komponentët: Koka, Kategoritë, Chips, Redaktori me Single/Split View,
Sirtari i Historikut me SQLite, dhe Shiriti i Statusit.
Ofron mbështetje për High-DPI, fokus të forcuar në nivel Windows API, Streaming në kohë reale,
dhe Auto-Paste në dritaren aktive.
"""

import os
import ctypes
import threading
import logging
from typing import Callable, Optional, List

from PIL import Image, ImageTk
import customtkinter as ctk

from app.config import (
    APP_NAME,
    AI_MODEL,
    BASE_DIR,
    ACTION_CATEGORIES,
)
from app.storage.history_store import HistoryStore
from app.clipboard_manager import ClipboardManager
from app.ai_service import AIService
from app.tray import _create_tray_icon_image

from app.ui_components.theme import Theme
from app.ui_components.header import HeaderBar
from app.ui_components.category_bar import CategoryBar
from app.ui_components.prompt_chips import PromptChipsBar
from app.ui_components.editor_view import EditorView
from app.ui_components.history_drawer import HistoryDrawer
from app.ui_components.status_bar import StatusBar

logger: logging.Logger = logging.getLogger(__name__)

# Konfigurimi global vizual i CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def enable_dpi_awareness() -> None:
    """
    Aktivizon njohjen e DPI-t (DPI Awareness) në Windows para krijimit të dritares Tkinter.
    """
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor DPI Aware V2
        logger.info("DPI Awareness u aktivizua: Per-Monitor V2.")
        return
    except Exception:
        pass

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # System DPI Aware
        logger.info("DPI Awareness u aktivizua: System Aware.")
        return
    except Exception:
        pass

    try:
        ctypes.windll.user32.SetProcessDPIAware()
        logger.info("DPI Awareness u aktivizua: Legacy.")
    except Exception:
        logger.warning("Nuk u arrit aktivizimi i DPI Awareness.")


class GhostClipboardUI(ctk.CTk):
    """
    Dritarja kryesore lundruese dhe ultra-responsive e Smart Ghost Clipboard v2.0.
    """

    def __init__(
        self,
        ai_service: AIService,
        on_quit_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__()
        self.configure(fg_color=Theme.BG_MAIN)

        self.ai_service: AIService = ai_service
        self.clipboard_mgr: ClipboardManager = ClipboardManager()
        self.history_store: HistoryStore = HistoryStore()
        self._on_quit_callback: Optional[Callable[[], None]] = on_quit_callback

        self._is_busy: bool = False
        self._icon_photo: Optional[ImageTk.PhotoImage] = None
        self._history_open: bool = False

        # Dimensionet e dritares
        self.base_width: int = 740
        self.base_height: int = 600
        self.split_width: int = 980
        self.history_drawer_width: int = 320

        # Konfigurimet bazë të dritares
        self.title(f"{APP_NAME} v2.0 — ({AI_MODEL})")
        self.geometry(f"{self.base_width}x{self.base_height}")
        self.minsize(640, 520)
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        # Vendosja e ikonës
        self._set_window_icon()

        # Ndërtimi i hierarkisë vizuale
        self._build_layout()
        self._bind_keyboard_shortcuts()
        self._center_window(self.base_width, self.base_height)

        logger.info("Ndërfaqja grafike v2.0 u inicializua me sukses.")

    def _set_window_icon(self) -> None:
        """Vendos ikonën e dritares dhe të Taskbar."""
        try:
            ico_path = os.path.join(BASE_DIR, "app_icon.ico")
            if os.path.isfile(ico_path):
                self.iconbitmap(ico_path)
        except Exception as error:
            logger.debug("Nuk u arrit vendosja e iconbitmap: %s", error)

        try:
            icon_img = _create_tray_icon_image()
            self._icon_photo = ImageTk.PhotoImage(icon_img)
            self.iconphoto(False, self._icon_photo)
        except Exception as error:
            logger.warning("Nuk u arrit vendosja e ikonës: %s", error)

    def _center_window(self, width: int, height: int) -> None:
        """Pozicionon dritaren saktësisht në qendër të ekranit."""
        try:
            self.update_idletasks()
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            pos_x = max(0, int((screen_width - width) / 2))
            pos_y = max(0, int((screen_height - height) / 2))
            self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        except Exception as error:
            logger.warning("Nuk u arrit qendërzimi: %s", error)

    def _force_foreground(self) -> None:
        """Forcon fokusin në Windows duke përdorur Windows API."""
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            hwnd = user32.GetAncestor(self.winfo_id(), 2) or user32.GetParent(self.winfo_id()) or self.winfo_id()
            fore_hwnd = user32.GetForegroundWindow()

            if fore_hwnd != hwnd:
                fore_thread = user32.GetWindowThreadProcessId(fore_hwnd, None)
                app_thread = kernel32.GetCurrentThreadId()

                user32.AttachThreadInput(fore_thread, app_thread, True)
                user32.keybd_event(0x12, 0, 0, 0)       # ALT Down
                user32.SetForegroundWindow(hwnd)
                user32.BringWindowToTop(hwnd)
                user32.ShowWindow(hwnd, 9)              # SW_RESTORE
                user32.keybd_event(0x12, 0, 0x0002, 0)  # ALT Up
                user32.AttachThreadInput(fore_thread, app_thread, False)
            else:
                user32.SetForegroundWindow(hwnd)
                user32.BringWindowToTop(hwnd)
        except Exception as error:
            logger.debug("Windows API focus info: %s", error)

        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()
        self.after(60, self.editor_view.focus_editor)

    def _build_layout(self) -> None:
        """Krijon strukturën kryesore të elementeve grafike."""
        # Kontejneri i jashtëm kryesor
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=12, pady=10)

        # 1. Shiriti i Kokës (Header)
        self.header_bar = HeaderBar(
            self.main_container,
            on_toggle_split_view=self.toggle_split_view,
            on_toggle_history=self.toggle_history_drawer,
            on_hide_window=self.hide_window,
        )
        self.header_bar.pack(fill="x", pady=(0, 8))

        # 2. Shiriti i Kategorive dhe Veprimeve të Shpejta
        self.category_bar = CategoryBar(
            self.main_container,
            on_action_selected=self.trigger_preset_action,
        )
        self.category_bar.pack(fill="x", pady=(0, 6))

        # 3. Shiriti i Modifikuesve të Shpejtë (Prompt Chips & Custom Entry)
        self.prompt_chips = PromptChipsBar(
            self.main_container,
            on_execute_instruction=self.trigger_custom_instruction,
        )
        self.prompt_chips.pack(fill="x", pady=(0, 6))

        # 4. Zona Qendrore e Përmbajtjes (Redaktori + Sirtari i Historikut)
        self.center_content = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.center_content.pack(fill="both", expand=True, pady=(0, 6))

        # Redaktori me Single/Split View
        self.editor_view = EditorView(
            self.center_content,
            on_text_changed=self._update_text_stats,
        )
        self.editor_view.pack(side="left", fill="both", expand=True)

        # Sirtari i Historikut (fillimisht i fshehur)
        self.history_drawer = HistoryDrawer(
            self.center_content,
            history_store=self.history_store,
            on_load_text=self._load_from_history,
            on_copy_text=self._copy_history_text,
            on_close=self.toggle_history_drawer,
        )
        # history_drawer pack_forget() në fillim

        # 5. Shiriti i Poshtëm i Statusit dhe Veprimeve
        self.status_bar = StatusBar(
            self.main_container,
            on_clear=self.clear_text,
            on_reload=self.reload_from_clipboard,
            on_copy=self.copy_result,
            on_paste_replace=self.copy_and_paste_replace,
            on_quit=self.quit_app,
        )
        self.status_bar.pack(fill="x")

    def _bind_keyboard_shortcuts(self) -> None:
        """Regjistron shkurtoret e tastierës brenda dritares."""
        # 1..5 për veprimet e kategorisë aktive
        for idx in range(1, 6):
            self.bind(f"<Alt-Key-{idx}>", lambda e, i=idx: self.category_bar.trigger_action_by_index(i))
            self.bind(f"<Control-Key-{idx}>", lambda e, i=idx: self.category_bar.trigger_action_by_index(i))

        # Ndërrimi i kategorive me shigjeta
        self.bind("<Control-Tab>", lambda e: self._cycle_category(1))
        self.bind("<Control-Shift-Tab>", lambda e: self._cycle_category(-1))

        # Veprimet kryesore
        self.bind("<F5>", lambda e: self.reload_from_clipboard())
        self.bind("<Control-r>", lambda e: self.reload_from_clipboard())
        self.bind("<Control-R>", lambda e: self.reload_from_clipboard())
        self.bind("<Control-Shift-C>", lambda e: self.copy_result())
        self.bind("<Control-Shift-c>", lambda e: self.copy_result())
        self.bind("<Control-k>", lambda e: self.copy_result())
        self.bind("<Control-l>", lambda e: self.clear_text())
        self.bind("<Control-h>", lambda e: self.toggle_history_drawer())
        self.bind("<Control-d>", lambda e: self.toggle_split_view())
        self.bind("<Control-Return>", lambda e: self.copy_and_paste_replace())
        self.bind("<Escape>", lambda e: self.hide_window())

    def _cycle_category(self, step: int) -> None:
        """Kalim te kategoria tjetër me shkurtore tastiere."""
        cat_keys = list(ACTION_CATEGORIES.keys())
        curr_idx = cat_keys.index(self.category_bar.active_category) if self.category_bar.active_category in cat_keys else 0
        next_idx = (curr_idx + step) % len(cat_keys)
        self.category_bar.select_category(cat_keys[next_idx])

    def _update_text_stats(self) -> None:
        """Përditëson statistikat e tekstit në kohë reale."""
        text = self.editor_view.get_active_text()
        self.status_bar.update_stats(text)

    def show_window(self) -> None:
        """Shfaq dritaren duke ngarkuar tekstin aktual nga clipboard."""
        if not self._is_busy:
            current_text = self.clipboard_mgr.get_text()
            self.editor_view.set_content_from_clipboard(current_text)
            if current_text:
                self.status_bar.set_status("Teksti u ngarkua nga Clipboard.", Theme.TEXT_SECONDARY)
            else:
                self.status_bar.set_status("Clipboard është bosh ose pa tekst.", Theme.WARNING)
            self._update_text_stats()

        self.deiconify()
        self._force_foreground()
        logger.info("Dritarja u shfaq në ekran.")

    def hide_window(self) -> None:
        """Fsheh dritaren në sfond (mbetet aktive në System Tray)."""
        self.withdraw()
        logger.info("Dritarja u fsheh.")

    def toggle_split_view(self) -> None:
        """Aktivizon ose çaktivizon pamjen e ndarë krah për krah (Split View)."""
        is_split = self.editor_view.toggle_split_view()
        self.header_bar.set_split_active(is_split)

        curr_w = self.winfo_width()
        curr_h = self.winfo_height()

        if is_split and curr_w < self.split_width:
            self._center_window(self.split_width, max(curr_h, 620))
        elif not is_split and curr_w >= self.split_width and not self._history_open:
            self._center_window(self.base_width, curr_h)

    def toggle_history_drawer(self) -> None:
        """Shfaq ose fsheh panelin anësor të historikut."""
        self._history_open = not self._history_open
        if self._history_open:
            self.history_drawer.refresh_history()
            self.history_drawer.pack(side="right", fill="y", padx=(6, 0))
            curr_w = self.winfo_width()
            curr_h = self.winfo_height()
            if curr_w < 900:
                self._center_window(min(curr_w + self.history_drawer_width, 1040), curr_h)
        else:
            self.history_drawer.pack_forget()

    def _load_from_history(self, original_text: str, transformed_text: str) -> None:
        """Ngarkon një regjistrim të historikut direkt në redaktor."""
        self.editor_view.set_content_from_clipboard(original_text)
        self.editor_view.finish_streaming(transformed_text)
        self.status_bar.set_status("U ngarkua nga historiku.", Theme.SUCCESS)

    def _copy_history_text(self, text: str) -> None:
        """Kopjon tekstin nga një kartë e historikut."""
        if self.clipboard_mgr.set_text(text):
            self.status_bar.set_status("Teksti nga historiku u kopjua!", Theme.SUCCESS)

    def clear_text(self) -> None:
        """Pastron tekstin në redaktor."""
        if not self._is_busy:
            self.editor_view.clear()
            self.status_bar.set_status("Teksti u pastrua.", Theme.TEXT_MUTED)

    def reload_from_clipboard(self) -> None:
        """Rifreskon përmbajtjen nga kujtesa e përkohshme."""
        if not self._is_busy:
            text = self.clipboard_mgr.get_text()
            self.editor_view.set_content_from_clipboard(text)
            if text:
                self.status_bar.set_status("Teksti u rifreskua nga Clipboard.", Theme.SUCCESS)
            else:
                self.status_bar.set_status("Clipboard është bosh.", Theme.WARNING)

    def trigger_preset_action(self, action_key: str) -> None:
        """Nis përpunimin e një veprimi të paracaktuar."""
        user_text = self.editor_view.get_active_text()
        if not user_text:
            self.status_bar.set_status("Kujdes: Nuk ka tekst për t'u përpunuar!", Theme.WARNING)
            return

        self._start_ai_processing(action_key=action_key, user_text=user_text, custom_instruction=None)

    def trigger_custom_instruction(self, instruction: str) -> None:
        """Nis përpunimin me një udhëzim të personalizuar ose chip."""
        user_text = self.editor_view.get_active_text()
        if not user_text:
            self.status_bar.set_status("Kujdes: Nuk ka tekst për t'u përpunuar!", Theme.WARNING)
            return

        self._start_ai_processing(action_key=None, user_text=user_text, custom_instruction=instruction)

    def _start_ai_processing(
        self,
        action_key: Optional[str],
        user_text: str,
        custom_instruction: Optional[str],
    ) -> None:
        """Fillon ekzekutimin në sfond me Streaming në kohë reale."""
        if self._is_busy:
            return

        self._is_busy = True
        self.set_loading(True)
        self.header_bar.set_latency_busy()
        self.editor_view.start_streaming()

        threading.Thread(
            target=self._run_streaming_task,
            args=(action_key, user_text, custom_instruction),
            daemon=True,
            name="StreamingWorkerThread",
        ).start()

    def _run_streaming_task(
        self,
        action_key: Optional[str],
        user_text: str,
        custom_instruction: Optional[str],
    ) -> None:
        """Puna në thread-in e pavarur duke përdorur callbacks."""
        action_title = custom_instruction[:30] if custom_instruction else (action_key or "AI Action")

        def on_chunk(chunk: str) -> None:
            self.after(0, self.editor_view.append_chunk, chunk)

        def on_complete(full_text: str, elapsed: float) -> None:
            # Ruaj në bazën e të dhënave të historikut
            latency_ms = int(elapsed * 1000)
            self.history_store.add_entry(
                action_name=action_title,
                original_text=user_text,
                transformed_text=full_text,
                latency_ms=latency_ms,
            )
            self.after(0, self._handle_stream_success, full_text, elapsed)

        def on_error(err_msg: str) -> None:
            self.after(0, self._handle_stream_error, err_msg)

        self.ai_service.transform_text_stream(
            action_key=action_key,
            user_text=user_text,
            custom_instruction=custom_instruction,
            on_chunk=on_chunk,
            on_complete=on_complete,
            on_error=on_error,
        )

    def _handle_stream_success(self, full_text: str, elapsed: float) -> None:
        """Përfundim me sukses i transformimit të tekstit."""
        self._is_busy = False
        self.set_loading(False)
        self.editor_view.finish_streaming(full_text)
        self.header_bar.update_latency(elapsed)
        self.status_bar.set_status(f"Përfunduar në {elapsed:.2f}s me {AI_MODEL}!", Theme.SUCCESS)

        if self._history_open:
            self.history_drawer.refresh_history()

    def _handle_stream_error(self, err_msg: str) -> None:
        """Trajtimi i gabimeve gjatë streaming."""
        self._is_busy = False
        self.set_loading(False)
        self.editor_view.set_error_message(err_msg)
        self.status_bar.set_status("Ndodhi një gabim gjatë përpunimit.", Theme.DANGER)

    def set_loading(self, is_loading: bool) -> None:
        """Ndryshon gjendjen e kontrolleve gjatë ngarkimit."""
        enabled = not is_loading
        self.category_bar.set_enabled(enabled)
        self.prompt_chips.set_enabled(enabled)
        self.status_bar.set_enabled(enabled)
        if is_loading:
            self.status_bar.set_status(f"⚡ Duke u shkruar në kohë reale me {AI_MODEL}...", Theme.ACCENT_CYAN)

    def copy_result(self) -> None:
        """Kopjon tekstin e rezultatit në Clipboard."""
        output_text = self.editor_view.get_result_text()
        if output_text:
            success = self.clipboard_mgr.set_text(output_text)
            if success:
                self.status_bar.show_copy_feedback()
            else:
                self.status_bar.set_status("Gabim: Nuk u arrit kopjimi!", Theme.DANGER)
        else:
            self.status_bar.set_status("Nuk ka tekst për t'u kopjuar!", Theme.WARNING)

    def copy_and_paste_replace(self) -> None:
        """Kopjon rezultatin, fsheh dritaren dhe e ngjit automatikisht në aplikacionin aktiv."""
        output_text = self.editor_view.get_result_text()
        if not output_text:
            self.status_bar.set_status("Nuk ka tekst për zëvendësim!", Theme.WARNING)
            return

        # Fsheh dritaren menjëherë që fokusi të kthehet te aplikacioni i mëparshëm
        self.hide_window()

        # Ekzekutohet në thread të shpejtë për të lejuar fokusimin e plotë të dritares së mëparshme
        def _do_paste() -> None:
            import time
            time.sleep(0.15)
            self.clipboard_mgr.paste_to_active_app(output_text)

        threading.Thread(target=_do_paste, daemon=True, name="AutoPasteWorker").start()

    def quit_app(self) -> None:
        """Mbyll përfundimisht aplikacionin dhe liron të gjitha burimet."""
        logger.info("Mbyllja e aplikacionit u kërkua nga përdoruesi.")
        if self._on_quit_callback:
            try:
                self._on_quit_callback()
            except Exception as error:
                logger.error("Gabim në quit callback: %s", error)
        try:
            self.destroy()
        except Exception:
            pass
