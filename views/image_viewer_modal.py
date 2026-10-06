"""
Image Viewer Modal for PurrfectMatch.
Displays full-size cat photos with carousel navigation (Prev/Next) and photo counter.
"""

import customtkinter as ctk
from controllers.image_service import ImageService


class ImageViewerModal(ctk.CTkToplevel):
    def __init__(self, parent, images, initial_index=0, title_prefix="Cat Photo"):
        super().__init__(parent)
        self.images = list(images) if images else []
        self.current_idx = max(0, min(initial_index, len(self.images) - 1)) if self.images else 0
        self.title_prefix = title_prefix

        self.title(f"📷 {self.title_prefix}")
        self.geometry("680x560")
        self.minsize(500, 420)
        self.transient(parent)
        self.grab_set()

        self._center_modal(parent)
        self._build_ui()
        self._show_current_image()

    def _center_modal(self, parent):
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        x = px + (pw // 2) - (680 // 2)
        y = py + (ph // 2) - (560 // 2)
        self.geometry(f"680x560+{x}+{y}")

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header Bar
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        hdr.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            hdr,
            text=f"📷 {self.title_prefix}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_lbl.grid(row=0, column=0, sticky="w")

        self.counter_lbl = ctk.CTkLabel(
            hdr,
            text="0 / 0",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray80", "gray25"),
            corner_radius=10,
            padx=10,
            pady=3
        )
        self.counter_lbl.grid(row=0, column=1, sticky="e")

        # Main Image Container
        self.image_container = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray85", "gray20"))
        self.image_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.image_container.grid_rowconfigure(0, weight=1)
        self.image_container.grid_columnconfigure(0, weight=1)

        self.display_label = ctk.CTkLabel(self.image_container, text="Loading image...")
        self.display_label.grid(row=0, column=0, sticky="nsew")

        # Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        nav_bar.grid_columnconfigure((0, 1, 2), weight=1)

        self.prev_btn = ctk.CTkButton(
            nav_bar,
            text="◀ Previous",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._prev
        )
        self.prev_btn.grid(row=0, column=0, padx=5, sticky="ew")

        close_btn = ctk.CTkButton(
            nav_bar,
            text="Close",
            fg_color="gray",
            hover_color="darkgray",
            height=36,
            corner_radius=8,
            command=self.destroy
        )
        close_btn.grid(row=0, column=1, padx=5, sticky="ew")

        self.next_btn = ctk.CTkButton(
            nav_bar,
            text="Next ▶",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._next
        )
        self.next_btn.grid(row=0, column=2, padx=5, sticky="ew")

        # Key bindings
        self.bind("<Left>", lambda e: self._prev())
        self.bind("<Right>", lambda e: self._next())
        self.bind("<Escape>", lambda e: self.destroy())

    def _show_current_image(self):
        if not self.images:
            self.display_label.configure(image=None, text="No images available")
            self.counter_lbl.configure(text="0 / 0")
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
            return

        total = len(self.images)
        self.counter_lbl.configure(text=f"Photo {self.current_idx + 1} of {total}")
        self.prev_btn.configure(state="normal" if self.current_idx > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_idx < total - 1 else "disabled")

        img_path = self.images[self.current_idx]
        ctk_img = ImageService.get_ctk_image(img_path, size=(600, 420))
        if ctk_img:
            self.display_label.configure(image=ctk_img, text="")
        else:
            self.display_label.configure(image=None, text=f"Could not load image:\n{img_path}")

    def _prev(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self._show_current_image()

    def _next(self):
        if self.current_idx < len(self.images) - 1:
            self.current_idx += 1
            self._show_current_image()
