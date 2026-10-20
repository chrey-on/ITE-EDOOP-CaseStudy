"""
PurrfectMatch Design System & Theme Tokens.
Provides a modern, high-contrast, polished desktop UI aesthetic:
- Refined typography hierarchy using Segoe UI.
- Harmonized pastel and vibrant action accents (Purple/Violet, Emerald Mint, Coral Rose).
- Clean elevated surface layers with hairline borders and rounded radii.
- Reusable empty-state rendering helper.
"""

import customtkinter as ctk


class Theme:
    # ==========================================
    # COLOR PALETTE (Light Mode, Dark Mode)
    # ==========================================
    # Backgrounds & Canvas Surfaces
    BG_ROOT = ("#f8fafc", "#110e1b")          # Clean Slate Canvas / Modern Obsidian
    BG_SIDEBAR = ("#f1f5f9", "#181426")       # Elevated Sidebar Surface
    BG_CARD = ("#ffffff", "#1f1a30")          # Crisp Elevated Card
    BG_CARD_ALT = ("#f8fafc", "#28223d")      # Subtle Sub-card / Chip Surface
    BG_CARD_HOVER = ("#f1f5f9", "#342c4f")    # Card / Row Hover Surface
    BG_INPUT = ("#ffffff", "#181426")         # Input Field Surface
    
    # Hairline Borders & Dividers
    BORDER = ("#e2e8f0", "#322a4d")           # Subtle Hairline Border
    BORDER_LIGHT = ("#cbd5e1", "#3f3560")     # Divider / Outer Boundary
    BORDER_ACCENT = ("#8b5cf6", "#a78bfa")    # Focus & Selected Border

    # Text & Typography (High-Contrast, Accessible)
    TEXT_PRIMARY = ("#0f172a", "#f8fafc")     # Deep Slate-900 / Crisp White
    TEXT_SECONDARY = ("#334155", "#cbd5e1")   # Crisp Slate-700 / Soft Slate-300
    TEXT_MUTED = ("#64748b", "#94a3b8")       # High-Contrast Slate-500 / Slate-400
    TEXT_ACCENT = ("#7c3aed", "#c084fc")      # Accent Violet Text

    # Action Accents & Button States
    # 1. Primary Action (Modern Violet)
    PRIMARY = ("#7c3aed", "#8b5cf6")
    PRIMARY_HOVER = ("#6d28d9", "#7c3aed")
    PRIMARY_TEXT = "#ffffff"

    # 2. Positive / Adoption Action (Emerald Mint)
    SUCCESS = ("#059669", "#10b981")
    SUCCESS_HOVER = ("#047857", "#059669")
    SUCCESS_TEXT = "#ffffff"

    # 3. Secondary / Neutral (Clean Gray-Slate)
    SECONDARY = ("#e2e8f0", "#28223d")
    SECONDARY_HOVER = ("#cbd5e1", "#352e4f")
    SECONDARY_TEXT = ("#0f172a", "#f1f5f9")

    # 4. Destructive (Coral Rose)
    DANGER = ("#e11d48", "#f43f5e")
    DANGER_HOVER = ("#be123c", "#e11d48")
    DANGER_TEXT = "#ffffff"

    # 5. Warning / Archive (Warm Amber)
    WARNING = ("#d97706", "#f59e0b")
    WARNING_HOVER = ("#b45309", "#d97706")
    WARNING_TEXT = "#ffffff"

    # Status Pill Colors: returns (background_tuple, text_color_tuple)
    @classmethod
    def get_status_colors(cls, status: str):
        status_clean = str(status).strip()
        if status_clean in ("Available", "Approved"):
            # Emerald Mint
            return (("#d1fae5", "#064e3b"), ("#065f46", "#6ee7b7"))
        elif status_clean in ("Pending", "Pending Review"):
            # Warm Amber
            return (("#fef3c7", "#78350f"), ("#92400e", "#fde047"))
        elif status_clean in ("Medical Hold", "Rejected"):
            # Soft Rose
            return (("#ffe4e6", "#881337"), ("#9f1239", "#fda4af"))
        elif status_clean in ("Adopted", "Completed"):
            # Royal Lilac
            return (("#f3e8ff", "#581c87"), ("#6b21a8", "#e9d5ff"))
        elif status_clean in ("Interview Scheduled", "Active"):
            # Sky Cyan
            return (("#e0f2fe", "#0c4a6e"), ("#0369a1", "#7dd3fc"))
        elif status_clean in ("Archived", "Inactive"):
            # Clean Slate Neutral
            return (("#e2e8f0", "#1e293b"), ("#475569", "#94a3b8"))
        else:
            return (("#e2e8f0", "#1e293b"), ("#475569", "#94a3b8"))

    # ==========================================
    # CORNER RADII (Fluid, Modern Contours)
    # ==========================================
    RADIUS_CARD = 14
    RADIUS_INPUT = 8
    RADIUS_BTN = 9
    RADIUS_PILL = 20

    # ==========================================
    # TYPOGRAPHY SCALES (Segoe UI Modern Scale)
    # ==========================================
    FONT_FAMILY = "Segoe UI"

    @classmethod
    def font_hero(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=22, weight="bold")

    @classmethod
    def font_title(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=17, weight="bold")

    @classmethod
    def font_subtitle(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=13, weight="bold")

    @classmethod
    def font_body(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=12)

    @classmethod
    def font_body_bold(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=12, weight="bold")

    @classmethod
    def font_caption(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=11)

    @classmethod
    def font_caption_bold(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=11, weight="bold")

    @classmethod
    def font_tiny(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=10, weight="bold")

    # ==========================================
    # EMPTY STATE HELPER
    # ==========================================
    @classmethod
    def create_empty_state(cls, parent, icon="🐾", title="No records found", subtitle="Try adjusting your search or filters"):
        """Creates a modern, centered empty state container."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(expand=True, fill="both", pady=40)

        ctk.CTkLabel(
            frame,
            text=icon,
            font=ctk.CTkFont(size=44)
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            frame,
            text=title,
            font=cls.font_subtitle(),
            text_color=cls.TEXT_PRIMARY
        ).pack(pady=(0, 2))

        ctk.CTkLabel(
            frame,
            text=subtitle,
            font=cls.font_caption(),
            text_color=cls.TEXT_MUTED
        ).pack()

        return frame
