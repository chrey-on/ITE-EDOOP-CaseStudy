"""
PurrfectMatch Design System & Theme Tokens.
Provides a modern, delightful Pastel aesthetic (Warm cream/blush canvas with soft pastel lilac, mint, and peach accents).
Replaces generic default Tkinter styling with cohesive, high-contrast, professional desktop UI tokens.
"""

import customtkinter as ctk


class Theme:
    # ==========================================
    # COLOR PALETTE (Light Mode, Dark Mode)
    # Pastel Aesthetic: Warm cream/blush canvas, soft pastel lilac primary,
    # pastel mint for adoptions/availability, pastel peach for pending reviews,
    # and pastel coral for destructive actions.
    # ==========================================
    # Backgrounds & Surfaces
    BG_ROOT = ("#faf6f8", "#17141f")          # Pastel Cream-Mist Canvas / Cozy Twilight
    BG_SIDEBAR = ("#f4ecf3", "#1e1929")       # Soft Pastel Lilac-Rose Sidebar
    BG_CARD = ("#ffffff", "#252033")          # Crisp White Card / Soft Elevated Plum
    BG_CARD_ALT = ("#faf2f7", "#2e273f")      # Delicate Pastel Strawberry Milk
    BG_CARD_HOVER = ("#f3e8f1", "#382f4d")    # Gentle Pastel Hover
    BG_INPUT = ("#ffffff", "#1e1929")         # Clean Input Surface
    
    # Hairline Borders
    BORDER = ("#ebdce7", "#3b324f")           # Soft Pastel Lavender Border
    BORDER_LIGHT = ("#dfcadb", "#4a3f63")     # Border Hover / Divider
    BORDER_ACCENT = ("#c084fc", "#d8b4fe")    # Pastel Lilac Focus Border

    # Text & Typography
    TEXT_PRIMARY = ("#2c223a", "#fcf7ff")     # Deep Plum Slate (Gentle, High-Contrast)
    TEXT_SECONDARY = ("#6b5d7d", "#c4b5d6")   # Soft Mauve Subtext
    TEXT_MUTED = ("#9e90af", "#8b7b9e")       # Pastel Heather Labels
    TEXT_ACCENT = ("#9333ea", "#c084fc")      # Pastel Lilac Accent Text

    # Action Accents
    # 1. Primary Action (Pastel Lilac / Sweet Lavender)
    PRIMARY = ("#9333ea", "#a855f7")
    PRIMARY_HOVER = ("#7e22ce", "#9333ea")
    PRIMARY_TEXT = "#ffffff"

    # 2. Positive / Adoption Action (Pastel Mint / Soft Sage)
    SUCCESS = ("#059669", "#10b981")
    SUCCESS_HOVER = ("#047857", "#059669")
    SUCCESS_TEXT = "#ffffff"

    # 3. Secondary / Neutral (Pastel Oat / Lavender Gray)
    SECONDARY = ("#f0e5ee", "#2e273f")
    SECONDARY_HOVER = ("#e5d7e3", "#3b3250")
    SECONDARY_TEXT = ("#3a2c49", "#f0e6f5")

    # 4. Destructive (Pastel Coral / Soft Salmon)
    DANGER = ("#e11d48", "#f43f5e")
    DANGER_HOVER = ("#be123c", "#e11d48")
    DANGER_TEXT = "#ffffff"

    # Status Pill Colors: returns (background_tuple, text_color_tuple)
    @classmethod
    def get_status_colors(cls, status: str):
        status_clean = str(status).strip()
        if status_clean in ("Available", "Approved"):
            # Pastel Mint / Sage
            return (("#d1fae5", "#134e4a"), ("#065f46", "#6ee7b7"))
        elif status_clean in ("Pending", "Pending Review"):
            # Pastel Peach / Apricot
            return (("#fef3c7", "#451a03"), ("#92400e", "#fde047"))
        elif status_clean in ("Medical Hold", "Rejected"):
            # Pastel Rose / Blush Coral
            return (("#ffe4e6", "#4c0519"), ("#9f1239", "#fda4af"))
        elif status_clean in ("Adopted", "Completed"):
            # Pastel Lilac / Sweet Lavender
            return (("#f3e8ff", "#3b0764"), ("#6b21a8", "#e9d5ff"))
        elif status_clean in ("Interview Scheduled", "Active"):
            # Pastel Sky / Periwinkle
            return (("#e0f2fe", "#082f49"), ("#0369a1", "#7dd3fc"))
        elif status_clean == "Inactive":
            # Pastel Heather Gray
            return (("#f3ebf2", "#282136"), ("#7a6c8a", "#b5a7c5"))
        else:
            return (("#f3ebf2", "#282136"), ("#5f516f", "#b5a7c5"))

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
