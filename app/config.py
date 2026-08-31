"""
Moduli i Konfigurimit të Aplikacionit (config.py).
Ngarkon variablat e mjedisit nga skedari .env dhe përcakton konstantet kryesore:
modelin e inteligjencës artificiale, shkurtoret e tastierës, kategoritë e pasuruara të veprimeve,
udhëzimet (prompts), modifikuesit e shpejtë (chips), timeout-et dhe shtegun bazë.
"""

import os
import sys
import logging
from typing import Dict, List, Tuple, Optional, Any
from dotenv import load_dotenv

# ───────────────────────────────────────────────────────────────────────────────
# Përcaktimi i shtegut bazë (BASE_DIR).
# Kur aplikacioni ekzekutohet si .exe i paketuar me PyInstaller, direktoria
# aktuale e punës (CWD) mund të ndryshojë nga vendndodhja e ekzekutuesit.
# ───────────────────────────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR: str = os.path.dirname(sys.executable)
else:
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ngarkon variablat nga skedari .env duke përdorur shtegun e saktë bazë
_dotenv_path: str = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=_dotenv_path, override=True)

# ───────────────────────────────────────────────────────────────────────────────
# Metadata & Konstantet e aplikacionit
# ───────────────────────────────────────────────────────────────────────────────

APP_NAME: str = "Smart Ghost Clipboard"
APP_VERSION: str = "2.0.0"
APP_TAGLINE: str = "AI-Powered Ghost Clipboard & Intelligent Text Transformer"

# Çelësi sekret dhe Base URL i OpenAI API (ose proxy / local endpoint)
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
_base_url_env: str = os.getenv("OPENAI_BASE_URL", "").strip()
OPENAI_BASE_URL: Optional[str] = _base_url_env if _base_url_env else None

# Modeli i inteligjencës artificiale (e konfiguruar nga .env, default 'gpt-5.4-nano')
AI_MODEL: str = os.getenv("AI_MODEL", "gpt-5.4-nano").strip()

# Shkurtorja globale e tastierës
HOTKEY_COMBINATION: str = os.getenv("HOTKEY_COMBINATION", "<ctrl>+<shift>+v").strip()

# Timeout në sekonda për kërkesat e AI
try:
    AI_TIMEOUT_SECONDS: float = float(os.getenv("AI_TIMEOUT_SECONDS", "30.0"))
except ValueError:
    AI_TIMEOUT_SECONDS = 30.0

# Shtegu i skedarit të log-eve
LOG_FILE: str = os.path.join(BASE_DIR, "smart_ghost_clipboard.log")

# Konfigurimi i tentativave për qasje në clipboard
try:
    CLIPBOARD_MAX_RETRIES: int = int(os.getenv("CLIPBOARD_MAX_RETRIES", "3"))
except ValueError:
    CLIPBOARD_MAX_RETRIES = 3

try:
    CLIPBOARD_RETRY_DELAY: float = float(os.getenv("CLIPBOARD_RETRY_DELAY", "0.1"))
except ValueError:
    CLIPBOARD_RETRY_DELAY = 0.1

# ───────────────────────────────────────────────────────────────────────────────
# Kategoritë dhe Veprimet e Pasuruara të AI
# ───────────────────────────────────────────────────────────────────────────────

ACTION_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "writing": {
        "title": "✍️ Shkrim & Gramatikë",
        "icon": "✍️",
        "actions": [
            ("✍️ [1] Rregullo Gramatikën", "fix_grammar", "Korrigjon automatikisht gabimet gramatikore dhe drejtshkrimore."),
            ("🇦🇱 [2] Shqip Standarde", "standard_sq", "Përshtat tekstin në gjuhë standarde letrare Shqipe pa zhargon."),
            ("🌊 [3] Rrjedhshmëri", "rephrase_flow", "Riformulon fjalitë që të lexohen bukur dhe në mënyrë natyrale."),
            ("🚀 [4] Zgjero Tekstin", "expand_text", "Pasuron idetë me më shumë qartësi dhe kontekst."),
            ("✨ [5] Më Koncize", "make_concise", "Shkurton dhe eliminon fjalët e tepërta pa humbur kuptimin."),
        ],
    },
    "business": {
        "title": "💼 Biznes & Email",
        "icon": "💼",
        "actions": [
            ("💼 [1] Ton Formal & Zyrtar", "professional", "Ton diplomatik, i respektueshëm për email zyrtar ose zyrë."),
            ("✉️ [2] Përgjigju Email-it", "email_reply", "Krijon përgjigje të gatshme, të qartë dhe të sjellshme për email."),
            ("🔥 [3] Ton Bindës (Sales)", "persuasive", "Rishkrim me energji bindëse për prezantime dhe shitje."),
            ("🤝 [4] Ton Miqësor & Ngrohtë", "friendly_tone", "Ton i hapur, miqësor dhe bashkëpunues."),
            ("📋 [5] Propozim Projekti", "project_proposal", "Strukturë profesionale për prezantim ideje ose propozimi."),
        ],
    },
    "translation": {
        "title": "🌐 Përkthim",
        "icon": "🌐",
        "actions": [
            ("🇦🇱 [1] Në Shqip", "translate_sq", "Përkthen rrjedhshëm dhe saktë në gjuhën Shqipe."),
            ("🇬🇧 [2] Në Anglisht", "translate_en", "Përkthen në anglishte të rrjedhshme e profesionale."),
            ("🇩🇪 [3] Në Gjermanisht", "translate_de", "Përkthen saktë në gjuhën Gjermane."),
            ("🇮🇹 [4] Në Italisht", "translate_it", "Përkthen në italishte natyrale."),
            ("🇫🇷 [5] Në Frëngjisht", "translate_fr", "Përkthen në gjuhën Frënge."),
        ],
    },
    "summary": {
        "title": "📝 Përmbledhje & Detyra",
        "icon": "📝",
        "actions": [
            ("📝 [1] Përmbledhje Bullet", "summarize", "Nxjerr thelbin në pika koncize dhe të qarta."),
            ("⚡ [2] TL;DR (1 Fjali)", "tldr_one_sentence", "Një fjali e vetme që përmbledh të gjithë mesazhin."),
            ("🎯 [3] Detyrat (Action Items)", "action_items", "Nxjerr listën e veprimeve dhe hapave të radhës me afate."),
            ("💡 [4] Idetë Kryesore", "key_takeaways", "Pikat më thelbësore dhe idetë kryesore të tekstit."),
            ("❓ [5] Pyetje & Përgjigje", "generate_qa", "Krijon pyetje-përgjigje nga përmbajtja e tekstit."),
        ],
    },
    "code": {
        "title": "💻 Kod & Zhvillim",
        "icon": "💻",
        "actions": [
            ("🛠️ [1] Rregullo & Optimizo", "fix_code", "Zbulon gabimet e sintaksës dhe optimizon performancën."),
            ("🔍 [2] Shpjego Kodin", "explain_code", "Shpjegon me terma të thjeshtë çdo rresht kodi."),
            ("💬 [3] Dokumento & Komente", "code_comments", "Shton docstrings dhe komente të plota profesionale."),
            ("🔄 [4] Refaktoro Kodin", "refactor_code", "Pastron strukturën sipas standardeve Clean Code."),
            ("🧪 [5] Gjenero Unit Tests", "generate_tests", "Krijon teste automatike për funksionet e kodit."),
        ],
    },
}

# ───────────────────────────────────────────────────────────────────────────────
# Prompts të dedikuara për secilin lloj transformimi të tekstit
# ───────────────────────────────────────────────────────────────────────────────
PROMPTS: Dict[str, str] = {
    # Shkrim & Gramatikë
    "fix_grammar": (
        "Je një ekspert i redaktimit gjuhësor. Rregullo të gjitha gabimet gramatikore, "
        "drejtshkrimore dhe sintaksore në tekstin e mëposhtëm. Ruaj kuptimin dhe tonin origjinal. "
        "Kthe VETËM tekstin e korrigjuar pa asnjë shpjegim shtesë ose thonjëza."
    ),
    "standard_sq": (
        "Përshtate tekstin e mëposhtëm në gjuhën letrare standarde Shqipe, duke hequr dialektizmat, "
        "gabimet drejtshkrimore dhe huazimet e panevojshme. Kthe VETËM tekstin e përshtatur."
    ),
    "rephrase_flow": (
        "Riformulo tekstin e mëposhtëm që të ketë një rrjedhshmëri natyrale, të bukur dhe të qartë "
        "për çdo lexues, duke ruajtur të gjitha faktet kryesore. Kthe VETËM tekstin e riformuluar."
    ),
    "expand_text": (
        "Zgjero tekstin e mëposhtëm me më shumë detaje, thellësi dhe qartësi logjike. "
        "Kthe VETËM tekstin e zgjeruar."
    ),
    "make_concise": (
        "Bëje tekstin e mëposhtëm sa më konciz dhe të drejtpërdrejtë, duke hequr çdo fjalë të tepërt. "
        "Kthe VETËM versionin e shkurtuar."
    ),

    # Biznes & Email
    "professional": (
        "Rishkruaj tekstin e mëposhtëm me një ton formal, profesional dhe diplomatik të përshtatshëm "
        "për komunikim në biznes ose email zyrtar. Kthe VETËM tekstin e transformuar."
    ),
    "email_reply": (
        "Krijo një përgjigje profesionale, të edukuar dhe koncize për mesazhin/email-in e mëposhtëm. "
        "Përfshi përshëndetje dhe mbyllje të përshtatshme. Kthe VETËM email-in e përgjigjes."
    ),
    "persuasive": (
        "Rishkruaj tekstin me një ton shumë bindës, të sigurt dhe tërheqës për shitje ose propozim ideje. "
        "Kthe VETËM tekstin e ri."
    ),
    "friendly_tone": (
        "Rishkruaj tekstin me një ton të ngrohtë, bashkëpunues, miqësor dhe shumë pozitiv. "
        "Kthe VETËM tekstin."
    ),
    "project_proposal": (
        "Strukturoje tekstin e mëposhtëm si një përmbledhje ekzekutive të një propozimi projekti "
        "(Qëllimi, Zgjidhja, Përfitimet, Hapat e Ardhshëm). Kthe VETËM tekstin e strukturuar."
    ),

    # Përkthim
    "translate_sq": (
        "Përkthe tekstin e mëposhtëm në mënyrë natyrale dhe të saktë në gjuhën Shqipe. "
        "Kthe VETËM përkthimin."
    ),
    "translate_en": (
        "Translate the following text naturally and accurately into fluent English. "
        "Return ONLY the translated text."
    ),
    "translate_de": (
        "Übersetze den folgenden Text präzise und natürlich ins Deutsche. "
        "Gib NUR den übersetzten Text zurück."
    ),
    "translate_it": (
        "Traduci il seguente testo in modo naturale e accurato in italiano fluente. "
        "Restituisci SOLO la traduzione."
    ),
    "translate_fr": (
        "Traduisez le texte suivant de manière fluide et précise en français. "
        "Renvoyez UNIQUEMENT la traduction."
    ),

    # Përmbledhje & Detyra
    "summarize": (
        "Përmblidh tekstin e mëposhtëm në pika të qarta dhe koncize (bullet points). "
        "Kthe VETËM listën e përmbledhur pa hyrje apo përfundime."
    ),
    "tldr_one_sentence": (
        "Shkruaj një përmbledhje në vetëm NJË fjali të vetme (TL;DR) të gjithë thelbit të këtij teksti. "
        "Kthe VETËM atë fjali."
    ),
    "action_items": (
        "Nxirr nga ky tekst të gjitha detyrat, hapat e veprimit (Action Items) dhe afatet në formë liste "
        "me kutiza kontrolli [ ]. Kthe VETËM listën e veprimeve."
    ),
    "key_takeaways": (
        "Nxirr 3 deri në 5 pikat më të rëndësishme dhe idetë kryesore (Key Takeaways) nga ky tekst. "
        "Kthe VETËM listën e pikave."
    ),
    "generate_qa": (
        "Krijo një listë me 3-5 pyetje dhe përgjigje kryesore bazuar në informacionin e këtij teksti. "
        "Kthe VETËM listën Q&A."
    ),

    # Kod & Zhvillim
    "fix_code": (
        "Je një inxhinier i lartë softueri. Rregullo gabimet, optimizo performancën dhe pastro kodin e mëposhtëm. "
        "Kthe VETËM kodin e përmirësuar pa asnjë shpjegim shtesë."
    ),
    "explain_code": (
        "Shpjego hap pas hapi dhe me terma të qartë se çfarë bën ky kod, çfarë algoritmesh përdor dhe si funksionon."
    ),
    "code_comments": (
        "Shto komente të qarta, docstrings dhe shpjegime për çdo funksion ose pjesë kryesore të kodit. "
        "Kthe VETËM kodin e plotë të dokumentuar."
    ),
    "refactor_code": (
        "Refaktoro kodin e mëposhtëm sipas parimeve më të mira të Clean Code, modularitetit dhe emërtimit të pastër. "
        "Kthe VETËM kodin e refaktoruar."
    ),
    "generate_tests": (
        "Shkruaj teste të plota njësie (Unit Tests) për kodin e mëposhtëm me raste normale dhe skajore. "
        "Kthe VETËM kodin e testeve."
    ),
}

# ───────────────────────────────────────────────────────────────────────────────
# Modifikuesit e Shpejtë (Prompt Chips me 1-Klikim)
# ───────────────────────────────────────────────────────────────────────────────
PROMPT_CHIPS: List[Tuple[str, str]] = [
    ("✨ Më e shkurtër", "Bëje sa më të shkurtër dhe koncize pa humbur kuptimin kryesor."),
    ("🎯 Pika Bullet", "Organizoje të gjithë përmbajtjen në pika të qarta dhe të lehta për t'u lexuar."),
    ("🏢 Email Zyrtar", "Formuloje si një email të plotë me përshëndetje formale dhe mbyllje të sjellshme."),
    ("💡 Shpjego Thjeshtë", "Shpjegoje konceptin në fjalë në mënyrë aq të thjeshtë sa ta kuptojë një fëmijë 10 vjeç."),
    ("😄 Shto Emojis", "Shto emoji të përshtatshme dhe të këndshme në vende strategjike."),
    ("📄 Tabela Markdown", "Strukturoje informacionin në një tabelë të rregullt Markdown me kolona."),
    ("🔍 Gjej Kontradiktat", "Analizo tekstin dhe nxirr çdo pasaktësi, supozim ose kontradiktë logjike."),
]


def setup_logging() -> None:
    """
    Konfigurimi i sistemit të log-eve me dy kanale:
    1. Konsola (stdout) - për zhvillimin dhe debug-imin
    2. Skedari i log-eve - për diagnostikim kur ekzekutohet si .exe pa konsolë
    """
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handlers: List[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
    ]

    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", delay=True)
        handlers.append(file_handler)
    except (PermissionError, OSError):
        pass

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
    )
