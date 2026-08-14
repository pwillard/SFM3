from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PNG = ASSETS / "SFM3_icon.png"
ICO = ASSETS / "SFM3.ico"

SIZES = [16, 24, 32, 48, 64, 128, 256]
CANVAS = 256


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def rounded_rectangle_gradient(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    height = y1 - y0
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(height, 1)
        r = int(20 + 10 * t)
        g = int(76 + 36 * t)
        b = int(116 + 40 * t)
        draw.line([(x0, y), (x1, y)], fill=(r, g, b, 255))


def make_base_icon() -> Image.Image:
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Main rounded tile mask and gradient.
    tile = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    tile_draw = ImageDraw.Draw(tile)
    mask = Image.new("L", (CANVAS, CANVAS), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((12, 12, 244, 244), radius=44, fill=255)
    rounded_rectangle_gradient(tile_draw, (12, 12, 244, 244))
    img.alpha_composite(Image.composite(tile, Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0)), mask))

    # Border/highlight.
    draw.rounded_rectangle((12, 12, 244, 244), radius=44, outline=(140, 210, 235, 255), width=5)
    draw.rounded_rectangle((20, 20, 236, 236), radius=36, outline=(255, 255, 255, 70), width=2)

    # Stylized rails converging upward.
    rail_shadow = (7, 32, 50, 180)
    rail = (232, 245, 250, 255)
    draw.line([(78, 204), (105, 78)], fill=rail_shadow, width=16)
    draw.line([(178, 204), (151, 78)], fill=rail_shadow, width=16)
    draw.line([(78, 204), (105, 78)], fill=rail, width=10)
    draw.line([(178, 204), (151, 78)], fill=rail, width=10)

    # Railroad ties.
    for y, w in [(190, 112), (166, 90), (142, 70), (118, 54), (96, 40)]:
        cx = 128
        draw.rounded_rectangle((cx - w // 2, y - 4, cx + w // 2, y + 4), radius=3, fill=(245, 184, 74, 255))
        draw.line([(cx - w // 2 + 5, y + 4), (cx + w // 2 - 5, y + 4)], fill=(116, 72, 22, 120), width=1)

    # Simple shape-file document badge.
    doc = [(62, 46), (151, 46), (184, 79), (184, 139), (62, 139)]
    draw.rounded_rectangle((62, 46, 184, 139), radius=10, fill=(239, 246, 248, 255), outline=(16, 60, 90, 220), width=3)
    draw.polygon([(151, 46), (184, 79), (151, 79)], fill=(188, 214, 224, 255), outline=(16, 60, 90, 220))
    draw.line([(76, 91), (168, 91)], fill=(36, 93, 124, 160), width=5)
    draw.line([(76, 111), (154, 111)], fill=(36, 93, 124, 130), width=5)

    # OR/SFM mark.
    draw.text((74, 50), "OR", font=font(35, True), fill=(20, 84, 122, 255))
    draw.text((72, 139), "SFM3", font=font(43, True), fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(6, 42, 66, 230))

    return img


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    icon = make_base_icon()
    icon.save(PNG)
    icon.save(ICO, sizes=[(size, size) for size in SIZES])
    print(PNG)
    print(ICO)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
