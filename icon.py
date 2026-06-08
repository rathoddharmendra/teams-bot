from PIL import Image, ImageDraw


def generate_icon(active: bool) -> Image.Image:
    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    color = (76, 175, 80, 255) if active else (158, 158, 158, 255)
    margin = 4
    draw.ellipse(
        (margin, margin, size - margin, size - margin),
        fill=color,
    )
    return image
