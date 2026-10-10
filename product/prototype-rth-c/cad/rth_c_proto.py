"""
RTH-C — نمونهٔ اولیه برای پرینت سه‌بعدی (نسخهٔ ۰.۱)

طراحی بر اساس دو قطعهٔ خریدنی که در ایران پیدا می‌شوند:
  ۱) لامپ حشره‌کش مهتابی T8 BL ۱۵ وات، پایهٔ G13 (طول با پین‌ها ≈ ۴۵۱.۶ میلی‌متر، قطر ۲۶)
  ۲) رول فیلم/کاغذ چسبی به عرض FILM_W، پیچیده روی لولهٔ برق PVC ۲۰ میلی‌متری

هر قطعهٔ پرینتی در بستر ۲۵۰ × ۲۵۰ میلی‌متر جا می‌شود (Bambu / Prusa / Ender 3 ۲۲۰ برای بیشتر قطعات).
صفحهٔ پشت از ورق ۵ میلی‌متری (PVC فوم، پلکسی یا MDF) بریده می‌شود — فایل DXF.

مختصات: X عرض (مرکز = ۰)، Y ارتفاع از پایین، Z از دیوار به جلو. واحد: میلی‌متر.
اجرا: python3 rth_c_proto.py  ← stl/  step/  dxf/  و manifest برای رندر
"""
import json
import math
import os

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))

# ---------------- انتخاب لامپ (هر سه در بازار ایران رایج‌اند) ----------------
LAMPS = {
    # طول شیشه، طول کل با پین، قطر
    "T8_15W": dict(glass=437.4, total=451.6, dia=26.0, base="G13"),
    "T8_18W": dict(glass=589.8, total=604.0, dia=26.0, base="G13"),
    "T5_8W": dict(glass=288.3, total=302.5, dia=16.0, base="G5"),
}
LAMP = LAMPS[os.environ.get("RTH_LAMP", "T8_15W")]

# ---------------- پارامترها ----------------
SOCKET = 18.0  # فاصلهٔ سطح نصب سرپیچ G13 تا انتهای لامپ (سرپیچ‌های چرخشی معمولی ۱۵ تا ۲۰)
FILM_W = float(os.environ.get("RTH_FILM_W", 400))  # عرض رول چسبی
CORE_OD = 20.0  # لولهٔ برق PVC ۲۰
CORE_ID = 16.4  # قطر داخلی لوله (بسته به برند ۱۶ تا ۱۷؛ درپوش‌ها کمی لقی دارند)
SUPPLY_MAX = 60.0  # بیشترین قطر رول نو (حدود ۱۰ تا ۱۲ متر فیلم ۱۳۰ میکرونی)
TAKEUP_MAX = 70.0  # بیشترین قطر قرقرهٔ جمع‌کننده

INNER = LAMP["total"] + 2 * SOCKET  # فاصلهٔ دو سطح نصب سرپیچ
XS = INNER / 2  # سطح داخلی پدهای سرپیچ
WALL = 6.0  # ضخامت دیوارهٔ کناری
XW = XS + 26  # سطح داخلی دیوارهٔ کناری
XO = XW + WALL  # سطح بیرونی بدنه
W = 2 * XO
H = 440.0
D = 100.0
BP = 5.0  # ضخامت صفحهٔ پشت

LAMP_Y, LAMP_Z = 392.0, 81.0  # فاصله با رول نو پر: ≥ ۱.۵ میلی‌متر
SUP_Y, SUP_Z = 404.0, 37.0
GUIDE_Y, GUIDE_Z = 362.0, 34.0
FILM_Z = 38.0
FILM_Y0, FILM_Y1 = 120.0, 356.0
TAK_Y, TAK_Z = 62.0, 52.0
CAS = dict(x=XS - 2, y0=2.0, y1=122.0, z0=8.0, z1=97.0, t=3.0)
WIN_X = FILM_W / 2 + 12  # نیم‌عرض پنل تیغه‌ای
SPLIT_Y = 200.0  # محل تقسیم دیوارهٔ کناری به بالا/پایین
PANEL_Y0, PANEL_Y1 = FILM_Y0 + 14, 352.0
PANEL_HOLES_Y = (PANEL_Y0 + 14, (PANEL_Y0 + PANEL_Y1) / 2, PANEL_Y1 - 14)

SUP_HALF = XS - 14  # نیم‌طول لولهٔ رول نو
SUP_STUB = (XS + 12) - (SUP_HALF + 3)  # پایهٔ محور تا وسط نگهدارنده
TAK_HALF = CAS["x"] - 8  # نیم‌طول لولهٔ جمع‌کننده
MAG_X = CAS["x"] - 6  # جای آهنربای ۱۰×۳ (کاست و سقف راهنما روبه‌روی هم)
assert CAS["x"] < 250, "نیمهٔ کاست از بستر ۲۵۰ بزرگ‌تر است"


# ---------------- ابزارها ----------------
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_x(r, x0, x1, y, z):
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(r).extrude(x1 - x0)


def hole_x(r, x0, x1, y, z):
    return cyl_x(r, x0 - 1, x1 + 1, y, z)


def mirror_x(wp):
    return wp.mirror("YZ")


def screw_hole_z(x, y, z0, z1, r=1.7):
    return cq.Workplane("XY", origin=(0, 0, z0 - 1)).center(x, y).circle(r).extrude(z1 - z0 + 2)


# ---------------- دیواره‌های کناری ----------------
def side_upper(right=True):
    """دیوارهٔ کناری بالا: پد سرپیچ لامپ، نگهدارندهٔ رول نو (شیار باز رو به جلو)، سوراخ میلهٔ راهنما، گونهٔ جلو"""
    s = box(XW, XO, SPLIT_Y, H, BP, D)
    # پد سرپیچ G13 با شیار تنظیم ±۵ میلی‌متر
    pad = box(XS, XW, LAMP_Y - 22, LAMP_Y + 22, LAMP_Z - 22, D - 2)
    pad = pad.cut(cq.Workplane("YZ", origin=(XS - 1, LAMP_Y, LAMP_Z)).slot2D(14, 4.4, 0).extrude(30))
    pad = pad.cut(cq.Workplane("YZ", origin=(XS - 1, LAMP_Y - 12, LAMP_Z)).slot2D(14, 4.4, 0).extrude(30))
    s = s.union(pad)
    # نگهدارندهٔ رول نو: استوانه با شیار U رو به جلو برای محور ۸ میلی‌متری
    boss = cyl_x(11, XS + 4, XW, SUP_Y, SUP_Z)
    boss = boss.cut(cyl_x(4.3, XS, XW + 1, SUP_Y, SUP_Z)).cut(box(XS, XW + 1, SUP_Y - 4.3, SUP_Y + 4.3, SUP_Z, SUP_Z + 20))
    s = s.union(boss)
    # میلهٔ راهنمای فیلم (میلهٔ فولادی/آلومینیومی ۸ میلی‌متری از سوراخ دیواره رد می‌شود)
    s = s.union(cyl_x(9, XW - 8, XW, GUIDE_Y, GUIDE_Z)).cut(hole_x(4.15, XW - 8, XO, GUIDE_Y, GUIDE_Z))
    # گونهٔ جلو کنار پنل تیغه‌ای
    s = s.union(box(WIN_X - 10, XW, SPLIT_Y, 352, D - 16, D - 8))
    for y in PANEL_HOLES_Y:
        if y > SPLIT_Y:
            s = s.cut(screw_hole_z(WIN_X - 5, y, D - 16, D - 8, 1.6))
    # زبانه‌های پیچ به صفحهٔ پشت
    for y in (230, 330, 420):
        s = s.union(box(XW - 14, XW, y - 8, y + 8, BP, BP + 6)).cut(screw_hole_z(XW - 7, y, BP, BP + 6, 1.7))
    # محل پیچ اتصال به نیمهٔ پایین (هم‌پوشانی)
    s = s.union(box(XW - 10, XW, SPLIT_Y, SPLIT_Y + 20, BP, D - 10)).cut(hole_x(1.7, XW - 10, XO, SPLIT_Y + 10, 50))
    if right:
        # سوراخ کابل برق
        s = s.cut(hole_x(5.2, XW, XO, 300, 22))
    return s if right else mirror_x(s)


def side_lower(right=True):
    """دیوارهٔ کناری پایین: راهنمای کاست، سوراخ محور دستگیره (سمت راست)، گونهٔ جلو"""
    s = box(XW, XO, 0, SPLIT_Y, BP, D)
    # پد راهنمای کاست (کاست از پایین بالا می‌رود)
    guide = box(XS, XW, CAS["y0"], CAS["y1"] + 4, BP, D - 2)
    guide = guide.cut(box(XS - 1, XW - 8, CAS["y0"] - 1, CAS["y1"] - 4, CAS["z0"] + 6, CAS["z1"] - 6))
    s = s.union(guide)
    # سقف کاست + جای آهنربای ۱۰×۳
    s = s.union(box(XS - 10, XW, CAS["y1"], CAS["y1"] + 6, CAS["z0"], CAS["z1"]))
    s = s.cut(cq.Workplane("XY").box(10.4, 3.4, 10.4).translate((MAG_X, CAS["y1"] + 1.6, (CAS["z0"] + CAS["z1"]) / 2)))
    # گونهٔ جلو
    s = s.union(box(WIN_X - 10, XW, CAS["y1"] + 6, SPLIT_Y, D - 16, D - 8))
    for y in PANEL_HOLES_Y:
        if y < SPLIT_Y:
            s = s.cut(screw_hole_z(WIN_X - 5, y, D - 16, D - 8, 1.6))
    for y in (40, 150):
        s = s.union(box(XW - 14, XW, y - 8, y + 8, BP, BP + 6)).cut(screw_hole_z(XW - 7, y, BP, BP + 6, 1.7))
    # جای پیچ اتصال به نیمهٔ بالا
    s = s.cut(hole_x(1.7, XW - 10, XO, SPLIT_Y + 10, 50))
    if right:
        # سوراخ محور دستگیره + گودی جای انگشت
        s = s.cut(hole_x(6.3, XS, XO, TAK_Y, TAK_Z))
        s = s.cut(cq.Workplane("XY").add(cq.Solid.makeCone(30, 24, 5, cq.Vector(XO + 0.5, TAK_Y, TAK_Z), cq.Vector(-1, 0, 0))))
    else:
        s = s.cut(hole_x(4.3, XS, XO, TAK_Y, TAK_Z))
    return s if right else mirror_x(s)


# ---------------- سرپوش بالا (سه تکه) ----------------
def head_segment(i):
    """سرپوش بالا: سقف + جلو با شبکهٔ افقی برای عبور نور لامپ. سه تکه با عرض برابر."""
    seg = 2 * XW / 3
    x0 = -XW + i * seg
    x1 = x0 + seg
    top = box(x0, x1, H - 4, H, BP, D)
    front = box(x0, x1, 350, H, D - 4, D)
    lip = box(x0, x1, 350, 354, D - 14, D)
    h = top.union(front).union(lip)
    # پنجرهٔ نور با میله‌های افقی ۳ میلی‌متری هر ۱۰ میلی‌متر
    m = 8 if 0 < i < 2 else 14
    xa = x0 + (m if i > 0 else 14)
    xb = x1 - (m if i < 2 else 14)
    for y in range(366, 428, 10):
        h = h.cut(box(xa, xb, y, y + 7, D - 5, D + 1))
    # زبانهٔ پشت با سوراخ پیچ به صفحهٔ پشت
    h = h.union(box(x0 + 10, x1 - 10, H - 16, H - 4, BP, BP + 5))
    for x in (x0 + seg * 0.25, x0 + seg * 0.75):
        h = h.cut(cq.Workplane("XZ", origin=(0, H - 10, 0)).center(x, BP + 2.5).circle(1.7).extrude(-20))
    # زبانه‌های اتصال به تکهٔ کناری (هم‌پوشانی ۱۰ میلی‌متر)
    if i < 2:
        h = h.union(box(x1 - 1, x1 + 10, H - 8, H - 4, 20, D - 20)).cut(screw_hole_z(x1 + 5, H - 6, 18, D - 18, 1.6))
    return h


# ---------------- پنل تیغه‌ای جلو (دو نیمه) ----------------
def slat_half(right=True):
    """قاب + تیغه‌های افقی با زاویهٔ ۳۰ درجه (رو به پایین و بدون ساپورت پرینت می‌شود).
    لبهٔ بیرونی روی گونهٔ دیواره و لبهٔ وسط روی زبانهٔ نیمهٔ راست پیچ می‌شود."""
    x0, x1 = (0.0, WIN_X) if right else (-WIN_X, 0.0)
    y0, y1 = PANEL_Y0, PANEL_Y1
    frame = box(x0, x1, y0, y1, D - 8, D)
    opening = box(x0 + 10, x1 - 10, y0 + 8, y1 - 8, D - 9, D + 1)
    frame = frame.cut(opening)
    y = y0 + 14
    region = box(x0 + 10, x1 - 10, y0 + 8, y1 - 8, D - 22, D - 0.5)
    while y < y1 - 10:
        s = cq.Workplane("XY").box(abs(x1 - x0) - 6, 2.2, 16).rotate((0, 0, 0), (1, 0, 0), -30).translate(((x0 + x1) / 2, y, D - 9))
        frame = frame.union(s.intersect(region))
        y += 15
    ex = x1 - 5 if right else x0 + 5
    for yy in PANEL_HOLES_Y:
        frame = frame.cut(screw_hole_z(ex, yy, D - 8, D, 1.6))
        frame = frame.cut(screw_hole_z(-5, yy, D - 16, D, 1.6))
    if right:
        tab = box(-9.5, 0, y0, y1, D - 16, D - 8)
        for yy in PANEL_HOLES_Y:
            tab = tab.cut(screw_hole_z(-5, yy, D - 16, D - 8, 1.4))
        frame = frame.union(tab)
    return frame


# ---------------- کاست جمع‌کننده (دو نیمه) ----------------
def cassette_half(right=True):
    c = CAS
    t = c["t"]
    x0, x1 = (0.0, c["x"]) if right else (-c["x"], 0.0)
    b = box(x0, x1, c["y0"], c["y1"], c["z0"], c["z1"])
    inner = box(x0 - 1 if right else x0 + t, x1 - t if right else x1 + 1, c["y0"] + t, c["y1"] - t, c["z0"] + t, c["z1"] - t)
    b = b.cut(inner)
    # شکاف ورود فیلم در سقف
    b = b.cut(box(-FILM_W / 2 - 4, FILM_W / 2 + 4, c["y1"] - t - 1, c["y1"] + 1, FILM_Z - 5, FILM_Z + 5).intersect(box(x0, x1, -10, 500, -10, 200)))
    # دیوارهٔ کناری با سوراخ محور
    xe = x1 if right else x0
    b = b.cut(hole_x(8.3 if right else 4.3, min(xe, xe - (t if right else -t)) - 1, max(xe, xe - (t if right else -t)) + 1, TAK_Y, TAK_Z))
    # لبهٔ اتصال دو نیمه + بوش پیچ
    flange = box(-4 if right else 0, 0 if right else 4, c["y0"] + t, c["y1"] - t, c["z0"] + t, c["z0"] + t + 6)
    flange = flange.union(box(-4 if right else 0, 0 if right else 4, c["y0"] + t, c["y0"] + t + 6, c["z0"] + t, c["z1"] - t))
    if right:
        b = b.union(flange)
    for (yy, zz) in ((c["y0"] + 10, c["z0"] + 12), (c["y0"] + 10, c["z1"] - 12), (c["y1"] - 10, c["z1"] - 12)):
        b = b.union(cq.Workplane("YZ", origin=(-6 if right else 0, yy, zz)).circle(5).extrude(6))
        b = b.cut(hole_x(1.6, -8, 8, yy, zz))
    # جای برچسب روی صورت جلو + شیار دستگیره
    b = b.cut(box(x0 + (20 if right else 10), x1 - (10 if right else 20), c["y0"] + 14, c["y0"] + 20, c["z1"] - 1, c["z1"] + 1))
    # جای آهنربا روی سقف (گوشه)
    xm = MAG_X if right else -MAG_X
    b = b.cut(cq.Workplane("XY").box(10.4, 3.4, 10.4).translate((xm, c["y1"] - 1.6, (c["z0"] + c["z1"]) / 2)))
    return b


# ---------------- قرقره‌ها، محور، دستگیره ----------------
def core_cap(kind, stub=14.0):
    """درپوش لولهٔ PVC: 'stub' محور ۸ میلی‌متری؛ 'drive' سوکت شش‌گوش برای محور دستگیره"""
    plug = cq.Workplane("YZ").circle(CORE_ID / 2 - 0.15).extrude(16)
    plug = plug.cut(cq.Workplane("YZ").rect(2, CORE_ID).extrude(16).translate((6, 0, 0)))  # شکاف فنری
    flange = cq.Workplane("YZ").circle(CORE_OD / 2 + 6).extrude(-3)
    cap = plug.union(flange)
    if kind == "stub":
        cap = cap.union(cq.Workplane("YZ").circle(3.9).extrude(-stub))
    else:
        stub = cq.Workplane("YZ").circle(7.9).extrude(-6)
        cap = cap.union(stub)
        cap = cap.cut(cq.Workplane("YZ").polygon(6, 8.6 / math.cos(math.pi / 6)).extrude(-30).translate((10, 0, 0)))
    return cap


def knob_shaft():
    """دستگیره Ø۵۲ با دستهٔ چرخان + محور Ø۱۲ با سر شش‌گوش ۸ (یک تکه)"""
    L_in = XO - XS + 10  # طول محور از بیرون بدنه تا داخل درپوش
    knob = cq.Workplane("YZ").circle(26).extrude(16)
    for i in range(14):
        a = 2 * math.pi * i / 14
        knob = knob.cut(cq.Workplane("YZ", origin=(3, 26.5 * math.cos(a), 26.5 * math.sin(a))).circle(3.6).extrude(16))
    knob = knob.union(cq.Workplane("YZ", origin=(16, 15, 0)).circle(6).extrude(16))
    shaft = cq.Workplane("YZ").circle(5.9).extrude(-(L_in - 12))
    tip = cq.Workplane("YZ").polygon(6, 8.2 / math.cos(math.pi / 6)).extrude(-12).translate((-(L_in - 12), 0, 0))
    groove = cq.Workplane("YZ").circle(6.5).circle(4.6).extrude(-2).translate((-8, 0, 0))  # شیار اورینگ
    return knob.union(shaft).union(tip).cut(groove)


def back_plate():
    p = box(-XO, XO, 0, H, 0, BP)
    holes = []
    for sx in (-1, 1):
        for y in (40, 150, 230, 330, 420):
            holes.append((sx * (XW - 7), y))
    seg = 2 * XW / 3
    for i in range(3):
        x0 = -XW + i * seg
        holes += [(x0 + seg * 0.25, H - 10), (x0 + seg * 0.75, H - 10)]
    for (x, y) in holes:
        p = p.cut(screw_hole_z(x, y, 0, BP, 1.8))
    # سوراخ‌های نصب دیواری (کلیدی)
    for x in (-XO + 80, XO - 80):
        p = p.cut(cq.Workplane("XY", origin=(0, 0, -1)).center(x, H - 60).slot2D(18, 5, 90).extrude(BP + 2))
        p = p.cut(cq.Workplane("XY", origin=(0, 0, -1)).center(x, H - 67).circle(5).extrude(BP + 2))
    return p, holes


# ---------------- قطعات خریدنی (فقط برای رندر) ----------------
def lamp():
    g = LAMP["glass"] / 2
    t = LAMP["total"] / 2
    body = cyl_x(LAMP["dia"] / 2, -g, g, LAMP_Y, LAMP_Z)
    pins = cyl_x(1.2, -t, -g, LAMP_Y, LAMP_Z).union(cyl_x(1.2, g, t, LAMP_Y, LAMP_Z))
    return body.union(pins)


def sockets():
    out = None
    for sx in (-1, 1):
        x0, x1 = (XS - SOCKET, XS) if sx > 0 else (-XS, -XS + SOCKET)
        s = box(x0, x1, LAMP_Y - 18, LAMP_Y + 18, LAMP_Z - 20, LAMP_Z + 16)
        out = s if out is None else out.union(s)
    return out


def rolls():
    fw = FILM_W / 2
    sup = cyl_x(SUPPLY_MAX / 2 - 4, -fw, fw, SUP_Y, SUP_Z)
    tak = cyl_x(24, -fw, fw, TAK_Y, TAK_Z)
    return sup.union(tak)


def cores():
    a = cyl_x(CORE_OD / 2, -SUP_HALF, SUP_HALF, SUP_Y, SUP_Z).union(cyl_x(CORE_OD / 2, -TAK_HALF, TAK_HALF, TAK_Y, TAK_Z))
    return a.union(cyl_x(4, -XW, XW, GUIDE_Y, GUIDE_Z))


def film():
    fw = FILM_W / 2
    return box(-fw, fw, FILM_Y0, FILM_Y1, FILM_Z - 0.4, FILM_Z)


def ballast():
    return box(-200, -70, 200, 240, BP, BP + 28)


# ---------------- ساخت و خروجی ----------------
PRINT = {
    # name: (shape fn, color, explode dir [x,y,z], تعداد، توضیح جهت پرینت)
}


def build():
    bp, holes = back_plate()
    parts = {
        "side_upper_R": (side_upper(True), "#FFFFFF", [120, 60, 0]),
        "side_upper_L": (side_upper(False), "#FFFFFF", [-120, 60, 0]),
        "side_lower_R": (side_lower(True), "#FFFFFF", [120, -40, 0]),
        "side_lower_L": (side_lower(False), "#FFFFFF", [-120, -40, 0]),
        "head_1": (head_segment(0), "#F4F6F7", [-40, 160, 60]),
        "head_2": (head_segment(1), "#F4F6F7", [0, 160, 60]),
        "head_3": (head_segment(2), "#F4F6F7", [40, 160, 60]),
        "slats_L": (slat_half(False), "#E9EEF0", [-30, 0, 160]),
        "slats_R": (slat_half(True), "#E9EEF0", [30, 0, 160]),
        "cassette_L": (cassette_half(False), "#FFFFFF", [-30, -170, 60]),
        "cassette_R": (cassette_half(True), "#FFFFFF", [30, -170, 60]),
        "knob": (knob_shaft().translate((XO, TAK_Y, TAK_Z)), "#0F6E56", [160, -60, 0]),
        # درپوش‌ها: جهت پایه (رو به +X) برای سمت چپ است؛ سمت راست قرینه می‌شود
        "cap_supply_L": (core_cap("stub", SUP_STUB).translate((-SUP_HALF, SUP_Y, SUP_Z)), "#0F6E56", [-60, 60, 0]),
        "cap_supply_R": (core_cap("stub", SUP_STUB).mirror("YZ").translate((SUP_HALF, SUP_Y, SUP_Z)), "#0F6E56", [60, 60, 0]),
        "cap_takeup_L": (core_cap("stub").translate((-TAK_HALF, TAK_Y, TAK_Z)), "#0F6E56", [-60, -170, 60]),
        "cap_takeup_R": (core_cap("drive").mirror("YZ").translate((TAK_HALF, TAK_Y, TAK_Z)), "#0F6E56", [60, -170, 60]),
    }
    bought = {
        "back_plate": (bp, "#DCE3E7", [0, 0, -80]),
        "lamp": (lamp(), "#C9C3F2", [0, 220, 120]),
        "sockets": (sockets(), "#3E3D3A", [0, 200, 80]),
        "rolls": (rolls(), "#F2D79E", [0, 0, 0]),
        "cores": (cores(), "#BA7517", [0, 0, 0]),
        "film": (film(), "#FAEEDA", [0, 0, 0]),
        "ballast": (ballast(), "#8C9196", [0, 0, 0]),
    }
    return parts, bought, holes


def main():
    os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "step"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "dxf"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "render-data"), exist_ok=True)
    parts, bought, holes = build()
    assy = cq.Assembly(name="RTH-C_proto")
    manifest = {
        "title": "RTH-C prototype",
        "size": [round(W), H, D],
        "lights": [{"color": "#7F77DD", "intensity": 10, "distance": 600, "pos": [0, LAMP_Y, LAMP_Z + 40]}],
        "ghost": [p for p in parts if p.startswith(("head", "slats", "cassette", "side_upper"))],
        "hideNormally": [],
        "parts": [],
    }
    sizes = {}
    for name, (shape, color, ex) in {**parts, **bought}.items():
        cq.exporters.export(shape, os.path.join(OUT, "render-data", f"{name}.stl"), tolerance=0.1, angularTolerance=0.1)
        if name in parts:
            # فایل پرینت: قطعه به مبدأ منتقل می‌شود
            bb = shape.val().BoundingBox()
            sizes[name] = sorted([round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)], reverse=True)
            cq.exporters.export(shape.translate((-bb.xmin, -bb.ymin, -bb.zmin)), os.path.join(OUT, "stl", f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
        assy.add(shape, name=name, color=cq.Color(color))
        mat = {"name": name, "color": color, "roughness": 0.4, "explode": ex}
        if name == "lamp":
            mat.update(emissive="#7F77DD", emissiveIntensity=1.2)
        manifest["parts"].append(mat)
    assy.export(os.path.join(OUT, "step", "RTH-C_proto_assembly.step"))
    bp = bought["back_plate"][0]
    cq.exporters.export(bp.section(BP / 2), os.path.join(OUT, "dxf", "back_plate_5mm.dxf"))
    with open(os.path.join(OUT, "render-data", "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    summary = dict(
        lamp=LAMP,
        overall_mm=[round(W, 1), H, D],
        socket_faces_mm=round(INNER, 1),
        film_width_mm=FILM_W,
        window_mm=[round(2 * WIN_X), FILM_Y1 - FILM_Y0],
        parts=sizes,
        back_plate_holes=len(holes),
    )
    with open(os.path.join(OUT, "dimensions.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
