# Image Quick Reference

- Card image: `(110, 78)`
- Preview image: `(120, 90)`
- Main API: `image_handler.get_image(image_path, size, cache_group)`
- Clear stale group cache: `image_handler.clear_group("cards")`

If JPEG doesn't render, ensure Pillow is installed from `requirements.txt`.
