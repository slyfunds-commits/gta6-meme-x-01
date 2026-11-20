from math import cos, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE = 1024
INK = (11, 8, 24)
WHITE = (255, 255, 255)
MAGENTA = (255, 40, 190)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def blend(start, end, amount):
    return tuple(round(a + (b - a) * amount) for a, b in zip(start, end))


def draw_background(image):
    draw = ImageDraw.Draw(image)
    stops = [
        (0, (39, 13, 79)),
        (350, (153, 27, 119)),
        (650, (255, 112, 63)),
        (824, (255, 179, 91)),
    ]
    for y in range(825):
        for (start_y, start), (end_y, end) in zip(stops, stops[1:]):
            if start_y <= y <= end_y:
                color = blend(start, end, (y - start_y) / (end_y - start_y))
                break
        draw.line((0, y, SIZE, y), fill=color)
    draw.rectangle((0, 825, SIZE, SIZE), fill=(20, 12, 34))
    draw.ellipse((355, 332, 669, 646), fill=(255, 205, 112))


def bezier(p0, p1, p2, p3, count=24):
    points = []
    for step in range(count + 1):
        t = step / count
        u = 1 - t
        points.append(
            (
                u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
                u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
            )
        )
    return points


def draw_palm(draw, base, crown, lean):
    bx, by = base
    cx, cy = crown
    trunk = [
        (bx - 13, by),
        (cx - 9, cy),
        (cx + 11, cy),
        (bx + 15, by),
    ]
    draw.polygon(trunk, fill=INK)
    for direction in (-1.0, -0.55, 0.0, 0.55, 1.0):
        end = (cx + direction * 145, cy - 68 + abs(direction) * 55)
        control = (cx + direction * 68 + lean, cy - 108)
        curve = bezier((cx, cy), control, (end[0] - direction * 36, end[1] - 3), end, 16)
        draw.line(curve, fill=INK, width=13, joint="curve")
        for index in range(3, len(curve) - 2, 3):
            x, y = curve[index]
            side = -1 if direction >= 0 else 1
            length = 28
            tip = (x + side * length, y + 22)
            draw.polygon(
                [(x, y), (x + side * 4, y + 7), tip, (x + side * (length - 4), y + 22)],
                fill=INK,
            )
    draw.ellipse((cx - 17, cy - 17, cx + 17, cy + 17), fill=INK)


def star_points(cx, cy, outer, inner, count=4):
    points = []
    for index in range(count * 2):
        radius = outer if index % 2 == 0 else inner
        angle = -1.57079632679 + index * 3.14159265359 / count
        points.append((cx + radius * cos(angle), cy + radius * sin(angle)))
    return points


def draw_ghost(draw):
    points = []
    points += bezier((319, 510), (313, 448), (314, 336), (326, 264))
    points += bezier((326, 264), (336, 184), (394, 158), (482, 158))[1:]
    points += bezier((482, 158), (578, 158), (658, 206), (670, 295))[1:]
    points += bezier((670, 295), (683, 365), (680, 454), (681, 510))[1:]
    points += bezier((681, 510), (650, 491), (635, 490), (612, 513))[1:]
    points += bezier((612, 513), (586, 539), (566, 535), (541, 511))[1:]
    points += bezier((541, 511), (515, 488), (495, 488), (469, 514))[1:]
    points += bezier((469, 514), (444, 539), (423, 536), (397, 511))[1:]
    points += bezier((397, 511), (370, 486), (348, 488), (319, 510))[1:]
    draw.polygon(points, fill=WHITE)
    draw.line(points + [points[0]], fill=INK, width=13, joint="curve")

    for center in ((423, 333), (558, 333)):
        draw.polygon(star_points(*center, 24, 5), fill=INK)

    # A rounded hand reaches around the coin so the held token remains distinct.
    draw.ellipse((653, 409, 738, 494), fill=WHITE, outline=INK, width=12)
    draw.ellipse((701, 392, 812, 503), fill=MAGENTA, outline=INK, width=12)
    draw.polygon(star_points(756, 447, 31, 13), fill=WHITE)


def fit_font(text, max_width, max_height, start_size):
    for size in range(start_size, 10, -1):
        font = ImageFont.truetype(FONT_PATH, size)
        box = font.getbbox(text, stroke_width=2)
        if box[2] - box[0] <= max_width and box[3] - box[1] <= max_height:
            return font
    raise ValueError(f"Text does not fit: {text}")


def draw_centered_text(draw, text, y, size, max_width, color, outline, stroke):
    font = fit_font(text, max_width, 150, size)
    box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    width = box[2] - box[0]
    x = (SIZE - width) / 2 - box[0]
    draw.text((x, y - box[1]), text, font=font, fill=color, stroke_width=stroke, stroke_fill=outline)


def draw_meme(image):
    draw = ImageDraw.Draw(image)
    draw_palm(draw, (91, 825), (142, 324), -4)
    draw_palm(draw, (946, 825), (875, 324), 4)
    draw_ghost(draw)

    draw_centered_text(draw, "GTA VI", 20, 132, 900, WHITE, INK, 8)
    draw_centered_text(draw, "LOADING... 99%", 550, 57, 880, WHITE, INK, 5)

    bar = (145, 616, 879, 677)
    draw.rounded_rectangle(bar, radius=30, fill=INK)
    draw.rounded_rectangle((155, 626, 869, 667), radius=20, fill=(255, 231, 245))
    draw.rounded_rectangle((155, 626, 155 + round(714 * 0.99), 667), radius=20, fill=MAGENTA)

    draw_centered_text(draw, "ESTIMATED TIME: 13 YEARS", 707, 49, 950, WHITE, INK, 5)
    draw_centered_text(draw, "make.fun", 864, 94, 850, MAGENTA, WHITE, 8)


def main():
    image = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    draw_background(image)
    draw_meme(image)
    image.save(Path(__file__).with_name("meme.png"), format="PNG", optimize=True)


if __name__ == "__main__":
    main()
