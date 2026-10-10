"""
مدل پارامتریک تلهٔ حشرهٔ دیواری با فیلم چسبی رولی (CadQuery)

دستگاه مختصات: X = عرض (چپ/راست)، Y = ارتفاع (بالا)، Z = عمق (از دیوار به سمت جلو؛ Z=0 روی دیوار).
همهٔ اندازه‌ها میلی‌متر.

اجرا:  python3 trap.py            ← خروجی‌ها در out/
"""
import math
import os
import random

import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# ---------------- پارامترهای اصلی ----------------
P = dict(
    W=340.0,          # عرض بدنه
    H=580.0,          # ارتفاع بدنه
    D=90.0,           # عمق بدنه
    R=36.0,           # شعاع گوشه‌های نمای جلو
    wall=2.5,         # ضخامت دیوارهٔ بدنه (برای قالب تزریق)
    bayW=304.0,       # عرض جای کارتریج
    film_w=260.0,     # عرض فیلم چسبی
    win_w=270.0,      # عرض پنجرهٔ دید سطح چسبی
    win_y0=165.0,     # لبهٔ پایین پنجره
    win_y1=455.0,     # لبهٔ بالای پنجره
    film_z=46.0,      # فاصلهٔ صفحهٔ فیلم از دیوار
    cas_y0=15.0,      # کاست جمع‌کننده: پایین
    cas_y1=148.0,     # کاست جمع‌کننده: بالا
    takeup_y=82.0,    # محور قرقرهٔ جمع‌کننده
    supply_y=497.0,   # محور رول فیلم نو
    core_r=12.5,      # شعاع هستهٔ قرقره (لولهٔ مقوایی ۲۵ میلی‌متری)
    supply_r=24.0,    # شعاع رول نو (حدود ۱۰ متر فیلم ۱۳۰ میکرونی)
    takeup_r=22.0,    # شعاع قرقرهٔ جمع‌کننده در حالت تقریباً پر
    led_y=506.0,      # مرکز نوار LED جلو
)


def rbox(w, h, d, r, x=0.0, y=0.0, z=0.0):
    """جعبه با گوشه‌های گرد در نمای جلو (XY) و اکسترود در جهت Z از z تا z+d."""
    return (
        cq.Workplane("XY", origin=(0, 0, z))
        .center(x, y)
        .rect(w, h)
        .extrude(d)
        .edges("|Z")
        .fillet(r)
    )


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_x(r, length, y, z, x=0.0):
    """استوانهٔ هم‌محور با X، مرکز در (x, y, z)."""
    return cq.Workplane("YZ", origin=(x - length / 2, y, z)).circle(r).extrude(length)


def housing():
    W, H, D = P["W"], P["H"], P["D"]
    body = rbox(W, H, D, P["R"], y=H / 2)
    try:
        body = body.faces(">Z").edges().fillet(8)
    except Exception:
        pass
    bw = P["bayW"] / 2
    # فضای کارتریج (از پایین باز است)
    body = body.cut(box(-bw, bw, -10, 545, 8, D - 6))
    # دهانهٔ جلو برای صورت کاست
    body = body.cut(box(-bw, bw, -10, P["cas_y1"], D - 8, D + 5))
    # پنجرهٔ سطح چسبی
    ww = P["win_w"]
    win = rbox(ww, P["win_y1"] - P["win_y0"], 30, 12, y=(P["win_y0"] + P["win_y1"]) / 2, z=D - 10)
    body = body.cut(win)
    # شیار نوار LED جلو
    body = body.cut(rbox(290, 30, 12, 14.5, y=P["led_y"], z=D - 6))
    # سوراخ‌های پیچ دیواری (کلیدی)
    for x in (-110, 110):
        body = body.cut(cq.Workplane("XY").center(x, 540).circle(4).extrude(10))
        body = body.cut(cq.Workplane("XY").center(x, 548).circle(8).extrude(3))
    # شیارهای تهویهٔ الکترونیک در کنارهٔ بالا
    for i in range(5):
        body = body.cut(box(W / 2 - 3, W / 2 + 1, 530 - i * 9, 534 - i * 9, 30, 60))
    return body


def guard():
    """محافظ جلوی پنجره: میله‌های عمودی نازک (جلوگیری از تماس دست)"""
    ww = P["win_w"]
    y0, y1 = P["win_y0"], P["win_y1"]
    g = None
    n = 17
    for i in range(n):
        x = -ww / 2 + 8 + i * (ww - 16) / (n - 1)
        bar = box(x - 1.2, x + 1.2, y0 - 2, y1 + 2, P["D"] - 9, P["D"] - 6.5)
        g = bar if g is None else g.union(bar)
    # دو میلهٔ افقی
    for y in (y0 + (y1 - y0) / 3, y0 + 2 * (y1 - y0) / 3):
        g = g.union(box(-ww / 2, ww / 2, y - 1.2, y + 1.2, P["D"] - 10, P["D"] - 8))
    return g


def led_front():
    return rbox(284, 24, 6, 11.5, y=P["led_y"], z=P["D"] - 6.5)


def led_inner():
    """نوار LED داخلی زیر لبهٔ بالای پنجره که سطح چسبی را روشن می‌کند"""
    return box(-125, 125, P["win_y1"] - 12, P["win_y1"] - 4, P["D"] - 30, P["D"] - 14)


def status_led():
    return cq.Workplane("XY", origin=(0, 0, P["D"] - 1)).center(P["W"] / 2 - 36, 545).circle(4.5).extrude(1.5)


def cartridge_shell():
    """کارتریج یکپارچه: کاست دربستهٔ جمع‌کننده + ریل‌ها + محفظهٔ رول نو (یک‌بارمصرف، قابل اتوکلاو/سوزاندن)"""
    bw = P["bayW"] / 2 - 2
    y0, y1 = P["cas_y0"], P["cas_y1"]
    cas = rbox(2 * bw, y1 - y0, P["D"] - 2 - 10, 14, y=(y0 + y1) / 2, z=10)
    try:
        cas = cas.faces(">Z").edges().fillet(5)
    except Exception:
        pass
    # شیار دستگیره
    cas = cas.cut(rbox(150, 9, 4, 4.2, y=y0 + 22, z=P["D"] - 5))
    # شکاف ورود فیلم (با نوار نمدی/برس بسته می‌شود)
    cas = cas.cut(box(-P["film_w"] / 2 - 2, P["film_w"] / 2 + 2, y1 - 6, y1 + 1, P["film_z"] - 3, P["film_z"] + 3))
    # ریل‌های کناری
    rails = box(-bw, -bw + 12, y1, 535, 10, 34).union(box(bw - 12, bw, y1, 535, 10, 34))
    # محفظهٔ رول نو (پشت سر LED، از جلو دیده نمی‌شود)
    sup = box(-bw, bw, 462, 535, 10, 76).cut(cyl_x(P["supply_r"] + 3, 2 * bw - 8, P["supply_y"], P["film_z"] - P["supply_r"] + 2 + 6))
    # شکاف خروج فیلم از محفظهٔ رول نو
    sup = sup.cut(box(-P["film_w"] / 2 - 2, P["film_w"] / 2 + 2, 455, 470, P["film_z"] - 3, P["film_z"] + 3))
    return cas.union(rails).union(sup)


def release_button():
    return cq.Workplane("XY", origin=(0, 0, P["D"] - 2)).center(0, P["cas_y0"] + 50).rect(46, 12).extrude(3).edges("|Z").fillet(5)


def label():
    return box(-62, 62, 88, 128, P["D"] - 2.2, P["D"] - 1.6)


def film():
    fw = P["film_w"] / 2
    return box(-fw, fw, P["cas_y1"] - 4, 468, P["film_z"] - 0.6, P["film_z"])


def supply_roll():
    return cyl_x(P["supply_r"], P["film_w"], P["supply_y"], P["film_z"] - P["supply_r"] + 6)


def takeup_roll():
    return cyl_x(P["takeup_r"], P["film_w"], P["takeup_y"], P["film_z"] - P["takeup_r"] + 4)


def cores():
    L = P["bayW"] - 10
    s = cyl_x(P["core_r"], L, P["supply_y"], P["film_z"] - P["supply_r"] + 6)
    t = cyl_x(P["core_r"], L, P["takeup_y"], P["film_z"] - P["takeup_r"] + 4)
    # غلتک اندازه‌گیر (انکودر) بالای کاست
    e = cyl_x(7, P["film_w"] + 10, P["cas_y1"] + 10, P["film_z"] - 7.6)
    return s.union(t).union(e)


def knob():
    """دستگیرهٔ چرخشی کنار بدنه (نسخهٔ دستی) با جغجغهٔ یک‌طرفه"""
    x0 = P["W"] / 2
    z = P["film_z"] - P["takeup_r"] + 4
    k = cq.Workplane("YZ", origin=(x0, P["takeup_y"], z)).circle(24).extrude(14)
    k = k.faces(">X").edges().fillet(4)
    for i in range(18):
        a = 2 * math.pi * i / 18
        k = k.cut(
            cq.Workplane("YZ", origin=(x0, P["takeup_y"] + 24 * math.cos(a), z + 24 * math.sin(a)))
            .circle(2.4)
            .extrude(14)
        )
    # فلش جهت چرخش
    k = k.cut(cq.Workplane("YZ", origin=(x0 + 13, P["takeup_y"] + 10, z)).rect(3, 14).extrude(2))
    return k


def drive_unit():
    """نسخهٔ برقی: موتور گیربکسی N20 + چرخ‌دنده در دیوارهٔ کناری"""
    x = P["bayW"] / 2 + 8
    z = P["film_z"] - P["takeup_r"] + 4
    m = cq.Workplane("XZ", origin=(x, P["takeup_y"] + 30, z)).rect(12, 10).extrude(-26)
    g = cyl_x(14, 4, P["takeup_y"], z, x=x)
    return m.union(g)


def pcb():
    return box(-120, 60, 540, 572, 12, 14).union(box(-110, -80, 548, 566, 14, 22))


def flies(seed=3, n=11):
    random.seed(seed)
    out = None
    for _ in range(n):
        x = random.uniform(-110, 110)
        y = random.uniform(185, 440)
        a = random.uniform(0, 360)
        body = (
            cq.Workplane("XY", origin=(0, 0, P["film_z"]))
            .ellipse(5.5, 3.2)
            .extrude(2.6)
            .union(cq.Workplane("XY", origin=(5.5, 0, P["film_z"])).circle(2.4).extrude(2.4))
            .rotate((0, 0, 0), (0, 0, 1), a)
            .translate((x, y, 0))
        )
        out = body if out is None else out.union(body)
    return out


COLORS = {
    "housing": (1.0, 1.0, 1.0),
    "guard": (0.80, 0.84, 0.86),
    "led_front": (0.50, 0.47, 0.87),
    "led_inner": (0.50, 0.47, 0.87),
    "status_led": (0.11, 0.62, 0.46),
    "cartridge": (0.37, 0.37, 0.35),
    "release_button": (0.06, 0.43, 0.34),
    "label": (0.98, 0.93, 0.85),
    "film": (0.98, 0.93, 0.85),
    "supply_roll": (0.96, 0.85, 0.62),
    "takeup_roll": (0.96, 0.85, 0.62),
    "cores": (0.73, 0.46, 0.09),
    "knob": (0.06, 0.43, 0.34),
    "drive_unit": (0.55, 0.57, 0.60),
    "pcb": (0.10, 0.45, 0.30),
    "flies": (0.12, 0.16, 0.19),
}


def build():
    parts = {
        "housing": housing(),
        "guard": guard(),
        "led_front": led_front(),
        "led_inner": led_inner(),
        "status_led": status_led(),
        "cartridge": cartridge_shell(),
        "release_button": release_button(),
        "label": label(),
        "film": film(),
        "supply_roll": supply_roll(),
        "takeup_roll": takeup_roll(),
        "cores": cores(),
        "knob": knob(),
        "drive_unit": drive_unit(),
        "pcb": pcb(),
        "flies": flies(),
    }
    return parts


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = build()
    assy = cq.Assembly(name="uv_roll_trap")
    for name, shape in parts.items():
        assy.add(shape, name=name, color=cq.Color(*COLORS[name]))
        cq.exporters.export(shape, os.path.join(OUT, f"{name}.stl"), tolerance=0.2, angularTolerance=0.2)
    assy.save(os.path.join(OUT, "uv_roll_trap.step"))
    assy.save(os.path.join(OUT, "uv_roll_trap.glb"))
    bb = parts["housing"].val().BoundingBox()
    print("housing bbox mm:", round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1))
    print("done ->", OUT)
