"""
Adoption Application Management View for PurrfectMatch.
Implements relational matching between Cats and Adopters, status tracking, and event synchronization.
"""

from datetime import date
from tkinter import messagebox
import customtkinter as ctk
from views.theme import Theme
from views.toast import ToastNotification
from views.dialogs import ConfirmModal, AlertModal
from views.certificate_modal import AdoptionCertificateModal
from controllers.application_controller import ApplicationController
from controllers.cat_controller import CatController
from controllers.adopter_controller import AdopterController
from models.application import AdoptionApplication


class ApplicationView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.on_data_changed = on_data_changed

        self.app_controller = ApplicationController()
        self.cat_controller = CatController()
        self.adopter_controller = AdopterController()

        self.selected_app_id = None
        self.cat_lookup = {}       # "Name (Breed) [ID: x]" -> id
        self.adopter_lookup = {}   # "Name (Phone) [ID: x]" -> id

        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=5, minsize=380)  # Left panel (Form)
        self.grid_columnconfigure(1, weight=7, minsize=520)  # Right panel (List)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # LEFT PANEL: Application Form
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
            text="📋 Adoption Application Review",
            font=Theme.font_subtitle(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="Match rescues with adopters & manage application stages",
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

        # Row 0: App ID
        ctk.CTkLabel(fields_frame, text="App ID:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=0, column=0, sticky="w", padx=(10, 5), pady=4)
        self.id_display = ctk.CTkLabel(
            fields_frame,
            text="[ New Application ]",
            font=Theme.font_caption_bold(),
            text_color=Theme.TEXT_PRIMARY,
            fg_color=Theme.BG_CARD_ALT,
            corner_radius=6,
            padx=8,
            pady=3
        )
        self.id_display.grid(row=0, column=1, sticky="w", padx=(5, 10), pady=4)

        # Row 1: Cat Selector
        ctk.CTkLabel(fields_frame, text="Select Cat *:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=1, column=0, sticky="w", padx=(10, 5), pady=4)
        self.cat_menu = ctk.CTkOptionMenu(
            fields_frame,
            values=["Loading..."],
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
        self.cat_menu.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Row 2: Adopter Selector
        ctk.CTkLabel(fields_frame, text="Select Adopter *:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=2, column=0, sticky="w", padx=(10, 5), pady=4)
        self.adopter_menu = ctk.CTkOptionMenu(
            fields_frame,
            values=["Loading..."],
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
        self.adopter_menu.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Row 3: Application Date
        ctk.CTkLabel(fields_frame, text="App Date:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=3, column=0, sticky="w", padx=(10, 5), pady=4)
        self.date_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="YYYY-MM-DD",
            height=34,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            placeholder_text_color=Theme.TEXT_MUTED
        )
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=3, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Row 4: Review Status
        ctk.CTkLabel(fields_frame, text="Review Status:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=4, column=0, sticky="w", padx=(10, 5), pady=4)
        self.status_menu = ctk.CTkOptionMenu(
            fields_frame,
            values=[
                "Pending Review",
                "Interview Scheduled",
                "Approved",
                "Rejected",
                "Completed",
                "Archived"
            ],
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
        self.status_menu.grid(row=4, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Row 5: Notes / Interview Remarks
        ctk.CTkLabel(fields_frame, text="Interview Notes:", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="nw").grid(row=5, column=0, sticky="nw", padx=(10, 5), pady=6)
        self.notes_box = ctk.CTkTextbox(
            fields_frame,
            height=75,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_width=1,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY
        )
        self.notes_box.grid(row=5, column=1, sticky="ew", padx=(5, 10), pady=4)

        # Feedback / Status Banner
        self.feedback_frame = ctk.CTkFrame(form_frame, fg_color=Theme.BG_CARD_ALT, corner_radius=6, border_width=1, border_color=Theme.BORDER)
        self.feedback_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(6, 4))
        self.feedback_frame.grid_columnconfigure(0, weight=1)

        self.feedback_lbl = ctk.CTkLabel(
            self.feedback_frame,
            text="Ready for application submission or review",
            text_color=Theme.TEXT_MUTED,
            font=Theme.font_caption()
        )
        self.feedback_lbl.grid(row=0, column=0, padx=8, pady=5)

        # Action Buttons (CRUD)
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=6, pady=(4, 8))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.submit_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Submit App",
            height=36,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            text_color=Theme.SUCCESS_TEXT,
            command=self._handle_submit
        )
        self.submit_btn.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Update Status",
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

        self.archive_btn = ctk.CTkButton(
            btn_frame,
            text="📦 Archive App",
            height=36,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.WARNING,
            hover_color=Theme.WARNING_HOVER,
            text_color=Theme.WARNING_TEXT,
            command=self._handle_archive_toggle
        )
        self.archive_btn.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        # Quick Finalize Button
        self.finalize_btn = ctk.CTkButton(
            form_frame,
            text="🎉 Finalize Adoption (Mark Completed)",
            height=36,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.PRIMARY_TEXT,
            command=self._handle_quick_finalize
        )
        self.finalize_btn.grid(row=4, column=0, padx=10, pady=(4, 6), sticky="ew")

        # Official Certificate Generator Button
        self.cert_btn = ctk.CTkButton(
            form_frame,
            text="📜 View Adoption Certificate",
            height=36,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            command=self._handle_show_certificate
        )
        self.cert_btn.grid(row=5, column=0, padx=10, pady=(0, 16), sticky="ew")

        # ==========================================
        # RIGHT PANEL: Search, Filter & List
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
            text="📄 Adoption Applications Registry",
            font=Theme.font_subtitle(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        self.count_badge = ctk.CTkLabel(
            header_bar,
            text="0 Applications",
            font=Theme.font_tiny(),
            fg_color=Theme.BG_CARD_ALT,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Theme.RADIUS_PILL,
            padx=10,
            pady=3
        )
        self.count_badge.grid(row=0, column=1, sticky="e")

        # Header Filter Bar
        filter_bar = ctk.CTkFrame(list_container, fg_color="transparent")
        filter_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search applications by cat or adopter name...",
            height=34,
            corner_radius=Theme.RADIUS_INPUT,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            placeholder_text_color=Theme.TEXT_MUTED
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._handle_search())

        self.filter_menu = ctk.CTkOptionMenu(
            filter_bar,
            values=["All Active", "Pending Review", "Interview Scheduled", "Approved", "Completed", "Rejected", "Archived", "All (Incl. Archived)"],
            height=34,
            corner_radius=Theme.RADIUS_INPUT,
            width=175,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_CARD_HOVER,
            button_hover_color=Theme.BORDER_LIGHT,
            text_color=Theme.TEXT_PRIMARY,
            dropdown_fg_color=Theme.BG_CARD,
            dropdown_hover_color=Theme.BG_CARD_HOVER,
            dropdown_text_color=Theme.TEXT_PRIMARY,
            command=lambda val: self._handle_search()
        )
        self.filter_menu.set("All Active")
        self.filter_menu.grid(row=0, column=1, sticky="e")

        # Table Header (Right padded by 31px for 16px scrollbar offset)
        tbl_hdr = ctk.CTkFrame(list_container, height=36, corner_radius=6, fg_color=Theme.BG_CARD_ALT, border_width=1, border_color=Theme.BORDER)
        tbl_hdr.grid(row=2, column=0, sticky="ew", padx=(15, 31), pady=(0, 4))
        tbl_hdr.grid_columnconfigure(0, weight=1, minsize=50)   # ID
        tbl_hdr.grid_columnconfigure(1, weight=2, minsize=110)  # Cat Name
        tbl_hdr.grid_columnconfigure(2, weight=2, minsize=120)  # Adopter Name
        tbl_hdr.grid_columnconfigure(3, weight=1, minsize=85)   # Date
        tbl_hdr.grid_columnconfigure(4, weight=2, minsize=110)  # Status

        ctk.CTkLabel(tbl_hdr, text="ID", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=0, column=0, sticky="w", padx=(12, 5), pady=7)
        ctk.CTkLabel(tbl_hdr, text="Cat Name", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=0, column=1, sticky="w", padx=5, pady=7)
        ctk.CTkLabel(tbl_hdr, text="Adopter Name", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=0, column=2, sticky="w", padx=5, pady=7)
        ctk.CTkLabel(tbl_hdr, text="Date", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="w").grid(row=0, column=3, sticky="w", padx=5, pady=7)
        ctk.CTkLabel(tbl_hdr, text="Status", font=Theme.font_caption_bold(), text_color=Theme.TEXT_SECONDARY, anchor="center").grid(row=0, column=4, sticky="ew", padx=5, pady=7)

        # Scrollable Applications Rows Frame
        self.rows_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.rows_frame.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.rows_frame.grid_columnconfigure(0, weight=1)

    def refresh_dropdowns(self):
        """Populates Cat and Adopter option menus."""
        # Cats: Available + currently selected if editing
        cats = self.cat_controller.get_all_cats()
        self.cat_lookup = {f"#{c.id} - {c.name} ({c.breed}) [{c.adoption_status}]": c.id for c in cats}
        cat_options = list(self.cat_lookup.keys()) if self.cat_lookup else ["No Cats Available"]
        self.cat_menu.configure(values=cat_options)
        if cat_options:
            self.cat_menu.set(cat_options[0])

        # Adopters
        adopters = self.adopter_controller.get_all_adopters()
        self.adopter_lookup = {f"#{a.id} - {a.full_name} ({a.contact_number})": a.id for a in adopters}
        adopter_options = list(self.adopter_lookup.keys()) if self.adopter_lookup else ["No Adopters Registered"]
        self.adopter_menu.configure(values=adopter_options)
        if adopter_options:
            self.adopter_menu.set(adopter_options[0])

    def refresh_applications_list(self, apps=None):
        """Refreshes the right-panel list with application records."""
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        if apps is None:
            status_filter = self.filter_menu.get()
            search_txt = self.search_entry.get().strip()
            if search_txt:
                apps = self.app_controller.search_applications(search_txt, status_filter)
            else:
                apps = self.app_controller.get_all_applications(status_filter)

        total_count = len(apps) if apps else 0
        if hasattr(self, "count_badge"):
            self.count_badge.configure(text=f"{total_count} Application{'s' if total_count != 1 else ''}")

        if not apps:
            empty_frame = Theme.create_empty_state(
                self.rows_frame,
                icon="📋",
                title="No Applications Found",
                subtitle="Try selecting a different status filter or clearing your search."
            )
            empty_frame.grid(row=0, column=0, pady=30)
            return

        for idx, app in enumerate(apps):
            is_selected = (self.selected_app_id == app.id)
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
            row_frame.grid_columnconfigure(1, weight=2, minsize=110)  # Cat Name
            row_frame.grid_columnconfigure(2, weight=2, minsize=120)  # Adopter Name
            row_frame.grid_columnconfigure(3, weight=1, minsize=85)   # Date
            row_frame.grid_columnconfigure(4, weight=2, minsize=110)  # Status

            id_lbl = ctk.CTkLabel(row_frame, text=f"#{app.id}", font=Theme.font_caption_bold(), text_color=Theme.TEXT_MUTED, anchor="w")
            id_lbl.grid(row=0, column=0, sticky="w", padx=(12, 5), pady=7)

            cat_lbl = ctk.CTkLabel(row_frame, text=f"🐱 {app.cat_name}", font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY, anchor="w")
            cat_lbl.grid(row=0, column=1, sticky="w", padx=5, pady=7)

            adopter_lbl = ctk.CTkLabel(row_frame, text=f"👤 {app.adopter_name}", font=Theme.font_body_bold(), text_color=Theme.TEXT_PRIMARY, anchor="w")
            adopter_lbl.grid(row=0, column=2, sticky="w", padx=5, pady=7)

            date_lbl = ctk.CTkLabel(row_frame, text=str(app.application_date), font=Theme.font_caption(), text_color=Theme.TEXT_SECONDARY, anchor="w")
            date_lbl.grid(row=0, column=3, sticky="w", padx=5, pady=7)

            # Modern Status Pill
            s_bg, s_txt = Theme.get_status_colors(app.review_status)
            status_lbl = ctk.CTkLabel(
                row_frame,
                text=f"  {app.review_status}  ",
                text_color=s_txt,
                fg_color=s_bg,
                corner_radius=Theme.RADIUS_PILL,
                font=Theme.font_tiny(),
                anchor="center"
            )
            status_lbl.grid(row=0, column=4, sticky="ew", padx=10, pady=7)

            # Hover & Click events
            def make_hover_handlers(f=row_frame, ap_id=app.id):
                def on_enter(e):
                    if self.selected_app_id != ap_id:
                        f.configure(fg_color=Theme.BG_CARD_HOVER)
                def on_leave(e):
                    if self.selected_app_id != ap_id:
                        f.configure(fg_color=Theme.BG_CARD_ALT)
                return on_enter, on_leave

            h_enter, h_leave = make_hover_handlers()

            for widget in (row_frame, id_lbl, cat_lbl, adopter_lbl, date_lbl, status_lbl):
                widget.bind("<Enter>", h_enter)
                widget.bind("<Leave>", h_leave)
                widget.bind("<Button-1>", lambda e, a=app: self._select_application(a))

    def refresh_all(self):
        self.refresh_dropdowns()
        self.refresh_applications_list()

    def _select_application(self, app: AdoptionApplication):
        """Populates form with selected application and configures dynamic archive/restore actions."""
        self.selected_app_id = app.id
        self.id_display.configure(text=f"App #{app.id}")

        # Match cat dropdown
        for label, c_id in self.cat_lookup.items():
            if c_id == app.cat_id:
                self.cat_menu.set(label)
                break

        # Match adopter dropdown
        for label, a_id in self.adopter_lookup.items():
            if a_id == app.adopter_id:
                self.adopter_menu.set(label)
                break

        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, str(app.application_date))

        self.status_menu.set(app.review_status)

        self.notes_box.delete("1.0", "end")
        self.notes_box.insert("1.0", app.notes or "")

        # Update Archive/Restore button state based on current review_status
        if app.review_status == "Archived":
            self.archive_btn.configure(
                text="🔄 Restore App",
                fg_color=Theme.PRIMARY,
                hover_color=Theme.PRIMARY_HOVER,
                text_color=Theme.PRIMARY_TEXT
            )
            self.finalize_btn.configure(state="disabled")
            self.feedback_lbl.configure(
                text=f"📦 Selected App #{app.id} is ARCHIVED. Click 'Restore App' to reopen review.",
                text_color=Theme.WARNING[0]
            )
        else:
            self.archive_btn.configure(
                text="📦 Archive App",
                fg_color=Theme.WARNING,
                hover_color=Theme.WARNING_HOVER,
                text_color=Theme.WARNING_TEXT
            )
            self.finalize_btn.configure(state="normal")
            self.feedback_lbl.configure(
                text=f"Selected App #{app.id} (Cat: {app.cat_name})",
                text_color=Theme.PRIMARY[0]
            )

        self.refresh_applications_list()

    def clear_form(self):
        """Clears form fields and resets button states."""
        self.selected_app_id = None
        self.id_display.configure(text="[ New Application ]")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, date.today().isoformat())
        self.status_menu.set("Pending Review")
        self.notes_box.delete("1.0", "end")
        self.feedback_lbl.configure(text="Ready for application submission or review", text_color=Theme.TEXT_MUTED[0])
        self.archive_btn.configure(
            text="📦 Archive App",
            fg_color=Theme.WARNING,
            hover_color=Theme.WARNING_HOVER,
            text_color=Theme.WARNING_TEXT
        )
        self.finalize_btn.configure(state="normal")
        self.refresh_dropdowns()
        self.refresh_applications_list()

    def _handle_submit(self):
        cat_key = self.cat_menu.get()
        adopter_key = self.adopter_menu.get()

        cat_id = self.cat_lookup.get(cat_key)
        adopter_id = self.adopter_lookup.get(adopter_key)

        if not cat_id or not adopter_id:
            messagebox.showwarning("Validation Error", "Please select a valid Cat and Adopter.")
            return

        app = AdoptionApplication(
            cat_id=cat_id,
            adopter_id=adopter_id,
            application_date=self.date_entry.get().strip() or date.today().isoformat(),
            review_status=self.status_menu.get(),
            notes=self.notes_box.get("1.0", "end").strip()
        )

        success, res = self.app_controller.create_application(app)
        if success:
            self.feedback_lbl.configure(text="Application submitted successfully!", text_color=Theme.SUCCESS[0])
            self.clear_form()
            if self.on_data_changed:
                self.on_data_changed()
        else:
            self.feedback_lbl.configure(text=str(res), text_color=Theme.DANGER[0])

    def _handle_update(self):
        if not self.selected_app_id:
            messagebox.showwarning("No Selection", "Please select an application to update.")
            return

        new_status = self.status_menu.get()
        notes = self.notes_box.get("1.0", "end").strip()

        success, msg = self.app_controller.update_application(self.selected_app_id, new_status, notes)
        if success:
            self.feedback_lbl.configure(text=msg, text_color=Theme.SUCCESS[0])
            self.refresh_all()
            if self.on_data_changed:
                self.on_data_changed()
        else:
            self.feedback_lbl.configure(text=msg, text_color=Theme.DANGER[0])

    def _handle_quick_finalize(self):
        """Quickly transitions application to Completed and triggers Cat adoption."""
        if not self.selected_app_id:
            ToastNotification.show(self, "Please select an application to finalize.", toast_type="warning")
            return

        def on_finalize_confirmed():
            self.status_menu.set("Completed")
            notes = self.notes_box.get("1.0", "end").strip()
            if "Adoption finalized" not in notes:
                notes = (notes + "\n[System Event: Adoption finalized.]").strip()
                self.notes_box.delete("1.0", "end")
                self.notes_box.insert("1.0", notes)

            success, msg = self.app_controller.update_application(self.selected_app_id, "Completed", notes)
            if success:
                ToastNotification.show(
                    self,
                    "Adoption finalized! Cat status updated to Adopted. 📜 Certificate generated.",
                    toast_type="success",
                    title="Adoption Finalized 🎉"
                )
                self.refresh_all()
                if self.on_data_changed:
                    self.on_data_changed()
                self._handle_show_certificate()
            else:
                self.feedback_lbl.configure(text=msg, text_color=Theme.DANGER[0])
                ToastNotification.show(self, msg, toast_type="danger")

        ConfirmModal(
            self,
            title="Finalize Cat Adoption",
            message="Marking this application as Completed will officially finalize the adoption and update the Cat's status to 'Adopted'.\n\nGenerate and view official adoption certificate now?",
            confirm_text="Finalize Adoption",
            icon="🎉",
            on_confirm=on_finalize_confirmed
        )

    def _handle_show_certificate(self):
        """Displays the official Adoption Certificate preview and printable export."""
        if not self.selected_app_id:
            ToastNotification.show(self, "Please select an application to view its certificate.", toast_type="warning")
            return

        # Fetch full application details
        all_apps = self.app_controller.get_all_applications()
        target_app = next((a for a in all_apps if a.id == self.selected_app_id), None)
        if not target_app:
            ToastNotification.show(self, "Application record not found.", toast_type="danger")
            return

        cat = self.cat_controller.get_cat_by_id(target_app.cat_id)
        adopter = self.adopter_controller.get_adopter_by_id(target_app.adopter_id)

        cert_data = {
            "id": target_app.id,
            "application_date": str(target_app.application_date),
            "review_status": target_app.review_status,
            "cat_name": cat.name if cat else target_app.cat_name,
            "breed": cat.breed if cat else "Domestic Shorthair",
            "color": cat.color if cat else "Mixed",
            "gender": cat.gender if cat else "Unknown",
            "cage_number": cat.cage_number if cat else "Shelter",
            "primary_image": cat.primary_image if cat else None,
            "adopter_name": adopter.full_name if adopter else target_app.adopter_name,
            "contact_number": adopter.contact_number if adopter else "N/A",
            "address": adopter.address if adopter else "N/A"
        }

        AdoptionCertificateModal(self, cert_data)

    def _handle_archive_toggle(self):
        """Archives an active application or restores an archived application."""
        if not self.selected_app_id:
            ToastNotification.show(self, "Please select an application from the list.", toast_type="warning")
            return

        current_status = self.status_menu.get()

        # Retrieve application summary for personalized modal text
        apps = self.app_controller.get_all_applications("All (Incl. Archived)")
        target_app = next((a for a in apps if a.id == self.selected_app_id), None)
        cat_name = target_app.cat_name if target_app else "Rescue Cat"
        adopter_name = target_app.adopter_name if target_app else "Applicant"

        if current_status == "Archived":
            # Action: Restore
            def on_restore_confirmed():
                success, msg = self.app_controller.restore_application(self.selected_app_id)
                if success:
                    ToastNotification.show(
                        self,
                        f"Application #{self.selected_app_id} restored to Pending Review! 🔄",
                        toast_type="success",
                        title="Application Restored"
                    )
                    self.feedback_lbl.configure(text=msg, text_color=Theme.SUCCESS[0])
                    self.clear_form()
                    if self.on_data_changed:
                        self.on_data_changed()
                else:
                    self.feedback_lbl.configure(text=msg, text_color=Theme.DANGER[0])
                    ToastNotification.show(self, msg, toast_type="danger")

            restore_msg = (
                f"Restore Application #{self.selected_app_id} for '{cat_name}' back to the active review pipeline?\n\n"
                "✓ Review Pipeline: Application status will reset to 'Pending Review'.\n"
                f"✓ Rescue Status: '{cat_name}' will automatically be placed on 'Pending' adoption.\n"
                "✓ Audit Trail: A restore event timestamp will be recorded in interview notes."
            )

            ConfirmModal(
                self,
                title="Restore Adoption Application",
                message=restore_msg,
                confirm_text="🔄 Restore Application",
                cancel_text="Keep Archived",
                icon="🔄",
                confirm_color=Theme.PRIMARY,
                confirm_hover=Theme.PRIMARY_HOVER,
                width=520,
                height=320,
                on_confirm=on_restore_confirmed
            )
        else:
            # Action: Archive
            def on_archive_confirmed():
                success, msg = self.app_controller.archive_application(self.selected_app_id)
                if success:
                    ToastNotification.show(
                        self,
                        f"Application #{self.selected_app_id} archived safely. 📦",
                        toast_type="warning",
                        title="Application Archived"
                    )
                    self.feedback_lbl.configure(text=msg, text_color=Theme.WARNING[0])
                    self.clear_form()
                    if self.on_data_changed:
                        self.on_data_changed()
                else:
                    self.feedback_lbl.configure(text=msg, text_color=Theme.DANGER[0])
                    ToastNotification.show(self, msg, toast_type="danger")

            archive_msg = (
                f"Are you sure you want to archive Application #{self.selected_app_id} for '{cat_name}' (Applicant: {adopter_name})?\n\n"
                "✓ Safe Preservation: Full details, dates, and interview remarks remain safely stored.\n"
                "✓ Backtrack Anytime: Choose 'Archived' from the filter dropdown to review or restore.\n"
                f"✓ Cat Availability: If '{cat_name}' has no other pending requests, its status returns to 'Available'."
            )

            ConfirmModal(
                self,
                title="Archive Adoption Application",
                message=archive_msg,
                confirm_text="📦 Archive Application",
                cancel_text="Keep Active",
                icon="📦",
                confirm_color=Theme.WARNING,
                confirm_hover=Theme.WARNING_HOVER,
                width=520,
                height=340,
                on_confirm=on_archive_confirmed
            )

    def _handle_search(self):
        search_txt = self.search_entry.get().strip()
        status_filter = self.filter_menu.get()
        if search_txt:
            results = self.app_controller.search_applications(search_txt, status_filter)
        else:
            results = self.app_controller.get_all_applications(status_filter)
        self.refresh_applications_list(results)
