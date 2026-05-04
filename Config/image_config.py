"""Image handling notes for CoffeeManager.

- Preferred format: PNG for smallest surprises in Tkinter.
- JPEG and other formats are supported when Pillow is installed.
- Product images are copied into ./uploads and referenced by relative path.
"""

SUPPORTED_NATIVE_FORMATS = (".png", ".gif", ".ppm", ".pgm")
SUPPORTED_PIL_FORMATS = (".jpg", ".jpeg", ".bmp", ".tiff", ".webp")

CARD_IMAGE_SIZE = (110, 78)
PREVIEW_IMAGE_SIZE = (120, 90)
