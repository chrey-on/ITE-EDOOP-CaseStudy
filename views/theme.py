"""
PurrfectMatch Design System & Theme Tokens.
Provides a modern, refined aesthetic (Obsidian/Slate palette with warm emerald & royal blue accents).
Replaces generic default Tkinter styling with cohesive, high-contrast, professional desktop UI tokens.
"""

import customtkinter as ctk


class Theme:
    # ==========================================
    # COLOR PALETTE (Light Mode, Dark Mode)
    # ==========================================
    # Backgrounds & Surfaces
    BG_ROOT = ("#f8fafc", "#0b0f19")          # Deep Obsidian Canvas
    BG_SIDEBAR = ("#f1f5f9", "#0f172a")       # Slate 900 Sidebar
    BG_CARD = ("#ffffff", "#141c2e")          # Elevated Surface
    BG_CARD_ALT = ("#f8fafc", "#182238")      # Sub-card Surface
    BG_CARD_HOVER = ("#f1f5f9", "#1e293b")    # Hover Highlight
    BG_INPUT = ("#ffffff", "#0f1626")         # Input Fields
    
    # Hairline Borders
    BORDER = ("#e2e8f0", "#222f46")           # Subtle Hairline
    BORDER_LIGHT = ("#cbd5e1", "#2d3e5c")     # Hover Border
    BORDER_ACCENT = ("#3b82f6", "#60a5fa")    # Focus / Active Border

    # Text & Typography
    TEXT_PRIMARY = ("#0f172a", "#f8fafc")     # Crisp High-Contrast
    TEXT_SECONDARY = ("#475569", "#94a3b8")   # Medium Subtext
    TEXT_MUTED = ("#94a3b8", "#64748b")       # Muted Labels / Placeholders
    TEXT_ACCENT = ("#2563eb", "#38bdf8")      # Highlights & Links

    # Action Accents
    # 1. Primary Action (Royal Blue)
    PRIMARY = ("#2563eb", "#3b82f6")
    PRIMARY_HOVER = ("#1d4ed8", "#2563eb")
    PRIMARY_TEXT = "#ffffff"

    # 2. Positive / Adoption Action (Emerald Mint)
    SUCCESS = ("#10b981", "#059669")
    SUCCESS_HOVER = ("#059669", "#047857")
    SUCCESS_TEXT = "#ffffff"

    # 3. Secondary / Neutral (Slate)
    SECONDARY = ("#e2e8f0", "#1e293b")
    SECONDARY_HOVER = ("#cbd5e1", "#2d3d57")
    SECONDARY_TEXT = ("#0f172a", "#e2e8f0")

    # 4. Destructive (Ruby / Coral)
    DANGER = ("#ef4444", "#dc2626")
    DANGER_HOVER = ("#dc2626", "#b91c1c")
    DANGER_TEXT = "#ffffff"

    # Status Pill Colors: returns (background_tuple, text_color_tuple)
    @classmethod
    def get_status_colors(cls, status: str):
        status_clean = str(status).strip()
        if status_clean in ("Available", "Approved"):
            return (("#dcfce7", "#064e3b"), ("#15803d", "#4ade80"))
        elif status_clean in ("Pending", "Pending Review"):
            return (("#fef3c7", "#78350f"), ("#b45309", "#fcd34d"))
        elif status_clean in ("Medical Hold", "Rejected"):
            return (("#fee2e2", "#7f1d1d"), ("#b91c1c", "#fca5a5"))
        elif status_clean in ("Adopted", "Completed"):
            return (("#f3e8ff", "#581c87"), ("#7e22ce", "#d8b4fe"))
        elif status_clean in ("Interview Scheduled", "Active"):
            return (("#e0f2fe", "#0c4a6e"), ("#0284c7", "#38bdf8"))
        elif status_clean == "Inactive":
            return (("#f1f5f9", "#1e293b"), ("#64748b", "#94a3b8"))
        else:
            return (("#f1f5f9", "#1e293b"), ("#475569", "#94a3b8"))

    # ==========================================
    # CORNER RADII
    # ==========================================
    RADIUS_CARD = 12
    RADIUS_INPUT = 8
    RADIUS_BTN = 8
    RADIUS_PILL = 16

    # ==========================================
    # TYPOGRAPHY SCALES
    # ==========================================
    @staticmethod
    def font_hero():
        return ctk.CTkFont(family="Segoe UI", size=22, weight="bold")

    @staticmethod
    def font_title():
        return ctk.CTkFont(family="Segoe UI", size=18, weight="bold")

    @staticmethod
    def font_subtitle():
        return ctk.CTkFont(family="Segoe UI", size=14, weight="bold")

    @staticmethod
    def font_body():
        return ctk.CTkFont(family="Segoe UI", size=12)

    @staticmethod
    def font_body_bold():
        return ctk.CTkFont(family="Segoe UI", size=12, weight="bold")

    @staticmethod
    def font_caption():
        return ctk.CTkFont(family="Segoe UI", size=11)

    @staticmethod
    def font_caption_bold():
        return ctk.CTkFont(family="Segoe UI", size=11, weight="bold")

    @staticmethod
    def font_tiny():
        return ctk.CTkFont(family="Segoe UI", size=10, weight="bold")
