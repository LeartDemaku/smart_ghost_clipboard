# ⚡ Smart Ghost Clipboard (v2.0.0)

Një asistent inteligjent dhe ultra i shpejtë për Windows që integron kujtesën e përkohshme (Clipboard) me modelet më të avancuara të OpenAI (`gpt-5.4-nano` / `gpt-4o-mini`).

---

## ✨ Karakteristikat Kryesore

- **📌 Nisje nga Kudo & Taskbar:** Ekzekutuesi nativ `SmartGhostClipboard.exe` mund të kapet direkt në Taskbar (Pin to taskbar), të vendoset në Desktop ose Start Menu, dhe hapet menjëherë pavarësisht se ku e zhvendosni dosjen e projektit.
- **⚡ IPC Wake-Up:** Nëse aplikacioni është tashmë aktiv në System Tray, klikimi mbi ikonën në Taskbar ose shkurtore e rikthen dhe e shfaq dritaren menjëherë në fokus me tekstin e freskët nga clipboard.
- **Shkurtore Globale në Çdo Vend:** Shtypni `Ctrl + Shift + V` ose `Ctrl + Alt + V` në çdo aplikacion në Windows (Word, Chrome, Slack, VS Code) për të hapur menjëherë dritaren.
- **Fokus i Forcuar (Windows API):** Dritarja vjen automatikisht në plan të parë me fokus të plotë pa pasur nevojë për klikime shtesë.
- **Power-User In-Window Hotkeys:** Ekzekutoni çdo veprim menjëherë nga tastiera (`Alt+1`..`Alt+5`, `Ctrl+1`..`Ctrl+5`, `F5`, `Ctrl+Shift+C`, `Ctrl+L`).
- **5 Kategori me 25 Veprime AI & 7 Prompt Chips:** Përfshin Shkrim & Gramatikë, Biznes & Email, Përkthim Multilingual, Përmbledhje & Action Items, Kod & Zhvillim.
- **Single & Split View me Diff Highlighter:** Krahasoni tekstin origjinal dhe atë të transformuar krah për krah.
- **Sirtar Historiku me SQLite:** Kërkim në kohë reale, ruajtje e preferencave (Favorites), dhe ri-ngarkim me 1 klikim.
- **System Tray i Integruar:** Rri i heshtur në sfond me ikonë në zonën e njoftimeve dhe menu të pasur kontekstuale.
- **DPI Awareness (HiDPI / 4K):** Ndërfaqe e mprehtë dhe e qartë në ekrane 100%, 125%, 150% dhe 200%.

---

## 🚀 Si të vendosni ikonën në Taskbar dhe Desktop

### 1. Vendosja në Taskbar (Pin to Taskbar):
1. Shkoni te dosja e projektit.
2. Klikoni me tastin e djathtë mbi skedarin **`SmartGhostClipboard.exe`**.
3. Zgjidhni **"Pin to taskbar"** (ose *Kap në shiritin e detyrave*).
4. Tani aplikacioni hapet në çdo moment me 1 klikim direkt nga Taskbari!

### 2. Krijimi i Shkurtores në Desktop:
- Klikoni dy herë mbi **`Create_Shortcut.bat`**, ose
- Klikoni me të djathtën mbi ikonën e aplikacionit te ora (System Tray) dhe zgjidhni **"📌 Krijo Shkurtore në Desktop"**.

---

## ⌨️ Shkurtoret e Tastierës (Keyboard Shortcuts)

| Shkurtorja | Veprimi |
|:---|:---|
| `Ctrl + Shift + V` / `Ctrl + Alt + V` | **Hap dritaren lundruese** nga kudo në Windows |
| `1` deri `5` (ose `Alt+1`..`5`) | ⚡ **Ekzekuto veprimin përkatës të kategorisë** |
| `Ctrl + Tab` / `Ctrl + Shift + Tab` | 🔄 **Ndërro Kategoritë** |
| `Ctrl + D` | 🔲 **Kalo midis Single View dhe Split View** |
| `Ctrl + H` | 📚 **Hap / Fsheh Sirtarin e Historikut** |
| `Ctrl + Enter` | 🚀 **Kopjo & Auto-Paste direkt në aplikacionin aktiv** |
| `F5` ose `Ctrl + R` | 🔄 **Rifresko nga Clipboard** |
| `Ctrl + Shift + C` ose `Ctrl + K` | 📋 **Kopjo Rezultatin në Clipboard** |
| `Ctrl + L` | 🧹 **Pastro Tekstin** |
| `Escape` | ❌ **Fsheh dritaren në sfond (System Tray)** |

---

## ⚙️ Konfigurimi (`.env`)

Krijoni skedarin `.env` në rrënjën e projektit:

```ini
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
AI_MODEL=gpt-5.4-nano
# OPENAI_BASE_URL=https://api.openai.com/v1
# HOTKEY_COMBINATION=<ctrl>+<shift>+v
# AI_TIMEOUT_SECONDS=30.0
```