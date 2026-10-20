"""
Customer / Adopter Portal View in CustomTkinter.
100% Native Python OOP Desktop GUI with Modern Obsidian & Slate Design System.
Features:
- Browse cat catalog with real photos, metadata chips, and interactive hover states.
- Hero Welcome Banner with live shelter statistics.
- Multi-criteria filtering (Gender, Age group, Spayed/Neutered) & fast search.
- Interactive Cat Profile & Photo Gallery modal with keyboard arrow navigation.
- Action-gated Auth Modal (Sign In / Register) with smooth inline validation.
- Direct Application modal with structured questionnaire and safety validation.
- 'My Applications' Adoption Journey Tracker with visual pipeline stepper.
- Official Adoption Certificate viewing & export for finalized adoptions.
- Dynamic Dark / Light mode toggle right in the header bar.
"""

from datetime import date
import customtkinter as ctk

from database.db_connection import DatabaseConnection
from controllers.cat_controller import CatController
from controllers.adopter_controller import AdopterController
from controllers.application_controller import ApplicationController
from controllers.image_service import ImageService
from views.image_viewer_modal import ImageViewerModal
from views.certificate_modal import AdoptionCertificateModal
from views.toast import ToastNotification
from views.dialogs import ConfirmModal, AlertModal
from views.theme import Theme
from models.adopter import Adopter
from models.application import AdoptionApplication


class CustomerAuthModal(ctk.CTkToplevel):
    """Centered modal for Guest Sign In / Registration with clean validation."""
    def __init__(self, parent, on_auth_success):
        super().__init__(parent)
        self.title("Sign In or Register to Adopt")
        self.geometry("480x570")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_auth_success = on_auth_success
        self.adopter_ctrl = AdopterController()

        self._center_modal(parent)
        self._build_ui()

    def _center_modal(self, parent):
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w, h = 480, 570
        x = max(0, px + (pw // 2) - (w // 2))
        y = max(0, py + (ph // 2) - (h // 2))
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        self.configure(fg_color=Theme.BG_ROOT)

        card = ctk.CTkFrame(
            self,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        # Header
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(
            hdr,
            text="🐾 Welcome to PurrfectMatch",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            hdr,
            text="Sign in or register an adopter account to submit your application.",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))

        # Tabview: Sign In vs Register
        self.tabview = ctk.CTkTabview(card, corner_radius=Theme.RADIUS_CARD)
        self.tabview.pack(fill="both", expand=True, padx=14, pady=(4, 12))

        tab_signin = self.tabview.add("🔑 Sign In")
        tab_signup = self.tabview.add("📝 Register Account")

        # -----------------------------
        # Tab 1: Sign In
        # -----------------------------
        ctk.CTkLabel(
            tab_signin,
            text="Contact Number or Registered Email:",
            font=Theme.font_caption_bold(),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=12, pady=(16, 4))

        self.login_entry = ctk.CTkEntry(
            tab_signin,
            placeholder_text="e.g. 0917-xxx-xxxx or email@example.com",
            height=40,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            placeholder_text_color=Theme.TEXT_MUTED
        )
        self.login_entry.pack(fill="x", padx=12, pady=(0, 6))
        self.login_entry.bind("<Return>", lambda e: self._handle_signin())

        self.signin_feedback = ctk.CTkLabel(
            tab_signin,
            text="",
            font=Theme.font_caption(),
            text_color=Theme.DANGER[0]
        )
        self.signin_feedback.pack(pady=4)

        ctk.CTkButton(
            tab_signin,
            text="Continue to Adoption 🐾",
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.PRIMARY_TEXT,
            font=Theme.font_body_bold(),
            cursor="hand2",
            command=self._handle_signin
        ).pack(fill="x", padx=12, pady=(12, 12))

        # -----------------------------
        # Tab 2: Register
        # -----------------------------
        reg_scroll = ctk.CTkScrollableFrame(tab_signup, fg_color="transparent")
        reg_scroll.pack(fill="both", expand=True, padx=6, pady=4)

        ctk.CTkLabel(reg_scroll, text="Full Name *", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.reg_name = ctk.CTkEntry(reg_scroll, placeholder_text="e.g. Maria Santos", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER, text_color=Theme.TEXT_PRIMARY)
        self.reg_name.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Contact Number *", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.reg_contact = ctk.CTkEntry(reg_scroll, placeholder_text="e.g. 0917-123-4567", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER, text_color=Theme.TEXT_PRIMARY)
        self.reg_contact.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Email Address", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.reg_email = ctk.CTkEntry(reg_scroll, placeholder_text="maria@example.com", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER, text_color=Theme.TEXT_PRIMARY)
        self.reg_email.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Home Address *", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.reg_address = ctk.CTkEntry(reg_scroll, placeholder_text="Barangay, City, Province", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER, text_color=Theme.TEXT_PRIMARY)
        self.reg_address.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Housing Environment *", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.reg_housing = ctk.CTkOptionMenu(
            reg_scroll,
            values=["House with Yard", "Apartment", "Condo (Pet-Friendly)", "Townhouse"],
            height=36,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BORDER_LIGHT,
            text_color=Theme.TEXT_PRIMARY
        )
        self.reg_housing.pack(fill="x", pady=(0, 10))

        self.reg_feedback = ctk.CTkLabel(reg_scroll, text="", font=Theme.font_caption(), text_color=Theme.DANGER[0])
        self.reg_feedback.pack(pady=2)

        ctk.CTkButton(
            reg_scroll,
            text="Create Profile & Continue 🐾",
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            text_color=Theme.SUCCESS_TEXT,
            font=Theme.font_body_bold(),
            cursor="hand2",
            command=self._handle_register
        ).pack(fill="x", pady=(6, 12))

    def _handle_signin(self):
        val = self.login_entry.get().strip()
        if not val:
            self.signin_feedback.configure(text="Please enter your contact number or email.")
            return

        results = self.adopter_ctrl.search_adopters(val)
        if results:
            adopter = results[0]
            self.destroy()
            self.on_auth_success(adopter)
        else:
            self.signin_feedback.configure(text="No account found. Click 'Register Account' to create one.")

    def _handle_register(self):
        name = self.reg_name.get().strip()
        contact = self.reg_contact.get().strip()
        address = self.reg_address.get().strip()

        if not name or not contact or not address:
            self.reg_feedback.configure(text="Please fill in all required fields (*).")
            return

        new_adopter = Adopter(
            full_name=name,
            contact_number=contact,
            email=self.reg_email.get().strip(),
            address=address,
            housing_type=self.reg_housing.get()
        )

        ok, res = self.adopter_ctrl.create_adopter(new_adopter)
        if ok:
            new_adopter._id = res
            self.destroy()
            self.on_auth_success(new_adopter)
        else:
            self.reg_feedback.configure(text=f"Error: {res}")


class CustomerApplyModal(ctk.CTkToplevel):
    """Centered modal for submitting an adoption application with structured questions."""
    def __init__(self, parent, cat, customer, on_submitted):
        super().__init__(parent)
        self.title(f"Apply to Adopt {cat.name}")
        self.geometry("560x640")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.cat = cat
        self.customer = customer
        self.portal_parent = parent
        self.on_submitted = on_submitted
        self.app_ctrl = ApplicationController()

        self._center_modal(parent)
        self._build_ui()

    def _center_modal(self, parent):
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w, h = 560, 640
        x = max(0, px + (pw // 2) - (w // 2))
        y = max(0, py + (ph // 2) - (h // 2))
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        self.configure(fg_color=Theme.BG_ROOT)

        card = ctk.CTkFrame(
            self,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        # 1. Action Buttons Row (PACKED AT THE BOTTOM FIRST to prevent cutoff)
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=18, pady=(12, 16))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            command=self.destroy
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="Submit Adoption Request 🐾",
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            text_color=Theme.SUCCESS_TEXT,
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            command=self._handle_submit
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # Divider
        ctk.CTkFrame(card, height=1, fg_color=Theme.BORDER).pack(side="bottom", fill="x", padx=18, pady=(0, 0))

        # 2. Scrollable Body
        body_scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        body_scroll.pack(side="top", fill="both", expand=True, padx=16, pady=(16, 8))

        # Title Header
        ctk.CTkLabel(
            body_scroll,
            text=f"🐾 Apply to Adopt {self.cat.name}",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            body_scroll,
            text="Please verify your applicant information and share details about your home.",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 12))

        # Cat Summary Card
        cat_card = ctk.CTkFrame(body_scroll, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER, corner_radius=10)
        cat_card.pack(fill="x", pady=(0, 10))
        cat_card.grid_columnconfigure(1, weight=1)

        ctk_img = ImageService.get_ctk_image(self.cat.primary_image, size=(75, 75))
        if ctk_img:
            img_lbl = ctk.CTkLabel(cat_card, image=ctk_img, text="")
            img_lbl.grid(row=0, column=0, rowspan=3, padx=(12, 10), pady=10)
        else:
            img_lbl = ctk.CTkLabel(cat_card, text="🐱", font=ctk.CTkFont(size=32))
            img_lbl.grid(row=0, column=0, rowspan=3, padx=(14, 10), pady=10)

        info_col = ctk.CTkFrame(cat_card, fg_color="transparent")
        info_col.grid(row=0, column=1, rowspan=3, padx=(0, 12), pady=10, sticky="nsew")

        name_row = ctk.CTkFrame(info_col, fg_color="transparent")
        name_row.pack(fill="x")
        ctk.CTkLabel(name_row, text=self.cat.name, font=Theme.font_subtitle(), text_color=Theme.TEXT_PRIMARY).pack(side="left")

        status_bg, status_txt = Theme.get_status_colors(self.cat.adoption_status)
        ctk.CTkLabel(
            name_row,
            text=f"  {self.cat.adoption_status}  ",
            font=Theme.font_tiny(),
            fg_color=status_bg,
            text_color=status_txt,
            corner_radius=Theme.RADIUS_PILL
        ).pack(side="right")

        ctk.CTkLabel(info_col, text=f"{self.cat.breed} • {self.cat.color}", font=Theme.font_caption_bold(), text_color=Theme.TEXT_ACCENT).pack(anchor="w", pady=(1, 2))
        ctk.CTkLabel(info_col, text=f"Age: {self.cat.formatted_age}  |  Gender: {self.cat.gender}  |  Health: {self.cat.health_status}", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")

        # Adopter Info Card
        adopter_card = ctk.CTkFrame(body_scroll, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER, corner_radius=10)
        adopter_card.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(adopter_card, text=f"👤 Applicant: {self.customer.full_name}", font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(8, 2))
        ctk.CTkLabel(adopter_card, text=f"📞 {self.customer.contact_number}   🏠 {self.customer.address} ({self.customer.housing_type or 'General'})", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", padx=14, pady=(0, 8))

        # Questionnaire / Other Pets
        ctk.CTkLabel(body_scroll, text="Do you currently have other pets?", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.other_pets_menu = ctk.CTkOptionMenu(
            body_scroll,
            values=["No other pets", "Yes, friendly cats", "Yes, dogs", "Yes, other small pets"],
            height=34,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BORDER_LIGHT,
            text_color=Theme.TEXT_PRIMARY
        )
        self.other_pets_menu.pack(fill="x", pady=(0, 10))

        # Statement / Notes
        ctk.CTkLabel(body_scroll, text="Why would you like to adopt this cat? / Care Notes:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.notes_box = ctk.CTkTextbox(
            body_scroll,
            height=85,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY
        )
        self.notes_box.pack(fill="x", pady=(0, 10))

    def _handle_submit(self):
        user_notes = self.notes_box.get("1.0", "end").strip()
        pets_info = self.other_pets_menu.get()

        full_notes = f"Household Pets: {pets_info}"
        if user_notes:
            full_notes += f"\nApplicant Statement: {user_notes}"

        app = AdoptionApplication(
            cat_id=self.cat.id,
            adopter_id=self.customer.id,
            notes=full_notes
        )

        ok, res = self.app_ctrl.create_application(app)
        if ok:
            ToastNotification.show(
                self.portal_parent,
                f"Application for {self.cat.name} submitted! Shelter caretakers will review it.",
                toast_type="success",
                title="Application Submitted 🐾"
            )
            self.destroy()
            self.on_submitted()
        else:
            AlertModal(self, title="Submission Error", message=str(res), alert_type="error")


class CustomerCatDetailModal(ctk.CTkToplevel):
    """
    Rich modal displaying complete Cat Profile and multi-photo gallery.
    Supports thumbnail carousel, fullscreen photo inspection, keyboard navigation,
    and direct adoption submission.
    """
    def __init__(self, parent, cat, customer=None, on_adopt=None):
        super().__init__(parent)
        self.title(f"{cat.name} - Profile & Gallery")
        self.geometry("680x760")
        self.minsize(600, 680)
        self.transient(parent)
        self.grab_set()

        self.cat = cat
        self.customer = customer
        self.on_adopt = on_adopt
        self.images = list(cat.images) if cat.images else []
        self.current_idx = 0
        self.thumb_buttons = []

        self._center_modal(parent)
        self._build_ui()
        if self.images:
            self._update_photo()

        # Keyboard Navigation for gallery
        self.bind("<Left>", lambda e: self._prev_photo())
        self.bind("<Right>", lambda e: self._next_photo())
        self.bind("<Escape>", lambda e: self.destroy())

    def _center_modal(self, parent):
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w, h = 680, 760
        x = max(0, px + (pw // 2) - (w // 2))
        y = max(0, py + (ph // 2) - (h // 2))
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        self.configure(fg_color=Theme.BG_ROOT)

        card = ctk.CTkFrame(
            self,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        card.pack(fill="both", expand=True, padx=16, pady=16)

        # 1. Action Buttons Row (PACKED AT THE BOTTOM FIRST)
        act_bar = ctk.CTkFrame(card, fg_color="transparent")
        act_bar.pack(side="bottom", fill="x", padx=18, pady=(12, 16))
        act_bar.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            act_bar,
            text="Close",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            command=self.destroy
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        if self.cat.adoption_status == "Available":
            ctk.CTkButton(
                act_bar,
                text=f"🐾 Apply to Adopt {self.cat.name}",
                fg_color=Theme.SUCCESS,
                hover_color=Theme.SUCCESS_HOVER,
                text_color=Theme.SUCCESS_TEXT,
                height=40,
                corner_radius=Theme.RADIUS_BTN,
                font=Theme.font_subtitle(),
                cursor="hand2",
                command=self._handle_adopt
            ).grid(row=0, column=1, padx=(6, 0), sticky="ew")
        else:
            ctk.CTkButton(
                act_bar,
                text=f"Status: {self.cat.adoption_status}",
                fg_color=Theme.SECONDARY,
                text_color=Theme.TEXT_MUTED,
                state="disabled",
                height=40,
                corner_radius=Theme.RADIUS_BTN
            ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # Divider
        ctk.CTkFrame(card, height=1, fg_color=Theme.BORDER).pack(side="bottom", fill="x", padx=18, pady=(0, 0))

        # 2. Header Bar
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(side="top", fill="x", padx=18, pady=(16, 8))
        hdr.grid_columnconfigure(0, weight=1)

        title_col = ctk.CTkFrame(hdr, fg_color="transparent")
        title_col.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_col, text=self.cat.name, font=Theme.font_hero(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(title_col, text=f"{self.cat.breed}  •  {self.cat.color}", font=Theme.font_caption_bold(), text_color=Theme.TEXT_ACCENT).pack(anchor="w")

        status_bg, status_txt = Theme.get_status_colors(self.cat.adoption_status)
        ctk.CTkLabel(
            hdr,
            text=f"  {self.cat.adoption_status}  ",
            font=Theme.font_caption_bold(),
            fg_color=status_bg,
            text_color=status_txt,
            corner_radius=Theme.RADIUS_PILL,
            padx=12,
            pady=4
        ).grid(row=0, column=1, sticky="e")

        # 3. Scrollable Main Content
        scroll_body = ctk.CTkScrollableFrame(card, fg_color="transparent")
        scroll_body.pack(side="top", fill="both", expand=True, padx=16, pady=(4, 8))

        # Photo Gallery Container
        gallery_frame = ctk.CTkFrame(scroll_body, corner_radius=10, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER)
        gallery_frame.pack(fill="x", pady=(0, 14))

        if self.images:
            # Main Photo Area
            self.photo_display_frame = ctk.CTkFrame(gallery_frame, height=290, fg_color="transparent", corner_radius=8)
            self.photo_display_frame.pack(fill="x", padx=10, pady=(10, 4))
            self.photo_display_frame.pack_propagate(False)

            self.main_photo_lbl = ctk.CTkLabel(self.photo_display_frame, text="", cursor="hand2")
            self.main_photo_lbl.pack(expand=True, fill="both")
            self.main_photo_lbl.bind("<Button-1>", lambda e: self._open_fullscreen_viewer())

            # Hint & Controls Row
            hint_row = ctk.CTkFrame(gallery_frame, fg_color="transparent")
            hint_row.pack(fill="x", padx=14, pady=(4, 6))
            hint_row.grid_columnconfigure(0, weight=1)

            self.hint_lbl = ctk.CTkLabel(
                hint_row,
                text=f"🔍 Click photo to view fullscreen • Photo 1 of {len(self.images)}",
                font=Theme.font_caption(),
                text_color=Theme.TEXT_SECONDARY
            )
            self.hint_lbl.grid(row=0, column=0, sticky="w")

            if len(self.images) > 1:
                nav_btns = ctk.CTkFrame(hint_row, fg_color="transparent")
                nav_btns.grid(row=0, column=1, sticky="e")
                ctk.CTkButton(
                    nav_btns,
                    text="◀",
                    width=32,
                    height=26,
                    corner_radius=6,
                    fg_color=Theme.SECONDARY,
                    hover_color=Theme.SECONDARY_HOVER,
                    text_color=Theme.SECONDARY_TEXT,
                    font=Theme.font_caption_bold(),
                    command=self._prev_photo
                ).pack(side="left", padx=2)
                ctk.CTkButton(
                    nav_btns,
                    text="▶",
                    width=32,
                    height=26,
                    corner_radius=6,
                    fg_color=Theme.SECONDARY,
                    hover_color=Theme.SECONDARY_HOVER,
                    text_color=Theme.SECONDARY_TEXT,
                    font=Theme.font_caption_bold(),
                    command=self._next_photo
                ).pack(side="left", padx=2)

                # Thumbnail Strip
                self.thumb_strip = ctk.CTkScrollableFrame(gallery_frame, orientation="horizontal", height=66, fg_color="transparent")
                self.thumb_strip.pack(fill="x", padx=10, pady=(0, 10))

                for i, img_path in enumerate(self.images):
                    thumb_img = ImageService.get_ctk_image(img_path, size=(52, 52))
                    btn = ctk.CTkButton(
                        self.thumb_strip,
                        image=thumb_img,
                        text="",
                        width=56,
                        height=56,
                        corner_radius=8,
                        fg_color=Theme.BG_CARD,
                        border_width=0,
                        hover_color=Theme.BORDER_ACCENT,
                        command=lambda idx=i: self._select_photo(idx)
                    )
                    btn.pack(side="left", padx=3, pady=2)
                    self.thumb_buttons.append(btn)
        else:
            no_img_frame = ctk.CTkFrame(gallery_frame, height=180, fg_color="transparent")
            no_img_frame.pack(fill="x", padx=10, pady=20)
            ctk.CTkLabel(no_img_frame, text="🐱\nNo Photos Attached", font=Theme.font_title(), text_color=Theme.TEXT_MUTED).pack(expand=True)

        # Profile Specs Grid
        specs_frame = ctk.CTkFrame(scroll_body, corner_radius=10, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER)
        specs_frame.pack(fill="x", pady=(0, 12))
        specs_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            specs_frame,
            text="Profile & Health Overview",
            font=Theme.font_subtitle(),
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 6))

        specs = [
            ("🎂 AGE", self.cat.formatted_age),
            ("⚧ GENDER", self.cat.gender),
            ("🎨 COAT COLOR", self.cat.color),
            ("🩺 HEALTH STATUS", self.cat.health_status),
            ("✂️ SPAYED / NEUTERED", "Yes ✓" if self.cat.is_spayed_neutered else "No"),
            ("📅 INTAKE DATE", self.cat.intake_date or "Unknown"),
            ("🏠 SHELTER HOUSING", self.cat.cage_number or "General Ward"),
            ("📷 ATTACHED PHOTOS", f"{len(self.images)} photo(s)")
        ]

        for s_idx, (k, v) in enumerate(specs):
            r = 1 + (s_idx // 2)
            c = s_idx % 2
            cell = ctk.CTkFrame(specs_frame, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER, corner_radius=6)
            cell.grid(row=r, column=c, padx=8, pady=4, sticky="ew")
            ctk.CTkLabel(cell, text=k, font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED).pack(side="left", padx=10, pady=7)
            ctk.CTkLabel(cell, text=v, font=Theme.font_caption_bold(), text_color=Theme.TEXT_PRIMARY).pack(side="right", padx=10, pady=7)

        # Personality & Caregiver Notes
        bio_frame = ctk.CTkFrame(scroll_body, corner_radius=10, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER)
        bio_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(bio_frame, text="Caregiver Notes & Personality", font=Theme.font_subtitle(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(12, 4))
        bio_text = self.cat.notes.strip() if self.cat.notes else "This gentle cat is friendly, adaptable, and eager to meet a loving forever family."
        ctk.CTkLabel(bio_frame, text=bio_text, font=Theme.font_body(), text_color=Theme.TEXT_SECONDARY, wraplength=580, justify="left").pack(anchor="w", padx=14, pady=(0, 14))

    def _open_fullscreen_viewer(self):
        if self.images:
            ImageViewerModal(self, self.images, initial_index=self.current_idx, title_prefix=f"{self.cat.name} Photos")

    def _update_photo(self):
        if not self.images:
            return
        img_path = self.images[self.current_idx]
        ctk_img = ImageService.get_ctk_image(img_path, size=(500, 280))
        if ctk_img:
            self.main_photo_lbl.configure(image=ctk_img, text="")
        else:
            self.main_photo_lbl.configure(image=None, text="Image preview unavailable")

        if hasattr(self, 'hint_lbl'):
            self.hint_lbl.configure(text=f"🔍 Click photo to view fullscreen • Photo {self.current_idx + 1} of {len(self.images)}")

        if hasattr(self, 'thumb_buttons'):
            for i, btn in enumerate(self.thumb_buttons):
                if i == self.current_idx:
                    btn.configure(border_width=2, border_color=Theme.BORDER_ACCENT[0], fg_color=Theme.BG_CARD)
                else:
                    btn.configure(border_width=0, fg_color=Theme.BG_CARD_ALT)

    def _select_photo(self, idx):
        self.current_idx = idx
        self._update_photo()

    def _prev_photo(self):
        if self.images:
            self.current_idx = (self.current_idx - 1) % len(self.images)
            self._update_photo()

    def _next_photo(self):
        if self.images:
            self.current_idx = (self.current_idx + 1) % len(self.images)
            self._update_photo()

    def _handle_adopt(self):
        cat = self.cat
        self.destroy()
        if self.on_adopt:
            self.on_adopt(cat)


class CustomerPortalView(ctk.CTkFrame):
    """
    Main Public / Adopter view in CustomTkinter.
    Provides browsing catalog, responsive filters, applicant tracking pipeline,
    and adoption certificate viewing.
    """
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.master = master

        self.current_customer = None
        self.cat_ctrl = CatController()
        self.app_ctrl = ApplicationController()

        self.active_tab = "catalog"
        self._build_ui()
        self.refresh_catalog()

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ==========================================
        # TOP HEADER BAR
        # ==========================================
        header = ctk.CTkFrame(self, height=64, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 12))
        header.grid_columnconfigure(1, weight=1)

        # Brand Title + Pill
        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=18, pady=12, sticky="w")
        ctk.CTkLabel(brand_frame, text="🐾 PurrfectMatch", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(
            brand_frame,
            text=" Adopter Portal ",
            font=Theme.font_tiny(),
            fg_color=Theme.BG_CARD_ALT,
            text_color=Theme.TEXT_MUTED,
            corner_radius=Theme.RADIUS_PILL
        ).pack(side="left", padx=(10, 6))

        db_type = DatabaseConnection().get_db_type()
        db_icon = "🟢" if "MySQL" in db_type else "🔵"
        ctk.CTkLabel(
            brand_frame,
            text=f" {db_icon} {db_type} ",
            font=Theme.font_tiny(),
            fg_color=Theme.BG_CARD_ALT,
            text_color=Theme.TEXT_MUTED,
            corner_radius=Theme.RADIUS_PILL
        ).pack(side="left")

        # Nav Buttons (Segmented look)
        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.grid(row=0, column=1, padx=10, pady=10)

        self.nav_catalog_btn = ctk.CTkButton(
            nav_frame,
            text="🐱 Browse Rescues",
            width=135,
            height=34,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_caption_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=lambda: self._switch_tab("catalog")
        )
        self.nav_catalog_btn.pack(side="left", padx=4)

        self.nav_apps_btn = ctk.CTkButton(
            nav_frame,
            text="📋 My Applications",
            width=140,
            height=34,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_caption_bold(),
            fg_color=Theme.SECONDARY,
            text_color=Theme.SECONDARY_TEXT,
            hover_color=Theme.SECONDARY_HOVER,
            command=lambda: self._switch_tab("applications")
        )
        self.nav_apps_btn.pack(side="left", padx=4)

        # Right Controls: Dark/Light Mode Switcher + Auth Info
        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.grid(row=0, column=2, padx=18, pady=10, sticky="e")

        # Appearance Mode Toggle Button
        current_mode = ctk.get_appearance_mode()
        self.mode_btn = ctk.CTkButton(
            right_frame,
            text="🌙 Dark" if current_mode == "Light" else "☀️ Light",
            width=75,
            height=32,
            corner_radius=Theme.RADIUS_BTN,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            font=Theme.font_tiny(),
            cursor="hand2",
            command=self._toggle_appearance_mode
        )
        self.mode_btn.pack(side="left", padx=(0, 8))

        self.auth_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        self.auth_frame.pack(side="left")
        self._update_auth_header()

        # ==========================================
        # CONTENT CONTAINER
        # ==========================================
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # ------------------------------------------
        # TAB 1: CATALOG FRAME
        # ------------------------------------------
        self.catalog_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.catalog_frame.grid(row=0, column=0, sticky="nsew")
        self.catalog_frame.grid_rowconfigure(2, weight=1)
        self.catalog_frame.grid_columnconfigure(0, weight=1)

        # Hero Banner
        self.hero_banner = ctk.CTkFrame(self.catalog_frame, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER)
        self.hero_banner.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.hero_banner.grid_columnconfigure(0, weight=1)

        hero_inner = ctk.CTkFrame(self.hero_banner, fg_color="transparent")
        hero_inner.pack(fill="x", padx=20, pady=14)
        hero_inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hero_inner,
            text="Find Your Purrfect Companion 🐾",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            hero_inner,
            text="Meet gentle shelter rescues ready for their forever families. View multi-photo galleries and apply online.",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_SECONDARY
        ).grid(row=1, column=0, sticky="w", pady=(2, 8))

        # Quick Stats Chips Row
        self.stats_row = ctk.CTkFrame(hero_inner, fg_color="transparent")
        self.stats_row.grid(row=2, column=0, sticky="w")

        self.chip_avail = ctk.CTkLabel(
            self.stats_row,
            text="🐾 Loading...",
            font=Theme.font_tiny(),
            fg_color=("#d1fae5", "#064e3b"),
            text_color=("#065f46", "#6ee7b7"),
            corner_radius=Theme.RADIUS_PILL,
            padx=10,
            pady=3
        )
        self.chip_avail.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            self.stats_row,
            text="🩺 Health Checked & Vaccinated",
            font=Theme.font_tiny(),
            fg_color=("#ede9fe", "#261b40"),
            text_color=("#6d28d9", "#c084fc"),
            corner_radius=Theme.RADIUS_PILL,
            padx=10,
            pady=3
        ).pack(side="left", padx=(0, 8))

        self.chip_rehomed = ctk.CTkLabel(
            self.stats_row,
            text="💖 Rehomed",
            font=Theme.font_tiny(),
            fg_color=("#fce7f3", "#3b1227"),
            text_color=("#be185d", "#f472b6"),
            corner_radius=Theme.RADIUS_PILL,
            padx=10,
            pady=3
        )
        self.chip_rehomed.pack(side="left")

        # Search & Filter Controls Bar
        filter_bar = ctk.CTkFrame(self.catalog_frame, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER)
        filter_bar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search available cats by name, breed, or color...",
            height=36,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            placeholder_text_color=Theme.TEXT_MUTED
        )
        self.search_entry.grid(row=0, column=0, padx=(14, 10), pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_catalog())

        # Gender Filter
        self.gender_filter = ctk.CTkOptionMenu(
            filter_bar,
            values=["All Genders", "Female", "Male"],
            width=120,
            height=36,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BORDER_LIGHT,
            text_color=Theme.TEXT_PRIMARY,
            command=lambda val: self.refresh_catalog()
        )
        self.gender_filter.grid(row=0, column=1, padx=(0, 8), pady=10)

        # Age Group Filter
        self.age_filter = ctk.CTkOptionMenu(
            filter_bar,
            values=["All Ages", "Kittens (< 1 yr)", "Young (1-3 yrs)", "Adults (3+ yrs)"],
            width=140,
            height=36,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BORDER_LIGHT,
            text_color=Theme.TEXT_PRIMARY,
            command=lambda val: self.refresh_catalog()
        )
        self.age_filter.grid(row=0, column=2, padx=(0, 8), pady=10)

        # Results Counter Badge
        self.results_badge = ctk.CTkLabel(
            filter_bar,
            text="0 Cats",
            font=Theme.font_tiny(),
            fg_color=Theme.BG_CARD_ALT,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Theme.RADIUS_PILL,
            padx=10,
            pady=4
        )
        self.results_badge.grid(row=0, column=3, padx=(0, 14), pady=10)

        # Scrollable Cards Grid
        self.cards_scroll = ctk.CTkScrollableFrame(self.catalog_frame, corner_radius=Theme.RADIUS_CARD, fg_color="transparent")
        self.cards_scroll.grid(row=2, column=0, sticky="nsew")
        self.cards_scroll.grid_columnconfigure((0, 1, 2), weight=1)

        # ------------------------------------------
        # TAB 2: MY APPLICATIONS FRAME
        # ------------------------------------------
        self.apps_frame = ctk.CTkFrame(self.content_container, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER)
        self.apps_frame.grid_rowconfigure(1, weight=1)
        self.apps_frame.grid_columnconfigure(0, weight=1)

        apps_hdr = ctk.CTkFrame(self.apps_frame, fg_color="transparent")
        apps_hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        apps_hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            apps_hdr,
            text="📋 My Adoption Journey & Applications",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            apps_hdr,
            text="Track your application progress from review to official pickup.",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_SECONDARY
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.user_apps_scroll = ctk.CTkScrollableFrame(self.apps_frame, fg_color="transparent")
        self.user_apps_scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.user_apps_scroll.grid_columnconfigure(0, weight=1)

    def _toggle_appearance_mode(self):
        new_mode = "Dark" if ctk.get_appearance_mode() == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        self.mode_btn.configure(text="🌙 Dark" if new_mode == "Light" else "☀️ Light")

    def _update_auth_header(self):
        for widget in self.auth_frame.winfo_children():
            widget.destroy()

        if self.current_customer:
            user_chip = ctk.CTkFrame(self.auth_frame, fg_color=Theme.BG_CARD_ALT, corner_radius=Theme.RADIUS_PILL, border_width=1, border_color=Theme.BORDER)
            user_chip.pack(side="left", padx=4)

            ctk.CTkLabel(
                user_chip,
                text=f"👤 {self.current_customer.full_name}",
                font=Theme.font_caption_bold(),
                text_color=Theme.TEXT_PRIMARY
            ).pack(side="left", padx=(10, 6), pady=4)

            ctk.CTkButton(
                self.auth_frame,
                text="Sign Out",
                width=72,
                height=30,
                corner_radius=Theme.RADIUS_BTN,
                fg_color=Theme.DANGER,
                hover_color=Theme.DANGER_HOVER,
                text_color=Theme.DANGER_TEXT,
                font=Theme.font_caption_bold(),
                cursor="hand2",
                command=self._logout
            ).pack(side="left", padx=(4, 0))
        else:
            ctk.CTkButton(
                self.auth_frame,
                text="Sign In / Register",
                width=140,
                height=34,
                corner_radius=Theme.RADIUS_BTN,
                fg_color=Theme.PRIMARY,
                hover_color=Theme.PRIMARY_HOVER,
                font=Theme.font_caption_bold(),
                cursor="hand2",
                command=self._open_auth_modal
            ).pack(side="left")

    def _switch_tab(self, tab):
        self.active_tab = tab
        if tab == "catalog":
            self.apps_frame.grid_forget()
            self.catalog_frame.grid(row=0, column=0, sticky="nsew")
            self.nav_catalog_btn.configure(fg_color=Theme.PRIMARY, hover_color=Theme.PRIMARY_HOVER, text_color="#ffffff")
            self.nav_apps_btn.configure(fg_color=Theme.SECONDARY, hover_color=Theme.SECONDARY_HOVER, text_color=Theme.SECONDARY_TEXT)
            self.refresh_catalog()
        else:
            self.catalog_frame.grid_forget()
            self.apps_frame.grid(row=0, column=0, sticky="nsew")
            self.nav_catalog_btn.configure(fg_color=Theme.SECONDARY, hover_color=Theme.SECONDARY_HOVER, text_color=Theme.SECONDARY_TEXT)
            self.nav_apps_btn.configure(fg_color=Theme.PRIMARY, hover_color=Theme.PRIMARY_HOVER, text_color="#ffffff")
            self._load_user_applications()

    def refresh_catalog(self):
        """Fetches and displays rescue cats filtered by user criteria."""
        for widget in self.cards_scroll.winfo_children():
            widget.destroy()

        cats = self.cat_ctrl.get_all_cats()
        search = self.search_entry.get().strip().lower()
        gender_val = self.gender_filter.get()
        age_val = self.age_filter.get()

        # Update stats chips
        avail_count = len([c for c in cats if c.adoption_status == "Available"])
        rehomed_count = len([c for c in cats if c.adoption_status == "Adopted"])
        self.chip_avail.configure(text=f"🐾 {avail_count} Rescues Ready for Adoption")
        self.chip_rehomed.configure(text=f"💖 {rehomed_count} Happily Rehomed")

        # Public filter: show Available or Pending cats
        filtered = []
        for c in cats:
            if c.adoption_status in ["Medical Hold", "Adopted"]:
                continue
            if search and (search not in c.name.lower() and search not in c.breed.lower() and search not in c.color.lower()):
                continue
            if gender_val != "All Genders" and c.gender != gender_val:
                continue
            if age_val == "Kittens (< 1 yr)" and c.age_months >= 12:
                continue
            elif age_val == "Young (1-3 yrs)" and not (12 <= c.age_months < 36):
                continue
            elif age_val == "Adults (3+ yrs)" and c.age_months < 36:
                continue

            filtered.append(c)

        count = len(filtered)
        self.results_badge.configure(text=f"{count} Cat{'s' if count != 1 else ''} Found")

        if not filtered:
            empty_box = Theme.create_empty_state(
                self.cards_scroll,
                icon="🐱",
                title="No Rescue Cats Match Your Filters",
                subtitle="Try clearing your search or switching gender/age filters."
            )
            empty_box.grid(row=0, column=0, columnspan=3, pady=60)
            return

        for idx, cat in enumerate(filtered):
            row = idx // 3
            col = idx % 3

            # Card Container
            card = ctk.CTkFrame(
                self.cards_scroll,
                corner_radius=Theme.RADIUS_CARD,
                fg_color=Theme.BG_CARD,
                border_width=1,
                border_color=Theme.BORDER
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            # Photo Container (185px high, clickable)
            photo_frame = ctk.CTkFrame(card, height=185, fg_color=Theme.BG_CARD_ALT, corner_radius=10)
            photo_frame.pack(fill="x", padx=10, pady=(10, 6))
            photo_frame.pack_propagate(False)

            ctk_img = ImageService.get_ctk_image(cat.primary_image, size=(280, 185))
            if ctk_img:
                photo_lbl = ctk.CTkLabel(photo_frame, image=ctk_img, text="", cursor="hand2")
                photo_lbl.pack(expand=True, fill="both")
                photo_lbl.bind("<Button-1>", lambda e, c=cat: self._open_cat_detail(c))
            else:
                photo_lbl = ctk.CTkLabel(photo_frame, text="🐱\nPhoto Coming Soon", font=Theme.font_subtitle(), text_color=Theme.TEXT_MUTED, cursor="hand2")
                photo_lbl.pack(expand=True, fill="both")
                photo_lbl.bind("<Button-1>", lambda e, c=cat: self._open_cat_detail(c))

            # Floating Status Pill on Top-Left of Image
            status_bg, status_txt = Theme.get_status_colors(cat.adoption_status)
            status_chip = ctk.CTkLabel(
                photo_frame,
                text=f"  {cat.adoption_status}  ",
                font=Theme.font_tiny(),
                fg_color=status_bg,
                text_color=status_txt,
                corner_radius=Theme.RADIUS_PILL
            )
            status_chip.place(relx=0.04, rely=0.06, anchor="nw")

            # Floating Photo Count Badge on Bottom-Right of Image
            if len(cat.images) > 1:
                badge = ctk.CTkLabel(
                    photo_frame,
                    text=f" 📷 {len(cat.images)} Photos ",
                    font=Theme.font_tiny(),
                    fg_color=("#181426", "#0f172a"),
                    text_color="#ffffff",
                    corner_radius=12
                )
                badge.place(relx=0.96, rely=0.92, anchor="se")

            # Card Content Container
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=14, pady=(6, 12))

            # Title Row: Name & Breed
            title_row = ctk.CTkFrame(content, fg_color="transparent")
            title_row.pack(fill="x")
            ctk.CTkLabel(title_row, text=cat.name, font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY).pack(side="left")

            ctk.CTkLabel(content, text=f"{cat.breed} • {cat.color}", font=Theme.font_caption_bold(), text_color=Theme.TEXT_ACCENT).pack(anchor="w", pady=(1, 6))

            # Trait Chips Row
            traits_row = ctk.CTkFrame(content, fg_color="transparent")
            traits_row.pack(fill="x", pady=(0, 10))

            gender_icon = "♀" if cat.gender == "Female" else "♂"
            ctk.CTkLabel(
                traits_row,
                text=f" {gender_icon} {cat.gender} ",
                font=Theme.font_tiny(),
                fg_color=Theme.BG_CARD_ALT,
                text_color=Theme.TEXT_SECONDARY,
                corner_radius=6,
                padx=6,
                pady=2
            ).pack(side="left", padx=(0, 4))

            ctk.CTkLabel(
                traits_row,
                text=f" {cat.formatted_age} ",
                font=Theme.font_tiny(),
                fg_color=Theme.BG_CARD_ALT,
                text_color=Theme.TEXT_SECONDARY,
                corner_radius=6,
                padx=6,
                pady=2
            ).pack(side="left", padx=(0, 4))

            if cat.is_spayed_neutered:
                ctk.CTkLabel(
                    traits_row,
                    text=" ✂️ Fixed ",
                    font=Theme.font_tiny(),
                    fg_color=Theme.BG_CARD_ALT,
                    text_color=Theme.TEXT_SECONDARY,
                    corner_radius=6,
                    padx=6,
                    pady=2
                ).pack(side="left")

            # Action Buttons Row
            btn_row = ctk.CTkFrame(content, fg_color="transparent")
            btn_row.pack(fill="x")
            btn_row.grid_columnconfigure((0, 1), weight=1)

            ctk.CTkButton(
                btn_row,
                text="Gallery & Profile",
                height=36,
                corner_radius=Theme.RADIUS_BTN,
                font=Theme.font_caption_bold(),
                fg_color=Theme.SECONDARY,
                hover_color=Theme.SECONDARY_HOVER,
                text_color=Theme.SECONDARY_TEXT,
                cursor="hand2",
                command=lambda c=cat: self._open_cat_detail(c)
            ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

            if cat.adoption_status == "Available":
                ctk.CTkButton(
                    btn_row,
                    text="🐾 Adopt Me",
                    height=36,
                    corner_radius=Theme.RADIUS_BTN,
                    fg_color=Theme.SUCCESS,
                    hover_color=Theme.SUCCESS_HOVER,
                    text_color=Theme.SUCCESS_TEXT,
                    font=Theme.font_caption_bold(),
                    cursor="hand2",
                    command=lambda c=cat: self._handle_adopt_click(c)
                ).grid(row=0, column=1, padx=(4, 0), sticky="ew")
            else:
                ctk.CTkButton(
                    btn_row,
                    text="⏳ In Review",
                    height=36,
                    corner_radius=Theme.RADIUS_BTN,
                    fg_color=Theme.SECONDARY,
                    text_color=Theme.TEXT_MUTED,
                    state="disabled"
                ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

            # Card hover glow
            def make_hover(c=card):
                return lambda e: c.configure(border_color=Theme.BORDER_ACCENT[0]), lambda e: c.configure(border_color=Theme.BORDER[0])

            h_in, h_out = make_hover()
            card.bind("<Enter>", h_in)
            card.bind("<Leave>", h_out)

    def _open_cat_detail(self, cat):
        CustomerCatDetailModal(
            self.master,
            cat=cat,
            customer=self.current_customer,
            on_adopt=self._handle_adopt_click
        )

    def _handle_adopt_click(self, cat):
        # Action-gated: Guest must sign in or register first
        if not self.current_customer:
            CustomerAuthModal(self.master, on_auth_success=lambda adopter: self._on_auth_success(adopter, pending_cat=cat))
        else:
            CustomerApplyModal(self.master, cat=cat, customer=self.current_customer, on_submitted=self.refresh_catalog)

    def _open_auth_modal(self):
        CustomerAuthModal(self.master, on_auth_success=self._on_auth_success)

    def _on_auth_success(self, adopter, pending_cat=None):
        self.current_customer = adopter
        self._update_auth_header()
        if pending_cat:
            CustomerApplyModal(self.master, cat=pending_cat, customer=self.current_customer, on_submitted=self.refresh_catalog)

    def _logout(self):
        self.current_customer = None
        self._update_auth_header()
        if self.active_tab == "applications":
            self._switch_tab("catalog")

    def _load_user_applications(self):
        """Displays submitted applications with visual stage pipeline and certificate viewer."""
        for widget in self.user_apps_scroll.winfo_children():
            widget.destroy()

        if not self.current_customer:
            prompt = ctk.CTkFrame(self.user_apps_scroll, fg_color="transparent")
            prompt.pack(pady=60)
            ctk.CTkLabel(prompt, text="🐾", font=ctk.CTkFont(size=44)).pack()
            ctk.CTkLabel(prompt, text="Sign in to Track Your Adoption Applications", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY).pack(pady=(6, 2))
            ctk.CTkLabel(prompt, text="View application status stages, meet-and-greet interview dates, and adoption certificates.", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY).pack(pady=(0, 14))

            ctk.CTkButton(
                prompt,
                text="Sign In or Register Now",
                height=38,
                corner_radius=Theme.RADIUS_BTN,
                fg_color=Theme.PRIMARY,
                hover_color=Theme.PRIMARY_HOVER,
                font=Theme.font_body_bold(),
                cursor="hand2",
                command=self._open_auth_modal
            ).pack()
            return

        all_apps = self.app_ctrl.get_all_applications("All (Incl. Archived)")
        my_apps = [a for a in all_apps if a.adopter_id == self.current_customer.id]

        if not my_apps:
            Theme.create_empty_state(
                self.user_apps_scroll,
                icon="📋",
                title="No Applications Submitted Yet",
                subtitle="Browse available rescue cats in the catalog and click 'Adopt Me' to submit an application!"
            )
            return

        for app in my_apps:
            card = ctk.CTkFrame(self.user_apps_scroll, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER)
            card.pack(fill="x", pady=6)
            card.grid_columnconfigure(0, weight=1)

            # Top Header Row in Application Card
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=16, pady=(14, 6))
            top_row.grid_columnconfigure(0, weight=1)

            title_box = ctk.CTkFrame(top_row, fg_color="transparent")
            title_box.grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(title_box, text=f"Application #{app.id}  •  {app.cat_name}", font=Theme.font_subtitle(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(title_box, text=f"Submitted on: {app.application_date}", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")

            badge_bg, badge_txt = Theme.get_status_colors(app.review_status)
            ctk.CTkLabel(
                top_row,
                text=f"  {app.review_status}  ",
                text_color=badge_txt,
                fg_color=badge_bg,
                font=Theme.font_tiny(),
                corner_radius=Theme.RADIUS_PILL,
                padx=10,
                pady=4
            ).grid(row=0, column=1, sticky="e")

            # Visual Progress Stepper Bar
            stages = ["Submitted", "Pending Review", "Interview Scheduled", "Approved", "Completed"]
            status_idx = {
                "Pending Review": 1,
                "Interview Scheduled": 2,
                "Approved": 3,
                "Completed": 4,
                "Rejected": -1,
                "Archived": -2
            }.get(app.review_status, 1)

            if status_idx >= 0:
                stepper = ctk.CTkFrame(card, fg_color=Theme.BG_CARD, corner_radius=8, border_width=1, border_color=Theme.BORDER)
                stepper.pack(fill="x", padx=16, pady=4)

                step_labels = ["① Submitted", "② Review", "③ Interview", "④ Approved", "⑤ Finalized"]
                for s_i, s_txt in enumerate(step_labels):
                    is_active = (s_i <= status_idx)
                    step_color = Theme.PRIMARY[0] if is_active else Theme.TEXT_MUTED[0]
                    step_weight = "bold" if s_i == status_idx else "normal"

                    ctk.CTkLabel(
                        stepper,
                        text=s_txt,
                        font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight=step_weight),
                        text_color=step_color
                    ).pack(side="left", expand=True, pady=6)

            # Stage Guidance Box
            guidance_map = {
                "Pending Review": "⏳ Our caretakers are reviewing your home environment. We will notify you once interview slots open.",
                "Interview Scheduled": "📞 An interview has been scheduled! Please keep your contact phone available for our staff call.",
                "Approved": "🎉 Congratulations! Your application has been approved. Staff will contact you for pickup scheduling.",
                "Completed": "🏆 Adoption finalized! Thank you for giving this rescue a forever home. Your official certificate is available below.",
                "Archived": "📦 This application is currently archived in shelter records.",
                "Rejected": "❌ This application was not approved. Thank you for your support of animal rescue."
            }
            guidance_msg = guidance_map.get(app.review_status, "Application in progress.")

            guide_frame = ctk.CTkFrame(card, fg_color="transparent")
            guide_frame.pack(fill="x", padx=16, pady=(4, 10))
            ctk.CTkLabel(guide_frame, text=guidance_msg, font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY, justify="left", wraplength=700).pack(anchor="w")

            # Notes / Bottom Actions
            if app.review_status == "Completed":
                cert_btn = ctk.CTkButton(
                    card,
                    text="📜 View Official Adoption Certificate",
                    height=36,
                    corner_radius=Theme.RADIUS_BTN,
                    fg_color=Theme.PRIMARY,
                    hover_color=Theme.PRIMARY_HOVER,
                    font=Theme.font_caption_bold(),
                    cursor="hand2",
                    command=lambda a=app: self._show_user_certificate(a)
                )
                cert_btn.pack(anchor="e", padx=16, pady=(0, 14))
            elif app.review_status == "Pending Review":
                withdraw_btn = ctk.CTkButton(
                    card,
                    text="Withdraw Request",
                    height=30,
                    corner_radius=Theme.RADIUS_BTN,
                    fg_color=Theme.SECONDARY,
                    hover_color=Theme.SECONDARY_HOVER,
                    text_color=Theme.TEXT_MUTED,
                    font=Theme.font_tiny(),
                    cursor="hand2",
                    command=lambda a=app: self._withdraw_application(a)
                )
                withdraw_btn.pack(anchor="e", padx=16, pady=(0, 12))

    def _show_user_certificate(self, app):
        """Displays official certificate for completed adoptions."""
        cat = self.cat_ctrl.get_cat_by_id(app.cat_id)
        adopter = self.current_customer

        cert_data = {
            "id": app.id,
            "application_date": str(app.application_date),
            "review_status": app.review_status,
            "cat_name": cat.name if cat else app.cat_name,
            "breed": cat.breed if cat else "Domestic Shorthair",
            "color": cat.color if cat else "Mixed",
            "gender": cat.gender if cat else "Unknown",
            "cage_number": cat.cage_number if cat else "Shelter",
            "primary_image": cat.primary_image if cat else None,
            "adopter_name": adopter.full_name if adopter else app.adopter_name,
            "contact_number": adopter.contact_number if adopter else "N/A",
            "address": adopter.address if adopter else "N/A"
        }
        AdoptionCertificateModal(self.master, cert_data)

    def _withdraw_application(self, app):
        """Allows adopter to cancel an active application."""
        def on_withdraw_confirmed():
            ok, msg = self.app_ctrl.archive_application(app.id, reason="Withdrawn by applicant")
            if ok:
                ToastNotification.show(
                    self,
                    f"Application #{app.id} for {app.cat_name} withdrawn.",
                    toast_type="info",
                    title="Application Withdrawn"
                )
                self._load_user_applications()
            else:
                AlertModal(self, title="Error", message=str(msg), alert_type="error")

        ConfirmModal(
            self.master,
            title="Withdraw Application",
            message=f"Are you sure you want to withdraw your adoption request for {app.cat_name}?\n\nThis will safely close your application and release {app.cat_name} for other adopters.",
            confirm_text="Withdraw Application",
            cancel_text="Keep Application",
            icon="⚠️",
            confirm_color=Theme.WARNING,
            confirm_hover=Theme.WARNING_HOVER,
            width=500,
            height=300,
            on_confirm=on_withdraw_confirmed
        )
