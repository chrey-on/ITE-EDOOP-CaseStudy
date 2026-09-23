"""
Adoption Application Management View for PurrfectMatch.
Implements relational matching between Cats and Adopters, status tracking, and event synchronization.
"""

from datetime import date
from tkinter import messagebox
import customtkinter as ctk
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
        self.grid_columnconfigure(0, weight=4)  # Left panel (Form)
        self.grid_columnconfigure(1, weight=6)  # Right panel (List)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # LEFT PANEL: Application Form
        # ==========================================
        form_frame = ctk.CTkScrollableFrame(self, label_text="📋 Adoption Application Details", corner_radius=10)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        form_frame.grid_columnconfigure(1, weight=1)

        # Row 0: App ID
        ctk.CTkLabel(form_frame, text="App ID:").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.id_display = ctk.CTkLabel(form_frame, text="[New Application]", font=ctk.CTkFont(weight="bold"))
        self.id_display.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        # Row 1: Cat Selector
        ctk.CTkLabel(form_frame, text="Select Cat *:").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        self.cat_menu = ctk.CTkOptionMenu(form_frame, values=["Loading..."])
        self.cat_menu.grid(row=1, column=1, sticky="ew", padx=10, pady=6)

        # Row 2: Adopter Selector
        ctk.CTkLabel(form_frame, text="Select Adopter *:").grid(row=2, column=0, sticky="w", padx=10, pady=6)
        self.adopter_menu = ctk.CTkOptionMenu(form_frame, values=["Loading..."])
        self.adopter_menu.grid(row=2, column=1, sticky="ew", padx=10, pady=6)

        # Row 3: Application Date
        ctk.CTkLabel(form_frame, text="Date:").grid(row=3, column=0, sticky="w", padx=10, pady=6)
        self.date_entry = ctk.CTkEntry(form_frame, placeholder_text="YYYY-MM-DD")
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=6)

        # Row 4: Review Status
        ctk.CTkLabel(form_frame, text="Review Status:").grid(row=4, column=0, sticky="w", padx=10, pady=6)
        self.status_menu = ctk.CTkOptionMenu(
            form_frame,
            values=[
                "Pending Review",
                "Interview Scheduled",
                "Approved",
                "Rejected",
                "Completed"
            ]
        )
        self.status_menu.grid(row=4, column=1, sticky="ew", padx=10, pady=6)

        # Row 5: Notes / Interview Remarks
        ctk.CTkLabel(form_frame, text="Interview / Notes:").grid(row=5, column=0, sticky="nw", padx=10, pady=6)
        self.notes_box = ctk.CTkTextbox(form_frame, height=85)
        self.notes_box.grid(row=5, column=1, sticky="ew", padx=10, pady=6)

        # Feedback Label
        self.feedback_lbl = ctk.CTkLabel(form_frame, text="", text_color="#2ecc71", font=ctk.CTkFont(size=12))
        self.feedback_lbl.grid(row=6, column=0, columnspan=2, padx=10, pady=(5, 5))

        # Action Buttons (CRUD)
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=7, column=0, columnspan=2, padx=5, pady=(5, 15), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.submit_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Submit Application",
            fg_color="#27ae60",
            hover_color="#219150",
            command=self._handle_submit
        )
        self.submit_btn.grid(row=0, column=0, padx=5, pady=4, sticky="ew")

        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Update Status",
            fg_color="#2980b9",
            hover_color="#2471a3",
            command=self._handle_update
        )
        self.update_btn.grid(row=0, column=1, padx=5, pady=4, sticky="ew")

        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Clear Form",
            fg_color="#7f8c8d",
            hover_color="#707b7c",
            command=self.clear_form
        )
        self.clear_btn.grid(row=1, column=0, padx=5, pady=4, sticky="ew")

        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete Application",
            fg_color="#c0392b",
            hover_color="#962d22",
            command=self._handle_delete
        )
        self.delete_btn.grid(row=1, column=1, padx=5, pady=4, sticky="ew")

        # Quick Finalize Button (Showcases the auto-update event)
        self.finalize_btn = ctk.CTkButton(
            form_frame,
            text="🎉 Finalize Adoption (Mark Completed)",
            fg_color="#8e44ad",
            hover_color="#71368a",
            command=self._handle_quick_finalize
        )
        self.finalize_btn.grid(row=8, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        # ==========================================
        # RIGHT PANEL: Search, Filter & List
        # ==========================================
        list_container = ctk.CTkFrame(self, corner_radius=10)
        list_container.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(2, weight=1)

        # Header Filter Bar
        filter_bar = ctk.CTkFrame(list_container, fg_color="transparent")
        filter_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search applications by cat or adopter name..."
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._handle_search())

        self.filter_menu = ctk.CTkOptionMenu(
            filter_bar,
            values=["All", "Pending Review", "Interview Scheduled", "Approved", "Rejected", "Completed"],
            command=lambda val: self._handle_search()
        )
        self.filter_menu.grid(row=0, column=1, sticky="e")

        # Table Header
        tbl_hdr = ctk.CTkFrame(list_container, height=35, fg_color=("gray85", "gray25"))
        tbl_hdr.grid(row=1, column=0, sticky="ew", padx=15, pady=(10, 0))
        tbl_hdr.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(tbl_hdr, text="ID", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Cat Name", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Adopter Name", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Date", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Status", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=6)

        # Scrollable Applications Rows Frame
        self.rows_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.rows_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 15))
        self.rows_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

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

        if not apps:
            no_data_lbl = ctk.CTkLabel(self.rows_frame, text="No application records found.", text_color="gray")
            no_data_lbl.grid(row=0, column=0, columnspan=5, pady=20)
            return

        for idx, app in enumerate(apps):
            is_selected = (self.selected_app_id == app.id)
            row_bg = ("#d5dbdb", "#34495e") if is_selected else ("gray90", "gray20")

            row_frame = ctk.CTkFrame(self.rows_frame, fg_color=row_bg, corner_radius=6)
            row_frame.grid(row=idx, column=0, columnspan=5, sticky="ew", pady=3)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

            id_lbl = ctk.CTkLabel(row_frame, text=f"#{app.id}")
            id_lbl.grid(row=0, column=0, padx=5, pady=8)

            cat_lbl = ctk.CTkLabel(row_frame, text=f"🐱 {app.cat_name}", font=ctk.CTkFont(weight="bold"))
            cat_lbl.grid(row=0, column=1, padx=5, pady=8)

            adopter_lbl = ctk.CTkLabel(row_frame, text=f"👤 {app.adopter_name}")
            adopter_lbl.grid(row=0, column=2, padx=5, pady=8)

            date_lbl = ctk.CTkLabel(row_frame, text=str(app.application_date))
            date_lbl.grid(row=0, column=3, padx=5, pady=8)

            status_colors = {
                "Completed": "#8e44ad",
                "Approved": "#27ae60",
                "Interview Scheduled": "#2980b9",
                "Pending Review": "#e67e22",
                "Rejected": "#c0392b"
            }
            badge_color = status_colors.get(app.review_status, "#7f8c8d")
            status_lbl = ctk.CTkLabel(
                row_frame,
                text=f" {app.review_status} ",
                text_color="white",
                fg_color=badge_color,
                corner_radius=6
            )
            status_lbl.grid(row=0, column=4, padx=5, pady=8)

            # Click row event
            for widget in (row_frame, id_lbl, cat_lbl, adopter_lbl, date_lbl, status_lbl):
                widget.bind("<Button-1>", lambda e, a=app: self._select_application(a))

    def refresh_all(self):
        self.refresh_dropdowns()
        self.refresh_applications_list()

    def _select_application(self, app: AdoptionApplication):
        """Populates form with selected application."""
        self.selected_app_id = app.id
        self.id_display.configure(text=f"#{app.id}")

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

        self.feedback_lbl.configure(text=f"Selected App #{app.id} (Cat: {app.cat_name})", text_color="#3498db")
        self.refresh_applications_list()

    def clear_form(self):
        """Clears form fields."""
        self.selected_app_id = None
        self.id_display.configure(text="[New Application]")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, date.today().isoformat())
        self.status_menu.set("Pending Review")
        self.notes_box.delete("1.0", "end")
        self.feedback_lbl.configure(text="")
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
            self.feedback_lbl.configure(text="Application submitted successfully!", text_color="#2ecc71")
            self.clear_form()
            if self.on_data_changed:
                self.on_data_changed()
        else:
            self.feedback_lbl.configure(text=str(res), text_color="#e74c3c")

    def _handle_update(self):
        if not self.selected_app_id:
            messagebox.showwarning("No Selection", "Please select an application to update.")
            return

        new_status = self.status_menu.get()
        notes = self.notes_box.get("1.0", "end").strip()

        success, msg = self.app_controller.update_application(self.selected_app_id, new_status, notes)
        if success:
            self.feedback_lbl.configure(text=msg, text_color="#2ecc71")
            self.refresh_all()
            if self.on_data_changed:
                self.on_data_changed()
        else:
            self.feedback_lbl.configure(text=msg, text_color="#e74c3c")

    def _handle_quick_finalize(self):
        """Quickly transitions application to Completed and triggers Cat adoption."""
        if not self.selected_app_id:
            messagebox.showwarning("No Selection", "Please select an application to finalize.")
            return

        confirm = messagebox.askyesno(
            "Finalize Adoption",
            "Marking this application as Completed will officially finalize the adoption and update the Cat status to 'Adopted'. Proceed?"
        )
        if confirm:
            self.status_menu.set("Completed")
            notes = self.notes_box.get("1.0", "end").strip()
            if "Adoption finalized" not in notes:
                notes = (notes + "\n[System Event: Adoption finalized.]").strip()
                self.notes_box.delete("1.0", "end")
                self.notes_box.insert("1.0", notes)

            success, msg = self.app_controller.update_application(self.selected_app_id, "Completed", notes)
            if success:
                messagebox.showinfo("Adoption Finalized 🎉", "Congratulations! The adoption has been completed and the cat's status is now 'Adopted'.")
                self.refresh_all()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                self.feedback_lbl.configure(text=msg, text_color="#e74c3c")

    def _handle_delete(self):
        if not self.selected_app_id:
            messagebox.showwarning("No Selection", "Please select an application to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete Application #{self.selected_app_id}?"
        )
        if confirm:
            success, msg = self.app_controller.delete_application(self.selected_app_id)
            if success:
                self.feedback_lbl.configure(text=msg, text_color="#e74c3c")
                self.clear_form()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                self.feedback_lbl.configure(text=msg, text_color="#e74c3c")

    def _handle_search(self):
        search_txt = self.search_entry.get().strip()
        status_filter = self.filter_menu.get()
        if search_txt:
            results = self.app_controller.search_applications(search_txt, status_filter)
        else:
            results = self.app_controller.get_all_applications(status_filter)
        self.refresh_applications_list(results)
