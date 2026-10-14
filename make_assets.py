#!/usr/bin/env python3
"""Generate site brand assets for Aether Labs:
   - favicon.png      (256x256 transparent logo mark)
   - favicon-32.png   (32x32)
   - og-image.png     (1200x630 social card)
Palette: bg #0a0e1a, card #121828, border #2a3654, text #e6edf7,
         accent #4f8dff, accent2 #7c5cff, muted #8b9ab3
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SITE = r"C:\Users\sydne\Desktop\Hermes-Aether\site"
os.makedirs(SITE, exist_ok=True)

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_DJ = r"C:\Windows\Fonts\DejaVuSans-Bold.ttf"

BG = (10, 14, 26, 255)
ACCENT = (79, 141, 255, 255)
ACCENT2 = (124, 92, 255, 255)
MUTED = (139, 154, 179, 255)
TEXT = (230, 237, 247, 255)
SUBBLUE = (124, 157, 255, 255)


# ---------------------------------------------------------------- favicon ---
def make_favicon(size=256, ss=4):
    """Draw the badge at 4x supersample, downscale to `size`."""
    S = size * ss
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # diagonal gradient badge #4f8dff -> #7c5cff
    grad = Image.new("RGBA", (S, S))
    gd = ImageDraw.Draw(grad)
    for y in range(S):
        t = y / (S - 1)
        r = int(79 + (124 - 79) * t)
        g = int(141 + (92 - 141) * t)
        b = int(255 + (255 - 255) * t)
        gd.line([(0, y), (S, y)], fill=(r, g, b, 255))
    # blend a left-to-right tilt so it reads diagonal
    grad2 = Image.new("RGBA", (S, S))
    g2 = ImageDraw.Draw(grad2)
    for x in range(S):
        t = x / (S - 1)
        a = 0.5 + 0.5 * t  # 0.5 -> 1.0 horizontal weight
        g2.line([(x, 0), (x, S)], fill=(255, 255, 255, int(255 * a)))
    grad = Image.composite(grad, grad.rotate(0), Image.new("L", (S, S), 255))
    # simpler: just use vertical gradient; diagonal tilt is subtle at 256px
    mask = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(mask)
    m = int(S * 0.02)  # outer transparent margin
    md.rounded_rectangle([m, m, S - m, S - m], radius=int(S * 0.22), fill=255)
    img.paste(grad, (0, 0), mask)

    # subtle dark inner border
    d = ImageDraw.Draw(img)
    inset = m + int(S * 0.012)
    d.rounded_rectangle(
        [inset, inset, S - inset, S - inset],
        radius=int(S * 0.20),
        outline=(10, 14, 26, 90),
        width=max(2, int(S * 0.014)),
    )

    # ---- white open-book glyph (two pages meeting at a center spine) ----
    # Kept deliberately simple: at 16-32px the fine detail (page lines, dark
    # inner border) blurs into noise, so the 32px must read as a clean
    # silhouette. Fine strokes are skipped for the small size.
    glyph = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glyph)
    cx = S / 2
    yt = S * 0.285           # top of book
    yb = S * 0.660           # bottom center (spine dip)
    w = S * 0.205            # half-width of pages

    def page(sign):  # sign=-1 left page, +1 right page
        outer = cx + sign * w
        dip = S * 0.028      # bottom outer corner lifts slightly
        pts = [
            (cx + sign * S * 0.008, yt + S * 0.030),   # top inner (spine)
            (outer, yt),                                # top outer
            (outer, yb - dip),                          # bottom outer
            (cx + sign * S * 0.008, yb),                # bottom inner
        ]
        gdraw.polygon(pts, fill=(255, 255, 255, 255))

    page(-1)
    page(+1)
    img = Image.alpha_composite(img, glyph)

    return img.resize((size, size), Image.LANCZOS)


def save(img, name):
    path = os.path.join(SITE, name)
    img.save(path, "PNG", optimize=True)
    return path


fav256 = make_favicon(256)
fav32 = make_favicon(32)
save(fav256, "favicon.png")
save(fav32, "favicon-32.png")


# --------------------------------------------------------------- og-image ---
def draw_tracked(draw, xy, text, font, fill, tracking):
    """Letterspaced text, drawn char by char. Returns end x."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def make_og():
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(img)

    # radial glow in brand blue, upper-left area
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gcx, gcy = int(W * 0.16), int(H * 0.10)
    gdraw.ellipse([gcx - 620, gcy - 620, gcx + 620, gcy + 620],
                  fill=(79, 141, 255, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    img = Image.alpha_composite(img, glow)
    # faint second glow lower-right in accent2
    glow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g2 = ImageDraw.Draw(glow2)
    g2.ellipse([W - 500, H - 420, W + 200, H + 280],
               fill=(124, 92, 255, 46))
    glow2 = glow2.filter(ImageFilter.GaussianBlur(160))
    img = Image.alpha_composite(img, glow2)
    d = ImageDraw.Draw(img)

    # top accent strip (thick enough to survive feed downscaling)
    d.rectangle([0, 0, W, 10], fill=ACCENT)
    d.rectangle([0, 0, int(W * 0.28), 10], fill=ACCENT2)

    ML = 80  # left margin

    # eyebrow
    f_eyebrow = ImageFont.truetype(FONT_BOLD, 26)
    draw_tracked(d, (ML, 96), "AETHER LABS", f_eyebrow, MUTED, 10)
    # small accent tick before headline
    d.rounded_rectangle([ML, 152, ML + 64, 158], radius=3, fill=ACCENT)

    # headline, two lines
    f_head = ImageFont.truetype(FONT_BOLD, 78)
    d.text((ML, 196), "Autonomous Ebook", font=f_head, fill=TEXT)
    d.text((ML, 296), "Production", font=f_head, fill=TEXT)

    # subtext (bright soft-white for contrast on dark; colon for flow)
    f_sub = ImageFont.truetype(FONT_REG, 34)
    d.text((ML, 420), "One command: topic to publication-ready ebook.",
           font=f_sub, fill=(214, 224, 240, 255))

    # stat chips (larger font for mobile legibility)
    f_chip = ImageFont.truetype(FONT_BOLD, 32)
    chips = ["40 books", "15 genres", "$0 cloud cost"]
    x = ML
    cy = 500
    for label in chips:
        tw = d.textlength(label, font=f_chip)
        pad_x, ch_h = 30, 62
        cw = int(tw + pad_x * 2)
        d.rounded_rectangle([x, cy, x + cw, cy + ch_h], radius=13,
                            fill=(18, 24, 40, 255),
                            outline=ACCENT, width=2)
        d.text((x + pad_x, cy + (ch_h - 40) // 2), label,
               font=f_chip, fill=TEXT)
        x += cw + 22

    # right-side small logo badge echo (brand consistency, subtle)
    bs = 96
    bx, by = W - ML - bs, 96
    badge = make_favicon(bs).resize((bs, bs), Image.LANCZOS)
    img.paste(badge, (bx, by), badge)

    path = os.path.join(SITE, "og-image.png")
    img.convert("RGB").save(path, "PNG", optimize=True)
    return path


make_og()

# ------------------------------------------------------------ verification --
print("\n=== VERIFICATION (PIL reopen + bytes) ===")
for name in ("favicon.png", "favicon-32.png", "og-image.png"):
    p = os.path.join(SITE, name)
    with Image.open(p) as im:
        im.load()
        dims = im.size
        mode = im.mode
    b = os.path.getsize(p)
    print(f"{name:16s} {dims[0]}x{dims[1]}  mode={mode}  bytes={b}")
print("ALL ASSETS WRITTEN AND VERIFIED")
