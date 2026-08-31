"""
Skedari Kryesor i Ekzekutimit (main.py).
Pika hyrëse e aplikacionit Smart Ghost Clipboard.
Përmban Single-Instance Mutex, IPC Wake-Up, AppUserModelID, DPI Awareness, Global Hotkeys, dhe System Tray.
"""

import os
import sys
import socket
import threading
import ctypes
import logging

# Sigurohemi që direktoria e punës dhe sys.path të jenë saktësisht te rrënja e projektit
PROJECT_DIR: str = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Vendosja e AppUserModelID për Windows Taskbar Grouping dhe Icons
try:
    APP_USER_MODEL_ID = "Swisstech.SmartGhostClipboard.App.2.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
except Exception:
    pass

from app.config import setup_logging, APP_NAME, AI_MODEL, HOTKEY_COMBINATION
from app.ui import enable_dpi_awareness, GhostClipboardUI
from app.ai_service import AIService
from app.hotkey_listener import HotkeyListener
from app.tray import SystemTray

logger: logging.Logger = logging.getLogger(__name__)

# Konstantet për Menaxhimin e Instancës së Vetme dhe IPC në Windows
ERROR_ALREADY_EXISTS: int = 183
MUTEX_NAME: str = "Global\\SmartGhostClipboard_SingleInstance_Mutex"
IPC_PORT: int = 58291
_mutex_handle = None
_ipc_server_socket = None


def _acquire_single_instance_mutex() -> bool:
    """
    Krijon një Named Mutex në Windows për të parandaluar ekzekutimin e shumëfishtë.
    Kthen True nëse kjo është instanca e parë, False nëse tashmë po ekzekutohet.
    """
    global _mutex_handle
    try:
        kernel32 = ctypes.windll.kernel32
        _mutex_handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        last_error = kernel32.GetLastError()
        if last_error == ERROR_ALREADY_EXISTS:
            return False
        return True
    except Exception as error:
        logger.warning("Nuk u arrit krijimi i mutex-it: %s", error)
        return True


def _signal_existing_instance() -> bool:
    """
    Dërgon një sinjal 'SHOW' te instanca aktive në mënyrë që të shfaqë dritaren menjëherë.
    Kthen True nëse komunikimi me instancën aktive ishte i suksesshëm.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            s.connect(("127.0.0.1", IPC_PORT))
            s.sendall(b"SHOW\n")
            return True
    except Exception:
        return False


def _start_ipc_listener(on_show_request) -> None:
    """
    Nis një dëgjues lokal (IPC Server) në sfond që pret thirrje për shfaqjen e dritares.
    """
    global _ipc_server_socket
    try:
        _ipc_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _ipc_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _ipc_server_socket.bind(("127.0.0.1", IPC_PORT))
        _ipc_server_socket.listen(5)

        def _listen_loop():
            while True:
                try:
                    client, _ = _ipc_server_socket.accept()
                    data = client.recv(64)
                    if b"SHOW" in data:
                        on_show_request()
                    client.close()
                except Exception:
                    break

        thread = threading.Thread(target=_listen_loop, daemon=True, name="IPCListenerThread")
        thread.start()
    except Exception as error:
        logger.warning("Nuk u arrit nisja e IPC Listener: %s", error)


def _disable_console_quickedit() -> None:
    """
    Çaktivizon 'QuickEdit Mode' në konsolën e Windows.
    Në Windows, nëse përdoruesi klikon brenda dritares CMD, QuickEdit e pezullon
    (pause/freeze) menjëherë procesin derisa të shtypet Enter ose Esc.
    Ky funksion parandalon ngrirjen aksidentale.
    """
    try:
        kernel32 = ctypes.windll.kernel32
        h_stdin = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE = -10
        if h_stdin and h_stdin != -1:
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(h_stdin, ctypes.byref(mode)):
                # ENABLE_QUICK_EDIT_MODE = 0x0040, ENABLE_EXTENDED_FLAGS = 0x0080
                new_mode = (mode.value & ~0x0040) | 0x0080
                kernel32.SetConsoleMode(h_stdin, new_mode)
    except Exception:
        pass


def main() -> None:
    """
    Funksioni kryesor i nisjes së aplikacionit.
    """
    _disable_console_quickedit()
    setup_logging()

    # Kontrolli i Instancës së Vetme (Single Instance Check)
    if not _acquire_single_instance_mutex():
        logger.info("Një instancë e %s po ekzekutohet. Duke dërguar sinjalin SHOW...", APP_NAME)
        if _signal_existing_instance():
            logger.info("Sinjali SHOW u dërgua me sukses. Instanca e dytë po mbyllet.")
            sys.exit(0)

        # Nëse komunikimi me rrjet dështoi, njofto përdoruesin
        try:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"{APP_NAME} është tashmë duke punuar në sfond (System Tray)!\n\n"
                f"Shtypni [ Ctrl + Shift + V ] ose [ Ctrl + Alt + V ] për të hapur dritaren.",
                f"{APP_NAME} — Instancë Aktive",
                0x40 | 0x10000  # MB_ICONINFORMATION | MB_SETFOREGROUND
            )
        except Exception:
            pass
        sys.exit(0)

    logger.info("=" * 55)
    logger.info(" %s po niset... (Modeli: %s)", APP_NAME, AI_MODEL)
    logger.info("=" * 55)

    enable_dpi_awareness()

    try:
        ai_service = AIService()
    except ValueError as err:
        logger.critical("Gabim Konfigurimi: %s", err)
        try:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Gabim Konfigurimi:\n{err}\n\n"
                "Ju lutem plotësoni skedarin .env me çelësin tuaj të OpenAI API.",
                f"{APP_NAME} — Gabim",
                0x10  # MB_ICONERROR
            )
        except Exception:
            pass
        sys.exit(1)

    hotkey_listener: HotkeyListener = None
    tray: SystemTray = None

    def on_quit() -> None:
        """Mbyll të gjitha shërbimet e aplikacionit dhe liron mutex-in dhe portat."""
        logger.info("Duke u mbyllur %s...", APP_NAME)
        if hotkey_listener is not None:
            hotkey_listener.stop()
        if tray is not None:
            tray.stop()

        global _ipc_server_socket
        if _ipc_server_socket is not None:
            try:
                _ipc_server_socket.close()
            except Exception:
                pass
            _ipc_server_socket = None

        try:
            app.destroy()
        except Exception:
            pass

        global _mutex_handle
        if _mutex_handle is not None:
            try:
                ctypes.windll.kernel32.CloseHandle(_mutex_handle)
            except Exception:
                pass
            _mutex_handle = None

        sys.exit(0)

    # Inicializimi i dritares kryesore
    app = GhostClipboardUI(ai_service=ai_service, on_quit_callback=on_quit)

    # Dëgjuesi i sinjaleve IPC nga taskbari / shkurtoret
    _start_ipc_listener(on_show_request=lambda: app.after(0, app.show_window))

    # Dëgjuesi i shkurtoreve globale (Ctrl+Shift+V / Ctrl+Alt+V)
    hotkey_listener = HotkeyListener(
        callback=lambda: app.after(0, app.show_window)
    )
    hotkey_listener.start()

    # Ikona e System Tray
    try:
        tray = SystemTray(
            on_show_callback=lambda: app.after(0, app.show_window),
            on_quit_callback=lambda: app.after(0, on_quit),
        )
        tray.start()
    except Exception as error:
        logger.warning("Nuk u arrit nisja e System Tray: %s", error)

    print("==================================================")
    print(f" {APP_NAME} është aktiv!")
    print(f" Shtypni [ Ctrl + Shift + V ] ose [ Ctrl + Alt + V ]")
    print(f" Modeli aktiv: {AI_MODEL}")
    print("==================================================")

    # Shfaq dritaren në fillim
    app.show_window()

    # Nis event loop
    app.mainloop()


if __name__ == "__main__":
    main()


