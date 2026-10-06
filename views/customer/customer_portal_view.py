"""
Customer / Adopter Portal View in CustomTkinter.
100% Native Python OOP Desktop GUI with Modern Obsidian & Slate Design System.
Features:
- Browse cat catalog with rich real photos and metadata pills.
- Interactive Cat Profile & Photo Gallery modal with thumbnail carousel.
- Centered Auth Modal (Sign In / Register) appears when clicking 'Adopt Me!' as guest.
- Direct Application modal when logged in with photo preview.
- 'My Applications' tab for tracking review status with modern status badges.
"""

from datetime import date
from tkinter import messagebox
import customtkinter as ctk

from controllers.cat_controller import CatController
from controllers.adopter_controller import AdopterController
from controllers.application_controller import ApplicationController
from controllers.image_service import ImageService
from views.image_viewer_modal import ImageViewerModal
from views.theme import Theme
from models.adopter import Adopter
from models.application import AdoptionApplication


class CustomerAuthModal(ctk.CTkToplevel):
    """Centered modal for Guest Sign In / Registration."""
    def __init__(self, parent, on_auth_success):
        super().__init__(parent)
        self.title("Sign In or Register to Adopt")
        self.geometry("460x540")
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
        w, h = 460, 540
        x = max(0, px + (pw // 2) - (w // 2))
        y = max(0, py + (ph // 2) - (h // 2))
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=25, pady=(24, 10))

        ctk.CTkLabel(hdr, text="Sign In to Adopt", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Create a profile or sign in to complete your adoption request.", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

        # Tabview: Sign In vs Register
        self.tabview = ctk.CTkTabview(self, corner_radius=Theme.RADIUS_CARD)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        tab_signin = self.tabview.add("Sign In")
        tab_signup = self.tabview.add("Register Account")

        # Tab 1: Sign In
        ctk.CTkLabel(tab_signin, text="Contact Number or Email:", font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=10, pady=(18, 5))
        self.login_entry = ctk.CTkEntry(
            tab_signin,
            placeholder_text="e.g. 0917-xxx-xxxx or email",
            height=40,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.login_entry.pack(fill="x", padx=10, pady=5)

        self.signin_feedback = ctk.CTkLabel(tab_signin, text="", font=Theme.font_caption(), text_color=Theme.DANGER[1])
        self.signin_feedback.pack(pady=4)

        ctk.CTkButton(
            tab_signin,
            text="Continue to Adoption",
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            font=Theme.font_subtitle(),
            command=self._handle_signin
        ).pack(fill="x", padx=10, pady=15)

        # Tab 2: Register
        reg_scroll = ctk.CTkScrollableFrame(tab_signup, fg_color="transparent")
        reg_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(reg_scroll, text="Full Name *", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.reg_name = ctk.CTkEntry(reg_scroll, placeholder_text="e.g. Juan Dela Cruz", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.reg_name.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Contact Number *", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.reg_contact = ctk.CTkEntry(reg_scroll, placeholder_text="0917-xxx-xxxx", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.reg_contact.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Email Address", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.reg_email = ctk.CTkEntry(reg_scroll, placeholder_text="juan@example.com", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.reg_email.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Home Address *", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.reg_address = ctk.CTkEntry(reg_scroll, placeholder_text="Street, City, Province", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.reg_address.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Housing Type", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self.reg_housing = ctk.CTkOptionMenu(reg_scroll, values=["House with Yard", "Apartment", "Condo", "Townhouse"], height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, button_color=Theme.BORDER_LIGHT)
        self.reg_housing.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            reg_scroll,
            text="Register & Continue",
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.font_subtitle(),
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
            self.signin_feedback.configure(text="No account found. Please click 'Register Account'.")

    def _handle_register(self):
        name = self.reg_name.get().strip()
        contact = self.reg_contact.get().strip()
        address = self.reg_address.get().strip()

        if not name or not contact or not address:
            messagebox.showwarning("Validation Error", "Full Name, Contact Number, and Address are required.", parent=self)
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
            messagebox.showerror("Registration Error", str(res), parent=self)


class CustomerApplyModal(ctk.CTkToplevel):
    """Centered modal for submitting an adoption application."""
    def __init__(self, parent, cat, customer, on_submitted):
        super().__init__(parent)
        self.title(f"Apply to Adopt {cat.name}")
        self.geometry("520x540")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.cat = cat
        self.customer = customer
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
        w, h = 520, 540
        x = max(0, px + (pw // 2) - (w // 2))
        y = max(0, py + (ph // 2) - (h // 2))
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(hdr, text=f"Apply to Adopt {self.cat.name}", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Review your application details below before submitting.", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=5)

        # Cat Summary Card with Photo
        cat_card = ctk.CTkFrame(body, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER, corner_radius=Theme.RADIUS_CARD)
        cat_card.pack(fill="x", pady=(5, 10))
        cat_card.grid_columnconfigure(1, weight=1)

        ctk_img = ImageService.get_ctk_image(self.cat.primary_image, size=(80, 80))
        if ctk_img:
            img_lbl = ctk.CTkLabel(cat_card, image=ctk_img, text="", corner_radius=8)
            img_lbl.grid(row=0, column=0, rowspan=3, padx=(12, 10), pady=10)
        else:
            img_lbl = ctk.CTkLabel(cat_card, text="🐱", font=ctk.CTkFont(size=36))
            img_lbl.grid(row=0, column=0, rowspan=3, padx=(14, 10), pady=10)

        info_col = ctk.CTkFrame(cat_card, fg_color="transparent")
        info_col.grid(row=0, column=1, rowspan=3, padx=(0, 12), pady=10, sticky="nsew")
        
        name_row = ctk.CTkFrame(info_col, fg_color="transparent")
        name_row.pack(fill="x")
        ctk.CTkLabel(name_row, text=self.cat.name, font=Theme.font_subtitle(), text_color=Theme.TEXT_PRIMARY).pack(side="left")
        
        status_bg, status_txt = Theme.get_status_colors(self.cat.adoption_status)
        ctk.CTkLabel(name_row, text=f"  {self.cat.adoption_status}  ", font=Theme.font_tiny(), fg_color=status_bg, text_color=status_txt, corner_radius=Theme.RADIUS_PILL).pack(side="right")

        ctk.CTkLabel(info_col, text=f"{self.cat.breed} • {self.cat.color}", font=Theme.font_caption_bold(), text_color=Theme.TEXT_ACCENT).pack(anchor="w", pady=(1, 2))
        ctk.CTkLabel(info_col, text=f"Age: {self.cat.formatted_age}  |  Gender: {self.cat.gender}  |  Health: {self.cat.health_status}", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")

        # Adopter Info Card
        adopter_card = ctk.CTkFrame(body, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER, corner_radius=Theme.RADIUS_CARD)
        adopter_card.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(adopter_card, text=f"Applicant: {self.customer.full_name}", font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(8, 2))
        ctk.CTkLabel(adopter_card, text=f"Contact: {self.customer.contact_number}  •  {self.customer.address}", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", padx=14, pady=(0, 8))

        # Notes / Remarks
        ctk.CTkLabel(body, text="Adoption Statement / Notes:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 3))
        self.notes_box = ctk.CTkTextbox(body, height=85, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_width=1, border_color=Theme.BORDER)
        self.notes_box.pack(fill="x", pady=(0, 15))

        # Action Buttons
        btn_frame = ctk.CTkFrame(body, fg_color="transparent")
        btn_frame.pack(fill="x")
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
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="Submit Application",
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            text_color=Theme.SUCCESS_TEXT,
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_subtitle(),
            command=self._handle_submit
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _handle_submit(self):
        notes = self.notes_box.get("1.0", "end").strip()
        app = AdoptionApplication(
            cat_id=self.cat.id,
            adopter_id=self.customer.id,
            notes=notes
        )

        ok, res = self.app_ctrl.create_application(app)
        if ok:
            messagebox.showinfo("Application Submitted", f"Thank you, {self.customer.full_name}! Your adoption application for {self.cat.name} has been submitted. Shelter caretakers will review your request.", parent=self)
            self.destroy()
            self.on_submitted()
        else:
            messagebox.showerror("Error", str(res), parent=self)


class CustomerCatDetailModal(ctk.CTkToplevel):
    """
    Rich modal displaying complete Cat Profile and multi-photo gallery.
    Allows viewing all attached photos (up to 10), switching active photo via thumbnails,
    inspecting fullscreen in ImageViewerModal, and submitting an adoption request.
    """
    def __init__(self, parent, cat, customer=None, on_adopt=None):
        super().__init__(parent)
        self.title(f"{cat.name} - Profile & Gallery")
        self.geometry("640x740")
        self.minsize(580, 620)
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

    def _center_modal(self, parent):
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w, h = 640, 740
        x = max(0, px + (pw // 2) - (w // 2))
        y = max(0, py + (ph // 2) - (h // 2))
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header Bar
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 10))
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
            padx=10,
            pady=4
        ).grid(row=0, column=1, sticky="e")

        # Scrollable Main Body
        scroll_body = ctk.CTkScrollableFrame(self, corner_radius=Theme.RADIUS_CARD, fg_color="transparent")
        scroll_body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        scroll_body.grid_columnconfigure(0, weight=1)

        # Photo Gallery Container
        gallery_frame = ctk.CTkFrame(scroll_body, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER)
        gallery_frame.pack(fill="x", pady=(0, 12))
        gallery_frame.grid_columnconfigure(0, weight=1)

        if self.images:
            # Main Photo Area
            self.photo_display_frame = ctk.CTkFrame(gallery_frame, height=280, fg_color=Theme.BG_CARD_ALT, corner_radius=10)
            self.photo_display_frame.pack(fill="x", padx=10, pady=(10, 4))
            self.photo_display_frame.pack_propagate(False)

            self.main_photo_lbl = ctk.CTkLabel(self.photo_display_frame, text="", cursor="hand2")
            self.main_photo_lbl.pack(expand=True, fill="both")
            self.main_photo_lbl.bind("<Button-1>", lambda e: self._open_fullscreen_viewer())

            # Hint / Counter Row
            hint_row = ctk.CTkFrame(gallery_frame, fg_color="transparent")
            hint_row.pack(fill="x", padx=14, pady=(4, 6))
            hint_row.grid_columnconfigure(0, weight=1)

            self.hint_lbl = ctk.CTkLabel(
                hint_row,
                text=f"Click photo to inspect full size • Photo 1 of {len(self.images)}",
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

                # Thumbnail Strip (Supports up to 10 images)
                self.thumb_strip = ctk.CTkScrollableFrame(gallery_frame, orientation="horizontal", height=66, fg_color="transparent")
                self.thumb_strip.pack(fill="x", padx=10, pady=(0, 10))

                for i, img_path in enumerate(self.images):
                    thumb_img = ImageService.get_ctk_image(img_path, size=(50, 50))
                    btn = ctk.CTkButton(
                        self.thumb_strip,
                        image=thumb_img,
                        text="",
                        width=54,
                        height=54,
                        corner_radius=8,
                        fg_color=Theme.BG_CARD_ALT,
                        border_width=0,
                        hover_color=Theme.BORDER_ACCENT,
                        command=lambda idx=i: self._select_photo(idx)
                    )
                    btn.pack(side="left", padx=3, pady=2)
                    self.thumb_buttons.append(btn)
        else:
            no_img_frame = ctk.CTkFrame(gallery_frame, height=180, fg_color="transparent")
            no_img_frame.pack(fill="x", padx=10, pady=20)
            ctk.CTkLabel(no_img_frame, text="🐱\nNo Photos Attached Yet", font=Theme.font_title(), text_color=Theme.TEXT_MUTED).pack(expand=True)

        # Profile Details Section
        details_frame = ctk.CTkFrame(scroll_body, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER)
        details_frame.pack(fill="x", pady=(0, 12))
        details_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(details_frame, text="Profile & Health Overview", font=Theme.font_subtitle(), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 8))

        specs = [
            ("AGE", self.cat.formatted_age),
            ("GENDER", self.cat.gender),
            ("COAT COLOR", self.cat.color),
            ("HEALTH STATUS", self.cat.health_status),
            ("SPAYED / NEUTERED", "Yes ✓" if self.cat.is_spayed_neutered else "No"),
            ("INTAKE DATE", self.cat.intake_date or "Unknown"),
            ("SHELTER HOUSING", self.cat.cage_number or "General Ward"),
            ("PHOTOS ATTACHED", f"{len(self.images)} photo(s)")
        ]

        for s_idx, (k, v) in enumerate(specs):
            r = 1 + (s_idx // 2)
            c = s_idx % 2
            cell = ctk.CTkFrame(details_frame, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER, corner_radius=6)
            cell.grid(row=r, column=c, padx=10, pady=4, sticky="ew")
            ctk.CTkLabel(cell, text=k, font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(cell, text=v, font=Theme.font_caption_bold(), text_color=Theme.TEXT_PRIMARY).pack(side="right", padx=10, pady=6)

        # Notes / Personality
        bio_frame = ctk.CTkFrame(scroll_body, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER)
        bio_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(bio_frame, text="Personality & Caregiver Notes", font=Theme.font_subtitle(), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 4))
        bio_text = self.cat.notes.strip() if self.cat.notes else "This cat is gentle, adaptable, and looking for a loving forever family."
        ctk.CTkLabel(bio_frame, text=bio_text, font=Theme.font_body(), text_color=Theme.TEXT_SECONDARY, wraplength=540, justify="left").pack(anchor="w", padx=16, pady=(0, 14))

        # Bottom Action Bar
        act_bar = ctk.CTkFrame(self, fg_color="transparent")
        act_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
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
                text=f"Apply to Adopt {self.cat.name}",
                fg_color=Theme.SUCCESS,
                hover_color=Theme.SUCCESS_HOVER,
                text_color=Theme.SUCCESS_TEXT,
                height=40,
                corner_radius=Theme.RADIUS_BTN,
                font=Theme.font_subtitle(),
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

    def _open_fullscreen_viewer(self):
        if self.images:
            ImageViewerModal(self, self.images, initial_index=self.current_idx, title_prefix=f"{self.cat.name} Photos")

    def _update_photo(self):
        if not self.images:
            return
        img_path = self.images[self.current_idx]
        ctk_img = ImageService.get_ctk_image(img_path, size=(460, 270))
        if ctk_img:
            self.main_photo_lbl.configure(image=ctk_img, text="")
        else:
            self.main_photo_lbl.configure(image=None, text="Image not found")

        if hasattr(self, 'hint_lbl'):
            self.hint_lbl.configure(text=f"Click photo to inspect full size • Photo {self.current_idx + 1} of {len(self.images)}")

        if hasattr(self, 'thumb_buttons'):
            for i, btn in enumerate(self.thumb_buttons):
                if i == self.current_idx:
                    btn.configure(border_width=2, border_color=Theme.BORDER_ACCENT[1], fg_color=Theme.BG_CARD)
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
    """Main Public / Adopter view in CustomTkinter with Modern Obsidian Design."""
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
        ).pack(side="left", padx=10)

        # Nav Buttons (Segmented look)
        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.grid(row=0, column=1, padx=10, pady=10)

        self.nav_catalog_btn = ctk.CTkButton(
            nav_frame,
            text="Browse Cats",
            width=120,
            height=34,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_caption_bold(),
            fg_color=Theme.PRIMARY,
            command=lambda: self._switch_tab("catalog")
        )
        self.nav_catalog_btn.pack(side="left", padx=4)

        self.nav_apps_btn = ctk.CTkButton(
            nav_frame,
            text="My Applications",
            width=130,
            height=34,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_caption_bold(),
            fg_color=Theme.SECONDARY,
            text_color=Theme.SECONDARY_TEXT,
            hover_color=Theme.SECONDARY_HOVER,
            command=lambda: self._switch_tab("applications")
        )
        self.nav_apps_btn.pack(side="left", padx=4)

        # Auth Badge / Sign In Button
        self.auth_frame = ctk.CTkFrame(header, fg_color="transparent")
        self.auth_frame.grid(row=0, column=2, padx=18, pady=10, sticky="e")
        self._update_auth_header()

        # ==========================================
        # CONTENT CONTAINER
        # ==========================================
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # TAB 1: CATALOG FRAME
        self.catalog_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.catalog_frame.grid(row=0, column=0, sticky="nsew")
        self.catalog_frame.grid_rowconfigure(1, weight=1)
        self.catalog_frame.grid_columnconfigure(0, weight=1)

        # Search & Filter Bar
        filter_bar = ctk.CTkFrame(self.catalog_frame, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER)
        filter_bar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="Search available cats by name, breed, or color...",
            height=38,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.search_entry.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_catalog())

        self.filter_menu = ctk.CTkOptionMenu(
            filter_bar,
            values=["All", "Kittens (< 1 yr)", "Female", "Male"],
            height=38,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BORDER_LIGHT,
            command=lambda val: self.refresh_catalog()
        )
        self.filter_menu.grid(row=0, column=1, padx=(0, 15), pady=10)

        # Scrollable Cards Grid
        self.cards_scroll = ctk.CTkScrollableFrame(self.catalog_frame, corner_radius=Theme.RADIUS_CARD, fg_color="transparent")
        self.cards_scroll.grid(row=1, column=0, sticky="nsew")
        self.cards_scroll.grid_columnconfigure((0, 1, 2), weight=1)

        # TAB 2: MY APPLICATIONS FRAME
        self.apps_frame = ctk.CTkFrame(self.content_container, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER)
        self.apps_frame.grid_rowconfigure(1, weight=1)
        self.apps_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.apps_frame, text="My Adoption Applications", font=Theme.font_title(), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        self.user_apps_scroll = ctk.CTkScrollableFrame(self.apps_frame, fg_color="transparent")
        self.user_apps_scroll.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.user_apps_scroll.grid_columnconfigure(0, weight=1)

    def _update_auth_header(self):
        for widget in self.auth_frame.winfo_children():
            widget.destroy()

        if self.current_customer:
            ctk.CTkLabel(self.auth_frame, text=f"👤 {self.current_customer.full_name}", font=Theme.font_caption_bold(), text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=6)
            ctk.CTkButton(
                self.auth_frame,
                text="Sign Out",
                width=75,
                height=30,
                corner_radius=Theme.RADIUS_BTN,
                fg_color=Theme.DANGER,
                hover_color=Theme.DANGER_HOVER,
                font=Theme.font_caption_bold(),
                command=self._logout
            ).pack(side="left", padx=4)
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
                command=self._open_auth_modal
            ).pack(side="left")

    def _switch_tab(self, tab):
        self.active_tab = tab
        if tab == "catalog":
            self.apps_frame.grid_forget()
            self.catalog_frame.grid(row=0, column=0, sticky="nsew")
            self.nav_catalog_btn.configure(fg_color=Theme.PRIMARY, text_color="#ffffff")
            self.nav_apps_btn.configure(fg_color=Theme.SECONDARY, text_color=Theme.SECONDARY_TEXT)
            self.refresh_catalog()
        else:
            self.catalog_frame.grid_forget()
            self.apps_frame.grid(row=0, column=0, sticky="nsew")
            self.nav_catalog_btn.configure(fg_color=Theme.SECONDARY, text_color=Theme.SECONDARY_TEXT)
            self.nav_apps_btn.configure(fg_color=Theme.PRIMARY, text_color="#ffffff")
            self._load_user_applications()

    def refresh_catalog(self):
        for widget in self.cards_scroll.winfo_children():
            widget.destroy()

        cats = self.cat_ctrl.get_all_cats()
        search = self.search_entry.get().strip().lower()
        filter_val = self.filter_menu.get()

        # Public filter: only show Available or Pending
        filtered = []
        for c in cats:
            if c.adoption_status in ["Medical Hold", "Adopted"]:
                continue
            if search and (search not in c.name.lower() and search not in c.breed.lower() and search not in c.color.lower()):
                continue
            if filter_val == "Kittens (< 1 yr)" and c.age_months >= 12:
                continue
            if filter_val == "Female" and c.gender != "Female":
                continue
            if filter_val == "Male" and c.gender != "Male":
                continue
            filtered.append(c)

        if not filtered:
            ctk.CTkLabel(self.cards_scroll, text="No cats match your filter criteria.", text_color=Theme.TEXT_MUTED, font=Theme.font_subtitle()).grid(row=0, column=0, columnspan=3, pady=60)
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

            # Photo Container (175px high, clickable)
            photo_frame = ctk.CTkFrame(card, height=175, fg_color=Theme.BG_CARD_ALT, corner_radius=10)
            photo_frame.pack(fill="x", padx=10, pady=(10, 6))
            photo_frame.pack_propagate(False)

            ctk_img = ImageService.get_ctk_image(cat.primary_image, size=(270, 175))
            if ctk_img:
                photo_lbl = ctk.CTkLabel(photo_frame, image=ctk_img, text="", cursor="hand2")
                photo_lbl.pack(expand=True, fill="both")
                photo_lbl.bind("<Button-1>", lambda e, c=cat: self._open_cat_detail(c))
            else:
                photo_lbl = ctk.CTkLabel(photo_frame, text="🐱\nNo Photo", font=Theme.font_subtitle(), text_color=Theme.TEXT_MUTED, cursor="hand2")
                photo_lbl.pack(expand=True, fill="both")
                photo_lbl.bind("<Button-1>", lambda e, c=cat: self._open_cat_detail(c))

            # Photo Count Badge if multiple photos
            if len(cat.images) > 1:
                badge = ctk.CTkLabel(
                    photo_frame,
                    text=f" 📷 {len(cat.images)} Photos ",
                    font=Theme.font_tiny(),
                    fg_color=("#0f172a", "#090d16"),
                    text_color="#ffffff",
                    corner_radius=12
                )
                badge.place(relx=0.96, rely=0.92, anchor="se")

            # Content Container
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=14, pady=(6, 12))

            # Title Row: Name & Status Pill
            title_row = ctk.CTkFrame(content, fg_color="transparent")
            title_row.pack(fill="x")
            ctk.CTkLabel(title_row, text=cat.name, font=Theme.font_subtitle(), text_color=Theme.TEXT_PRIMARY).pack(side="left")

            status_bg, status_txt = Theme.get_status_colors(cat.adoption_status)
            ctk.CTkLabel(
                title_row,
                text=f"  {cat.adoption_status}  ",
                font=Theme.font_tiny(),
                fg_color=status_bg,
                text_color=status_txt,
                corner_radius=Theme.RADIUS_PILL
            ).pack(side="right")

            # Breed & Attributes
            ctk.CTkLabel(content, text=cat.breed, font=Theme.font_caption_bold(), text_color=Theme.TEXT_ACCENT).pack(anchor="w", pady=(1, 2))
            ctk.CTkLabel(content, text=f"{cat.formatted_age}  •  {cat.gender}  •  {cat.color}", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 10))

            # Action Buttons Row
            btn_row = ctk.CTkFrame(content, fg_color="transparent")
            btn_row.pack(fill="x")
            btn_row.grid_columnconfigure((0, 1), weight=1)

            ctk.CTkButton(
                btn_row,
                text="View Gallery",
                height=36,
                corner_radius=Theme.RADIUS_BTN,
                font=Theme.font_caption_bold(),
                fg_color=Theme.SECONDARY,
                hover_color=Theme.SECONDARY_HOVER,
                text_color=Theme.SECONDARY_TEXT,
                command=lambda c=cat: self._open_cat_detail(c)
            ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

            if cat.adoption_status == "Available":
                ctk.CTkButton(
                    btn_row,
                    text="Adopt Me",
                    height=36,
                    corner_radius=Theme.RADIUS_BTN,
                    fg_color=Theme.SUCCESS,
                    hover_color=Theme.SUCCESS_HOVER,
                    text_color=Theme.SUCCESS_TEXT,
                    font=Theme.font_caption_bold(),
                    command=lambda c=cat: self._handle_adopt_click(c)
                ).grid(row=0, column=1, padx=(4, 0), sticky="ew")
            else:
                ctk.CTkButton(
                    btn_row,
                    text="Pending",
                    height=36,
                    corner_radius=Theme.RADIUS_BTN,
                    fg_color=Theme.SECONDARY,
                    text_color=Theme.TEXT_MUTED,
                    state="disabled"
                ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

    def _open_cat_detail(self, cat):
        CustomerCatDetailModal(
            self.master,
            cat=cat,
            customer=self.current_customer,
            on_adopt=self._handle_adopt_click
        )

    def _handle_adopt_click(self, cat):
        # ACTION-GATED: If guest, centered modal appears!
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
        for widget in self.user_apps_scroll.winfo_children():
            widget.destroy()

        if not self.current_customer:
            prompt = ctk.CTkFrame(self.user_apps_scroll, fg_color="transparent")
            prompt.pack(pady=60)
            ctk.CTkLabel(prompt, text="Please sign in to view your submitted applications.", font=Theme.font_subtitle(), text_color=Theme.TEXT_SECONDARY).pack()
            ctk.CTkButton(
                prompt,
                text="Sign In Now",
                height=38,
                corner_radius=Theme.RADIUS_BTN,
                fg_color=Theme.PRIMARY,
                hover_color=Theme.PRIMARY_HOVER,
                font=Theme.font_body_bold(),
                command=self._open_auth_modal
            ).pack(pady=12)
            return

        all_apps = self.app_ctrl.get_all_applications()
        my_apps = [a for a in all_apps if a.adopter_id == self.current_customer.id]

        if not my_apps:
            ctk.CTkLabel(self.user_apps_scroll, text="You have not submitted any adoption applications yet.", text_color=Theme.TEXT_MUTED, font=Theme.font_body()).pack(pady=60)
            return

        for app in my_apps:
            card = ctk.CTkFrame(self.user_apps_scroll, corner_radius=Theme.RADIUS_CARD, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER)
            card.pack(fill="x", pady=5)
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(card, text=f"Application #{app.id}  •  {app.cat_name}", font=Theme.font_subtitle(), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 2))
            ctk.CTkLabel(card, text=f"Submitted: {app.application_date}  |  Notes: {app.notes or 'None'}", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

            badge_bg, badge_txt = Theme.get_status_colors(app.review_status)
            ctk.CTkLabel(card, text=f"  {app.review_status}  ", text_color=badge_txt, fg_color=badge_bg, font=Theme.font_tiny(), corner_radius=Theme.RADIUS_PILL).grid(row=0, column=1, rowspan=2, padx=16, pady=12)
