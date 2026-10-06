"""
Adopter Management View for PurrfectMatch.
Implements full CRUD operations, live search, and form population events for adopters.
"""

from tkinter import messagebox
import customtkinter as ctk
from views.theme import Theme
from controllers.adopter_controller import AdopterController
from models.adopter import Adopter


class AdopterView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.on_data_changed = on_data_changed
        self.controller = AdopterController()
        self.selected_adopter_id = None

        self._build_ui()
        self.refresh_adopter_list()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=5, minsize=380)  # Left panel (Form)
        self.grid_columnconfigure(1, weight=7, minsize=520)  # Right panel (List)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # LEFT PANEL: Adopter Profile Form
        # ==========================================
        form_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        form_frame.grid_columnconfigure(0, weight=1)

        # Header inside form
        header_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 8))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="👤 Adopter Profile Details",
            font=Theme.font_subtitle(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="Register adopters or update applicant profiles",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).grid(row=1, column=0, sticky="w", pady=(1, 6))

        ctk.CTkFrame(header_frame, height=1, fg_color=Theme.BORDER).grid(row=2, column=0, sticky="ew", pady=(2, 0))

        # Fields Grid Container
        fields_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fields_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=0)
        fields_frame.grid_columnconfigure(0, weight=0, minsize=115)
        fields_frame.grid_columnconfigure(1, weight=1)

        # Row 0: Adopter ID
        ctk.CTkLabel(fields_frame, text="Adopter ID:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=0, column=0, sticky="w", padx=(10, 5), pady=4)
        self.id_display = ctk.CTkLabel(
            fields_frame,
            text="[ New Adopter ]",
            font=Theme.font_caption_bold(),
            text_color=Theme.TEXT_PRIMARY,
            fg_color=Theme.BG_CARD_ALT,
            corner_radius=6,
            padx=8,
            pady=3
        )
        self.id_display.grid(row=0, column=1, sticky="w", padx=(5, 10), pady=4)

        # Row 1: Full Name
        ctk.CTkLabel(fields_frame, text="Full Name *:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=1, column=0, sticky="w", padx=(10, 5), pady=4)
        self.name_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="e.g. Sophia Martinez",
            height=34,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            placeholder_text_color=Theme.TEXT_MUTED
        )
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Row 2: Contact Number
        ctk.CTkLabel(fields_frame, text="Contact No. *:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=2, column=0, sticky="w", padx=(10, 5), pady=4)
        self.contact_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="e.g. 0917-555-1234",
            height=34,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            placeholder_text_color=Theme.TEXT_MUTED
        )
        self.contact_entry.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Row 3: Email
        ctk.CTkLabel(fields_frame, text="Email:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=3, column=0, sticky="w", padx=(10, 5), pady=4)
        self.email_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="e.g. sophia@example.com",
            height=34,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            placeholder_text_color=Theme.TEXT_MUTED
        )
        self.email_entry.grid(row=3, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Row 4: Address
        ctk.CTkLabel(fields_frame, text="Home Address *:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="nw").grid(row=4, column=0, sticky="nw", padx=(10, 5), pady=6)
        self.address_box = ctk.CTkTextbox(
            fields_frame,
            height=65,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY
        )
        self.address_box.grid(row=4, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Row 5: Housing Type
        ctk.CTkLabel(fields_frame, text="Housing Type:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=5, column=0, sticky="w", padx=(10, 5), pady=4)
        self.housing_menu = ctk.CTkOptionMenu(
            fields_frame,
            values=["House with Yard", "Apartment", "Condo", "Townhouse"],
            height=32,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_CARD_HOVER,
            button_hover_color=Theme.BORDER_LIGHT,
            text_color=Theme.TEXT_PRIMARY,
            dropdown_fg_color=Theme.BG_CARD,
            dropdown_hover_color=Theme.BG_CARD_HOVER,
            dropdown_text_color=Theme.TEXT_PRIMARY
        )
        self.housing_menu.grid(row=5, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Row 6: Has other pets
        ctk.CTkLabel(fields_frame, text="Other Pets:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=6, column=0, sticky="w", padx=(10, 5), pady=4)
        self.pets_var = ctk.BooleanVar(value=False)
        self.pets_check = ctk.CTkCheckBox(
            fields_frame,
            text="Already owns other pets",
            variable=self.pets_var,
            font=Theme.font_caption(),
            text_color=Theme.TEXT_PRIMARY,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER
        )
        self.pets_check.grid(row=6, column=1, sticky="w", padx=(5, 10), pady=4)

        # Row 7: Status
        ctk.CTkLabel(fields_frame, text="Status:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=7, column=0, sticky="w", padx=(10, 5), pady=4)
        self.status_menu = ctk.CTkOptionMenu(
            fields_frame,
            values=["Active", "Approved", "Inactive"],
            height=32,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_CARD_HOVER,
            button_hover_color=Theme.BORDER_LIGHT,
            text_color=Theme.TEXT_PRIMARY,
            dropdown_fg_color=Theme.BG_CARD,
            dropdown_hover_color=Theme.BG_CARD_HOVER,
            dropdown_text_color=Theme.TEXT_PRIMARY
        )
        self.status_menu.grid(row=7, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Feedback / Status Banner
        self.feedback_frame = ctk.CTkFrame(form_frame, fg_color=Theme.BG_CARD_ALT, corner_radius=6, border_width=1, border_color=Theme.BORDER)
        self.feedback_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(6, 4))
        self.feedback_frame.grid_columnconfigure(0, weight=1)

        self.feedback_lbl = ctk.CTkLabel(
            self.feedback_frame,
            text="Ready for adopter registration or selection",
            text_color=Theme.TEXT_MUTED,
            font=Theme.font_caption()
        )
        self.feedback_lbl.grid(row=0, column=0, padx=8, pady=5)

        # Action Buttons (CRUD)
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=6, pady=(4, 15))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Register Adopter",
            height=36,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            text_color=Theme.SUCCESS_TEXT,
            command=self._handle_add
        )
        self.add_btn.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Update Selected",
            height=36,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.PRIMARY_TEXT,
            command=self._handle_update
        )
        self.update_btn.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Clear Form",
            height=36,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            command=self.clear_form
        )
        self.clear_btn.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete Adopter",
            height=36,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.DANGER,
            hover_color=Theme.DANGER_HOVER,
            text_color=Theme.DANGER_TEXT,
            command=self._handle_delete
        )
        self.delete_btn.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        # ==========================================
        # RIGHT PANEL: Search & Table List
        # ==========================================
        list_container = ctk.CTkFrame(
            self,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=Theme.BORDER
        )
        list_container.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(3, weight=1)

        # Header Bar with Count Badge
        header_bar = ctk.CTkFrame(list_container, fg_color="transparent")
        header_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 6))
        header_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_bar,
            text="📋 Adopter Registry Directory",
            font=Theme.font_subtitle(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        self.count_badge = ctk.CTkLabel(
            header_bar,
            text="0 Adopters",
            font=Theme.font_tiny(),
            fg_color=Theme.BG_CARD_ALT,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Theme.RADIUS_PILL,
            padx=10,
            pady=3
        )
        self.count_badge.grid(row=0, column=1, sticky="e")

        # Search Bar
        search_bar = ctk.CTkFrame(list_container, fg_color="transparent")
        search_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        search_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_bar,
            placeholder_text="🔍 Search adopters by name, phone, or email...",
            height=34,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            placeholder_text_color=Theme.TEXT_MUTED
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self._handle_search())

        # Table Header (Right padded by 31px for 16px scrollbar offset)
        tbl_hdr = ctk.CTkFrame(list_container, height=36, corner_radius=6, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER)
        tbl_hdr.grid(row=2, column=0, sticky="ew", padx=(15, 31), pady=(0, 4))
        tbl_hdr.grid_columnconfigure(0, weight=1, minsize=50)   # ID
        tbl_hdr.grid_columnconfigure(1, weight=2, minsize=120)  # Full Name
        tbl_hdr.grid_columnconfigure(2, weight=2, minsize=110)  # Contact No.
        tbl_hdr.grid_columnconfigure(3, weight=2, minsize=100)  # Housing
        tbl_hdr.grid_columnconfigure(4, weight=1, minsize=85)   # Status

        ctk.CTkLabel(tbl_hdr, text="ID", font=Theme.font_caption_bold(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="w", padx=(12, 5), pady=7)
        ctk.CTkLabel(tbl_hdr, text="Full Name", font=Theme.font_caption_bold(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=1, sticky="w", padx=5, pady=7)
        ctk.CTkLabel(tbl_hdr, text="Contact No.", font=Theme.font_caption_bold(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=2, sticky="w", padx=5, pady=7)
        ctk.CTkLabel(tbl_hdr, text="Housing", font=Theme.font_caption_bold(), text_color=Theme.TEXT_MUTED, anchor="w").grid(row=0, column=3, sticky="w", padx=5, pady=7)
        ctk.CTkLabel(tbl_hdr, text="Status", font=Theme.font_caption_bold(), text_color=Theme.TEXT_MUTED, anchor="center").grid(row=0, column=4, sticky="ew", padx=5, pady=7)

        # Scrollable Adopters Rows Frame
        self.rows_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.rows_frame.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.rows_frame.grid_columnconfigure(0, weight=1)

    def refresh_adopter_list(self, adopters=None):
        """Refreshes the right-panel list with adopter records."""
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        if adopters is None:
            search_txt = self.search_entry.get().strip()
            if search_txt:
                adopters = self.controller.search_adopters(search_txt)
            else:
                adopters = self.controller.get_all_adopters()

        total_count = len(adopters) if adopters else 0
        if hasattr(self, "count_badge"):
            self.count_badge.configure(text=f"{total_count} Adopter{'s' if total_count != 1 else ''}")

        if not adopters:
            no_data_lbl = ctk.CTkLabel(self.rows_frame, text="No adopter records found.", text_color=Theme.TEXT_MUTED, font=Theme.font_body())
            no_data_lbl.grid(row=0, column=0, pady=30)
            return

        for idx, adopter in enumerate(adopters):
            is_selected = (self.selected_adopter_id == adopter.id)
            row_bg = Theme.BG_CARD_HOVER if is_selected else Theme.BG_CARD_ALT

            row_frame = ctk.CTkFrame(
                self.rows_frame,
                fg_color=row_bg,
                corner_radius=6,
                border_width=1,
                border_color=Theme.BORDER_ACCENT if is_selected else Theme.BORDER
            )
            row_frame.grid(row=idx, column=0, sticky="ew", pady=3)
            row_frame.grid_columnconfigure(0, weight=1, minsize=50)   # ID
            row_frame.grid_columnconfigure(1, weight=2, minsize=120)  # Full Name
            row_frame.grid_columnconfigure(2, weight=2, minsize=110)  # Contact No.
            row_frame.grid_columnconfigure(3, weight=2, minsize=100)  # Housing
            row_frame.grid_columnconfigure(4, weight=1, minsize=85)   # Status

            id_lbl = ctk.CTkLabel(row_frame, text=f"#{adopter.id}", font=Theme.font_caption_bold(), text_color=Theme.TEXT_MUTED, anchor="w")
            id_lbl.grid(row=0, column=0, sticky="w", padx=(12, 5), pady=7)

            name_lbl = ctk.CTkLabel(row_frame, text=adopter.full_name, font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY, anchor="w")
            name_lbl.grid(row=0, column=1, sticky="w", padx=5, pady=7)

            contact_lbl = ctk.CTkLabel(row_frame, text=adopter.contact_number, font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY, anchor="w")
            contact_lbl.grid(row=0, column=2, sticky="w", padx=5, pady=7)

            housing_lbl = ctk.CTkLabel(row_frame, text=adopter.housing_type, font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY, anchor="w")
            housing_lbl.grid(row=0, column=3, sticky="w", padx=5, pady=7)

            # Modern Status Pill
            s_bg, s_txt = Theme.get_status_colors(adopter.status)
            status_lbl = ctk.CTkLabel(
                row_frame,
                text=f"  {adopter.status}  ",
                text_color=s_txt,
                fg_color=s_bg,
                corner_radius=Theme.RADIUS_PILL,
                font=Theme.font_tiny(),
                anchor="center"
            )
            status_lbl.grid(row=0, column=4, sticky="ew", padx=10, pady=7)

            # Hover & Click events
            def make_hover_handlers(f=row_frame, a_id=adopter.id):
                def on_enter(e):
                    if self.selected_adopter_id != a_id:
                        f.configure(fg_color=Theme.BG_CARD_HOVER)
                def on_leave(e):
                    if self.selected_adopter_id != a_id:
                        f.configure(fg_color=Theme.BG_CARD_ALT)
                return on_enter, on_leave

            h_enter, h_leave = make_hover_handlers()

            for widget in (row_frame, id_lbl, name_lbl, contact_lbl, housing_lbl, status_lbl):
                widget.bind("<Enter>", h_enter)
                widget.bind("<Leave>", h_leave)
                widget.bind("<Button-1>", lambda e, a=adopter: self._select_adopter(a))

    def _select_adopter(self, adopter: Adopter):
        """Populates form with selected adopter."""
        self.selected_adopter_id = adopter.id
        self.id_display.configure(text=f"Adopter #{adopter.id}")
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, adopter.full_name)

        self.contact_entry.delete(0, "end")
        self.contact_entry.insert(0, adopter.contact_number)

        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, adopter.email or "")

        self.address_box.delete("1.0", "end")
        self.address_box.insert("1.0", adopter.address or "")

        self.housing_menu.set(adopter.housing_type)
        self.pets_var.set(adopter.has_other_pets)
        self.status_menu.set(adopter.status)

        self.feedback_lbl.configure(text=f"Selected Adopter #{adopter.id}: {adopter.full_name}", text_color="#3498db")
        self.refresh_adopter_list()

    def clear_form(self):
        """Clears all form fields."""
        self.selected_adopter_id = None
        self.id_display.configure(text="[ New Adopter ]")
        self.name_entry.delete(0, "end")
        self.contact_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.address_box.delete("1.0", "end")
        self.housing_menu.set("House with Yard")
        self.pets_var.set(False)
        self.status_menu.set("Active")
        self.feedback_lbl.configure(text="Ready for adopter registration or selection", text_color="gray")
        self.refresh_adopter_list()

    def _handle_add(self):
        try:
            name = self.name_entry.get().strip()
            contact = self.contact_entry.get().strip()
            address = self.address_box.get("1.0", "end").strip()

            if not name or not contact or not address:
                messagebox.showwarning("Validation Error", "Full Name, Contact Number, and Address are required.")
                return

            new_adopter = Adopter(
                full_name=name,
                contact_number=contact,
                email=self.email_entry.get().strip(),
                address=address,
                housing_type=self.housing_menu.get(),
                has_other_pets=self.pets_var.get(),
                status=self.status_menu.get()
            )

            success, res = self.controller.create_adopter(new_adopter)
            if success:
                self.feedback_lbl.configure(text=f"Adopter '{name}' registered successfully!", text_color="#2ecc71")
                self.clear_form()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                self.feedback_lbl.configure(text=res, text_color="#e74c3c")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _handle_update(self):
        if not self.selected_adopter_id:
            messagebox.showwarning("No Selection", "Please select an adopter from the list to update.")
            return

        try:
            name = self.name_entry.get().strip()
            contact = self.contact_entry.get().strip()
            address = self.address_box.get("1.0", "end").strip()

            if not name or not contact or not address:
                messagebox.showwarning("Validation Error", "Full Name, Contact Number, and Address are required.")
                return

            adopter_to_update = Adopter(
                id=self.selected_adopter_id,
                full_name=name,
                contact_number=contact,
                email=self.email_entry.get().strip(),
                address=address,
                housing_type=self.housing_menu.get(),
                has_other_pets=self.pets_var.get(),
                status=self.status_menu.get()
            )

            success, msg = self.controller.update_adopter(adopter_to_update)
            if success:
                self.feedback_lbl.configure(text=msg, text_color="#2ecc71")
                self.refresh_adopter_list()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                self.feedback_lbl.configure(text=msg, text_color="#e74c3c")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _handle_delete(self):
        if not self.selected_adopter_id:
            messagebox.showwarning("No Selection", "Please select an adopter from the list to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete Adopter #{self.selected_adopter_id} ({self.name_entry.get()})?\nAssociated applications will also be removed."
        )
        if confirm:
            success, msg = self.controller.delete_adopter(self.selected_adopter_id)
            if success:
                self.feedback_lbl.configure(text=msg, text_color="#e74c3c")
                self.clear_form()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                self.feedback_lbl.configure(text=msg, text_color="#e74c3c")

    def _handle_search(self):
        search_txt = self.search_entry.get().strip()
        if search_txt:
            results = self.controller.search_adopters(search_txt)
        else:
            results = self.controller.get_all_adopters()
        self.refresh_adopter_list(results)
