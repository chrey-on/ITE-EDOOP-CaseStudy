"""
Custom Dialogs & Modal Components for PurrfectMatch.
Replaces native Win32 Tkinter messagebox popups with modern,
theme-compliant CustomTkinter modals with smooth focus and clean layout.
"""

import customtkinter as ctk
from views.theme import Theme


class ConfirmModal(ctk.CTkToplevel):
    """
    Modern confirmation dialog (Yes/No or Confirm/Cancel) built with CustomTkinter.
    Ensures action buttons are never clipped and scales dynamically to message length.
    """
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        on_confirm,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        is_destructive: bool = False,
        icon: str = None,
        confirm_color=None,
        confirm_hover=None,
        width: int = 500,
        height: int = None
    ):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()

        self.on_confirm = on_confirm
        self.is_destructive = is_destructive
        self.icon_symbol = icon or ("⚠️" if is_destructive else "❓")
        self.confirm_color = confirm_color
        self.confirm_hover = confirm_hover

        # Compute optimal height to prevent button cutoff
        if height is None:
            lines = message.count("\n") + 1
            wrapped_extra = sum(max(0, len(line) // 46) for line in message.split("\n"))
            effective_lines = lines + wrapped_extra
            computed_height = max(270, 195 + effective_lines * 20)
            final_height = min(420, computed_height)
        else:
            final_height = height

        final_width = max(480, width)
        self.geometry(f"{final_width}x{final_height}")
        self.resizable(False, False)

        self._center_window(parent, final_width, final_height)
        self._build_ui(title, message, confirm_text, cancel_text)

    def _center_window(self, parent, width, height):
        parent.update_idletasks()
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = max(20, px + (pw // 2) - (width // 2))
        y = max(20, py + (ph // 2) - (height // 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self, title, message, confirm_text, cancel_text):
        self.configure(fg_color=Theme.BG_ROOT)

        card = ctk.CTkFrame(
            self,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        # 1. Action Buttons Row (PACKED AT THE BOTTOM FIRST so buttons are NEVER clipped)
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(side="bottom", fill="x", padx=18, pady=(12, 16))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        cancel_btn = ctk.CTkButton(
            btn_row,
            text=cancel_text,
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            cursor="hand2",
            command=self.destroy
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        # Resolve confirm button colors
        if self.confirm_color:
            cfg_color = self.confirm_color
            chover_color = self.confirm_hover or self.confirm_color
        elif self.is_destructive:
            cfg_color = Theme.DANGER
            chover_color = Theme.DANGER_HOVER
        else:
            cfg_color = Theme.PRIMARY
            chover_color = Theme.PRIMARY_HOVER

        confirm_btn = ctk.CTkButton(
            btn_row,
            text=confirm_text,
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=cfg_color,
            hover_color=chover_color,
            text_color="#ffffff",
            cursor="hand2",
            command=self._do_confirm
        )
        confirm_btn.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # 2. Subtle Divider Line above buttons
        divider = ctk.CTkFrame(card, height=1, fg_color=Theme.BORDER)
        divider.pack(side="bottom", fill="x", padx=16, pady=(0, 0))

        # 3. Content Area (Header + Message)
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(side="top", fill="both", expand=True, padx=16, pady=(16, 8))
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Left Icon Chip Badge Container
        if self.is_destructive:
            badge_bg = ("#fee2e2", "#450a0a")
            badge_border = ("#fca5a5", "#7f1d1d")
        elif self.icon_symbol in ("📦", "⚠️"):
            badge_bg = ("#fef3c7", "#382405")
            badge_border = ("#fde68a", "#78350f")
        elif self.icon_symbol in ("🎉", "✅"):
            badge_bg = ("#d1fae5", "#064e3b")
            badge_border = ("#a7f3d0", "#065f46")
        else:
            badge_bg = ("#ede9fe", "#261b40")
            badge_border = ("#ddd6fe", "#432874")

        icon_box = ctk.CTkFrame(
            content_frame,
            width=46,
            height=46,
            corner_radius=12,
            fg_color=badge_bg,
            border_width=1,
            border_color=badge_border
        )
        icon_box.grid(row=0, column=0, rowspan=2, padx=(0, 14), pady=(2, 0), sticky="nw")
        icon_box.grid_propagate(False)

        icon_lbl = ctk.CTkLabel(
            icon_box,
            text=self.icon_symbol,
            font=ctk.CTkFont(size=22)
        )
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        title_lbl = ctk.CTkLabel(
            content_frame,
            text=title,
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        )
        title_lbl.grid(row=0, column=1, sticky="w", pady=(2, 6))

        # Message
        msg_lbl = ctk.CTkLabel(
            content_frame,
            text=message,
            font=Theme.font_body(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="nw",
            wraplength=380,
            justify="left"
        )
        msg_lbl.grid(row=1, column=1, sticky="nsew", pady=(0, 4))

        # Bind Enter and Escape keys
        self.bind("<Return>", lambda e: self._do_confirm())
        self.bind("<Escape>", lambda e: self.destroy())

    def _do_confirm(self):
        self.destroy()
        if self.on_confirm:
            self.on_confirm()


class AlertModal(ctk.CTkToplevel):
    """
    Modern informational/alert dialog.
    Guarantees buttons are never clipped and uses modern badge styling.
    """
    def __init__(self, parent, title: str, message: str, alert_type: str = "info", width: int = 460, height: int = None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()

        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        self.icon_symbol = icons.get(alert_type, "ℹ️")
        self.alert_type = alert_type

        # Compute optimal height to prevent button cutoff
        if height is None:
            lines = message.count("\n") + 1
            wrapped_extra = sum(max(0, len(line) // 44) for line in message.split("\n"))
            effective_lines = lines + wrapped_extra
            computed_height = max(240, 180 + effective_lines * 20)
            final_height = min(380, computed_height)
        else:
            final_height = height

        final_width = max(440, width)
        self.geometry(f"{final_width}x{final_height}")
        self.resizable(False, False)

        self._center_window(parent, final_width, final_height)
        self._build_ui(title, message)

    def _center_window(self, parent, width, height):
        parent.update_idletasks()
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = max(20, px + (pw // 2) - (width // 2))
        y = max(20, py + (ph // 2) - (height // 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self, title, message):
        self.configure(fg_color=Theme.BG_ROOT)

        card = ctk.CTkFrame(
            self,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        # 1. OK Button (PACKED AT THE BOTTOM FIRST)
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(side="bottom", fill="x", padx=18, pady=(12, 16))

        ok_btn = ctk.CTkButton(
            btn_row,
            text="Got It",
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color="#ffffff",
            cursor="hand2",
            command=self.destroy
        )
        ok_btn.pack(fill="x")

        # 2. Subtle Divider
        divider = ctk.CTkFrame(card, height=1, fg_color=Theme.BORDER)
        divider.pack(side="bottom", fill="x", padx=16, pady=(0, 0))

        # 3. Content Frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(side="top", fill="both", expand=True, padx=16, pady=(16, 8))
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Badge container
        if self.alert_type == "error":
            badge_bg = ("#fee2e2", "#450a0a")
            badge_border = ("#fca5a5", "#7f1d1d")
        elif self.alert_type == "warning":
            badge_bg = ("#fef3c7", "#382405")
            badge_border = ("#fde68a", "#78350f")
        elif self.alert_type == "success":
            badge_bg = ("#d1fae5", "#064e3b")
            badge_border = ("#a7f3d0", "#065f46")
        else:
            badge_bg = ("#ede9fe", "#261b40")
            badge_border = ("#ddd6fe", "#432874")

        icon_box = ctk.CTkFrame(
            content_frame,
            width=46,
            height=46,
            corner_radius=12,
            fg_color=badge_bg,
            border_width=1,
            border_color=badge_border
        )
        icon_box.grid(row=0, column=0, rowspan=2, padx=(0, 14), pady=(2, 0), sticky="nw")
        icon_box.grid_propagate(False)

        icon_lbl = ctk.CTkLabel(
            icon_box,
            text=self.icon_symbol,
            font=ctk.CTkFont(size=22)
        )
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        title_lbl = ctk.CTkLabel(
            content_frame,
            text=title,
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        )
        title_lbl.grid(row=0, column=1, sticky="w", pady=(2, 6))

        # Message
        msg_lbl = ctk.CTkLabel(
            content_frame,
            text=message,
            font=Theme.font_body(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="nw",
            wraplength=340,
            justify="left"
        )
        msg_lbl.grid(row=1, column=1, sticky="nsew", pady=(0, 4))

        self.bind("<Return>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())
