"""
Moduli i Ikonës së Tray-it të Sistemit (tray.py).
Shfaq një ikonë në zonën e njoftimeve (System Tray / Notification Area) të Windows.
Ofron menu kontekstuale me opsione të pasura për menaxhimin e aplikacionit.
"""

import os
import threading
import logging
import subprocess
from typing import Callable, Optional

from PIL import Image, ImageDraw, ImageFont
import pystray

from app.config import APP_NAME, AI_MODEL, LOG_FILE, BASE_DIR

logger: logging.Logger = logging.getLogger(__name__)


def _create_tray_icon_image() -> Image.Image:
    """
    Gjeneron një ikonë me cilësi të lartë (supersampled 4x për antialiasing të përkryer)
    ose ngarkon ikonën ekzistuese nëse ndodhet në disk.

    Kthen:
        Image.Image: Imazhi i ikonës 64x64 RGBA.
    """
    icon_path = os.path.join(BASE_DIR, "test_icon.png")
    if os.path.isfile(icon_path):
        try:
            return Image.open(icon_path).convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)
        except Exception:
            pass

    # Krijimi i imazhit me rezolucion të lartë 256x256 dhe zvogëlimi në 64x64 (Antialiasing)
    high_res = 256
    img = Image.new("RGBA", (high_res, high_res), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rreth i thellë blu me kornizë të bardhë të butë
    draw.ellipse(
        [10, 10, high_res - 10, high_res - 10],
        fill=(24, 119, 242, 255),
        outline=(255, 255, 255, 255),
        width=12,
    )

    # Shkronja 'G' e stilizuar
    font = None
    for font_name in ["arialbd.ttf", "segoeuib.ttf", "calibrib.ttf", "arial.ttf"]:
        try:
            font = ImageFont.truetype(font_name, 140)
            break
        except (OSError, IOError):
            continue

    if font is None:
        font = ImageFont.load_default()

    text = "G"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (high_res - tw) / 2
    ty = (high_res - th) / 2 - 12
    draw.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)

    # Resample me cilësi maksimale
    return img.resize((64, 64), Image.Resampling.LANCZOS)


class SystemTray:
    """
    Menaxhon ikonën e aplikacionit në System Tray të Windows.
    Ofron funksionalitete për shfaqjen e dritares dhe mbylljen e plotë të programit.
    """

    def __init__(
        self,
        on_show_callback: Callable[[], None],
        on_quit_callback: Callable[[], None],
    ) -> None:
        """
        Inicializon ikonën e tray-it me callback-et përkatëse.
        """
        self._on_show: Callable[[], None] = on_show_callback
        self._on_quit: Callable[[], None] = on_quit_callback
        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def _handle_show(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """
        Thirret kur përdoruesi zgjedh 'Shfaq Dritaren' ose klikon mbi ikonë.
        """
        logger.info("Shfaqja e dritares u kërkua nga System Tray.")
        try:
            self._on_show()
        except Exception as error:
            logger.error("Gabim gjatë shfaqjes nga tray: %s", error, exc_info=True)

    def _handle_open_logs(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """
        Hap skedarin e log-eve me programin e paracaktuar në Windows (Notepad).
        """
        try:
            if os.path.exists(LOG_FILE):
                os.startfile(LOG_FILE)
            else:
                os.startfile(BASE_DIR)
        except Exception as error:
            logger.error("Gabim gjatë hapjes së log-eve: %s", error)

    def _handle_create_shortcut(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """
        Krijon automatikisht shkurtoren e aplikacionit në Desktop dhe Start Menu.
        """
        try:
            ps_script = os.path.join(BASE_DIR, "Create_Shortcut.ps1")
            if os.path.exists(ps_script):
                subprocess.Popen(
                    ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ps_script],
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
                )
                logger.info("Krijimi i shkurtores u ekzekutua me sukses nga Tray.")
        except Exception as error:
            logger.error("Gabim gjatë krijimit të shkurtores nga Tray: %s", error)

    def _handle_quit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """
        Thirret kur përdoruesi zgjedh 'Dil' nga menya e tray-it.
        """
        logger.info("Mbyllja e aplikacionit u kërkua nga System Tray.")
        try:
            self.stop()
        except Exception as error:
            logger.warning("Gabim gjatë ndalimit të ikonës së tray-it: %s", error)

        try:
            self._on_quit()
        except Exception as error:
            logger.error("Gabim gjatë mbylljes nga tray: %s", error, exc_info=True)

    def start(self) -> None:
        """
        Nis ikonën e tray-it në një fije të pavarur (daemon thread).
        """
        menu = pystray.Menu(
            pystray.MenuItem(
                "⚡ Shfaq Dritaren (Ctrl+Shift+V)",
                self._handle_show,
                default=True,
            ),
            pystray.MenuItem(
                f"🤖 Modeli: {AI_MODEL}",
                lambda i, it: None,
                enabled=False,
            ),
            pystray.MenuItem(
                "📌 Krijo Shkurtore në Desktop",
                self._handle_create_shortcut,
            ),
            pystray.MenuItem(
                "📂 Hape Skedarin e Log-eve",
                self._handle_open_logs,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Dil Plotësisht", self._handle_quit),
        )

        self._icon = pystray.Icon(
            name="SmartGhostClipboard",
            icon=_create_tray_icon_image(),
            title=f"{APP_NAME} ({AI_MODEL})",
            menu=menu,
        )

        def _setup_icon(icon: pystray.Icon) -> None:
            icon.visible = True
            logger.info("Ikona e System Tray është aktive dhe e dukshme.")

        def _run_icon() -> None:
            try:
                self._icon.run(setup=_setup_icon)
            except Exception as error:
                logger.error("Gabim gjatë ekzekutimit të System Tray: %s", error, exc_info=True)

        self._thread = threading.Thread(
            target=_run_icon, daemon=True, name="SystemTrayThread"
        )
        self._thread.start()

    def stop(self) -> None:
        """
        Ndalon dhe heq ikonën nga System Tray.
        """
        if self._icon is not None:
            try:
                self._icon.visible = False
                self._icon.stop()
                logger.info("Ikona e System Tray u ndalua me sukses.")
            except Exception as error:
                logger.warning("Gabim gjatë ndalimit të ikonës: %s", error)
        self._icon = None
