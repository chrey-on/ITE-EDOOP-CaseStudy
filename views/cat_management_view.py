"""
Cat Management View for PurrfectMatch.
Implements full CRUD operations, live search, status filtering,
and multi-image attachments (up to 10 photos) via file picker or live webcam capture.
"""

from datetime import date
from tkinter import messagebox, filedialog
import customtkinter as ctk

from PIL import Image, ImageGrab

from controllers.cat_controller import CatController
from controllers.image_service import ImageService
from models.cat import Cat
from views.camera_capture_modal import CameraCaptureModal
from views.image_viewer_modal import ImageViewerModal
from views.theme import Theme


class CatManagementView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.on_data_changed = on_data_changed
        self.controller = CatController()
        self.selected_cat_id = None
        self.attached_images = []  # List of relative image paths (up to 10)

        self._build_ui()
        self.refresh_cat_list()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=5, minsize=400)  # Left panel (Form)
        self.grid_columnconfigure(1, weight=7, minsize=520)  # Right panel (List & Search)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # LEFT PANEL: Cat Intake Form & CRUD Actions
        # ==========================================
        form_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        form_frame.grid_columnconfigure(0, weight=1)

        # Header inside form
        header_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="Cat Intake & Profile Details",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="Register rescues or update cat records & photos",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        ).grid(row=1, column=0, sticky="w", pady=(1, 6))

        ctk.CTkFrame(header_frame, height=1, fg_color=Theme.BORDER[1]).grid(row=2, column=0, sticky="ew", pady=(2, 0))

        # Fields Grid Container
        fields_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fields_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=0)
        fields_frame.grid_columnconfigure(0, weight=0, minsize=115)
        fields_frame.grid_columnconfigure(1, weight=1)

        # Row 0: Cat ID (Display only)
        ctk.CTkLabel(fields_frame, text="CAT ID", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="w", padx=(6, 5), pady=4)
        self.id_display = ctk.CTkLabel(
            fields_frame,
            text="[ New Cat ]",
            font=Theme.font_caption_bold(),
            fg_color=Theme.BG_CARD_ALT,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Theme.RADIUS_INPUT,
            padx=10,
            pady=4
        )
        self.id_display.grid(row=0, column=1, sticky="w", padx=(5, 6), pady=4)

        # Row 1: Name
        ctk.CTkLabel(fields_frame, text="NAME *", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=1, column=0, sticky="w", padx=(6, 5), pady=4)
        self.name_entry = ctk.CTkEntry(fields_frame, placeholder_text="e.g. Luna", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=(5, 6), pady=4)

        # Row 2: Breed
        ctk.CTkLabel(fields_frame, text="BREED", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=2, column=0, sticky="w", padx=(6, 5), pady=4)
        self.breed_entry = ctk.CTkEntry(fields_frame, placeholder_text="e.g. British Shorthair", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.breed_entry.grid(row=2, column=1, sticky="ew", padx=(5, 6), pady=4)

        # Row 3: Age (Months)
        ctk.CTkLabel(fields_frame, text="AGE (MONTHS)", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=3, column=0, sticky="w", padx=(6, 5), pady=4)
        self.age_entry = ctk.CTkEntry(fields_frame, placeholder_text="e.g. 12", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.age_entry.grid(row=3, column=1, sticky="ew", padx=(5, 6), pady=4)

        # Row 4: Gender
        ctk.CTkLabel(fields_frame, text="GENDER", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=4, column=0, sticky="w", padx=(6, 5), pady=4)
        self.gender_menu = ctk.CTkOptionMenu(fields_frame, values=["Female", "Male", "Unknown"], height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, button_color=Theme.BORDER_LIGHT)
        self.gender_menu.grid(row=4, column=1, sticky="ew", padx=(5, 6), pady=4)

        # Row 5: Color
        ctk.CTkLabel(fields_frame, text="COAT COLOR", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=5, column=0, sticky="w", padx=(6, 5), pady=4)
        self.color_entry = ctk.CTkEntry(fields_frame, placeholder_text="e.g. Silver Grey", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.color_entry.grid(row=5, column=1, sticky="ew", padx=(5, 6), pady=4)

        # Row 6: Intake Date
        ctk.CTkLabel(fields_frame, text="INTAKE DATE", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=6, column=0, sticky="w", padx=(6, 5), pady=4)
        self.intake_entry = ctk.CTkEntry(fields_frame, placeholder_text="YYYY-MM-DD", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.intake_entry.insert(0, date.today().isoformat())
        self.intake_entry.grid(row=6, column=1, sticky="ew", padx=(5, 6), pady=4)

        # Row 7: Health Status
        ctk.CTkLabel(fields_frame, text="HEALTH STATUS", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=7, column=0, sticky="w", padx=(6, 5), pady=4)
        self.health_entry = ctk.CTkEntry(fields_frame, placeholder_text="e.g. Healthy & Vaccinated", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.health_entry.grid(row=7, column=1, sticky="ew", padx=(5, 6), pady=4)

        # Row 8: Spayed/Neutered Checkbox
        ctk.CTkLabel(fields_frame, text="STERILIZED", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=8, column=0, sticky="w", padx=(6, 5), pady=4)
        self.spayed_var = ctk.BooleanVar(value=False)
        self.spayed_check = ctk.CTkCheckBox(fields_frame, text="Spayed / Neutered", variable=self.spayed_var, font=Theme.font_caption())
        self.spayed_check.grid(row=8, column=1, sticky="w", padx=(5, 6), pady=4)

        # Row 9: Adoption Status
        ctk.CTkLabel(fields_frame, text="STATUS", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=9, column=0, sticky="w", padx=(6, 5), pady=4)
        self.status_menu = ctk.CTkOptionMenu(
            fields_frame,
            values=["Available", "Pending", "Adopted", "Medical Hold"],
            height=36,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BORDER_LIGHT
        )
        self.status_menu.grid(row=9, column=1, sticky="ew", padx=(5, 6), pady=4)

        # Row 10: Cage / Pen #
        ctk.CTkLabel(fields_frame, text="PEN / CAGE", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=10, column=0, sticky="w", padx=(6, 5), pady=4)
        self.cage_entry = ctk.CTkEntry(fields_frame, placeholder_text="e.g. Suite A-1", height=36, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_color=Theme.BORDER)
        self.cage_entry.grid(row=10, column=1, sticky="ew", padx=(5, 6), pady=4)

        # Row 11: Notes
        ctk.CTkLabel(fields_frame, text="NOTES / BIO", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="nw").grid(row=11, column=0, sticky="nw", padx=(6, 5), pady=6)
        self.notes_box = ctk.CTkTextbox(fields_frame, height=70, corner_radius=Theme.RADIUS_INPUT, fg_color=Theme.BG_INPUT, border_width=1, border_color=Theme.BORDER)
        self.notes_box.grid(row=11, column=1, sticky="ew", padx=(5, 6), pady=4)

        # ==========================================
        # CAT PHOTOS SECTION (Up to 10 images)
        # ==========================================
        photos_sec = ctk.CTkFrame(
            form_frame,
            fg_color=Theme.BG_CARD_ALT,
            corner_radius=Theme.RADIUS_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        photos_sec.grid(row=2, column=0, sticky="ew", padx=10, pady=(8, 6))
        photos_sec.grid_columnconfigure(0, weight=1)

        photo_hdr = ctk.CTkFrame(photos_sec, fg_color="transparent")
        photo_hdr.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))
        photo_hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            photo_hdr,
            text="Cat Photos (Up to 10)",
            font=Theme.font_subtitle(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        self.photo_count_lbl = ctk.CTkLabel(
            photo_hdr,
            text="0 / 10 photos",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_MUTED,
            anchor="e"
        )
        self.photo_count_lbl.grid(row=0, column=1, sticky="e")

        # Photo Action Buttons
        photo_btn_row = ctk.CTkFrame(photos_sec, fg_color="transparent")
        photo_btn_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        photo_btn_row.grid_columnconfigure((0, 1, 2), weight=1)

        self.attach_btn = ctk.CTkButton(
            photo_btn_row,
            text="📁 Attach",
            height=34,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_caption_bold(),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            command=self._handle_attach_photos
        )
        self.attach_btn.grid(row=0, column=0, padx=(0, 3), sticky="ew")

        self.capture_btn = ctk.CTkButton(
            photo_btn_row,
            text="📷 Capture",
            height=34,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_caption_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._handle_capture_camera
        )
        self.capture_btn.grid(row=0, column=1, padx=3, sticky="ew")

        self.paste_btn = ctk.CTkButton(
            photo_btn_row,
            text="📋 Paste (Ctrl+V)",
            height=34,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_caption_bold(),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            command=self._handle_paste_photo
        )
        self.paste_btn.grid(row=0, column=2, padx=(3, 0), sticky="ew")

        # Global Ctrl+V shortcut for pasting images
        self.bind("<Control-v>", lambda e: self._handle_paste_photo())

        # Scrollable Thumbnail Strip
        self.thumbs_scroll = ctk.CTkScrollableFrame(
            photos_sec,
            orientation="horizontal",
            height=85,
            fg_color=Theme.BG_INPUT,
            corner_radius=8
        )
        self.thumbs_scroll.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Initial thumbnail refresh
        self._refresh_photo_thumbnails()

        # Feedback / Status Banner
        self.feedback_frame = ctk.CTkFrame(form_frame, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER, corner_radius=6)
        self.feedback_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(4, 6))
        self.feedback_frame.grid_columnconfigure(0, weight=1)

        self.feedback_lbl = ctk.CTkLabel(
            self.feedback_frame,
            text="Ready for cat intake or selection",
            text_color=Theme.TEXT_MUTED,
            font=Theme.font_caption()
        )
        self.feedback_lbl.grid(row=0, column=0, padx=8, pady=6)

        # Action Buttons (CRUD)
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="ew", padx=8, pady=(4, 16))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="Add Cat",
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_subtitle(),
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            command=self._handle_add
        )
        self.add_btn.grid(row=0, column=0, padx=3, pady=3, sticky="ew")

        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="Update Selected",
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_subtitle(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._handle_update
        )
        self.update_btn.grid(row=0, column=1, padx=3, pady=3, sticky="ew")

        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear Form",
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            command=self.clear_form
        )
        self.clear_btn.grid(row=1, column=0, padx=3, pady=3, sticky="ew")

        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete Cat",
            height=38,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.DANGER,
            hover_color=Theme.DANGER_HOVER,
            command=self._handle_delete
        )
        self.delete_btn.grid(row=1, column=1, padx=3, pady=3, sticky="ew")

        # ==========================================
        # RIGHT PANEL: Search, Filter, and Table List
        # ==========================================
        list_container = ctk.CTkFrame(
            self,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        list_container.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(3, weight=1)

        # Header Bar with Count Badge
        header_bar = ctk.CTkFrame(list_container, fg_color="transparent")
        header_bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_bar,
            text="Shelter Cats Directory",
            font=Theme.font_title(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        self.count_badge = ctk.CTkLabel(
            header_bar,
            text="0 Cats",
            font=Theme.font_caption_bold(),
            fg_color=Theme.BG_CARD_ALT,
            text_color=Theme.TEXT_MUTED,
            corner_radius=Theme.RADIUS_PILL,
            padx=12,
            pady=4
        )
        self.count_badge.grid(row=0, column=1, sticky="e")

        # Search & Filter Bar
        filter_bar = ctk.CTkFrame(list_container, fg_color="transparent")
        filter_bar.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="Search by name, breed, color, or cage...",
            height=36,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._handle_search())

        self.filter_menu = ctk.CTkOptionMenu(
            filter_bar,
            values=["All", "Available", "Pending", "Adopted", "Medical Hold"],
            height=36,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BORDER_LIGHT,
            width=130,
            command=lambda val: self._handle_search()
        )
        self.filter_menu.grid(row=0, column=1, sticky="e")

        # Table Header (Right padded for scrollbar offset)
        tbl_hdr = ctk.CTkFrame(list_container, height=36, corner_radius=6, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER)
        tbl_hdr.grid(row=2, column=0, sticky="ew", padx=(16, 32), pady=(0, 4))
        tbl_hdr.grid_columnconfigure(0, weight=1, minsize=50)   # ID
        tbl_hdr.grid_columnconfigure(1, weight=2, minsize=110)  # Photo + Name
        tbl_hdr.grid_columnconfigure(2, weight=2, minsize=100)  # Breed
        tbl_hdr.grid_columnconfigure(3, weight=1, minsize=75)   # Age
        tbl_hdr.grid_columnconfigure(4, weight=2, minsize=95)   # Status
        tbl_hdr.grid_columnconfigure(5, weight=1, minsize=75)   # Cage

        ctk.CTkLabel(tbl_hdr, text="ID", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="w", padx=(12, 5), pady=7)
        ctk.CTkLabel(tbl_hdr, text="CAT / NAME", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=1, sticky="w", padx=5, pady=7)
        ctk.CTkLabel(tbl_hdr, text="BREED", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=2, sticky="w", padx=5, pady=7)
        ctk.CTkLabel(tbl_hdr, text="AGE", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=3, sticky="w", padx=5, pady=7)
        ctk.CTkLabel(tbl_hdr, text="STATUS", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="center").grid(row=0, column=4, sticky="ew", padx=5, pady=7)
        ctk.CTkLabel(tbl_hdr, text="HOUSING", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=5, sticky="w", padx=5, pady=7)

        # Scrollable Cat Rows Frame
        self.rows_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.rows_frame.grid(row=3, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.rows_frame.grid_columnconfigure(0, weight=1)

    # ==========================================
    # PHOTO MANAGEMENT HELPERS
    # ==========================================
    def _refresh_photo_thumbnails(self):
        """Rebuilds the horizontal thumbnail preview strip in the intake form."""
        for w in self.thumbs_scroll.winfo_children():
            w.destroy()

        count = len(self.attached_images)
        self.photo_count_lbl.configure(text=f"{count} / 10 photos")
        self.attach_btn.configure(state="normal" if count < 10 else "disabled")
        self.capture_btn.configure(state="normal" if count < 10 else "disabled")

        if not self.attached_images:
            empty_lbl = ctk.CTkLabel(
                self.thumbs_scroll,
                text="No photos attached yet (up to 10 allowed).",
                font=Theme.font_caption(),
                text_color=Theme.TEXT_MUTED
            )
            empty_lbl.pack(padx=20, pady=25)
            return

        for idx, img_path in enumerate(self.attached_images):
            thumb_card = ctk.CTkFrame(self.thumbs_scroll, fg_color=Theme.BG_CARD, border_width=1, border_color=Theme.BORDER, corner_radius=8)
            thumb_card.pack(side="left", padx=4, pady=4)

            # Primary badge indicator on first photo
            if idx == 0:
                ctk.CTkLabel(
                    thumb_card,
                    text="★ Primary",
                    font=Theme.font_tiny(),
                    text_color="#f59e0b"
                ).pack(pady=(2, 0))

            # Thumbnail Image
            ctk_thumb = ImageService.get_ctk_image(img_path, size=(55, 55))
            if ctk_thumb:
                img_lbl = ctk.CTkLabel(thumb_card, image=ctk_thumb, text="", cursor="hand2")
            else:
                img_lbl = ctk.CTkLabel(thumb_card, text="🖼️", width=55, height=55, cursor="hand2")
            img_lbl.pack(padx=3, pady=(2, 1))
            img_lbl.bind("<Button-1>", lambda e, i=idx: self._view_full_photo(i))

            # Delete button (✕)
            del_btn = ctk.CTkButton(
                thumb_card,
                text="✕ Remove",
                width=55,
                height=20,
                corner_radius=4,
                fg_color=Theme.DANGER,
                hover_color=Theme.DANGER_HOVER,
                font=Theme.font_tiny(),
                command=lambda i=idx: self._remove_attached_photo(i)
            )
            del_btn.pack(padx=3, pady=(1, 3))

    def _handle_attach_photos(self):
        """Prompts staff to select one or more image files from disk."""
        if len(self.attached_images) >= 10:
            messagebox.showwarning("Limit Reached", "A maximum of 10 photos can be attached per cat.")
            return

        file_paths = filedialog.askopenfilenames(
            title="Attach Cat Photos (Max 10)",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.webp")]
        )
        if not file_paths:
            return

        remaining = 10 - len(self.attached_images)
        if len(file_paths) > remaining:
            messagebox.showinfo(
                "Selection Truncated",
                f"Only the first {remaining} selected photos were added to adhere to the 10-photo limit."
            )
            file_paths = file_paths[:remaining]

        for fp in file_paths:
            try:
                rel_path = ImageService.save_image_from_path(fp, cat_id=self.selected_cat_id or 0)
                self.attached_images.append(rel_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to attach image '{fp}': {e}")

        self._refresh_photo_thumbnails()
        if self.selected_cat_id:
            self.controller.set_cat_images(self.selected_cat_id, self.attached_images)
            self.refresh_cat_list()
            if self.on_data_changed:
                self.on_data_changed()
        self.feedback_lbl.configure(
            text=f"📁 Attached {len(file_paths)} photo(s)! ({len(self.attached_images)}/10 photos)",
            text_color="#10b981"
        )

    def _handle_capture_camera(self):
        """Opens live camera snapshot modal to take a photo of the cat."""
        if len(self.attached_images) >= 10:
            messagebox.showwarning("Limit Reached", "A maximum of 10 photos can be attached per cat.")
            return

        CameraCaptureModal(
            self,
            on_photo_captured=self._on_camera_photo_captured,
            cat_id=self.selected_cat_id or 0
        )

    def _on_camera_photo_captured(self, rel_path):
        if len(self.attached_images) < 10:
            self.attached_images.append(rel_path)
            self._refresh_photo_thumbnails()
            if self.selected_cat_id:
                self.controller.set_cat_images(self.selected_cat_id, self.attached_images)
                self.refresh_cat_list()
                if self.on_data_changed:
                    self.on_data_changed()
            self.feedback_lbl.configure(
                text=f"📷 Photo captured & saved! ({len(self.attached_images)}/10 photos)",
                text_color="#10b981"
            )

    def _handle_paste_photo(self):
        """Pastes image from system clipboard (e.g. from Snipping tool, Win+Shift+S, or copied file)."""
        if len(self.attached_images) >= 10:
            messagebox.showwarning("Limit Reached", "A maximum of 10 photos can be attached per cat.")
            return

        try:
            img = ImageGrab.grabclipboard()
            if img is None:
                messagebox.showinfo(
                    "Clipboard Empty",
                    "No image found in clipboard.\n\nTip: Take a screenshot with Win + Shift + S, then click 'Paste (Ctrl+V)'."
                )
                return

            if isinstance(img, list):
                # list of copied file paths
                added = 0
                for fp in img:
                    if len(self.attached_images) >= 10:
                        break
                    if fp.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                        rel = ImageService.save_image_from_path(fp, cat_id=self.selected_cat_id or 0)
                        self.attached_images.append(rel)
                        added += 1
                if not added:
                    messagebox.showinfo("Clipboard", "No image files found in copied items.")
                    return
            elif isinstance(img, Image.Image):
                import io
                buf = io.BytesIO()
                img.convert("RGB").save(buf, format="JPEG", quality=90)
                rel = ImageService.save_image_from_bytes(buf.getvalue(), cat_id=self.selected_cat_id or 0)
                self.attached_images.append(rel)
            else:
                messagebox.showinfo("Clipboard", "Clipboard does not contain image data.")
                return

            self._refresh_photo_thumbnails()
            if self.selected_cat_id:
                self.controller.set_cat_images(self.selected_cat_id, self.attached_images)
                self.refresh_cat_list()
                if self.on_data_changed:
                    self.on_data_changed()
            self.feedback_lbl.configure(
                text=f"📋 Pasted photo saved! ({len(self.attached_images)}/10 photos)",
                text_color="#10b981"
            )
        except Exception as e:
            messagebox.showerror("Paste Error", f"Failed to paste image: {e}")

    def _remove_attached_photo(self, index):
        if 0 <= index < len(self.attached_images):
            self.attached_images.pop(index)
            self._refresh_photo_thumbnails()
            if self.selected_cat_id:
                self.controller.set_cat_images(self.selected_cat_id, self.attached_images)
                self.refresh_cat_list()
                if self.on_data_changed:
                    self.on_data_changed()
            self.feedback_lbl.configure(
                text=f"Photo removed. ({len(self.attached_images)}/10 photos remaining)",
                text_color=Theme.TEXT_MUTED
            )

    def _view_full_photo(self, initial_index):
        if self.attached_images:
            name = self.name_entry.get().strip() or "Cat"
            ImageViewerModal(
                self,
                self.attached_images,
                initial_index=initial_index,
                title_prefix=f"{name} Photo"
            )

    def _view_cat_gallery(self, cat: Cat):
        if cat.images:
            ImageViewerModal(
                self,
                cat.images,
                initial_index=0,
                title_prefix=f"{cat.name} ({cat.breed})"
            )
        else:
            messagebox.showinfo("No Photos", f"Cat #{cat.id} ({cat.name}) does not have attached photos yet.")

    # ==========================================
    # DIRECTORY LIST REFRESH
    # ==========================================
    def refresh_cat_list(self, cats=None):
        """Refreshes the right-panel list with cat records and visual thumbnail avatars."""
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        if cats is None:
            status_filter = self.filter_menu.get()
            search_txt = self.search_entry.get().strip()
            if search_txt:
                cats = self.controller.search_cats(search_txt, status_filter)
            else:
                cats = self.controller.get_all_cats(status_filter)

        total_count = len(cats) if cats else 0
        if hasattr(self, "count_badge"):
            self.count_badge.configure(text=f"{total_count} Cat{'s' if total_count != 1 else ''}")

        if not cats:
            no_data_lbl = ctk.CTkLabel(self.rows_frame, text="No cat records found.", text_color=Theme.TEXT_MUTED, font=Theme.font_subtitle())
            no_data_lbl.grid(row=0, column=0, pady=40)
            return

        for idx, cat in enumerate(cats):
            is_selected = (self.selected_cat_id == cat.id)
            row_bg = ("#f3e8ff", "#362e4a") if is_selected else Theme.BG_CARD_ALT
            row_border = Theme.BORDER_ACCENT if is_selected else Theme.BORDER

            row_frame = ctk.CTkFrame(
                self.rows_frame,
                fg_color=row_bg,
                border_width=1,
                border_color=row_border,
                corner_radius=8
            )
            row_frame.grid(row=idx, column=0, sticky="ew", pady=3)
            row_frame.grid_columnconfigure(0, weight=1, minsize=50)   # ID
            row_frame.grid_columnconfigure(1, weight=2, minsize=115)  # Photo + Name
            row_frame.grid_columnconfigure(2, weight=2, minsize=100)  # Breed
            row_frame.grid_columnconfigure(3, weight=1, minsize=75)   # Age
            row_frame.grid_columnconfigure(4, weight=2, minsize=95)   # Status
            row_frame.grid_columnconfigure(5, weight=1, minsize=75)   # Cage

            # Col 0: ID
            id_lbl = ctk.CTkLabel(row_frame, text=f"#{cat.id}", font=Theme.font_caption_bold(), text_color=Theme.TEXT_MUTED, anchor="w")
            id_lbl.grid(row=0, column=0, sticky="w", padx=(12, 5), pady=7)

            # Col 1: Photo Thumbnail Avatar + Name
            name_cell = ctk.CTkFrame(row_frame, fg_color="transparent")
            name_cell.grid(row=0, column=1, sticky="w", padx=5, pady=4)

            cat_thumb = ImageService.get_ctk_image(cat.primary_image, size=(34, 34))
            if cat_thumb:
                thumb_lbl = ctk.CTkLabel(name_cell, image=cat_thumb, text="", cursor="hand2")
                thumb_lbl.pack(side="left", padx=(0, 8))
                thumb_lbl.bind("<Button-1>", lambda e, c=cat: self._view_cat_gallery(c))
            else:
                thumb_lbl = ctk.CTkLabel(name_cell, text="🐱", font=ctk.CTkFont(size=16))
                thumb_lbl.pack(side="left", padx=(0, 8))

            name_lbl = ctk.CTkLabel(name_cell, text=cat.name, font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY, anchor="w")
            name_lbl.pack(side="left")

            # Col 2: Breed
            breed_lbl = ctk.CTkLabel(row_frame, text=cat.breed, font=Theme.font_caption(), text_color=Theme.TEXT_ACCENT, anchor="w")
            breed_lbl.grid(row=0, column=2, sticky="w", padx=5, pady=7)

            # Col 3: Age
            age_lbl = ctk.CTkLabel(row_frame, text=cat.formatted_age, font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY, anchor="w")
            age_lbl.grid(row=0, column=3, sticky="w", padx=5, pady=7)

            # Col 4: Status Badge (Modern Pill)
            s_bg, s_txt = Theme.get_status_colors(cat.adoption_status)
            status_lbl = ctk.CTkLabel(
                row_frame,
                text=f"  {cat.adoption_status}  ",
                text_color=s_txt,
                fg_color=s_bg,
                corner_radius=Theme.RADIUS_PILL,
                font=Theme.font_tiny(),
                anchor="center"
            )
            status_lbl.grid(row=0, column=4, sticky="ew", padx=10, pady=7)

            # Col 5: Cage
            cage_lbl = ctk.CTkLabel(row_frame, text=cat.cage_number or "-", font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY, anchor="w")
            cage_lbl.grid(row=0, column=5, sticky="w", padx=5, pady=7)

            # Hover & Click events
            def make_hover_handlers(f=row_frame, c_id=cat.id):
                def on_enter(e):
                    if self.selected_cat_id != c_id:
                        f.configure(fg_color=Theme.BG_CARD_HOVER)
                def on_leave(e):
                    if self.selected_cat_id != c_id:
                        f.configure(fg_color=Theme.BG_CARD_ALT)
                return on_enter, on_leave

            h_enter, h_leave = make_hover_handlers()

            for widget in (row_frame, id_lbl, name_cell, name_lbl, breed_lbl, age_lbl, status_lbl, cage_lbl):
                widget.bind("<Enter>", h_enter)
                widget.bind("<Leave>", h_leave)
                widget.bind("<Button-1>", lambda e, c=cat: self._select_cat(c))

    def _select_cat(self, cat: Cat):
        """Populates form and loads photos for the selected cat."""
        self.selected_cat_id = cat.id
        self.id_display.configure(text=f"Cat #{cat.id}")
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, cat.name)

        self.breed_entry.delete(0, "end")
        self.breed_entry.insert(0, cat.breed)

        self.age_entry.delete(0, "end")
        self.age_entry.insert(0, str(cat.age_months))

        self.gender_menu.set(cat.gender)

        self.color_entry.delete(0, "end")
        self.color_entry.insert(0, cat.color)

        self.intake_entry.delete(0, "end")
        self.intake_entry.insert(0, str(cat.intake_date))

        self.health_entry.delete(0, "end")
        self.health_entry.insert(0, cat.health_status)

        self.spayed_var.set(cat.is_spayed_neutered)
        self.status_menu.set(cat.adoption_status)

        self.cage_entry.delete(0, "end")
        self.cage_entry.insert(0, cat.cage_number)

        self.notes_box.delete("1.0", "end")
        self.notes_box.insert("1.0", cat.notes or "")

        # Load attached photos (up to 10)
        self.attached_images = list(cat.images)
        self._refresh_photo_thumbnails()

        self.feedback_lbl.configure(text=f"Editing Cat #{cat.id}: {cat.name}", text_color=Theme.TEXT_ACCENT)
        self.refresh_cat_list()

    def clear_form(self):
        """Clears all input fields and attached photos."""
        self.selected_cat_id = None
        self.attached_images = []
        self._refresh_photo_thumbnails()

        self.id_display.configure(text="[ New Cat ]")
        self.name_entry.delete(0, "end")
        self.breed_entry.delete(0, "end")
        self.age_entry.delete(0, "end")
        self.gender_menu.set("Female")
        self.color_entry.delete(0, "end")
        self.intake_entry.delete(0, "end")
        self.intake_entry.insert(0, date.today().isoformat())
        self.health_entry.delete(0, "end")
        self.health_entry.insert(0, "Healthy")
        self.spayed_var.set(False)
        self.status_menu.set("Available")
        self.cage_entry.delete(0, "end")
        self.notes_box.delete("1.0", "end")
        self.feedback_lbl.configure(text="Ready for cat intake or selection", text_color=Theme.TEXT_MUTED)
        self.refresh_cat_list()

    def _handle_add(self):
        try:
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showwarning("Validation Error", "Please enter the cat's name.")
                return

            age_val = self.age_entry.get().strip() or "12"
            new_cat = Cat(
                name=name,
                breed=self.breed_entry.get().strip() or "Domestic Shorthair",
                age_months=int(age_val),
                gender=self.gender_menu.get(),
                color=self.color_entry.get().strip() or "Mixed",
                intake_date=self.intake_entry.get().strip() or date.today().isoformat(),
                health_status=self.health_entry.get().strip() or "Healthy",
                is_spayed_neutered=self.spayed_var.get(),
                adoption_status=self.status_menu.get(),
                cage_number=self.cage_entry.get().strip() or "Cage A-1",
                notes=self.notes_box.get("1.0", "end").strip(),
                images=list(self.attached_images)
            )

            success, res = self.controller.create_cat(new_cat)
            if success:
                self.feedback_lbl.configure(text=f"Cat '{name}' registered successfully with {len(self.attached_images)} photos!", text_color="#10b981")
                self.clear_form()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                self.feedback_lbl.configure(text=res, text_color=Theme.DANGER)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _handle_update(self):
        if not self.selected_cat_id:
            messagebox.showwarning("No Selection", "Please select a cat from the list to update.")
            return

        try:
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showwarning("Validation Error", "Cat name cannot be empty.")
                return

            age_val = self.age_entry.get().strip() or "12"
            cat_to_update = Cat(
                id=self.selected_cat_id,
                name=name,
                breed=self.breed_entry.get().strip() or "Domestic Shorthair",
                age_months=int(age_val),
                gender=self.gender_menu.get(),
                color=self.color_entry.get().strip() or "Mixed",
                intake_date=self.intake_entry.get().strip() or date.today().isoformat(),
                health_status=self.health_entry.get().strip() or "Healthy",
                is_spayed_neutered=self.spayed_var.get(),
                adoption_status=self.status_menu.get(),
                cage_number=self.cage_entry.get().strip() or "Cage A-1",
                notes=self.notes_box.get("1.0", "end").strip(),
                images=list(self.attached_images)
            )

            success, msg = self.controller.update_cat(cat_to_update)
            if success:
                self.feedback_lbl.configure(text=f"Cat #{self.selected_cat_id} updated with {len(self.attached_images)} photos!", text_color="#10b981")
                self.refresh_cat_list()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                self.feedback_lbl.configure(text=msg, text_color=Theme.DANGER)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _handle_delete(self):
        if not self.selected_cat_id:
            messagebox.showwarning("No Selection", "Please select a cat from the list to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete Cat #{self.selected_cat_id} ({self.name_entry.get()})?\nAll attached photos will also be deleted."
        )
        if confirm:
            success, msg = self.controller.delete_cat(self.selected_cat_id)
            if success:
                self.feedback_lbl.configure(text=msg, text_color=Theme.DANGER)
                self.clear_form()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                self.feedback_lbl.configure(text=msg, text_color=Theme.DANGER)

    def _handle_search(self):
        search_txt = self.search_entry.get().strip()
        status_filter = self.filter_menu.get()
        if search_txt:
            results = self.controller.search_cats(search_txt, status_filter)
        else:
            results = self.controller.get_all_cats(status_filter)
        self.refresh_cat_list(results)
