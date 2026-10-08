from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

root = Path(__file__).resolve().parents[1]
source = root / "public" / "modules" / "tr-01" / "cover.png"
image = Image.open(source).convert("RGB")
width, height = image.size
half_w, half_h = width // 2, height // 2

quadrants = {
    "tr-01": (0, 0, half_w, half_h),
    "rp-4": (half_w, 0, width, half_h),
    "st-5": (0, half_h, half_w, height),
    "as-12": (half_w, half_h, width, height),
}

for module_id, bounds in quadrants.items():
    crop = image.crop(bounds)
    background = crop.resize((960, 960), Image.Resampling.LANCZOS)
    background = background.crop((0, 180, 960, 780)).filter(ImageFilter.GaussianBlur(20))
    background = ImageEnhance.Brightness(background).enhance(0.62)
    foreground = crop.copy()
    foreground.thumbnail((590, 560), Image.Resampling.LANCZOS)
    x = (960 - foreground.width) // 2
    y = (600 - foreground.height) // 2
    background.paste(foreground, (x, y))
    output = root / "public" / "modules" / module_id / "cover.png"
    background.save(output, "PNG", optimize=True, compress_level=9)
