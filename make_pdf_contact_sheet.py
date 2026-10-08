from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
render_dir = root / "work" / "pdf-render"
modules = ["tr-01-guide", "rp-4-guide", "st-5-guide", "as-12-guide"]
thumb_w = 180
label_h = 26
gap = 12
rows = []

for module in modules:
    images = []
    for page in range(1, 7):
        image = Image.open(render_dir / f"{module}-{page}.png").convert("RGB")
        ratio = thumb_w / image.width
        image = image.resize((thumb_w, int(image.height * ratio)), Image.Resampling.LANCZOS)
        images.append(image)
    rows.append(images)

thumb_h = rows[0][0].height
sheet = Image.new("RGB", (gap + 6 * (thumb_w + gap), gap + 4 * (thumb_h + label_h + gap)), "#202321")
draw = ImageDraw.Draw(sheet)

for row_index, images in enumerate(rows):
    y = gap + row_index * (thumb_h + label_h + gap)
    draw.text((gap, y), modules[row_index], fill="#d9ff66")
    y += label_h
    for column_index, image in enumerate(images):
        x = gap + column_index * (thumb_w + gap)
        sheet.paste(image, (x, y))

sheet.save(render_dir / "contact-sheet.png", optimize=True)
