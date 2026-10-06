"""
Downloads and seeds accurate, high-quality real cat images from public repositories
matching each cat's breed, coat color, and profile characteristics.
"""

import os
import sys

# Ensure root directory is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import json
import urllib.request
import urllib.parse
import ssl
from PIL import Image
from database.db_connection import DatabaseConnection
from controllers.image_service import ImageService
from controllers.cat_controller import CatController

ctx = ssl._create_unverified_context()

def get_wikimedia_url(file_title: str) -> str:
    """Fetches the direct Wikimedia Commons original image URL."""
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&titles={urllib.parse.quote(file_title)}&prop=imageinfo&iiprop=url|mime"
    req = urllib.request.Request(url, headers={"User-Agent": "PurrfectMatchShelter/1.0 (shelter-edu@case-study.edu)"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for pid, p in pages.items():
                if "imageinfo" in p and p["imageinfo"]:
                    return p["imageinfo"][0].get("url")
    except Exception as e:
        print(f"Error fetching url for {file_title}: {e}")
    return None

def download_and_save(url: str, cat_id: int) -> str:
    """Downloads an image from URL and saves via ImageService."""
    req = urllib.request.Request(url, headers={"User-Agent": "PurrfectMatchShelter/1.0 (shelter-edu@case-study.edu)"})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        data = resp.read()
    return ImageService.save_image_from_bytes(data, cat_id)

def seed_images():
    cat_ctrl = CatController()
    cats = cat_ctrl.get_all_cats()
    print(f"Found {len(cats)} cats to check images for.")

    # Curated real photos accurate to each cat's description
    CAT_PHOTOS = {
        # 1: Luna - British Shorthair, Silver Grey
        1: [
            "File:Spiritland British Shorthair Silver Shaded.jpg",
            "File:Silver Classic Tabby British Shorthair Kitten.jpg"
        ],
        # 2: Oliver - Orange Tabby, Ginger Orange
        2: [
            "File:Orange tabby cat sitting on fallen leaves-Hisashi-01A.jpg",
            "File:Ginger cat on the street.jpg",
            "File:Ginger cat on the street02.jpg"
        ],
        # 3: Milo - Calico, Tri-Color
        3: [
            "File:Calico cat, - Assisi, Italy.jpg",
            "File:Calico cat, Lebanon 2.jpg",
            "File:Calico cat, Lebanon 8.jpg"
        ],
        # 4: Bella - Siamese Mix, Seal Point
        4: [
            "File:A classic seal point Siamese cat.jpg",
            "File:Seal Point Siamese cat in a graden (2).jpg",
            "File:Mixed breed tabby seal-point Siamese cat.jpg"
        ],
        # 5: Leo - Maine Coon Mix, Brown Tabby
        5: [
            "File:Maine Coon Cat Atticus.jpg",
            "File:Maine Coon female 2.jpg"
        ],
        # 6: Kasi - Tilapia (Philippine domestic mackerel striped tabby), Grey and black
        6: [
            "File:Grey tabby cat.jpg",
            "File:Cat - Flickr - davispuh (4).jpg",
            "File:British Shorthair black-silver tabby mackerel.JPG"
        ],
        # 7: Gero - Persian, Grey and brown
        7: [
            "File:Grey Persian Cat (5339239070).jpg",
            "File:Grey Persian Cat - Chilerito (5339239144).jpg"
        ]
    }

    for cat in cats:
        # Check if cat already has valid images on disk
        existing = cat_ctrl.get_cat_images(cat.id)
        valid_existing = [p for p in existing if os.path.isfile(p)]
        if valid_existing and len(valid_existing) == len(existing):
            print(f"Cat #{cat.id} ({cat.name}) already has {len(valid_existing)} valid images.")
            continue

        wiki_titles = CAT_PHOTOS.get(cat.id, [])
        saved_paths = []
        for title in wiki_titles:
            print(f"Fetching {title} for Cat #{cat.id} ({cat.name})...")
            url = get_wikimedia_url(title)
            if url:
                try:
                    rel_path = download_and_save(url, cat.id)
                    saved_paths.append(rel_path)
                    print(f"  -> Saved {rel_path}")
                except Exception as e:
                    print(f"  -> Download failed: {e}")

        if saved_paths:
            cat_ctrl.set_cat_images(cat.id, saved_paths)
            print(f"Successfully attached {len(saved_paths)} images to Cat #{cat.id} ({cat.name}).")

    print("\nImage seeding complete!")

if __name__ == "__main__":
    seed_images()
