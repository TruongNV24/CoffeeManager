# Fixing CoffeeManager Image Issues

## What was fixed
- Centralized image loading into `Utils/image_handler.py`.
- Added cache keys by size/group so re-rendering cards reuses loaded images.
- Added persistent internal references to prevent Tkinter image garbage collection.
- Added Pillow-first loading path (JPEG/WebP/etc.), with Tk fallback.
- Added graceful placeholder output when files are invalid/missing.

## Developer notes
- Keep relative DB paths (e.g., `uploads/abc.png`) when possible.
- Use `ImageHandler.get_image(path, size, cache_group=...)` from views.
- Keep widget-level reference assignment (`label.image = image`) for safety.
