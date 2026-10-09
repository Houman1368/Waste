"""Persian captions + Rayateb logo overlays for the vertical clip (PIL, RTL via libraqm).

Logo: video/assets/logo_rayateb.jpg - its sun ring is cut out and spun in the header corner.
Font: drop BNazanin.ttf (and optionally BNazaninBold.ttf) into video/assets/ to use B Nazanin;
otherwise Vazirmatn is used. Re-run with: python video.py --compose-only
"""
import glob
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ASSETS = os.path.join(os.path.dirname(__file__), "..", "video", "assets")
def _pick(*names):
    for n in names:
        p = os.path.join(ASSETS, n)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(names)


F_REG = _pick("BNazanin.ttf", "Vazirmatn-Regular.ttf")
F_BOLD = _pick("BNazaninBold.ttf", "BNazanin.ttf", "Vazirmatn-ExtraBold.ttf")
LOGO = os.path.join(ASSETS, "logo_rayateb.jpg")
RING_C, RING_R = (783, 850), (440, 730)   # sun-ring centre / annulus radii in the logo file (px)
SPIN_SEC = 8.0                            # one revolution of the ring

ACCENT = (34, 101, 160)      # Rayateb blue
RED = (208, 35, 42)          # Rayateb red
INK = (25, 27, 35)
MUTED = (85, 90, 105)
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
COMPANY = "رایاطب"
PROJECT = "پایه UV-C چهاربازو ۳۰ وات"
INTRO, OUTRO = 60, 84


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


_LOGO_CACHE = {}


def _logo_parts(h):
    """(static layer, ring layer, centre) scaled to height h; ring pixels removed from static."""
    if h in _LOGO_CACHE:
        return _LOGO_CACHE[h]
    import numpy as np
    src = Image.open(LOGO).convert("RGB")
    a = np.asarray(src).astype(np.int16)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    r = np.hypot(xx - RING_C[0], yy - RING_C[1])
    red = (a[..., 0] > 140) & (a[..., 1] < 110)
    from PIL import ImageFilter as _IF
    text = ((a[..., 0] < 70) & (a[..., 2] > 110)) | red          # dark-blue "RAYA" + red text
    near_text = np.asarray(Image.fromarray((text * 255).astype("uint8")).filter(_IF.MaxFilter(13))) > 0
    ring = (r > RING_R[0]) & (r < RING_R[1]) & (a.min(2) < 245) & ~near_text
    static = a.copy(); static[ring] = 255
    ringimg = np.full_like(a, 255); ringimg[ring] = a[ring]
    nonw = np.nonzero(a.min(2) < 235)
    box = (nonw[1].min() - 10, nonw[0].min() - 10, nonw[1].max() + 10, nonw[0].max() + 10)
    k = h / (box[3] - box[1])
    size = (int((box[2] - box[0]) * k), h)
    st = Image.fromarray(static.astype("uint8")).crop(box).resize(size, Image.LANCZOS)
    rg = Image.fromarray(ringimg.astype("uint8")).crop(box).resize(size, Image.LANCZOS)
    c = ((RING_C[0] - box[0]) * k, (RING_C[1] - box[1]) * k)
    _LOGO_CACHE[h] = (st, rg, c)
    return _LOGO_CACHE[h]


def logo_image(h, t=0.0):
    """Logo at height h with the sun ring rotated for time t (s); opaque on white."""
    from PIL import ImageChops
    st, rg, c = _logo_parts(h)
    rot = rg.rotate(-360.0 * t / SPIN_SEC, resample=Image.BICUBIC, center=c, fillcolor=(255, 255, 255))
    return ImageChops.multiply(st, rot).convert("RGBA")


def header(img, W, t):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, W, 210), fill=(255, 255, 255, 255))
    d.rectangle((0, 206, W, 212), fill=RED + (255,))
    lg = logo_image(170, t)
    img.alpha_composite(lg, (W - 30 - lg.width, 20))
    x = W - 55 - lg.width
    rtl(d, (x, 50), PROJECT, font(F_BOLD, 40), INK)
    rtl(d, (x, 112), "مدل سه‌بعدی مونتاژ و حرکت بازوها", font(F_REG, 28), MUTED)


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


def title_card(base, W, H, lines, alpha=1.0, t=0.0):
    img = base.copy()
    veil = Image.new("RGBA", img.size, (255, 255, 255, int(255 * alpha)))
    img.alpha_composite(veil)
    d = ImageDraw.Draw(img, "RGBA")
    lg = logo_image(420, t)
    if alpha < 1:
        lg.putalpha(int(255 * alpha))
    img.alpha_composite(lg, ((W - lg.width) // 2, H // 2 - 560))
    y = H // 2 - 60
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
        save(title_card(first, W, H, intro, 1.0 if i < INTRO - 12 else (INTRO - i) / 12, t=i / 24))
    for i, (fp, cap) in enumerate(zip(files, captions)):
        img = Image.open(fp).convert("RGBA")
        header(img, W, (INTRO + i) / 24)
        footer(img, W, H, cap, (i + 1) / n)
        save(img)
    last = Image.open(files[-1]).convert("RGBA")
    outro = [("شرکت دانش‌بنیان رایا طب هگمتانه نوین", font(F_BOLD, 46), RED),
             (PROJECT, font(F_BOLD, 42), INK),
             ("ارتفاع محور ۱۱۵۰ · ارتفاع کل ۲۰۶۰ · دهانه ۲۰۲۰ میلی‌متر · وزن حدود ۳۸ کیلوگرم", font(F_REG, 32), MUTED)]
    for i in range(OUTRO):
        save(title_card(last, W, H, outro, min(1.0, (i + 1) / 12), t=(INTRO + n + i) / 24))
