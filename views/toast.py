"""
Toast Notification Component for PurrfectMatch.
Provides modern, floating, non-blocking in-app notification toasts
with auto-dismiss, smooth fading, and theme-compliant styling.
"""

import customtkinter as ctk
from views.theme import Theme


class ToastNotification(ctk.CTkFrame):
    """
    Floating in-app toast notification card that appears at the top or bottom of a parent window.
    """
    _active_toasts = []

    def __init__(
        self,
        parent,
        message: str,
        toast_type: str = "success",
        duration_ms: int = 3200,
        title: str = None
    ):
        # Configure colors based on type
        if toast_type == "success":
            icon = "✓"
            accent_color = Theme.SUCCESS[0]
            default_title = "Success"
        elif toast_type == "danger" or toast_type == "error":
            icon = "✕"
            accent_color = Theme.DANGER[0]
            default_title = "Notice"
        elif toast_type == "warning":
            icon = "!"
            accent_color = "#eab308"
            default_title = "Attention"
        else:
            icon = "ℹ"
            accent_color = Theme.PRIMARY[0]
            default_title = "Information"

        display_title = title or default_title

        super().__init__(
            parent,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=2,
            border_color=accent_color
        )
        self.parent = parent
        self.duration_ms = duration_ms

        # Content Layout
        self.grid_columnconfigure(1, weight=1)

        # Icon Pill
        icon_lbl = ctk.CTkLabel(
            self,
            text=f" {icon} ",
            font=Theme.font_subtitle(),
            fg_color=accent_color,
            text_color="#ffffff",
            corner_radius=12,
            width=28,
            height=28
        )
        icon_lbl.grid(row=0, column=0, rowspan=2, padx=(12, 10), pady=10)

        # Title
        title_lbl = ctk.CTkLabel(
            self,
            text=display_title,
            font=Theme.font_caption_bold(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        )
        title_lbl.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(10, 0))

        # Message Body
        msg_lbl = ctk.CTkLabel(
            self,
            text=message,
            font=Theme.font_caption(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
            wraplength=320,
            justify="left"
        )
        msg_lbl.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 10))

        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="✕",
            width=22,
            height=22,
            corner_radius=11,
            fg_color="transparent",
            hover_color=Theme.BG_CARD_HOVER,
            text_color=Theme.TEXT_MUTED,
            font=Theme.font_tiny(),
            command=self.dismiss
        )
        close_btn.grid(row=0, column=2, sticky="ne", padx=(0, 8), pady=(8, 0))

        # Position at top-right
        self.place(relx=0.98, rely=0.04, anchor="ne")
        self.lift()

        # Auto-dismiss timer
        self._timer_id = self.after(self.duration_ms, self.dismiss)

    def dismiss(self):
        """Removes the toast from screen cleanly."""
        try:
            if hasattr(self, "_timer_id"):
                self.after_cancel(self._timer_id)
            self.destroy()
        except Exception:
            pass

    @classmethod
    def show(cls, parent, message: str, toast_type: str = "success", title: str = None, duration_ms: int = 3200):
        """Static helper to show toast easily."""
        return cls(parent, message=message, toast_type=toast_type, title=title, duration_ms=duration_ms)
