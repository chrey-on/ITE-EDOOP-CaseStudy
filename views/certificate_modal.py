"""
Adoption Certificate Modal and Print Generator for PurrfectMatch.
Generates an official Certificate of Adoption with cat details, adopter profile,
shelter crest, date, and 1-click printable HTML/PDF export.
"""

import os
import webbrowser
import tempfile
from datetime import date
import customtkinter as ctk

from controllers.image_service import ImageService
from views.theme import Theme
from views.toast import ToastNotification


class AdoptionCertificateModal(ctk.CTkToplevel):
    def __init__(self, parent, application_data: dict):
        super().__init__(parent)
        self.title("📜 Official Adoption Certificate — PurrfectMatch")
        self.geometry("640x720")
        self.minsize(580, 640)
        self.transient(parent)
        self.grab_set()

        self.app_data = application_data
        self._center_window(parent, 640, 720)
        self._build_ui()

    def _center_window(self, parent, width, height):
        parent.update_idletasks()
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = max(20, px + (pw // 2) - (width // 2))
        y = max(20, py + (ph // 2) - (height // 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        self.configure(fg_color=Theme.BG_ROOT)

        # Main Scroll Container
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Certificate Card with Double Border
        cert_card = ctk.CTkFrame(
            scroll,
            corner_radius=16,
            fg_color=Theme.BG_CARD,
            border_width=2,
            border_color=Theme.BORDER_ACCENT
        )
        cert_card.pack(fill="both", expand=True, padx=4, pady=4)

        # Top Ornate Bar
        top_bar = ctk.CTkFrame(cert_card, height=8, fg_color=Theme.PRIMARY, corner_radius=0)
        top_bar.pack(fill="x")

        # Inner Content Padding
        inner = ctk.CTkFrame(cert_card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=24)

        # Shelter Crest & Brand
        crest_lbl = ctk.CTkLabel(
            inner,
            text="🐾",
            font=ctk.CTkFont(size=36)
        )
        crest_lbl.pack(pady=(0, 2))

        shelter_title = ctk.CTkLabel(
            inner,
            text="PURRFECTMATCH ANIMAL SHELTER",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=Theme.TEXT_MUTED
        )
        shelter_title.pack()

        cert_heading = ctk.CTkLabel(
            inner,
            text="Certificate of Adoption",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        cert_heading.pack(pady=(4, 16))

        # Declaration Text
        cat_name = self.app_data.get("cat_name", "Lovely Cat")
        adopter_name = self.app_data.get("adopter_name", "Loving Family")
        app_date = self.app_data.get("application_date", str(date.today()))

        declaration = (
            f"This is to certify that\n\n"
            f"✨  {cat_name.upper()}  ✨\n\n"
            f"has officially found a forever home and has been lovingly adopted by\n\n"
            f"❤️  {adopter_name}  ❤️\n\n"
            f"on this day of {app_date}."
        )

        decl_lbl = ctk.CTkLabel(
            inner,
            text=declaration,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=Theme.TEXT_SECONDARY,
            justify="center"
        )
        decl_lbl.pack(pady=10)

        # Cat Photo & Details Box
        details_box = ctk.CTkFrame(
            inner,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.BG_CARD_ALT,
            border_width=1,
            border_color=Theme.BORDER
        )
        details_box.pack(fill="x", pady=16, padx=10)
        details_box.grid_columnconfigure(1, weight=1)

        # Photo Preview
        primary_img = self.app_data.get("primary_image")
        ctk_img = ImageService.get_ctk_image(primary_img, size=(110, 110))
        if ctk_img:
            photo_lbl = ctk.CTkLabel(details_box, image=ctk_img, text="", corner_radius=10)
            photo_lbl.grid(row=0, column=0, rowspan=4, padx=12, pady=12)
        else:
            photo_placeholder = ctk.CTkLabel(
                details_box,
                text="🐱\nShelter Pet",
                font=Theme.font_caption(),
                width=110,
                height=110,
                fg_color=Theme.BG_CARD,
                corner_radius=10
            )
            photo_placeholder.grid(row=0, column=0, rowspan=4, padx=12, pady=12)

        # Metadata Specs
        breed = self.app_data.get("breed", "Domestic Shorthair")
        color = self.app_data.get("color", "Mixed")
        gender = self.app_data.get("gender", "Unknown")
        cage = self.app_data.get("cage_number", "Shelter Care")

        ctk.CTkLabel(
            details_box,
            text=f"Pet Name: {cat_name}  •  Breed: {breed}",
            font=Theme.font_caption_bold(),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=1, sticky="w", pady=(12, 2))

        ctk.CTkLabel(
            details_box,
            text=f"Coat: {color}  •  Gender: {gender}",
            font=Theme.font_caption(),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        ).grid(row=1, column=1, sticky="w", pady=2)

        ctk.CTkLabel(
            details_box,
            text=f"Intake Unit: {cage}  •  Status: Officially Rehomed",
            font=Theme.font_caption(),
            text_color=Theme.SUCCESS[0],
            anchor="w"
        ).grid(row=2, column=1, sticky="w", pady=2)

        ctk.CTkLabel(
            details_box,
            text=f"Certificate ID: PM-ADOPT-{self.app_data.get('id', 0):04d}",
            font=Theme.font_tiny(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).grid(row=3, column=1, sticky="w", pady=(2, 12))

        # Bottom Signatures Row
        sig_row = ctk.CTkFrame(inner, fg_color="transparent")
        sig_row.pack(fill="x", pady=(20, 8))
        sig_row.grid_columnconfigure((0, 1), weight=1)

        sig1 = ctk.CTkFrame(sig_row, fg_color="transparent")
        sig1.grid(row=0, column=0, padx=16, sticky="ew")
        ctk.CTkFrame(sig1, height=1, fg_color=Theme.BORDER[1]).pack(fill="x")
        ctk.CTkLabel(sig1, text="Adopter's Signature", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED).pack(pady=4)

        sig2 = ctk.CTkFrame(sig_row, fg_color="transparent")
        sig2.grid(row=0, column=1, padx=16, sticky="ew")
        ctk.CTkFrame(sig2, height=1, fg_color=Theme.BORDER[1]).pack(fill="x")
        ctk.CTkLabel(sig2, text="Shelter Director / Caregiver", font=Theme.font_tiny(), text_color=Theme.TEXT_MUTED).pack(pady=4)

        # Bottom Action Buttons Bar
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=20, pady=(6, 18))
        action_bar.grid_columnconfigure((0, 1), weight=1)

        print_btn = ctk.CTkButton(
            action_bar,
            text="🖨️ Export & Print Certificate (HTML / PDF)",
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self.export_and_open_html
        )
        print_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        close_btn = ctk.CTkButton(
            action_bar,
            text="Close",
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            font=Theme.font_body_bold(),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            command=self.destroy
        )
        close_btn.grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def export_and_open_html(self):
        """Generates an official, high-resolution HTML certificate and opens it in browser."""
        cat_name = self.app_data.get("cat_name", "Lovely Cat")
        adopter_name = self.app_data.get("adopter_name", "Adopter")
        app_date = self.app_data.get("application_date", str(date.today()))
        cert_id = f"PM-ADOPT-{self.app_data.get('id', 0):04d}"
        breed = self.app_data.get("breed", "Domestic Shorthair")
        color = self.app_data.get("color", "Mixed")
        gender = self.app_data.get("gender", "Unknown")

        # HTML Template for High-Quality Printable Certificate
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Adoption Certificate - {cat_name}</title>
  <style>
    @page {{
      size: A4 landscape;
      margin: 15mm;
    }}
    body {{
      font-family: 'Georgia', serif;
      background: #fdfbf7;
      color: #2c223a;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      padding: 20px;
      box-sizing: border-box;
    }}
    .cert-frame {{
      width: 900px;
      border: 8px double #9333ea;
      padding: 35px 45px;
      background: #ffffff;
      box-shadow: 0 10px 30px rgba(0,0,0,0.08);
      position: relative;
      text-align: center;
      border-radius: 12px;
    }}
    .corner-dec {{
      position: absolute;
      font-size: 24px;
      color: #9333ea;
    }}
    .tl {{ top: 12px; left: 16px; }}
    .tr {{ top: 12px; right: 16px; }}
    .bl {{ bottom: 12px; left: 16px; }}
    .br {{ bottom: 12px; right: 16px; }}
    .shelter-badge {{
      font-size: 13px;
      letter-spacing: 3px;
      text-transform: uppercase;
      font-weight: bold;
      color: #8b5cf6;
      margin-bottom: 8px;
    }}
    h1 {{
      font-family: 'Cinzel', 'Georgia', serif;
      font-size: 38px;
      margin: 6px 0 16px;
      color: #2e1065;
      letter-spacing: 1px;
    }}
    .lead-text {{
      font-size: 17px;
      color: #581c87;
      margin-bottom: 22px;
      font-style: italic;
    }}
    .highlight {{
      font-size: 32px;
      font-weight: bold;
      color: #7e22ce;
      border-bottom: 2px solid #e9d5ff;
      display: inline-block;
      padding: 0 20px 4px;
      margin: 10px 0;
    }}
    .adopter-name {{
      font-size: 28px;
      font-weight: bold;
      color: #1e1b4b;
      margin: 10px 0;
    }}
    .meta-box {{
      display: flex;
      justify-content: center;
      gap: 30px;
      background: #faf5ff;
      border: 1px dashed #c084fc;
      border-radius: 8px;
      padding: 12px 20px;
      margin: 24px auto;
      max-width: 650px;
      font-size: 14px;
      color: #4c1d95;
    }}
    .signatures {{
      display: flex;
      justify-content: space-between;
      margin-top: 50px;
      padding: 0 40px;
    }}
    .sig-line {{
      width: 240px;
      border-top: 1px solid #4a044e;
      padding-top: 6px;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #6b21a8;
    }}
    .cert-id {{
      position: absolute;
      bottom: 12px;
      right: 25px;
      font-size: 11px;
      color: #a855f7;
      font-family: monospace;
    }}
    @media print {{
      body {{ background: transparent; padding: 0; }}
      .cert-frame {{ box-shadow: none; width: 100%; border: 6px double #9333ea; }}
      .no-print {{ display: none; }}
    }}
    .btn-print {{
      margin-bottom: 15px;
      padding: 10px 20px;
      background: #9333ea;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 15px;
      cursor: pointer;
      font-weight: bold;
    }}
    .btn-print:hover {{
      background: #7e22ce;
    }}
  </style>
</head>
<body>
  <div>
    <div style="text-align: center;" class="no-print">
      <button class="btn-print" onclick="window.print()">🖨️ Click Here to Print / Save as PDF</button>
    </div>
    <div class="cert-frame">
      <span class="corner-dec tl">🐾</span>
      <span class="corner-dec tr">🐾</span>
      <span class="corner-dec bl">🐾</span>
      <span class="corner-dec br">🐾</span>

      <div class="shelter-badge">PurrfectMatch Animal Rescue & Rehoming</div>
      <h1>Official Certificate of Adoption</h1>
      <p class="lead-text">This certifies that through compassion, care, and responsible guardianship,</p>

      <div class="highlight">{cat_name.upper()}</div>
      <p style="font-size: 16px; margin: 12px 0;">has been permanently welcomed into the loving family of</p>
      <div class="adopter-name">{adopter_name}</div>
      <p style="font-size: 14px; color: #6b21a8; margin-top: 8px;">on this day: <strong>{app_date}</strong></p>

      <div class="meta-box">
        <span><strong>Breed:</strong> {breed}</span>
        <span>•</span>
        <span><strong>Color:</strong> {color}</span>
        <span>•</span>
        <span><strong>Gender:</strong> {gender}</span>
        <span>•</span>
        <span><strong>Shelter Registry:</strong> Verified</span>
      </div>

      <div class="signatures">
        <div class="sig-line">Adopter Signature</div>
        <div class="sig-line">Shelter Authority Signature</div>
      </div>

      <div class="cert-id">Registry Seal: {cert_id}</div>
    </div>
  </div>
</body>
</html>
"""
        # Save to temporary file and launch in default web browser
        temp_dir = tempfile.gettempdir()
        cert_filename = f"PurrfectMatch_Certificate_{cat_name}_{self.app_data.get('id', 0)}.html"
        cert_filepath = os.path.join(temp_dir, cert_filename)

        with open(cert_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        webbrowser.open(f"file://{cert_filepath}")
        ToastNotification.show(self, f"Adoption Certificate generated! Opened in browser for printing.", toast_type="success")
