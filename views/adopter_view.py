"""
Adopter Management View for PurrfectMatch.
Implements full CRUD operations, live search, and form population events for adopters.
"""

from tkinter import messagebox
import customtkinter as ctk
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
        self.grid_columnconfigure(0, weight=4)  # Left panel (Form)
        self.grid_columnconfigure(1, weight=6)  # Right panel (List)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # LEFT PANEL: Adopter Profile Form
        # ==========================================
        form_frame = ctk.CTkScrollableFrame(self, label_text="👤 Adopter Profile Details", corner_radius=10)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        form_frame.grid_columnconfigure(1, weight=1)

        # Row 0: Adopter ID
        ctk.CTkLabel(form_frame, text="Adopter ID:").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.id_display = ctk.CTkLabel(form_frame, text="[New Adopter]", font=ctk.CTkFont(weight="bold"))
        self.id_display.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        # Row 1: Full Name
        ctk.CTkLabel(form_frame, text="Full Name *:").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. Sophia Martinez")
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=6)

        # Row 2: Contact Number
        ctk.CTkLabel(form_frame, text="Contact No. *:").grid(row=2, column=0, sticky="w", padx=10, pady=6)
        self.contact_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. 0917-555-1234")
        self.contact_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=6)

        # Row 3: Email
        ctk.CTkLabel(form_frame, text="Email:").grid(row=3, column=0, sticky="w", padx=10, pady=6)
        self.email_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. sophia@example.com")
        self.email_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=6)

        # Row 4: Address
        ctk.CTkLabel(form_frame, text="Home Address *:").grid(row=4, column=0, sticky="nw", padx=10, pady=6)
        self.address_box = ctk.CTkTextbox(form_frame, height=65)
        self.address_box.grid(row=4, column=1, sticky="ew", padx=10, pady=6)

        # Row 5: Housing Type
        ctk.CTkLabel(form_frame, text="Housing Type:").grid(row=5, column=0, sticky="w", padx=10, pady=6)
        self.housing_menu = ctk.CTkOptionMenu(
            form_frame,
            values=["House with Yard", "Apartment", "Condo", "Townhouse"]
        )
        self.housing_menu.grid(row=5, column=1, sticky="ew", padx=10, pady=6)

        # Row 6: Has other pets
        self.pets_var = ctk.BooleanVar(value=False)
        self.pets_check = ctk.CTkCheckBox(form_frame, text="Already owns other pets", variable=self.pets_var)
        self.pets_check.grid(row=6, column=1, sticky="w", padx=10, pady=8)

        # Row 7: Status
        ctk.CTkLabel(form_frame, text="Status:").grid(row=7, column=0, sticky="w", padx=10, pady=6)
        self.status_menu = ctk.CTkOptionMenu(
            form_frame,
            values=["Active", "Approved", "Inactive"]
        )
        self.status_menu.grid(row=7, column=1, sticky="ew", padx=10, pady=6)

        # Feedback Label
        self.feedback_lbl = ctk.CTkLabel(form_frame, text="", text_color="#2ecc71", font=ctk.CTkFont(size=12))
        self.feedback_lbl.grid(row=8, column=0, columnspan=2, padx=10, pady=(5, 5))

        # Action Buttons (CRUD)
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=9, column=0, columnspan=2, padx=5, pady=(5, 15), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Register Adopter",
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
            text="🗑️ Delete Adopter",
            fg_color="#c0392b",
            hover_color="#962d22",
            command=self._handle_delete
        )
        self.delete_btn.grid(row=1, column=1, padx=5, pady=4, sticky="ew")

        # ==========================================
        # RIGHT PANEL: Search & Table List
        # ==========================================
        list_container = ctk.CTkFrame(self, corner_radius=10)
        list_container.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(2, weight=1)

        # Search Bar
        search_bar = ctk.CTkFrame(list_container, fg_color="transparent")
        search_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        search_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_bar,
            placeholder_text="🔍 Search adopters by name, phone, or email..."
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self._handle_search())

        # Table Header
        tbl_hdr = ctk.CTkFrame(list_container, height=35, fg_color=("gray85", "gray25"))
        tbl_hdr.grid(row=1, column=0, sticky="ew", padx=15, pady=(10, 0))
        tbl_hdr.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(tbl_hdr, text="ID", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Full Name", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Contact No.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Housing", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=6)
        ctk.CTkLabel(tbl_hdr, text="Status", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=6)

        # Scrollable Adopters Rows Frame
        self.rows_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.rows_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 15))
        self.rows_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

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

        if not adopters:
            no_data_lbl = ctk.CTkLabel(self.rows_frame, text="No adopter records found.", text_color="gray")
            no_data_lbl.grid(row=0, column=0, columnspan=5, pady=20)
            return

        for idx, adopter in enumerate(adopters):
            is_selected = (self.selected_adopter_id == adopter.id)
            row_bg = ("#d5dbdb", "#34495e") if is_selected else ("gray90", "gray20")

            row_frame = ctk.CTkFrame(self.rows_frame, fg_color=row_bg, corner_radius=6)
            row_frame.grid(row=idx, column=0, columnspan=5, sticky="ew", pady=3)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

            id_lbl = ctk.CTkLabel(row_frame, text=f"#{adopter.id}")
            id_lbl.grid(row=0, column=0, padx=5, pady=8)

            name_lbl = ctk.CTkLabel(row_frame, text=adopter.full_name, font=ctk.CTkFont(weight="bold"))
            name_lbl.grid(row=0, column=1, padx=5, pady=8)

            contact_lbl = ctk.CTkLabel(row_frame, text=adopter.contact_number)
            contact_lbl.grid(row=0, column=2, padx=5, pady=8)

            housing_lbl = ctk.CTkLabel(row_frame, text=adopter.housing_type)
            housing_lbl.grid(row=0, column=3, padx=5, pady=8)

            status_colors = {
                "Approved": "#27ae60",
                "Active": "#2980b9",
                "Inactive": "#7f8c8d"
            }
            badge_color = status_colors.get(adopter.status, "#7f8c8d")
            status_lbl = ctk.CTkLabel(
                row_frame,
                text=f" {adopter.status} ",
                text_color="white",
                fg_color=badge_color,
                corner_radius=6
            )
            status_lbl.grid(row=0, column=4, padx=5, pady=8)

            # Click row event
            for widget in (row_frame, id_lbl, name_lbl, contact_lbl, housing_lbl, status_lbl):
                widget.bind("<Button-1>", lambda e, a=adopter: self._select_adopter(a))

    def _select_adopter(self, adopter: Adopter):
        """Populates form with selected adopter."""
        self.selected_adopter_id = adopter.id
        self.id_display.configure(text=f"#{adopter.id}")
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
        self.id_display.configure(text="[New Adopter]")
        self.name_entry.delete(0, "end")
        self.contact_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.address_box.delete("1.0", "end")
        self.housing_menu.set("House with Yard")
        self.pets_var.set(False)
        self.status_menu.set("Active")
        self.feedback_lbl.configure(text="")
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
