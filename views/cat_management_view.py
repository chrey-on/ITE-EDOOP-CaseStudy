"""
Cat Management View for PurrfectMatch.
Implements full CRUD operations, live search, status filtering, and form population events.
"""

from datetime import date
from tkinter import messagebox
import customtkinter as ctk
from controllers.cat_controller import CatController
from models.cat import Cat


class CatManagementView(ctk.CTkFrame):
    def __init__(self, master, on_data_changed=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.on_data_changed = on_data_changed
        self.controller = CatController()
        self.selected_cat_id = None

        self._build_ui()
        self.refresh_cat_list()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=4)  # Left panel (Form)
        self.grid_columnconfigure(1, weight=6)  # Right panel (List & Search)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # LEFT PANEL: Cat Intake Form & CRUD Actions
        # ==========================================
        form_frame = ctk.CTkScrollableFrame(self, label_text="🐱 Cat Intake & Profile Details", corner_radius=10)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        form_frame.grid_columnconfigure(1, weight=1)

        # Row 0: Cat ID (Display only)
        ctk.CTkLabel(form_frame, text="Cat ID:").grid(row=0, column=0, sticky="w", padx=10, pady=4)
        self.id_display = ctk.CTkLabel(form_frame, text="[New Cat]", font=ctk.CTkFont(weight="bold"))
        self.id_display.grid(row=0, column=1, sticky="w", padx=10, pady=4)

        # Row 1: Name
        ctk.CTkLabel(form_frame, text="Name *:").grid(row=1, column=0, sticky="w", padx=10, pady=4)
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. Luna")
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=4)

        # Row 2: Breed
        ctk.CTkLabel(form_frame, text="Breed:").grid(row=2, column=0, sticky="w", padx=10, pady=4)
        self.breed_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. British Shorthair")
        self.breed_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=4)

        # Row 3: Age (Months)
        ctk.CTkLabel(form_frame, text="Age (Months):").grid(row=3, column=0, sticky="w", padx=10, pady=4)
        self.age_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. 12")
        self.age_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=4)

        # Row 4: Gender
        ctk.CTkLabel(form_frame, text="Gender:").grid(row=4, column=0, sticky="w", padx=10, pady=4)
        self.gender_menu = ctk.CTkOptionMenu(form_frame, values=["Female", "Male", "Unknown"])
        self.gender_menu.grid(row=4, column=1, sticky="ew", padx=10, pady=4)

        # Row 5: Color
        ctk.CTkLabel(form_frame, text="Color/Coat:").grid(row=5, column=0, sticky="w", padx=10, pady=4)
        self.color_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. Silver Tabby")
        self.color_entry.grid(row=5, column=1, sticky="ew", padx=10, pady=4)

        # Row 6: Intake Date
        ctk.CTkLabel(form_frame, text="Intake Date:").grid(row=6, column=0, sticky="w", padx=10, pady=4)
        self.intake_entry = ctk.CTkEntry(form_frame, placeholder_text="YYYY-MM-DD")
        self.intake_entry.insert(0, date.today().isoformat())
        self.intake_entry.grid(row=6, column=1, sticky="ew", padx=10, pady=4)

        # Row 7: Health Status
        ctk.CTkLabel(form_frame, text="Health Status:").grid(row=7, column=0, sticky="w", padx=10, pady=4)
        self.health_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. Healthy & Vaccinated")
        self.health_entry.grid(row=7, column=1, sticky="ew", padx=10, pady=4)

        # Row 8: Spayed/Neutered Checkbox
        self.spayed_var = ctk.BooleanVar(value=False)
        self.spayed_check = ctk.CTkCheckBox(form_frame, text="Spayed / Neutered", variable=self.spayed_var)
        self.spayed_check.grid(row=8, column=1, sticky="w", padx=10, pady=6)

        # Row 9: Adoption Status
        ctk.CTkLabel(form_frame, text="Status:").grid(row=9, column=0, sticky="w", padx=10, pady=4)
        self.status_menu = ctk.CTkOptionMenu(
            form_frame,
            values=["Available", "Pending", "Adopted", "Medical Hold"]
        )
        self.status_menu.grid(row=9, column=1, sticky="ew", padx=10, pady=4)

        # Row 10: Cage / Pen #
        ctk.CTkLabel(form_frame, text="Shelter Pen/Cage:").grid(row=10, column=0, sticky="w", padx=10, pady=4)
        self.cage_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. Suite A-1")
        self.cage_entry.grid(row=10, column=1, sticky="ew", padx=10, pady=4)

        # Row 11: Notes
        ctk.CTkLabel(form_frame, text="Behavior / Notes:").grid(row=11, column=0, sticky="nw", padx=10, pady=4)
        self.notes_box = ctk.CTkTextbox(form_frame, height=70)
        self.notes_box.grid(row=11, column=1, sticky="ew", padx=10, pady=4)

        # Feedback / Message Label
        self.feedback_lbl = ctk.CTkLabel(form_frame, text="", text_color="#2ecc71", font=ctk.CTkFont(size=12))
        self.feedback_lbl.grid(row=12, column=0, columnspan=2, padx=10, pady=(5, 5))

        # Action Buttons (CRUD)
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=13, column=0, columnspan=2, padx=5, pady=(5, 15), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Add Cat",
            fg_color="#27ae60",
            hover_color="#219150",
            command=self._handle_add
        )
        self.add_btn.grid(row=0, column=0, padx=5, pady=4, sticky="ew")

        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Update Selected",
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
            text="🗑️ Delete Cat",
            fg_color="#c0392b",
            hover_color="#962d22",
            command=self._handle_delete
        )
        self.delete_btn.grid(row=1, column=1, padx=5, pady=4, sticky="ew")

        # ==========================================
        # RIGHT PANEL: Search, Filter, and Table List
        # ==========================================
        list_container = ctk.CTkFrame(self, corner_radius=10)
        list_container.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(2, weight=1)

        # Header & Filter Bar
        filter_bar = ctk.CTkFrame(list_container, fg_color="transparent")
        filter_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        filter_bar.grid_columnconfigure(0, weight=1)

        # Live Search Entry
        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search by name, breed, color, or cage..."
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._handle_search())

        # Status Filter Dropdown
        self.filter_menu = ctk.CTkOptionMenu(
            filter_bar,
            values=["All", "Available", "Pending", "Adopted", "Medical Hold"],
            command=lambda val: self._handle_search()
        )
        self.filter_menu.grid(row=0, column=1, sticky="e")

        # Table Header
        tbl_hdr = ctk.CTkFrame(list_container, height=35, fg_color=("gray85", "gray25"))
        tbl_hdr.grid(row=1, column=0, sticky="ew", padx=15, pady=(10, 0))
        tbl_hdr.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(tbl_hdr, text="ID", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Name", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Breed", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Age", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Status", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Cage", font=ctk.CTkFont(weight="bold")).grid(row=0, column=5, padx=5, pady=6)

        # Scrollable Cat Rows Frame
        self.rows_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.rows_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 15))
        self.rows_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

    def refresh_cat_list(self, cats=None):
        """Refreshes the right-panel list with cat records."""
        # Clear existing row widgets
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        if cats is None:
            status_filter = self.filter_menu.get()
            search_txt = self.search_entry.get().strip()
            if search_txt:
                cats = self.controller.search_cats(search_txt, status_filter)
            else:
                cats = self.controller.get_all_cats(status_filter)

        if not cats:
            no_data_lbl = ctk.CTkLabel(self.rows_frame, text="No cat records found.", text_color="gray")
            no_data_lbl.grid(row=0, column=0, columnspan=6, pady=20)
            return

        for idx, cat in enumerate(cats):
            # Row container card
            is_selected = (self.selected_cat_id == cat.id)
            row_bg = ("#d5dbdb", "#34495e") if is_selected else ("gray90", "gray20")

            row_frame = ctk.CTkFrame(self.rows_frame, fg_color=row_bg, corner_radius=6)
            row_frame.grid(row=idx, column=0, columnspan=6, sticky="ew", pady=3)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            # Columns
            id_lbl = ctk.CTkLabel(row_frame, text=f"#{cat.id}")
            id_lbl.grid(row=0, column=0, padx=5, pady=8)

            name_lbl = ctk.CTkLabel(row_frame, text=cat.name, font=ctk.CTkFont(weight="bold"))
            name_lbl.grid(row=0, column=1, padx=5, pady=8)

            breed_lbl = ctk.CTkLabel(row_frame, text=cat.breed)
            breed_lbl.grid(row=0, column=2, padx=5, pady=8)

            age_lbl = ctk.CTkLabel(row_frame, text=cat.formatted_age)
            age_lbl.grid(row=0, column=3, padx=5, pady=8)

            # Status Badge color
            status_colors = {
                "Available": "#27ae60",
                "Pending": "#e67e22",
                "Adopted": "#2980b9",
                "Medical Hold": "#c0392b"
            }
            badge_color = status_colors.get(cat.adoption_status, "#7f8c8d")
            status_lbl = ctk.CTkLabel(
                row_frame,
                text=f" {cat.adoption_status} ",
                text_color="white",
                fg_color=badge_color,
                corner_radius=6
            )
            status_lbl.grid(row=0, column=4, padx=5, pady=8)

            cage_lbl = ctk.CTkLabel(row_frame, text=cat.cage_number or "-")
            cage_lbl.grid(row=0, column=5, padx=5, pady=8)

            # Click event: populate form
            for widget in (row_frame, id_lbl, name_lbl, breed_lbl, age_lbl, status_lbl, cage_lbl):
                widget.bind("<Button-1>", lambda e, c=cat: self._select_cat(c))

    def _select_cat(self, cat: Cat):
        """Populates form with selected cat details."""
        self.selected_cat_id = cat.id
        self.id_display.configure(text=f"#{cat.id}")
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

        self.feedback_lbl.configure(text=f"Selected Cat #{cat.id}: {cat.name}", text_color="#3498db")
        self.refresh_cat_list()

    def clear_form(self):
        """Clears all input fields in the form."""
        self.selected_cat_id = None
        self.id_display.configure(text="[New Cat]")
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
        self.feedback_lbl.configure(text="")
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
                notes=self.notes_box.get("1.0", "end").strip()
            )

            success, res = self.controller.create_cat(new_cat)
            if success:
                self.feedback_lbl.configure(text=f"Cat '{name}' registered successfully!", text_color="#2ecc71")
                self.clear_form()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                self.feedback_lbl.configure(text=res, text_color="#e74c3c")
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
                notes=self.notes_box.get("1.0", "end").strip()
            )

            success, msg = self.controller.update_cat(cat_to_update)
            if success:
                self.feedback_lbl.configure(text=msg, text_color="#2ecc71")
                self.refresh_cat_list()
                if self.on_data_changed:
                    self.on_data_changed()
            else:
                self.feedback_lbl.configure(text=msg, text_color="#e74c3c")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _handle_delete(self):
        if not self.selected_cat_id:
            messagebox.showwarning("No Selection", "Please select a cat from the list to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete Cat #{self.selected_cat_id} ({self.name_entry.get()})?\nThis action cannot be undone."
        )
        if confirm:
            success, msg = self.controller.delete_cat(self.selected_cat_id)
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
            results = self.controller.search_cats(search_txt, status_filter)
        else:
            results = self.controller.get_all_cats(status_filter)
        self.refresh_cat_list(results)
