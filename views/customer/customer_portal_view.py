"""
Customer / Adopter Portal View in CustomTkinter.
100% Native Python OOP Desktop GUI.
Features:
- Browse cat catalog as guest.
- Centered Auth Modal (Sign In / Register) appears when clicking 'Adopt Me!' as guest.
- Direct Application modal when logged in.
- 'My Applications' tab for tracking review status.
"""

from datetime import date
from tkinter import messagebox
import customtkinter as ctk

from controllers.cat_controller import CatController
from controllers.adopter_controller import AdopterController
from controllers.application_controller import ApplicationController
from models.adopter import Adopter
from models.application import AdoptionApplication


class CustomerAuthModal(ctk.CTkToplevel):
    """Centered modal for Guest Sign In / Registration."""
    def __init__(self, parent, on_auth_success):
        super().__init__(parent)
        self.title("Sign In or Register to Adopt")
        self.geometry("450x520")
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
        x = px + (pw // 2) - (450 // 2)
        y = py + (ph // 2) - (520 // 2)
        self.geometry(f"450x520+{x}+{y}")

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(hdr, text="🐾 Sign In to Adopt", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Create a profile or sign in to complete your adoption request.", font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w")

        # Tabview: Sign In vs Register
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        tab_signin = self.tabview.add("Sign In")
        tab_signup = self.tabview.add("Register Account")

        # Tab 1: Sign In
        ctk.CTkLabel(tab_signin, text="Enter your Contact Number or Email:", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10, pady=(20, 5))
        self.login_entry = ctk.CTkEntry(tab_signin, placeholder_text="0917-xxx-xxxx or email", height=38)
        self.login_entry.pack(fill="x", padx=10, pady=5)

        self.signin_feedback = ctk.CTkLabel(tab_signin, text="", font=ctk.CTkFont(size=12), text_color="#e74c3c")
        self.signin_feedback.pack(pady=5)

        ctk.CTkButton(
            tab_signin,
            text="Continue to Adoption",
            height=40,
            font=ctk.CTkFont(weight="bold"),
            command=self._handle_signin
        ).pack(fill="x", padx=10, pady=15)

        # Tab 2: Register
        reg_scroll = ctk.CTkScrollableFrame(tab_signup, fg_color="transparent")
        reg_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(reg_scroll, text="Full Name *:").pack(anchor="w", pady=(2, 2))
        self.reg_name = ctk.CTkEntry(reg_scroll, placeholder_text="e.g. Juan Dela Cruz")
        self.reg_name.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Contact Number *:").pack(anchor="w", pady=(2, 2))
        self.reg_contact = ctk.CTkEntry(reg_scroll, placeholder_text="0917-xxx-xxxx")
        self.reg_contact.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Email Address:").pack(anchor="w", pady=(2, 2))
        self.reg_email = ctk.CTkEntry(reg_scroll, placeholder_text="juan@example.com")
        self.reg_email.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Address *:").pack(anchor="w", pady=(2, 2))
        self.reg_address = ctk.CTkEntry(reg_scroll, placeholder_text="Street, City")
        self.reg_address.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(reg_scroll, text="Housing Type:").pack(anchor="w", pady=(2, 2))
        self.reg_housing = ctk.CTkOptionMenu(reg_scroll, values=["House with Yard", "Apartment", "Condo", "Townhouse"])
        self.reg_housing.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            reg_scroll,
            text="Register & Continue",
            height=38,
            fg_color="#27ae60",
            hover_color="#219150",
            font=ctk.CTkFont(weight="bold"),
            command=self._handle_register
        ).pack(fill="x", pady=(5, 10))

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
        self.geometry("500x520")
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
        x = px + (pw // 2) - (500 // 2)
        y = py + (ph // 2) - (520 // 2)
        self.geometry(f"500x520+{x}+{y}")

    def _build_ui(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(hdr, text=f"🐾 Apply to Adopt {self.cat.name}", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Review your details and submit your adoption request.", font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=5)

        # Cat Summary Card
        cat_card = ctk.CTkFrame(body, fg_color=("gray85", "gray25"), corner_radius=8)
        cat_card.pack(fill="x", pady=(5, 10))
        ctk.CTkLabel(cat_card, text=f"🐱 {self.cat.name} ({self.cat.breed})", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(8, 2))
        ctk.CTkLabel(cat_card, text=f"Age: {self.cat.formatted_age}  |  Gender: {self.cat.gender}  |  Coat: {self.cat.color}", font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", padx=12, pady=(0, 8))

        # Adopter Info Card
        adopter_card = ctk.CTkFrame(body, fg_color=("gray85", "gray25"), corner_radius=8)
        adopter_card.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(adopter_card, text=f"Applicant: {self.customer.full_name}", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=(8, 2))
        ctk.CTkLabel(adopter_card, text=f"Contact: {self.customer.contact_number}  |  {self.customer.address}", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=12, pady=(0, 8))

        # Notes / Remarks
        ctk.CTkLabel(body, text="Why do you want to adopt this cat? / Notes:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
        self.notes_box = ctk.CTkTextbox(body, height=80)
        self.notes_box.pack(fill="x", pady=(0, 15))

        # Action Buttons
        btn_frame = ctk.CTkFrame(body, fg_color="transparent")
        btn_frame.pack(fill="x")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="gray",
            hover_color="darkgray",
            height=38,
            command=self.destroy
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="Submit Application 🎉",
            fg_color="#27ae60",
            hover_color="#219150",
            height=38,
            font=ctk.CTkFont(weight="bold"),
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
            messagebox.showinfo("Application Submitted 🎉", f"Thank you, {self.customer.full_name}! Your adoption application for {self.cat.name} has been submitted. Shelter staff will review your request.", parent=self)
            self.destroy()
            self.on_submitted()
        else:
            messagebox.showerror("Error", str(res), parent=self)


class CustomerPortalView(ctk.CTkFrame):
    """Main Public / Adopter view in CustomTkinter."""
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
        # TOP HEADER
        # ==========================================
        header = ctk.CTkFrame(self, height=60, corner_radius=10)
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header.grid_columnconfigure(1, weight=1)

        # Brand
        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        ctk.CTkLabel(brand_frame, text="🐾 PurrfectMatch", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        ctk.CTkLabel(brand_frame, text=" [Adopter Portal]", font=ctk.CTkFont(size=12), text_color="gray").pack(side="left", padx=5)

        # Nav Buttons (Browse Cats vs My Applications)
        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.grid(row=0, column=1, padx=10, pady=10)

        self.nav_catalog_btn = ctk.CTkButton(
            nav_frame,
            text="🐱 Browse Cats",
            width=120,
            command=lambda: self._switch_tab("catalog")
        )
        self.nav_catalog_btn.pack(side="left", padx=5)

        self.nav_apps_btn = ctk.CTkButton(
            nav_frame,
            text="📋 My Applications",
            width=130,
            fg_color=("gray85", "gray25"),
            command=lambda: self._switch_tab("applications")
        )
        self.nav_apps_btn.pack(side="left", padx=5)

        # Auth Badge / Sign In Button
        self.auth_frame = ctk.CTkFrame(header, fg_color="transparent")
        self.auth_frame.grid(row=0, column=2, padx=15, pady=10, sticky="e")
        self._update_auth_header()

        # ==========================================
        # CONTENT AREA
        # ==========================================
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # TAB 1: CATALOG FRAME
        self.catalog_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.catalog_frame.grid(row=0, column=0, sticky="nsew")
        self.catalog_frame.grid_rowconfigure(1, weight=1)
        self.catalog_frame.grid_columnconfigure(0, weight=1)

        # Search & Filter Bar
        filter_bar = ctk.CTkFrame(self.catalog_frame, corner_radius=10)
        filter_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(filter_bar, placeholder_text="🔍 Search available cats by name, breed, or color...")
        self.search_entry.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_catalog())

        self.filter_menu = ctk.CTkOptionMenu(
            filter_bar,
            values=["All", "Kittens (< 1 yr)", "Female", "Male"],
            command=lambda val: self.refresh_catalog()
        )
        self.filter_menu.grid(row=0, column=1, padx=15, pady=10)

        # Scrollable Cards Grid
        self.cards_scroll = ctk.CTkScrollableFrame(self.catalog_frame, corner_radius=10)
        self.cards_scroll.grid(row=1, column=0, sticky="nsew")
        self.cards_scroll.grid_columnconfigure((0, 1, 2), weight=1)

        # TAB 2: MY APPLICATIONS FRAME
        self.apps_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        self.apps_frame.grid_rowconfigure(1, weight=1)
        self.apps_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.apps_frame, text="📋 My Adoption Applications", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        self.user_apps_scroll = ctk.CTkScrollableFrame(self.apps_frame, fg_color="transparent")
        self.user_apps_scroll.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.user_apps_scroll.grid_columnconfigure(0, weight=1)

    def _update_auth_header(self):
        for widget in self.auth_frame.winfo_children():
            widget.destroy()

        if self.current_customer:
            ctk.CTkLabel(self.auth_frame, text=f"👤 {self.current_customer.full_name}", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkButton(
                self.auth_frame,
                text="Sign Out",
                width=75,
                height=28,
                fg_color="#c0392b",
                hover_color="#962d22",
                command=self._logout
            ).pack(side="left", padx=5)
        else:
            ctk.CTkButton(
                self.auth_frame,
                text="Sign In / Register",
                width=130,
                height=32,
                font=ctk.CTkFont(weight="bold"),
                command=self._open_auth_modal
            ).pack(side="left")

    def _switch_tab(self, tab):
        self.active_tab = tab
        if tab == "catalog":
            self.apps_frame.grid_forget()
            self.catalog_frame.grid(row=0, column=0, sticky="nsew")
            self.nav_catalog_btn.configure(fg_color=("#3b8ed0", "#1f6aa5"))
            self.nav_apps_btn.configure(fg_color=("gray85", "gray25"))
            self.refresh_catalog()
        else:
            self.catalog_frame.grid_forget()
            self.apps_frame.grid(row=0, column=0, sticky="nsew")
            self.nav_catalog_btn.configure(fg_color=("gray85", "gray25"))
            self.nav_apps_btn.configure(fg_color=("#3b8ed0", "#1f6aa5"))
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
            ctk.CTkLabel(self.cards_scroll, text="No cats match your filter.", text_color="gray", font=ctk.CTkFont(size=14)).grid(row=0, column=0, columnspan=3, pady=40)
            return

        for idx, cat in enumerate(filtered):
            row = idx // 3
            col = idx % 3

            # Card
            card = ctk.CTkFrame(self.cards_scroll, corner_radius=12)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            # Avatar Header
            avatar_frame = ctk.CTkFrame(card, height=90, fg_color=("gray80", "gray30"), corner_radius=10)
            avatar_frame.pack(fill="x", padx=10, pady=(10, 8))
            ctk.CTkLabel(avatar_frame, text="🐱", font=ctk.CTkFont(size=44)).pack(pady=10)

            # Name & Breed
            ctk.CTkLabel(card, text=cat.name, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=12, pady=(2, 0))
            ctk.CTkLabel(card, text=cat.breed, font=ctk.CTkFont(size=12), text_color="#3498db").pack(anchor="w", padx=12, pady=(0, 4))

            # Details
            ctk.CTkLabel(card, text=f"Age: {cat.formatted_age}  |  {cat.gender}", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=12)
            ctk.CTkLabel(card, text=f"Coat: {cat.color}", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=12, pady=(0, 8))

            # Adopt Button
            if cat.adoption_status == "Available":
                adopt_btn = ctk.CTkButton(
                    card,
                    text="🐾 Adopt Me!",
                    fg_color="#27ae60",
                    hover_color="#219150",
                    font=ctk.CTkFont(weight="bold"),
                    command=lambda c=cat: self._handle_adopt_click(c)
                )
                adopt_btn.pack(fill="x", padx=12, pady=(0, 12))
            else:
                pending_btn = ctk.CTkButton(
                    card,
                    text="Pending Application",
                    fg_color="gray",
                    state="disabled"
                )
                pending_btn.pack(fill="x", padx=12, pady=(0, 12))

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
            prompt.pack(pady=40)
            ctk.CTkLabel(prompt, text="Please sign in to view your submitted applications.", font=ctk.CTkFont(size=14), text_color="gray").pack()
            ctk.CTkButton(prompt, text="Sign In Now", command=self._open_auth_modal).pack(pady=10)
            return

        all_apps = self.app_ctrl.get_all_applications()
        my_apps = [a for a in all_apps if a.adopter_id == self.current_customer.id]

        if not my_apps:
            ctk.CTkLabel(self.user_apps_scroll, text="You have not submitted any adoption applications yet.", text_color="gray", font=ctk.CTkFont(size=13)).pack(pady=40)
            return

        status_colors = {
            "Completed": "#8e44ad",
            "Approved": "#27ae60",
            "Interview Scheduled": "#2980b9",
            "Pending Review": "#e67e22",
            "Rejected": "#c0392b"
        }

        for app in my_apps:
            card = ctk.CTkFrame(self.user_apps_scroll, corner_radius=10)
            card.pack(fill="x", pady=5)
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(card, text=f"Application #{app.id} - 🐱 {app.cat_name}", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 2))
            ctk.CTkLabel(card, text=f"Submitted: {app.application_date}  |  Notes: {app.notes or 'None'}", font=ctk.CTkFont(size=12), text_color="gray").grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

            badge_col = status_colors.get(app.review_status, "gray")
            ctk.CTkLabel(card, text=f" {app.review_status} ", text_color="white", fg_color=badge_col, corner_radius=6).grid(row=0, column=1, rowspan=2, padx=15, pady=10)
