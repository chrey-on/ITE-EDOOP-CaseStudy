"""
Image Service for PurrfectMatch.
Handles image file management, webcam frame capturing, resizing/optimization,
and CustomTkinter CTkImage generation/caching.
"""

import os
import uuid
from PIL import Image
import customtkinter as ctk

# Directory for storing cat images
IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "cat_images")
os.makedirs(IMAGE_DIR, exist_ok=True)


class ImageService:
    _cache = {}

    @staticmethod
    def get_image_dir() -> str:
        os.makedirs(IMAGE_DIR, exist_ok=True)
        return IMAGE_DIR

    @staticmethod
    def save_image_from_path(src_path: str, cat_id: int, max_size=(1000, 800)) -> str:
        """
        Loads an image from source path, optimizes/resizes it, and saves to assets/cat_images/.
        Returns the relative path to the saved image.
        """
        os.makedirs(IMAGE_DIR, exist_ok=True)
        unique_name = f"cat_{cat_id}_{uuid.uuid4().hex[:8]}.jpg"
        dest_path = os.path.join(IMAGE_DIR, unique_name)

        with Image.open(src_path) as img:
            img = img.convert("RGB")
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(dest_path, "JPEG", quality=88, optimize=True)

        return os.path.relpath(dest_path).replace("\\", "/")

    @staticmethod
    def save_image_from_bytes(data: bytes, cat_id: int, max_size=(1000, 800)) -> str:
        """Saves raw image bytes directly to an optimized JPEG."""
        import io
        os.makedirs(IMAGE_DIR, exist_ok=True)
        unique_name = f"cat_{cat_id}_{uuid.uuid4().hex[:8]}.jpg"
        dest_path = os.path.join(IMAGE_DIR, unique_name)

        with Image.open(io.BytesIO(data)) as img:
            img = img.convert("RGB")
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(dest_path, "JPEG", quality=88, optimize=True)

        return os.path.relpath(dest_path).replace("\\", "/")

    @staticmethod
    def save_cv2_frame(frame, cat_id: int, max_size=(1000, 800)) -> str:
        """
        Saves a BGR numpy frame from OpenCV to assets/cat_images/.
        Returns the relative path to the saved image.
        """
        import cv2
        os.makedirs(IMAGE_DIR, exist_ok=True)
        unique_name = f"cat_{cat_id}_{uuid.uuid4().hex[:8]}.jpg"
        dest_path = os.path.join(IMAGE_DIR, unique_name)

        # Convert BGR (OpenCV) to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(dest_path, "JPEG", quality=90, optimize=True)

        return os.path.relpath(dest_path).replace("\\", "/")

    @classmethod
    def get_ctk_image(cls, image_path: str, size=(200, 150)) -> ctk.CTkImage:
        """
        Loads and returns a cached CTkImage with high-quality PIL scaling.
        If file doesn't exist, returns None.
        """
        if not image_path:
            return None

        # Resolve path
        if not os.path.isabs(image_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(base_dir, image_path)
        else:
            full_path = image_path

        if not os.path.isfile(full_path):
            return None

        cache_key = (full_path, size)
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        try:
            with Image.open(full_path) as img:
                img = img.convert("RGB")
                # Create a nicely fitted/cropped thumbnail preserving aspect
                target_w, target_h = size
                
                # Fit within or cover
                img_copy = img.copy()
                img_copy.thumbnail((target_w * 2, target_h * 2), Image.Resampling.LANCZOS)
                
                ctk_img = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=size)
                cls._cache[cache_key] = ctk_img
                return ctk_img
        except Exception as e:
            print(f"Error loading image '{full_path}': {e}")
            return None

    @classmethod
    def delete_image_file(cls, image_path: str):
        """Removes an image file from disk and clears its cache entries."""
        if not image_path:
            return

        if not os.path.isabs(image_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(base_dir, image_path)
        else:
            full_path = image_path

        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception as e:
                print(f"Error deleting file {full_path}: {e}")

        # Clear matching cache
        cls._cache = {k: v for k, v in cls._cache.items() if k[0] != full_path}
