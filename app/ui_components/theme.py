"""
Moduli i Temës dhe Stilit Vizual (theme.py).
Përcakton paletën e ngjyrave 'Obsidian Dark Glassmorphism', fontet,
radiuset e qosheve, ngjyrat e ndriçimit (glow), dhe stilet e elementeve.
"""

from typing import Dict, Any
import customtkinter as ctk

# ───────────────────────────────────────────────────────────────────────────────
# Paleta e Ngjyrave (Obsidian Dark Glassmorphism & Fluent 2)
# ───────────────────────────────────────────────────────────────────────────────

class Theme:
    # Sfondet kryesore
    BG_MAIN: str = "#0B0F19"           # Sfondi kryesor i dritares (Obsidian)
    BG_SURFACE: str = "#111827"        # Sipërfaqja e kartave kryesore (Dark Slate)
    BG_SURFACE_HOVER: str = "#1A2234"  # Hover mbi karta
    BG_INPUT: str = "#0F172A"          # Sfondi i fushave të tekstit dhe inputeve
    BG_SUBTLE: str = "#1F2937"         # Sfond dytësor i zbehtë për seksione

    # Bordurat dhe Ndarësit
    BORDER_MAIN: str = "#1F2937"       # Bordurë e lehtë e errët
    BORDER_LIGHT: str = "#374151"      # Bordurë e dallueshme
    BORDER_FOCUS: str = "#6366F1"      # Bordurë gjatë fokusimit (Indigo Glow)
    BORDER_ACCENT: str = "#3B82F6"     # Bordurë me theks blu

    # Ngjyrat e Theksit (Accent & Gradients)
    ACCENT_PRIMARY: str = "#6366F1"    # Indigo e ndritur
    ACCENT_PRIMARY_HOVER: str = "#4F46E5"
    ACCENT_SECONDARY: str = "#3B82F6"  # Blu e qartë
    ACCENT_SECONDARY_HOVER: str = "#2563EB"
    ACCENT_CYAN: str = "#06B6D4"       # Cyan për latency / telemetry
    ACCENT_PURPLE: str = "#8B5CF6"     # Vjollcë për prompt chips

    # Ngjyrat e Statusit
    SUCCESS: str = "#10B981"           # Emerald Green për sukses / kopjim
    SUCCESS_HOVER: str = "#059669"
    WARNING: str = "#F59E0B"           # Amber për paralajmërime
    DANGER: str = "#EF4444"            # Crimson për gabime / dalje
    DANGER_HOVER: str = "#DC2626"
    INFO: str = "#38BDF8"              # Sky Blue për njoftime informative

    # Tekstet & Kontrasti
    TEXT_PRIMARY: str = "#F9FAFB"      # Teksti kryesor i bardhë me kontrast të plotë
    TEXT_SECONDARY: str = "#9CA3AF"    # Teksti dytësor (gri e lehtë)
    TEXT_MUTED: str = "#6B7280"        # Tekst i zbehtë për shkurtesa
    TEXT_ACCENT: str = "#A5B4FC"       # Tekst me nuancë indigo

    # Theksimi i Diff (Krahasimi i ndryshimeve)
    DIFF_ADDED_BG: str = "#064E3B"     # Sfond i gjelbër i errët për fjalët e reja
    DIFF_ADDED_FG: str = "#34D399"     # Tekst i gjelbër i ndritur
    DIFF_REMOVED_BG: str = "#450A0A"   # Sfond i kuq i errët për gabimet e hequra
    DIFF_REMOVED_FG: str = "#F87171"   # Tekst i kuq i ndritur

    # Rrumbullakimet e Qosheve (Border Radius)
    RADIUS_LG: int = 12                # Për kartat dhe dritaren kryesore
    RADIUS_MD: int = 8                 # Për butonat dhe inputet
    RADIUS_SM: int = 6                 # Për badges dhe chips
    RADIUS_ROUND: int = 20             # Për pill buttons

    # Fontet
    FONT_FAMILY_MAIN: str = "Segoe UI"
    FONT_FAMILY_MONO: str = "Consolas"

    @classmethod
    def font_title(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY_MAIN, size=15, weight="bold")

    @classmethod
    def font_subtitle(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY_MAIN, size=11)

    @classmethod
    def font_badge(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY_MAIN, size=11, weight="bold")

    @classmethod
    def font_button(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY_MAIN, size=12, weight="bold")

    @classmethod
    def font_button_sm(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY_MAIN, size=11, weight="bold")

    @classmethod
    def font_tab(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY_MAIN, size=12, weight="bold")

    @classmethod
    def font_chip(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY_MAIN, size=11, weight="bold")

    @classmethod
    def font_editor(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY_MONO, size=13)

    @classmethod
    def font_status(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family=cls.FONT_FAMILY_MAIN, size=11)
