"""
Camera Capture Modal for PurrfectMatch.
Enables shelter staff / administrators to take photos of cats using a webcam.
Features:
- Live video stream preview rendered natively with CTkImage (High-DPI optimized).
- Multi-camera device switching (Camera 0, Camera 1, Camera 2, etc.).
- Camera mirroring (flip horizontal) toggle.
- Camera snapshot flash effect with freeze preview.
- Retake & Save directly to Cat profile.
- Keyboard shortcuts: Space (Snap), Enter (Save), R (Retake), Esc (Close).
"""

from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
from controllers.image_service import ImageService
from views.theme import Theme

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    cv2 = None
    OPENCV_AVAILABLE = False


class CameraCaptureModal(ctk.CTkToplevel):
    def __init__(self, parent, on_photo_captured, cat_id=0):
        super().__init__(parent)
        self.title("📷 Capture Cat Photo")
        self.geometry("580x560")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_photo_captured = on_photo_captured
        self.cat_id = cat_id

        self.cap = None
        self.current_cam_idx = 0
        self.available_cams = self._detect_available_cameras()
        self.is_running = False
        self.current_frame = None
        self.frozen_frame = None
        self.mirror_mode = False

        self._center_modal(parent)
        self._build_ui()

        # Keyboard shortcuts
        self.bind("<space>", lambda e: self._on_space_pressed())
        self.bind("<Return>", lambda e: self._on_enter_pressed())
        self.bind("<r>", lambda e: self._retake() if self.frozen_frame is not None else None)
        self.bind("<R>", lambda e: self._retake() if self.frozen_frame is not None else None)
        self.bind("<Escape>", lambda e: self._on_close())

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._start_camera(self.current_cam_idx)

    def _center_modal(self, parent):
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        x = max(0, px + (pw // 2) - (580 // 2))
        y = max(0, py + (ph // 2) - (560 // 2))
        self.geometry(f"580x560+{x}+{y}")

    def _detect_available_cameras(self) -> list:
        """Probes available camera indices."""
        if not OPENCV_AVAILABLE:
            return [0]
        cams = []
        for idx in range(4):
            try:
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if cap and cap.isOpened():
                    cams.append(idx)
                    cap.release()
                else:
                    cap = cv2.VideoCapture(idx)
                    if cap and cap.isOpened():
                        cams.append(idx)
                        cap.release()
            except Exception:
                pass
        return cams if cams else [0]

    def _build_ui(self):
        # Header Row
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(15, 6))
        hdr.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(hdr, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_box, text="📷 Live Camera Capture", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Position cat in frame • Press Spacebar to snap", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")

        # Camera Switcher + Mirror Controls in Header
        opt_box = ctk.CTkFrame(hdr, fg_color="transparent")
        opt_box.grid(row=0, column=1, sticky="e")

        if len(self.available_cams) > 1:
            cam_options = [f"Camera {i}" for i in self.available_cams]
            self.cam_menu = ctk.CTkOptionMenu(
                opt_box,
                values=cam_options,
                width=110,
                height=28,
                command=self._on_cam_selected
            )
            self.cam_menu.set(f"Camera {self.current_cam_idx}")
            self.cam_menu.pack(side="left", padx=4)

        self.mirror_switch = ctk.CTkCheckBox(
            opt_box,
            text="Mirror",
            font=ctk.CTkFont(size=11),
            width=65,
            height=24,
            command=self._toggle_mirror
        )
        self.mirror_switch.pack(side="left", padx=(4, 0))

        # Video Preview Viewport
        self.preview_container = ctk.CTkFrame(self, width=540, height=360, corner_radius=10, fg_color=("gray85", "gray18"))
        self.preview_container.pack(padx=20, pady=8)
        self.preview_container.pack_propagate(False)

        self.video_label = ctk.CTkLabel(self.preview_container, text="Initializing Camera...", font=ctk.CTkFont(size=13))
        self.video_label.pack(expand=True)

        # Controls Container
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=(10, 15))
        self._render_live_controls()

    def _toggle_mirror(self):
        self.mirror_mode = bool(self.mirror_switch.get())

    def _on_cam_selected(self, choice: str):
        try:
            new_idx = int(choice.replace("Camera ", "").strip())
            if new_idx != self.current_cam_idx:
                self.current_cam_idx = new_idx
                self._start_camera(new_idx)
        except Exception as e:
            print(f"Error switching camera: {e}")

    def _render_live_controls(self):
        for w in self.controls_frame.winfo_children():
            w.destroy()

        self.controls_frame.grid_columnconfigure((0, 1), weight=1)

        self.cancel_btn = ctk.CTkButton(
            self.controls_frame,
            text="Cancel [Esc]",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            font=ctk.CTkFont(size=12),
            command=self._on_close
        )
        self.cancel_btn.grid(row=0, column=0, padx=5, sticky="ew")

        self.capture_btn = ctk.CTkButton(
            self.controls_frame,
            text="📸 Take Photo [Space]",
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            text_color=Theme.SUCCESS_TEXT,
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._take_snapshot
        )
        self.capture_btn.grid(row=0, column=1, padx=5, sticky="ew")

    def _render_freeze_controls(self):
        for w in self.controls_frame.winfo_children():
            w.destroy()

        self.controls_frame.grid_columnconfigure((0, 1), weight=1)

        retake_btn = ctk.CTkButton(
            self.controls_frame,
            text="🔄 Retake [R]",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._retake
        )
        retake_btn.grid(row=0, column=0, padx=5, sticky="ew")

        save_btn = ctk.CTkButton(
            self.controls_frame,
            text="✅ Save Photo to Profile [Enter]",
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.PRIMARY_TEXT,
            height=40,
            corner_radius=Theme.RADIUS_BTN,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._save_photo
        )
        save_btn.grid(row=0, column=1, padx=5, sticky="ew")

    def _start_camera(self, cam_idx=0):
        # Release existing camera if any
        self.is_running = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        if not OPENCV_AVAILABLE:
            self._show_no_camera_message("OpenCV library is not available.")
            return

        # Reset preview viewport
        for w in self.preview_container.winfo_children():
            w.destroy()
        self.video_label = ctk.CTkLabel(self.preview_container, text="Connecting to camera...", font=ctk.CTkFont(size=13))
        self.video_label.pack(expand=True)
        self._render_live_controls()

        try:
            self.cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
            if not self.cap or not self.cap.isOpened():
                # Fallback to default backend
                self.cap = cv2.VideoCapture(cam_idx)

            if not self.cap.isOpened():
                self._show_no_camera_message(f"Could not open Camera {cam_idx}.")
                return

            self.is_running = True
            self._video_loop()
        except Exception as e:
            self._show_no_camera_message(f"Could not connect to camera: {e}")

    def _show_no_camera_message(self, reason):
        for w in self.preview_container.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.preview_container,
            text="⚠️ Camera Unavailable",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e67e22"
        ).pack(pady=(70, 8))

        ctk.CTkLabel(
            self.preview_container,
            text=f"{reason}\n\nPlease check camera permissions or connect an external webcam.\nYou can also attach image files directly from your computer.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            justify="center",
            wraplength=380
        ).pack(padx=20, pady=5)

        for w in self.controls_frame.winfo_children():
            w.destroy()

        ctk.CTkButton(
            self.controls_frame,
            text="Close Camera Window",
            height=38,
            corner_radius=8,
            command=self._on_close
        ).pack(fill="x", padx=10)

    def _video_loop(self):
        if not self.is_running or not self.cap:
            return

        ret, frame = self.cap.read()
        if ret and frame is not None:
            if self.mirror_mode:
                frame = cv2.flip(frame, 1)

            # Store latest raw frame
            self.current_frame = frame

            # Convert BGR to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            pil_img.thumbnail((530, 350), Image.Resampling.LANCZOS)

            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(pil_img.width, pil_img.height))
            self.video_label.configure(image=ctk_img, text="")
            self.video_label.image = ctk_img

        self.after(30, self._video_loop)

    def _on_space_pressed(self):
        if self.is_running:
            self._take_snapshot()

    def _on_enter_pressed(self):
        if self.frozen_frame is not None:
            self._save_photo()

    def _take_snapshot(self):
        if hasattr(self, "current_frame") and self.current_frame is not None:
            self.is_running = False
            self.frozen_frame = self.current_frame.copy()

            # Render frozen preview
            rgb = cv2.cvtColor(self.frozen_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            pil_img.thumbnail((530, 350), Image.Resampling.LANCZOS)

            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(pil_img.width, pil_img.height))
            self.video_label.configure(image=ctk_img, text="")
            self.video_label.image = ctk_img

            self._render_freeze_controls()

    def _retake(self):
        self.frozen_frame = None
        self.is_running = True
        self._render_live_controls()
        self._video_loop()

    def _save_photo(self):
        if self.frozen_frame is not None:
            try:
                rel_path = ImageService.save_cv2_frame(self.frozen_frame, self.cat_id or 0)
                self.on_photo_captured(rel_path)
                self._on_close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save captured photo: {e}", parent=self)

    def _on_close(self):
        self.is_running = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        self.destroy()
