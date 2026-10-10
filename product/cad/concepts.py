"""
سه طرح مفهومی ظاهری برای تلهٔ حشرهٔ UV با فیلم چسبی رولی (همان سازوکار: رول نو بالا، کاست دربستهٔ پایین)

A  «چراغ دیواری»   — پنل جلوی سفید و خمیده؛ سطح چسبی پشت پنل پنهان است و نور UV از لبه‌ها بیرون می‌زند.
B  «ستون باریک»    — بدنهٔ بلند و باریک؛ سطح چسبی پشت تیغه‌های افقی مایل.
C  «اصلاح‌شده»      — همان طرح قبلی با فرم نرم‌تر، تیغه به‌جای میله، کاست هم‌رنگ بدنه و دستگیرهٔ هم‌سطح.

مختصات: X عرض، Y ارتفاع، Z از دیوار به جلو. واحد: میلی‌متر.
اجرا: python3 concepts.py   ← خروجی در out/concepts/<a|b|c>/ (STL + STEP + manifest.json)
"""
import json
import math
import os
import random

import cadquery as cq

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "concepts")

WHITE = {"color": "#FFFFFF", "roughness": 0.32}
SOFT = {"color": "#E6ECEF", "roughness": 0.45}
SLAT = {"color": "#F4F6F7", "roughness": 0.35, "emissive": "#3A3480", "emissiveIntensity": 0.55}
UV = {"color": "#4A42C0", "emissive": "#6A61E0", "emissiveIntensity": 1.1, "roughness": 0.2}
FILM = {"color": "#F6E2B4", "roughness": 0.3}
FLY = {"color": "#1F2A30", "roughness": 0.4}
GREEN = {"color": "#0F6E56", "roughness": 0.4}
OK = {"color": "#1D9E75", "emissive": "#1D9E75", "emissiveIntensity": 1.4}
ROLL = {"color": "#F2D79E", "roughness": 0.3}
CORE = {"color": "#BA7517", "roughness": 0.6}


# ---------------- ابزارها ----------------
def rbox(w, h, d, r, x=0.0, y=0.0, z=0.0):
    r = min(r, w / 2 - 0.01, h / 2 - 0.01)
    return cq.Workplane("XY", origin=(0, 0, z)).center(x, y).rect(w, h).extrude(d).edges("|Z").fillet(r)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_x(r, length, y, z, x=0.0):
    return cq.Workplane("YZ", origin=(x - length / 2, y, z)).circle(r).extrude(length)


def cyl_z(r, x, y, z0, z1):
    return cq.Workplane("XY", origin=(0, 0, z0)).center(x, y).circle(r).extrude(z1 - z0)


def front_fillet(wp, r):
    try:
        return wp.faces(">Z").edges().fillet(r)
    except Exception:
        return wp


def compound(solids):
    return cq.Workplane("XY").add(cq.Compound.makeCompound([s.val() for s in solids]))


def slats(x0, x1, y0, y1, pitch, z_back, depth, tilt_deg, thick=2.4):
    """تیغه‌های افقی مایل (لبهٔ جلو پایین‌تر) تا سطح چسبی از روبه‌رو و پایین دیده نشود"""
    out = []
    y = y0 + pitch / 2
    while y < y1 - pitch / 3:
        s = (
            cq.Workplane("XY")
            .box(x1 - x0, thick, depth)
            .rotate((0, 0, 0), (1, 0, 0), tilt_deg)
            .translate(((x0 + x1) / 2, y, z_back + depth / 2))
        )
        out.append(s)
        y += pitch
    return compound(out)


def flies(x0, x1, y0, y1, z, n, seed):
    random.seed(seed)
    out = []
    for _ in range(n):
        a = random.uniform(0, 360)
        f = (
            cq.Workplane("XY", origin=(0, 0, z))
            .ellipse(5.5, 3.2)
            .extrude(2.6)
            .union(cq.Workplane("XY", origin=(5.5, 0, z)).circle(2.4).extrude(2.4))
            .rotate((0, 0, 0), (0, 0, 1), a)
            .translate((random.uniform(x0, x1), random.uniform(y0, y1), 0))
        )
        out.append(f)
    return compound(out)


# ---------------- A: چراغ دیواری ----------------
def concept_a():
    W, H = 360, 540
    parts = {}
    base = rbox(W, H, 34, 70, y=H / 2)
    base = front_fillet(base, 6)
    # جای کاست از پایین
    base = base.cut(box(-150, 150, -5, 112, 4, 40))
    parts["base"] = (base, SOFT)
    parts["film"] = (box(-140, 140, 120, 445, 34, 34.8), FILM)
    parts["flies"] = (flies(-120, 120, 140, 430, 34.8, 13, 7), FLY)
    cas = rbox(296, 104, 34, 18, y=60, z=4)
    cas = front_fillet(cas, 4)
    parts["cassette"] = (cas, WHITE)
    # پنل جلوی خمیده
    R, SW, SH, ZF = 900.0, 400.0, 560.0, 98.0
    outer = cq.Workplane("XZ").center(0, ZF - R).circle(R).extrude(-(SH + 60)).translate((0, -40, 0))
    inner = cq.Workplane("XZ").center(0, ZF - R).circle(R - 5).extrude(-(SH + 60)).translate((0, -40, 0))
    shell = outer.cut(inner)
    clip = rbox(SW, SH, 200, 110, y=H / 2, z=0)
    shield = shell.intersect(clip)
    # لبهٔ نورانی دورتادور پنل (آکریلیک لبه‌تاب)
    rim = shell.intersect(clip.cut(rbox(SW - 12, SH - 12, 200, 104, y=H / 2, z=0)))
    shield = shield.cut(rim)
    parts["shield"] = (shield, WHITE)
    parts["rim"] = (rim, UV)
    # پایه‌های فاصله‌انداز
    st = [cyl_z(9, x, y, 34, 76) for x in (-120, 120) for y in (150, 420)]
    parts["standoffs"] = (compound(st), SOFT)
    # نوار LED پشت لبه‌های پنل (رو به دیوار)
    ring = rbox(360, 520, 3, 95, y=H / 2, z=62).cut(rbox(344, 504, 3, 88, y=H / 2, z=62))
    parts["led_ring"] = (ring, UV)
    parts["status_led"] = (cyl_z(4.5, 150, 40, ZF - 18, ZF - 0.3), OK)
    # رول‌ها (فقط در نمای برش دیده می‌شوند)
    parts["supply_roll"] = (cyl_x(24, 280, 470, 26), ROLL)
    parts["takeup_roll"] = (cyl_x(24, 280, 62, 26), ROLL)
    manifest = {
        "title": "A — چراغ دیواری",
        "size": [W, H, 100],
        "decals": [{"image": "assets/logo.jpg", "x": 0, "y": 75, "z": ZF + 0.6, "w": 120, "h": 68}],
        "lights": [
            {"color": "#7F77DD", "intensity": 18, "distance": 600, "pos": [0, 575, 40]},
            {"color": "#7F77DD", "intensity": 18, "distance": 600, "pos": [0, -35, 40]},
            {"color": "#7F77DD", "intensity": 14, "distance": 560, "pos": [-225, 270, 40]},
            {"color": "#7F77DD", "intensity": 14, "distance": 560, "pos": [225, 270, 40]},
        ],
        "ghost": ["shield", "rim", "led_ring"],
        "hideNormally": ["supply_roll", "takeup_roll"],
    }
    return parts, manifest


# ---------------- B: ستون باریک ----------------
def concept_b():
    W, H, D = 200, 900, 84
    parts = {}
    body = rbox(W, H, D, 99.9, y=H / 2)
    body = front_fillet(body, 10)
    ch = rbox(132, 620, 60, 30, y=455, z=34)
    body = body.cut(ch)
    body = body.cut(box(-80, 80, -5, 138, 6, D + 5))
    parts["body"] = (body, WHITE)
    parts["film"] = (box(-62, 62, 150, 760, 34, 34.8), FILM)
    parts["flies"] = (flies(-50, 50, 170, 740, 34.8, 12, 11), FLY)
    parts["slats"] = (slats(-64, 64, 148, 762, 19, 40, 36, -32), SLAT)
    parts["uv_left"] = (box(-66, -61, 160, 750, 58, 74), UV)
    parts["uv_right"] = (box(61, 66, 160, 750, 58, 74), UV)
    cas = rbox(158, 134, D - 8, 30, y=72, z=6).intersect(rbox(W, H, D + 10, 99.9, y=H / 2))
    cas = front_fillet(cas, 8)
    parts["cassette"] = (cas, WHITE)
    parts["cassette_line"] = (box(-79, 79, 138, 141, D - 12, D - 3), GREEN)
    parts["status_led"] = (cyl_z(4.5, 0, 830, D - 2, D + 0.5), OK)
    parts["supply_roll"] = (cyl_x(24, 124, 795, 30), ROLL)
    parts["takeup_roll"] = (cyl_x(24, 124, 75, 34), ROLL)
    manifest = {
        "title": "B — ستون باریک",
        "size": [W, H, D],
        "decals": [{"image": "assets/logo.jpg", "x": 0, "y": 72, "z": D + 0.6, "w": 104, "h": 59}],
        "lights": [
            {"color": "#7F77DD", "intensity": 1.4, "distance": 300, "pos": [0, 300, 95]},
            {"color": "#7F77DD", "intensity": 1.4, "distance": 300, "pos": [0, 610, 95]},
        ],
        "ghost": ["body", "slats", "cassette"],
        "hideNormally": ["supply_roll", "takeup_roll"],
    }
    return parts, manifest


# ---------------- C: اصلاح‌شدهٔ طرح اول ----------------
def concept_c():
    W, H, D = 340, 560, 80
    parts = {}
    body = rbox(W, H, D, 72, y=H / 2)
    body = front_fillet(body, 14)
    body = body.cut(rbox(272, 290, 60, 24, y=305, z=30))
    body = body.cut(box(-150, 150, -5, 136, 6, D + 5))
    body = body.cut(rbox(240, 10, 8, 4.9, y=500, z=D - 5))
    parts["body"] = (body, WHITE)
    parts["film"] = (box(-132, 132, 162, 448, 30, 30.8), FILM)
    parts["flies"] = (flies(-115, 115, 175, 435, 30.8, 12, 5), FLY)
    parts["slats"] = (slats(-136, 136, 160, 450, 17, 36, 38, -32), SLAT)
    parts["led_bar"] = (rbox(236, 7, 4, 3.4, y=500, z=D - 5), UV)
    parts["uv_inner"] = (box(-125, 125, 438, 446, 50, 64), UV)
    cas = rbox(296, 128, D - 10, 40, y=70, z=6).intersect(rbox(W, H, D + 10, 72, y=H / 2))
    cas = front_fillet(cas, 10)
    parts["cassette"] = (cas, WHITE)
    parts["cassette_line"] = (box(-149, 149, 136, 139, D - 14, D - 4), GREEN)
    # دستگیرهٔ هم‌سطح در کنار
    dial = cq.Workplane("YZ", origin=(W / 2 - 3, 70, 40)).circle(22).extrude(4.5)
    dial = dial.cut(cq.Workplane("YZ", origin=(W / 2 + 0.5, 70, 40)).rect(30, 6).extrude(2))
    parts["dial"] = (dial, GREEN)
    parts["status_led"] = (cyl_z(4.5, 140, 500, D - 3, D + 0.5), OK)
    parts["supply_roll"] = (cyl_x(24, 264, 488, 30), ROLL)
    parts["takeup_roll"] = (cyl_x(24, 264, 70, 34), ROLL)
    manifest = {
        "title": "C — طرح اصلاح‌شده",
        "size": [W, H, D],
        "decals": [{"image": "assets/logo.jpg", "x": 0, "y": 72, "z": D + 0.6, "w": 120, "h": 68}],
        "lights": [{"color": "#7F77DD", "intensity": 1.2, "distance": 300, "pos": [0, 420, 95]}],
        "ghost": ["body", "slats", "cassette"],
        "hideNormally": ["supply_roll", "takeup_roll"],
    }
    return parts, manifest


def export(key, fn):
    parts, manifest = fn()
    out = os.path.join(ROOT, key)
    os.makedirs(out, exist_ok=True)
    assy = cq.Assembly(name=f"concept_{key}")
    manifest["parts"] = []
    for name, (shape, mat) in parts.items():
        cq.exporters.export(shape, os.path.join(out, f"{name}.stl"), tolerance=0.15, angularTolerance=0.15)
        c = cq.Color(mat["color"])
        assy.add(shape, name=name, color=c)
        manifest["parts"].append({"name": name, **mat})
    assy.export(os.path.join(out, f"concept_{key}.step"))
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("exported", key, len(parts), "parts")


if __name__ == "__main__":
    import sys

    keys = sys.argv[1:] or ["a", "b", "c"]
    fns = {"a": concept_a, "b": concept_b, "c": concept_c}
    for k in keys:
        export(k, fns[k])
