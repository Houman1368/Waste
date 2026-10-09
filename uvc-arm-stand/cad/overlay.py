"""Persian captions + Rayateb logo overlays for the vertical clip (PIL, RTL via libraqm).

Put the real company logo at video/assets/logo.png (transparent PNG) and re-run video.py;
without it a plain text wordmark is drawn instead.
"""
import glob
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ASSETS = os.path.join(os.path.dirname(__file__), "..", "video", "assets")
F_REG = os.path.join(ASSETS, "Vazirmatn-Regular.ttf")
F_BOLD = os.path.join(ASSETS, "Vazirmatn-ExtraBold.ttf")
LOGO = os.path.join(ASSETS, "logo.png")

ACCENT = (92, 60, 190)       # UV violet
INK = (25, 27, 35)
MUTED = (85, 90, 105)
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
COMPANY = "رایاطب"
PROJECT = "پایه UV-C چهاربازو ۳۰ وات"
INTRO, OUTRO = 48, 72


def font(path, size):
    return ImageFont.truetype(path, size)


def rtl(d, xy, text, f, fill, anchor="ra"):
    d.text(xy, text, font=f, fill=fill, anchor=anchor, direction="rtl", language="fa")


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f, direction="rtl", language="fa") <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def logo_image(h):
    if os.path.exists(LOGO):
        im = Image.open(LOGO).convert("RGBA")
        return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    # fallback wordmark (replace with the real logo file)
    f = font(F_BOLD, int(h * 0.62))
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = int(tmp.textlength(COMPANY, font=f, direction="rtl", language="fa"))
    im = Image.new("RGBA", (tw + int(h * 0.7), h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, h - 1), radius=h // 4, fill=ACCENT + (255,))
    rtl(d, (im.width - h * 0.35, h * 0.47), COMPANY, f, (255, 255, 255), anchor="rm")
    return im


def header(img, W):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, W, 210), fill=(255, 255, 255, 225))
    d.rectangle((0, 206, W, 212), fill=ACCENT + (255,))
    lg = logo_image(110)
    img.alpha_composite(lg, (W - 50 - lg.width, 50))
    x = W - 80 - lg.width
    rtl(d, (x, 52), PROJECT, font(F_BOLD, 44), INK)
    rtl(d, (x, 118), "مدل سه‌بعدی مونتاژ و حرکت بازوها", font(F_REG, 30), MUTED)


def footer(img, W, H, cap, progress):
    d = ImageDraw.Draw(img, "RGBA")
    top = H - 400
    # card shadow + card
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, top + 8, W - 40, H - 60 + 8), 36, fill=(0, 0, 0, 60))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle((40, top, W - 40, H - 60), 36, fill=(255, 255, 255, 240))
    # step badge
    cx, cy, r = W - 120, top + 95, 52
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ACCENT + (255,))
    d.text((cx, cy + 2), str(cap["step"]).translate(FA_DIGITS), font=font(F_BOLD, 50), fill="white", anchor="mm")
    fb, fr = font(F_BOLD, 44), font(F_REG, 32)
    y = top + 50
    for line in wrap(d, cap["title"], fb, W - 300)[:2]:
        rtl(d, (W - 200, y), line, fb, INK)
        y += 64
    y = max(y + 18, top + 175)
    for line in wrap(d, cap["sub"], fr, W - 180)[:3]:
        rtl(d, (W - 90, y), line, fr, MUTED)
        y += 50
    # progress bar
    by = H - 110
    d.rounded_rectangle((90, by, W - 90, by + 10), 5, fill=(220, 222, 230, 255))
    x0 = W - 90 - int((W - 180) * progress)
    d.rounded_rectangle((x0, by, W - 90, by + 10), 5, fill=ACCENT + (255,))
    d.text((W // 2, H - 30), "طراحی و مدل‌سازی: " + COMPANY,
           font=font(F_REG, 24), fill=MUTED, anchor="mm", direction="rtl", language="fa")


def title_card(base, W, H, lines, alpha=1.0):
    img = base.copy()
    veil = Image.new("RGBA", img.size, (255, 255, 255, int(215 * alpha)))
    img.alpha_composite(veil)
    d = ImageDraw.Draw(img, "RGBA")
    lg = logo_image(170)
    img.alpha_composite(lg, ((W - lg.width) // 2, H // 2 - 330))
    y = H // 2 - 100
    for txt, f, col in lines:
        for ln in wrap(d, txt, f, W - 140):
            d.text((W // 2, y), ln, font=f, fill=col, anchor="ma", direction="rtl", language="fa")
            y += int(f.size * 1.55)
    return img


def compose_all(frames_dir, captions, W, H):
    files = sorted(glob.glob(os.path.join(frames_dir, "f*.png")))
    for f in glob.glob(os.path.join(frames_dir, "o*.png")):
        os.remove(f)
    n = len(files)
    out = 0

    def save(im):
        nonlocal out
        im.convert("RGB").save(os.path.join(frames_dir, f"o{out:05d}.png"))
        out += 1

    first = Image.open(files[0]).convert("RGBA")
    intro = [(PROJECT, font(F_BOLD, 62), INK),
             ("طراحی فلزی، مونتاژ مرحله‌به‌مرحله و حرکت بازوها", font(F_REG, 36), MUTED),
             ("۴ بازوی مستقل · قفل هر ۱۵ درجه · ۰ تا ۱۸۰ درجه", font(F_REG, 34), ACCENT)]
    for i in range(INTRO):
        save(title_card(first, W, H, intro, 1.0 if i < INTRO - 12 else (INTRO - i) / 12))
    for i, (fp, cap) in enumerate(zip(files, captions)):
        img = Image.open(fp).convert("RGBA")
        header(img, W)
        footer(img, W, H, cap, (i + 1) / n)
        save(img)
    last = Image.open(files[-1]).convert("RGBA")
    outro = [(COMPANY, font(F_BOLD, 66), ACCENT),
             (PROJECT, font(F_BOLD, 42), INK),
             ("ارتفاع محور ۱۱۵۰ · ارتفاع کل ۲۰۶۰ · دهانه ۲۰۱۰ میلی‌متر · وزن حدود ۳۸ کیلوگرم", font(F_REG, 32), MUTED)]
    for i in range(OUTRO):
        save(title_card(last, W, H, outro, min(1.0, (i + 1) / 12)))
