import os
import tkinter as tk
from typing import Dict, Optional, Tuple

try:
    from PIL import Image, ImageOps, ImageTk
except ImportError:  # optional dependency at runtime
    Image = None
    ImageOps = None
    ImageTk = None


class ImageHandler:
    """Centralized image loading/caching for Tkinter widgets."""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self._cache: Dict[str, tk.PhotoImage] = {}
        self._references: Dict[str, tk.PhotoImage] = {}

    def get_image(self, image_path: Optional[str], size: Tuple[int, int], cache_group: str = "card") -> tk.PhotoImage:
        width, height = size
        resolved = self.resolve_path(image_path)
        cache_key = f"{cache_group}|{resolved or image_path}|{width}x{height}"

        if cache_key in self._cache:
            image = self._cache[cache_key]
            self._references[cache_key] = image
            return image

        image = self._load_image(resolved, width, height)
        self._cache[cache_key] = image
        self._references[cache_key] = image
        return image

    def resolve_path(self, image_path: Optional[str]) -> Optional[str]:
        if not image_path:
            return None

        raw_path = image_path.strip()
        if not raw_path:
            return None

        candidates = {
            os.path.normpath(raw_path),
            os.path.normpath(raw_path.replace("\\", os.sep)),
            os.path.normpath(raw_path.replace("/", os.sep)),
        }

        for path in candidates:
            if os.path.isabs(path) and os.path.exists(path):
                return path

            cwd_candidate = os.path.normpath(os.path.join(os.getcwd(), path))
            if os.path.exists(cwd_candidate):
                return cwd_candidate

            project_candidate = os.path.normpath(os.path.join(self.project_root, path))
            if os.path.exists(project_candidate):
                return project_candidate

        return None

    def clear_group(self, cache_group: str):
        prefix = f"{cache_group}|"
        for key in list(self._cache.keys()):
            if key.startswith(prefix):
                self._cache.pop(key, None)
                self._references.pop(key, None)

    def _load_image(self, resolved_path: Optional[str], width: int, height: int) -> tk.PhotoImage:
        if resolved_path and Image and ImageTk and ImageOps:
            try:
                with Image.open(resolved_path) as raw:
                    prepared = ImageOps.contain(raw.convert("RGBA"), (width, height))
                    return ImageTk.PhotoImage(prepared)
            except Exception:
                pass

        if resolved_path:
            try:
                native = tk.PhotoImage(file=resolved_path)
                return self._fit_native(native, width, height)
            except tk.TclError:
                pass

        return self._placeholder(width, height)

    @staticmethod
    def _fit_native(image: tk.PhotoImage, width: int, height: int) -> tk.PhotoImage:
        x_ratio = max(1, (image.width() + width - 1) // width)
        y_ratio = max(1, (image.height() + height - 1) // height)
        return image.subsample(x_ratio, y_ratio)

    @staticmethod
    def _placeholder(width: int, height: int) -> tk.PhotoImage:
        image = tk.PhotoImage(width=width, height=height)
        image.put("#d9d9d9", to=(0, 0, width, height))
        return image
