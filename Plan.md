# Smart Ghost Clipboard — Plani i Plotë i Zhvillimit (v1.1.0)

Ky dokument përmban planin arkitekturor dhe udhëzuesin hap pas hapi nga e para (*from scratch*) për ndërtimin e aplikacionit **Smart Ghost Clipboard** në Windows duke përdorur **Python**, **CustomTkinter** dhe modelin **`gpt-5.4-nano`** të OpenAI.

> **Versioni 1.1.0** — Përditësimi kryesor me përmirësime specifike për Windows: DPI Awareness, System Tray, Single Instance Mutex, Forcim i Fokusit me Windows API, Logim i Strukturuar, Siguri Thread-i dhe Mbyllje e Pastër.

---

## 1. Arkitektura & Mekanizmi i Funksionimit

```
[ Tastiera: Shtypet Ctrl + Shift + V ]
                 │
                 ▼
     [ Global Hotkey Listener ] (Pynput - Thread në Sfond)
                 │
                 ▼
      [ Clipboard Manager ] ── Lexon tekstin e kopjuar (me retry logjikë)
                 │
                 ▼
       [ UI Launcher ] ────── Shfaq dritaren lundruese (DPI Aware + Fokus i Forcuar)
                 │
                 ▼
      [ OpenAI Service ] ──── Dërgon kërkesën te model: "gpt-5.4-nano" (Thread i pavarur)
                 │
                 ▼
      [ Rezultati në UI ] ── Përdoruesi e kopjon ose e zëvendëson menjëherë

      [ System Tray ] ─────── Ikonë në zonën e njoftimeve (Shfaq / Dil)
```

### Karakteristikat Kryesore Teknike

1. **Modeli AI:** Përdoret modeli **`gpt-5.4-nano`**. Ky model është i optimizuar për shpejtësi ekstreme (latencë nën-sekondëshe) dhe efikasitet kostoje, duke qenë zgjedhja ideale për transformime të menjëhershme teksti.
2. **UI Moderne & E Lehtë:** Ndërtuar me `customtkinter` me mbështetje native për Dark Mode në Windows.
3. **DPI Awareness:** Aktivizimi i Per-Monitor DPI Awareness v2 përmes Windows API (`shcore.SetProcessDpiAwareness`) para inicializimit të Tkinter, duke siguruar pamje të pastër në ekrane me shkallëzim 125%, 150% dhe 200%.
4. **Multithreading pa Ngrirje (Thread Safety):** Thirrjet e rrjetit në OpenAI API ekzekutohen në fije paralele (`threading.Thread`), me flagë `_is_busy` që parandalon kërkesat paralele nga klikime të shpejta.
5. **Dëgjues Global i Shkurtoreve (Global Hotkeys):** Përdor bibliotekën `pynput` për të kapur kombinimin `Ctrl + Shift + V` në çdo vend të Windows pa kërkuar të drejta administratori.
6. **System Tray:** Ikonë në zonën e njoftimeve të Windows me meny kontekstuale (Shfaq Dritaren / Dil), e domosdoshme kur dritarja fshihet.
7. **Instancë e Vetme (Single Instance):** Mutex i emërtuar në Windows parandalon ekzekutimin e shumëfishtë të aplikacionit.
8. **Fokus i Forcuar (Windows Foreground):** Përdor trukun e tastit ALT + `SetForegroundWindow` API për të kaluar politikën restriktive të Windows për fokusin e dritareve.
9. **Logim i Strukturuar:** Modulin `logging` të Python me shkrim në skedar dhe konsolë, i dobishëm për diagnostikim kur ekzekutohet si `.exe` pa konsolë.
10. **Rezistencë e Clipboard-it:** Logjikë retry me 3 tentativa dhe vonesë 100ms mes tyre kur clipboard-i është i bllokuar nga procese të tjera.

---

## 2. Struktura e Plotë e Dosjeve dhe Skedarëve (Codebase)

Krijoni strukturën e mëposhtme në kompjuterin tuaj:

```text
smart-ghost-clipboard/
│
├── .env                       # Çelësi sekret i OpenAI API
├── .env.example               # Shembull i konfigurimit të çelësit
├── .gitignore                 # Injoron mjedisin virtual, çelësat sekretë dhe log-et
├── requirements.txt           # Paketat e nevojshme të Python
│
├── app/
│   ├── __init__.py            # Tregon që dosja 'app' është një paketë Python
│   ├── config.py              # Konfigurimet globale, prompt-et, logimi dhe shtegu bazë
│   ├── ai_service.py          # Logjika e komunikimit me OpenAI API (gpt-5.4-nano)
│   ├── clipboard_manager.py   # Leximi dhe shkrimi në Windows Clipboard (me retry)
│   ├── hotkey_listener.py     # Dëgjimi i shkurtoreve në sfond
│   ├── tray.py                # Ikona e System Tray me pystray
│   └── ui.py                  # Dritarja grafike lundruese me CustomTkinter (DPI Aware)
│
└── main.py                    # Pika hyrëse e ekzekutimit të aplikacionit

```

---

## 3. Përgatitja e Mjedisit në VS Code (Hap pas Hapi)

### Hapi 1: Hapja e Terminalit dhe Krijimi i Dosjes

Hapni **VS Code**, hapni Terminalin e integruar (`Ctrl + ~` ose `Terminal -> New Terminal`) dhe ekzekutoni:

```bash
mkdir smart-ghost-clipboard
cd smart-ghost-clipboard

```

### Hapi 2: Krijimi dhe Aktivizimi i Mjedisit Virtual (Virtual Environment)

Krijimi i një mjedisi të izoluar parandalon konfliktet mes paketave të ndryshme në Windows:

```bash
# Krijimi i mjedisit virtual
python -m venv venv

# Aktivizimi në Windows PowerShell
.\venv\Scripts\Activate.ps1

# NËSE PowerShell jep gabim sigurie për ekzekutim skriptesh, ekzekutoni këtë komandë më parë:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

```

Kur mjedisi të jetë aktiv, do të shihni `(venv)` në fillim të rreshtit të terminalit.

### Hapi 3: Instalimi i Bibliotekave të Nevojshme

Krijoni skedarin `requirements.txt` dhe shtoni përmbajtjen:

```text
customtkinter>=5.2.0
openai>=1.30.0
pynput>=1.7.6
pyperclip>=1.8.2
python-dotenv>=1.0.0
pystray>=0.19.5
Pillow>=10.0.0

```

Instaloni të gjitha paketat me një komandë:

```bash
pip install -r requirements.txt

```

---

## 4. Implementimi i Kodit Burimor

### 1. Konfigurimi i Mjedisit (`.env` dhe `.gitignore`)

Krijoni skedarin `.env`:

```ini
OPENAI_API_KEY=vendos_ketu_celesin_tend_openai_sk-...

```

Krijoni skedarin `.env.example`:

```ini
OPENAI_API_KEY=your_openai_api_key_here

```

Krijoni skedarin `.gitignore`:

```text
venv/
.venv/
env/
__pycache__/
*.pyc
*.pyo
*.pyd
.env
build/
dist/
*.spec
*.log
.vscode/
.idea/

```

---

### 2. Skedari i Konfigurimit (`app/config.py`)

Ky skedar përcakton modelin `gpt-5.4-nano`, rolet e sistemit, veprimet e paracaktuara, shtegun bazë për `.env` (i domosdoshëm kur paketuar si `.exe`), dhe sistemin e logimit.

```python
import os
import sys
import logging
from typing import Dict
from dotenv import load_dotenv

# Përcaktimi i shtegut bazë — funksionon si skript dhe si .exe
if getattr(sys, "frozen", False):
    BASE_DIR: str = os.path.dirname(sys.executable)
else:
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_dotenv_path: str = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=_dotenv_path)

APP_NAME: str = "Smart Ghost Clipboard"
APP_VERSION: str = "1.1.0"
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
AI_MODEL: str = "gpt-5.4-nano"
HOTKEY_COMBINATION: str = "<ctrl>+<shift>+v"
LOG_FILE: str = os.path.join(BASE_DIR, "smart_ghost_clipboard.log")
CLIPBOARD_MAX_RETRIES: int = 3
CLIPBOARD_RETRY_DELAY: float = 0.1

PROMPTS: Dict[str, str] = {
    "fix_grammar": (
        "Je një ekspert i redaktimit gjuhësor. Rregullo të gjitha gabimet gramatikore, "
        "drejtshkrimore dhe sintaksore në tekstin e mëposhtëm. Ruaj kuptimin dhe tonin origjinal. "
        "Kthe VETËM tekstin e korrigjuar pa asnjë shpjegim shtesë ose thonjëza."
    ),
    "summarize": (
        "Përmblidh tekstin e mëposhtëm në pika të qarta dhe koncize (bullet points). "
        "Kthe VETËM listën e përmbledhur pa hyrje apo përfundime."
    ),
    "professional": (
        "Rishkruaj tekstin e mëposhtëm me një ton formal, profesional dhe diplomatik të përshtatshëm "
        "për komunikim në biznes ose email zyrtar. Kthe VETËM tekstin e transformuar."
    ),
    "translate_sq": (
        "Përkthe tekstin e mëposhtëm në mënyrë natyrale dhe të saktë në gjuhën Shqipe. "
        "Kthe VETËM përkthimin."
    ),
    "translate_en": (
        "Translate the following text naturally and accurately into fluent English. "
        "Return ONLY the translated text."
    )
}


def setup_logging() -> None:
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    handlers = [logging.StreamHandler(sys.stdout)]
    try:
        handlers.append(logging.FileHandler(LOG_FILE, encoding="utf-8", delay=True))
    except (PermissionError, OSError):
        pass
    logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers)

```

---

### 3. Shërbimi i Inteligjencës Artificiale (`app/ai_service.py`)

Ky modul menaxhon kërkesat e shpejta drejt `gpt-5.4-nano` me logim të strukturuar.

```python
import logging
from typing import Optional
from openai import OpenAI
from app.config import OPENAI_API_KEY, AI_MODEL, PROMPTS

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        invalid_values = {"", "vendos_ketu_celesin_tend_openai_sk-...", "your_openai_api_key_here"}
        if not OPENAI_API_KEY or OPENAI_API_KEY.strip() in invalid_values:
            logger.critical("Çelësi OPENAI_API_KEY mungon.")
            raise ValueError("OPENAI_API_KEY nuk u gjet! Sigurohuni që e keni vendosur në skedarin .env.")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("Shërbimi AI u inicializua. Modeli: %s", AI_MODEL)

    def transform_text(self, action_key: Optional[str], user_text: str, custom_instruction: Optional[str] = None) -> str:
        if not user_text or not user_text.strip():
            return "Nuk ka tekst në kujtesën e përkohshme (Clipboard) për t'u përpunuar."
        if custom_instruction and custom_instruction.strip():
            system_prompt = custom_instruction.strip()
        else:
            system_prompt = PROMPTS.get(action_key or "", "Je një asistent i dobishëm. Përmirëso tekstin.")
        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text.strip()}
                ],
                temperature=0.3
            )
            result_content = response.choices[0].message.content
            if result_content is not None:
                return result_content.strip()
            return "Nuk u kthye asnjë përmbajtje nga modeli AI."
        except Exception as error:
            logger.error("Gabim API: %s", error, exc_info=True)
            return f"Gabim gjatë komunikimit me OpenAI API: {str(error)}"

```

---

### 4. Menaxhuesi i Clipboard-it (`app/clipboard_manager.py`)

Me logjikë retry për rastet kur clipboard-i është i bllokuar nga procese të tjera Windows.

```python
import time
import logging
import pyperclip
from app.config import CLIPBOARD_MAX_RETRIES, CLIPBOARD_RETRY_DELAY

logger = logging.getLogger(__name__)

class ClipboardManager:
    @staticmethod
    def get_text() -> str:
        for attempt in range(1, CLIPBOARD_MAX_RETRIES + 1):
            try:
                text = pyperclip.paste()
                return text if text is not None else ""
            except Exception as error:
                logger.warning("Tentativa %d/%d lexim clipboard: %s", attempt, CLIPBOARD_MAX_RETRIES, error)
                if attempt < CLIPBOARD_MAX_RETRIES:
                    time.sleep(CLIPBOARD_RETRY_DELAY)
        return ""

    @staticmethod
    def set_text(text: str) -> bool:
        for attempt in range(1, CLIPBOARD_MAX_RETRIES + 1):
            try:
                pyperclip.copy(text)
                return True
            except Exception as error:
                logger.warning("Tentativa %d/%d shkrim clipboard: %s", attempt, CLIPBOARD_MAX_RETRIES, error)
                if attempt < CLIPBOARD_MAX_RETRIES:
                    time.sleep(CLIPBOARD_RETRY_DELAY)
        return False

```

---

### 5. Dritarja Grafike Lundruese (`app/ui.py`)

Ndërfaqja me `CustomTkinter` me DPI Awareness, fokus të forcuar me Windows API, siguri thread-i, dhe buton eksplicit Dil.

```python
import ctypes
import threading
import logging
from typing import Callable, Optional, List
import customtkinter as ctk
from app.clipboard_manager import ClipboardManager
from app.ai_service import AIService

logger = logging.getLogger(__name__)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def enable_dpi_awareness() -> None:
    """Aktivizon DPI Awareness në Windows para Tkinter."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor V2
        return
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class GhostClipboardUI(ctk.CTk):
    def __init__(self, ai_service: AIService, on_quit_callback: Optional[Callable] = None):
        super().__init__()
        self.ai_service = ai_service
        self.clipboard_mgr = ClipboardManager()
        self._on_quit_callback = on_quit_callback
        self._is_busy = False
        self.action_buttons: List[ctk.CTkButton] = []

        self.title("Smart Ghost Clipboard (gpt-5.4-nano)")
        self.geometry("620x520")
        self.minsize(500, 420)
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        self._build_widgets()
        self._center_window(620, 520)

    def _center_window(self, width, height):
        self.update_idletasks()
        sx, sy = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{width}x{height}+{max(0,(sx-width)//2)}+{max(0,(sy-height)//2)}")

    def _force_foreground(self):
        """Forcon fokusin me Windows API (ALT trick)."""
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id()) or self.winfo_id()
            u = ctypes.windll.user32
            u.keybd_event(0x12, 0, 0, 0)       # ALT down
            u.SetForegroundWindow(hwnd)
            u.BringWindowToTop(hwnd)
            u.keybd_event(0x12, 0, 0x0002, 0)   # ALT up
        except Exception:
            pass
        self.lift()
        self.focus_force()

    def _build_widgets(self):
        # ... (shih skedarin e plotë ui.py për implementimin e detajuar)
        # Përmban: header, 5 butona veprimesh, input custom, text area,
        # status label, butona Kopjo/Mbyll/Dil
        pass

    def show_window(self):
        if not self._is_busy:
            text = self.clipboard_mgr.get_text()
            self.text_area.delete("1.0", "end")
            if text:
                self.text_area.insert("1.0", text)
        self.deiconify()
        self._force_foreground()

    def hide_window(self):
        self.withdraw()

    def quit_app(self):
        if self._on_quit_callback:
            self._on_quit_callback()
        self.destroy()

    def trigger_ai_action(self, action_key):
        if self._is_busy:
            return
        # ... nis thread AI
        self._is_busy = True
        self.set_loading(True)

    def set_loading(self, is_loading):
        state = "disabled" if is_loading else "normal"
        self.copy_btn.configure(state=state)
        self.custom_btn.configure(state=state)
        self.custom_entry.configure(state=state)
        for btn in self.action_buttons:
            btn.configure(state=state)

```

---

### 6. Ikona e System Tray (`app/tray.py`) — E RE

Shfaq ikonë në zonën e njoftimeve (System Tray) të Windows me meny kontekstuale.

```python
import threading
import logging
from typing import Callable, Optional
from PIL import Image, ImageDraw, ImageFont
import pystray
from app.config import APP_NAME

logger = logging.getLogger(__name__)

def _create_tray_icon_image() -> Image.Image:
    """Gjeneron ikonë programatikisht (rreth blu me 'G')."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 2, size-2, size-2], fill="#1f538d")
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except (OSError, IOError):
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "G", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size-tw)/2, (size-th)/2 - 2), "G", fill="white", font=font)
    return img

class SystemTray:
    def __init__(self, on_show_callback, on_quit_callback):
        self._on_show = on_show_callback
        self._on_quit = on_quit_callback
        self._icon = None

    def start(self):
        menu = pystray.Menu(
            pystray.MenuItem("⚡ Shfaq Dritaren", lambda i, item: self._on_show(), default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Dil", self._handle_quit),
        )
        self._icon = pystray.Icon("smart_ghost_clipboard", _create_tray_icon_image(), APP_NAME, menu)
        threading.Thread(target=self._icon.run, daemon=True, name="SystemTrayThread").start()

    def _handle_quit(self, icon, item):
        icon.stop()
        self._on_quit()

    def stop(self):
        if self._icon:
            self._icon.stop()

```

---

### 7. Dëgjuesi i Shkurtoreve në Sfond (`app/hotkey_listener.py`)

Me logim dhe trajtim të saktë të gabimeve.

```python
import threading
import logging
from typing import Callable, Optional
from pynput import keyboard
from app.config import HOTKEY_COMBINATION

logger = logging.getLogger(__name__)

class HotkeyListener:
    def __init__(self, callback: Callable[[], None]):
        self.callback = callback
        self.listener = None

    def _on_hotkey_triggered(self):
        logger.info("Shkurtorja u detektua: %s", HOTKEY_COMBINATION)
        try:
            self.callback()
        except Exception as e:
            logger.error("Gabim callback: %s", e, exc_info=True)

    def start(self):
        def run():
            try:
                with keyboard.GlobalHotKeys({
                    HOTKEY_COMBINATION: self._on_hotkey_triggered
                }) as self.listener:
                    self.listener.join()
            except Exception as e:
                logger.error("Gabim dëgjuesi: %s", e, exc_info=True)
        threading.Thread(target=run, daemon=True, name="HotkeyListenerThread").start()

    def stop(self):
        if self.listener:
            self.listener.stop()

```

---

### 8. Pika Kryesore e Ekzekutimit (`main.py`)

Me DPI Awareness, Single Instance Mutex, System Tray, Logim, dhe Graceful Shutdown.

```python
import sys
import ctypes
import logging
from app.config import setup_logging, APP_NAME
from app.ui import enable_dpi_awareness, GhostClipboardUI
from app.ai_service import AIService
from app.hotkey_listener import HotkeyListener
from app.tray import SystemTray

logger = logging.getLogger(__name__)
ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Global\\SmartGhostClipboard_SingleInstance_Mutex"

def _acquire_single_instance_mutex() -> bool:
    try:
        ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            return False
        return True
    except Exception:
        return True

def main():
    setup_logging()
    enable_dpi_awareness()

    if not _acquire_single_instance_mutex():
        ctypes.windll.user32.MessageBoxW(0, f"{APP_NAME} tashmë ekziston.", APP_NAME, 0x40)
        sys.exit(0)

    try:
        ai_service = AIService()
    except ValueError as err:
        ctypes.windll.user32.MessageBoxW(0, f"Gabim:\n{err}", f"{APP_NAME} — Gabim", 0x10)
        sys.exit(1)

    hotkey_listener = None
    tray = None

    def on_quit():
        if hotkey_listener: hotkey_listener.stop()
        if tray: tray.stop()
        try: app.destroy()
        except: pass

    app = GhostClipboardUI(ai_service=ai_service, on_quit_callback=on_quit)

    hotkey_listener = HotkeyListener(callback=lambda: app.after(0, app.show_window))
    hotkey_listener.start()

    tray = SystemTray(
        on_show_callback=lambda: app.after(0, app.show_window),
        on_quit_callback=lambda: app.after(0, on_quit),
    )
    tray.start()

    app.show_window()
    app.mainloop()

if __name__ == "__main__":
    main()

```

---

## 5. Ekzekutimi dhe Testimi i Aplikacionit

1. Vendosni çelësin tuaj të OpenAI në skedarin `.env`:
```ini
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

```


2. Ekzekutoni aplikacionin nga terminali i VS Code:
```bash
python main.py

```


3. **Provoni funksionimin:**
* Kopjoni një tekst çfarëdo në shfletues ose Word (`Ctrl + C`).
* Shtypni shkurtoren globale `Ctrl + Shift + V`.
* Dritarja e aplikacionit do të hapet menjëherë me tekstin e kopjuar.
* Klikoni mbi **"✍️ Rregullo Gramatikën"** ose **"📝 Përmblidh"**.
* Modeli `gpt-5.4-nano` do të kthejë përgjigjen me shpejtësi të lartë.
* Klikoni **"📋 Kopjo Rezultatin"** dhe ngjiteni ku të dëshironi (`Ctrl + V`).
* **E RE:** Shihni ikonën në System Tray — klik i djathtë për meny, klik i dyfishtë për shfaqje.
* **E RE:** Klikoni **"🚪 Dil"** ose zgjidhni "Dil" nga menya e tray-it për mbyllje të plotë.



---

## 6. Krijimi i një Skedari Ekzekutues `.exe` për Windows

Kur të keni përfunduar testimin, mund ta paketoni projektin në një program të vetëm ekzekutues pa pasur nevojë të hapni VS Code çdo herë.

1. Instaloni `pyinstaller`:
```bash
pip install pyinstaller

```


2. Krijoni skedarin `.exe`:
```bash
pyinstaller --noconsole --onefile --name="SmartGhostClipboard" --collect-all customtkinter main.py

```


3. Skedari ekzekutues i pavarur do të gjendet brenda dosjes **`dist/SmartGhostClipboard.exe`**. Sigurohuni që skedari `.env` të ndodhet në të njëjtën dosje me `.exe` ose çelësi të jetë i konfiguruar si variabël mjedisi në sistemin Windows.

---

## 7. Ndryshimet e Versionit 1.1.0 (Changelog)

| Ndryshimi | Përshkrimi |
|:---|:---|
| **DPI Awareness** | Aktivizim i Per-Monitor DPI Aware v2 para Tkinter — pamje e pastër në ekrane HiDPI. |
| **System Tray** | Ikonë e re në zonën e njoftimeve me meny kontekstuale (Shfaq / Dil). |
| **Single Instance** | Windows Mutex parandalon ekzekutimin e shumëfishtë. |
| **Fokus i Forcuar** | Windows API (ALT + SetForegroundWindow) zëvendëson focus_force(). |
| **Logim i Strukturuar** | Modulin logging me skedar + konsolë, zëvendëson print(). |
| **Clipboard Retry** | 3 tentativa me 100ms vonesë kur clipboard-i bllokuar. |
| **Thread Safety** | Flagë _is_busy + çaktivizim i custom_entry gjatë ngarkimit. |
| **Buton Dil** | Mbyllje eksplicite e plotë e aplikacionit (tray + hotkey + UI). |
| **MessageBox Gabimi** | Dialog vizual Windows kur çelësi API mungon (i dobishëm pa konsolë). |
| **BASE_DIR** | Rezolvim i saktë i shtegut .env kur paketuar si .exe me PyInstaller. |