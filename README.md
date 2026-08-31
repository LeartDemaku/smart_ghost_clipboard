# ⚡ Smart Ghost Clipboard (v2.0.0)

An intelligent, ultra-fast Windows assistant that seamlessly connects your system clipboard with state-of-the-art OpenAI models (`gpt-5.4-nano` / `gpt-4o-mini`).

---

## ✨ Key Features

- **📌 Launch from Anywhere & Pin to Taskbar:** The native `SmartGhostClipboard.exe` launcher can be pinned directly to your Windows Taskbar, placed on your Desktop, or pinned to the Start Menu. It launches instantly and reliably regardless of where the project folder is located.
- **⚡ IPC Wake-Up:** If the application is already running in the background (System Tray), launching the app via shortcut or Taskbar icon sends an inter-process wake-up signal, immediately bringing the floating overlay to the front with the latest clipboard content.
- **Global Hotkeys:** Press `Ctrl + Shift + V` or `Ctrl + Alt + V` from any Windows application (browsers, Word, Slack, VS Code, etc.) to summon the assistant instantly.
- **Forced Foreground Focus (Windows API):** The window is automatically brought to the foreground with immediate keyboard focus, eliminating the need for extra mouse clicks.
- **Power-User In-Window Hotkeys:** Execute actions at keyboard speed (`Alt+1`..`Alt+5`, `Ctrl+1`..`Ctrl+5`, `F5`, `Ctrl+Shift+C`, `Ctrl+L`).
- **5 Action Categories with 25 AI Presets & 7 Prompt Chips:** Includes Writing & Grammar, Business & Email, Multilingual Translation, Summaries & Action Items, and Code & Development.
- **Single & Split View with Diff Highlighter:** Compare original input and transformed output side-by-side with color-coded diff highlighting.
- **SQLite History Drawer:** Persistent clipboard history with real-time fuzzy search, favorite pinning, and 1-click restoration.
- **Integrated System Tray:** Runs quietly in the notification area with a full-featured context menu.
- **HiDPI & 4K Ready:** Crisp, perfectly scaled UI across 100%, 125%, 150%, and 200% display scaling.

---

## 🚀 How to Pin to Taskbar & Desktop

### 1. Pin to Taskbar
1. Open the project directory in File Explorer.
2. Right-click on **`SmartGhostClipboard.exe`**.
3. Select **"Pin to taskbar"**.
4. You can now launch and focus Smart Ghost Clipboard with a single click at any time!

### 2. Create Desktop Shortcut
- Double-click **`Create_Shortcut.bat`**, or
- Right-click the application icon in the System Tray (notification area by the clock) and select **"📌 Create Desktop Shortcut"**.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|:---|:---|
| `Ctrl + Shift + V` / `Ctrl + Alt + V` | **Open floating overlay** from anywhere in Windows |
| `1` to `5` (or `Alt+1`..`5`) | ⚡ **Execute corresponding action** in the active category |
| `Ctrl + Tab` / `Ctrl + Shift + Tab` | 🔄 **Switch categories** |
| `Ctrl + D` | 🔲 **Toggle between Single View and Split View** |
| `Ctrl + H` | 📚 **Open / Close History Drawer** |
| `Ctrl + Enter` | 🚀 **Copy & Auto-Paste directly into the active application** |
| `F5` or `Ctrl + R` | 🔄 **Refresh content from Clipboard** |
| `Ctrl + Shift + C` or `Ctrl + K` | 📋 **Copy result to Clipboard** |
| `Ctrl + L` | 🧹 **Clear text** |
| `Escape` | ❌ **Hide window to System Tray** |

---

## ⚙️ Configuration (`.env`)

Create a `.env` file in the project root directory (or copy from `.env.example`):

```ini
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
AI_MODEL=gpt-5.4-nano
# OPENAI_BASE_URL=https://api.openai.com/v1
# HOTKEY_COMBINATION=<ctrl>+<shift>+v
# AI_TIMEOUT_SECONDS=30.0
```

---

## 🛠️ Installation & Setup

1. **Clone or download** the repository.
2. **Create a virtual environment & install dependencies:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure API Key:** Add your `OPENAI_API_KEY` to `.env`.
4. **Launch:** Run `SmartGhostClipboard.exe` or `run.bat`.