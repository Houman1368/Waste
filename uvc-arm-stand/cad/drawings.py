"""Dimensioned 2D shop drawings (SVG) of every manufactured part, generated from model.Cfg."""
import math
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon, FancyBboxPatch
from model import C

c = C
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "drawings")
os.makedirs(OUT, exist_ok=True)
INK, DIMC, HID, BEND = "#1c1e26", "#2265a0", "#888888", "#d0232a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})


def new(w, h, scale=1.0):
    fig = plt.figure(figsize=(w / 25.4 * scale, h / 25.4 * scale))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save(fig, ax, name, lims):
    (x0, x1), (y0, y1) = lims
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    w = 8.0                                   # every sheet printed ~190 mm wide -> uniform text size
    fig.set_size_inches(w, w * (y1 - y0) / (x1 - x0))
    fig.savefig(os.path.join(OUT, name + ".svg"), bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def rect(ax, x0, y0, w, h, **kw):
    kw.setdefault("fill", False)
    kw.setdefault("ec", INK)
    kw.setdefault("lw", 1.2)
    ax.add_patch(Rectangle((x0, y0), w, h, **kw))


def hole(ax, x, y, d, cross=True):
    ax.add_patch(Circle((x, y), d / 2, fill=False, ec=INK, lw=1))
    if cross:
        k = d / 2 + 2.5
        ax.plot([x - k, x + k], [y, y], color=HID, lw=0.4)
        ax.plot([x, x], [y - k, y + k], color=HID, lw=0.4)


def dim_h(ax, x1, x2, y, ybase, text=None, fs=7.5):
    ax.plot([x1, x1], [ybase, y + (2 if y > ybase else -2)], color=DIMC, lw=0.5)
    ax.plot([x2, x2], [ybase, y + (2 if y > ybase else -2)], color=DIMC, lw=0.5)
    ax.annotate("", (x1, y), (x2, y), arrowprops=dict(arrowstyle="<->", color=DIMC, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text((x1 + x2) / 2, y + 1.2, text or f"{abs(x2 - x1):g}", ha="center", va="bottom", color=DIMC, fontsize=fs)


def dim_v(ax, y1, y2, x, xbase, text=None, fs=7.5):
    ax.plot([xbase, x + (2 if x > xbase else -2)], [y1, y1], color=DIMC, lw=0.5)
    ax.plot([xbase, x + (2 if x > xbase else -2)], [y2, y2], color=DIMC, lw=0.5)
    ax.annotate("", (x, y1), (x, y2), arrowprops=dict(arrowstyle="<->", color=DIMC, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text(x - 1.2, (y1 + y2) / 2, text or f"{abs(y2 - y1):g}", ha="right", va="center", rotation=90, color=DIMC, fontsize=fs)


def tag(ax, x, y, t):
    ax.text(x, y, t, fontsize=7, color="white", ha="center", va="center", weight="bold",
            bbox=dict(boxstyle="circle,pad=0.15", fc=BEND, ec="none"))


def note(ax, x, y, tx, ty, text, fs=7.5):
    ax.annotate(text, (x, y), (tx, ty), fontsize=fs, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.5, shrinkA=0, shrinkB=2))


def bendline(ax, x0, y0, x1, y1, label=None):
    ax.plot([x0, x1], [y0, y1], color=BEND, lw=0.8, ls=(0, (6, 3)))
    if label:
        ax.text(x1, y1 + 1.5, label, color=BEND, fontsize=6.5, ha="right", va="bottom")


# ------------------------------------------------------------------ T1 head plate
def t1():
    fig, ax = new(1, 1)
    W, H = c.t1_w, c.t1_h
    rect(ax, -W / 2, 0, W, H)
    ya, yp = H - c.hinge_from_top, H - c.hinge_from_top - c.index_r
    z0 = c.z_t1_top - H
    for s in (-1, 1):
        hole(ax, s * c.hinge_dx, ya, 10.5)
        hole(ax, s * c.hinge_dx, yp, 6.5)
    for x, z in c.t1_bolts:
        hole(ax, x, z - z0, 9)
        ax.add_patch(Circle((x, z - z0), 8.5, fill=False, ec=HID, lw=0.5, ls="--"))
    # column outline behind (dashed) and column top
    rect(ax, -c.col_x / 2, 0, c.col_x, c.z_col1 - z0, ec=HID, lw=0.6, ls="--")
    ax.text(0, c.z_col1 - z0 - 6, "column top (behind)", ha="center", color=HID, fontsize=6.5)
    dim_h(ax, -W / 2, W / 2, -24, 0)
    dim_h(ax, -c.hinge_dx, c.hinge_dx, -12, yp - 4)
    dim_h(ax, c.hinge_dx, W / 2, H + 10, H, f"{W/2 - c.hinge_dx:g}")
    dim_h(ax, -55, 55, 6, 20, "110")
    dim_h(ax, -20, 20, 98, 112, "40")
    dim_v(ax, 0, H, W / 2 + 26, W / 2)
    dim_v(ax, ya, H, W / 2 + 13, c.hinge_dx + 6, f"{c.hinge_from_top:g}")
    dim_v(ax, yp, ya, -W / 2 - 10, -c.hinge_dx - 6, f"{c.index_r:g}")
    dim_v(ax, 0, 20, -W / 2 - 10, -55, "20")
    dim_v(ax, 0, 112, -W / 2 - 22, -20, "112")
    for s_ in (-1, 1):
        tag(ax, s_ * c.hinge_dx + s_ * 10, ya + 8, "A")
        tag(ax, s_ * c.hinge_dx + s_ * 9, yp + 6, "B")
    for x, z in c.t1_bolts:
        tag(ax, x + 9, z - z0 + 8, "C")
    ax.text(-W / 2, -40, "A: 2x Ø10.5 hinge bolt M10     B: 2x Ø6.5 index pin + M12x1.5 weld nut on BACK face"
            "     C: 6x Ø9 countersunk 90° on FRONT (M8)", fontsize=7.5)
    ax.text(-W / 2, H + 22, "T1  HEAD PLATE   steel S235 t=4   qty 2   (view from front)", fontsize=9, weight="bold")
    save(fig, ax, "T1_head_plate", ((-W / 2 - 40, W / 2 + 40), (-48, H + 30)))


# ------------------------------------------------------------------ H2 index disc
def h2():
    fig, ax = new(1, 1)
    R = c.disc_d / 2
    ax.add_patch(Circle((0, 0), R, fill=False, ec=INK, lw=1.2))
    hole(ax, 0, 0, 14)
    ax.add_patch(Circle((0, 0), c.index_r, fill=False, ec=HID, lw=0.5, ls="-."))
    for k in range(13):
        g = math.radians(c.plunger_beta - 15 * k)
        x, y = c.index_r * math.sin(g), -c.index_r * math.cos(g)
        hole(ax, x, y, 6.2, cross=False)
        ax.text(x * 1.22, y * 1.22, f"{15*k}°", ha="center", va="center", fontsize=6, color=DIMC)
    dim_h(ax, -R, R, -R - 12, 0, f"Ø{c.disc_d:g}")
    dim_v(ax, 0, -c.index_r, 14, 3, f"R{c.index_r:g}")
    note(ax, 5, 5, 30, 40, "Ø14 (bronze bush)")
    note(ax, -c.index_r * 0.707 - 2, c.index_r * 0.707 * -1 - 2, -R - 5, -R - 2,
         "13x Ø6.2 on R50, 15° pitch\nlaser Ø5.8 then drill/ream Ø6.2")
    ax.text(-R, R + 10, "H2  INDEX DISC   steel S235 t=5   qty 4", fontsize=9, weight="bold")
    ax.text(-R, R + 3, "0° = arm parked (down). Same part for all 4 arms; left arms: install flipped.", fontsize=7)
    save(fig, ax, "H2_index_disc", ((-R - 25, R + 25), (-R - 22, R + 18)))


# ------------------------------------------------------------------ H1 bracket blank + section
def h1():
    fig, ax = new(1, 1)
    L, Wd = 120, c.br_len
    rect(ax, -L / 2, -Wd / 2, L, Wd)
    hole(ax, 0, 0, 14)
    for sx in (-1, 1):
        for sy in (-1, 1):
            hole(ax, sx * 45, sy * c.br_bolt_dz, 5.5)
        bendline(ax, sx * 34, -Wd / 2 - 4, sx * 34, Wd / 2 + 4, "bend 90° up" if sx > 0 else None)
    dim_h(ax, -L / 2, L / 2, -Wd / 2 - 14, -Wd / 2, "120 (developed - check bend allowance)")
    dim_h(ax, -34, 34, Wd / 2 + 10, Wd / 2, "68 (outside)")
    dim_h(ax, 34, 45, -Wd / 2 - 5, -c.br_bolt_dz, "11")
    dim_v(ax, -Wd / 2, Wd / 2, L / 2 + 16, L / 2)
    dim_v(ax, -c.br_bolt_dz, c.br_bolt_dz, -L / 2 - 8, -45, f"{2*c.br_bolt_dz:g}")
    note(ax, 5, 5, 14, 22, "Ø14")
    note(ax, 47, c.br_bolt_dz + 2, 58, 38, "4x Ø5.5 (M5)")
    # section view of the bent U
    ox, oy = 0, -95
    t = c.br_t
    pts = [(-34, oy), (34, oy), (34, oy - 26), (30, oy - 26), (30, oy - t), (-30, oy - t), (-30, oy - 26), (-34, oy - 26)]
    ax.add_patch(Polygon(pts, closed=True, fill=True, fc="#dfe6f0", ec=INK, lw=1))
    rect(ax, -30, oy - 4 - 45, 60, 45, ec=HID, lw=0.6, ls="--")
    ax.text(0, oy - 30, "arm channel A1", ha="center", color=HID, fontsize=6.5)
    rect(ax, -65, oy, 130, 5, ec=INK, lw=0.8, fill=True, fc="#eeeeee")
    ax.text(68, oy + 1, "disc H2 welded on top", fontsize=6.5, va="bottom")
    dim_h(ax, -30, 30, oy - 58, oy - 26, "60 inside")
    dim_v(ax, oy - 26, oy, 46, 34, "26")
    ax.text(-L / 2, Wd / 2 + 24, "H1  ARM BRACKET   steel S235 t=4   qty 4", fontsize=9, weight="bold")
    ax.text(-L / 2, oy + 16, "SECTION after bending (U fits snugly over 60 mm channel)", fontsize=7)
    save(fig, ax, "H1_bracket", ((-L / 2 - 25, L / 2 + 70), (oy - 68, Wd / 2 + 32)))


# ------------------------------------------------------------------ A1 arm blank + section
def a1():
    fig, ax = new(1, 1)
    L = c.arm_len
    rect(ax, 0, -85, L, 170)
    e = c.axis_from_end
    hole(ax, e, 0, 14)
    for dz in (-c.br_bolt_dz, c.br_bolt_dz):
        for sy in (-1, 1):
            hole(ax, e + dz, sy * 43, 5.5, cross=False)
    hole(ax, c.grommet_from_end, 52, 10)
    for y, lab in ((75, "lip 10"), (30, "wall 45"), (-30, "floor 60"), (-75, "wall 45")):
        bendline(ax, -5, y, L + 5, y)
    for y, lab in ((80, "lip 10"), (52, "wall 45"), (0, "floor 60 (outside)"), (-52, "wall 45"), (-80, "lip 10")):
        ax.text(L - 120, y, lab, fontsize=6.5, color=BEND, va="center")
    dim_h(ax, 0, L, -100, -85)
    dim_h(ax, 0, e, 96, 0)
    dim_h(ax, 0, c.grommet_from_end, 110, 52)
    dim_v(ax, -85, 85, L + 30, L)
    dim_v(ax, 30, 75, L + 14, L, "45")
    dim_v(ax, -30, 30, L + 14, L, "60")
    note(ax, e + 5, 5, e + 60, 30, "Ø14 hinge bush")
    note(ax, e + 20, 45, e + 60, 62, "4x Ø5.5 (M5) in walls, 13 from floor, ±18 from hinge")
    note(ax, c.grommet_from_end + 4, 55, c.grommet_from_end + 60, 80, "Ø10 cable grommet")
    # section
    ox = L / 2
    oy = -175
    t = 3
    prof = [(-30, 0), (30, 0), (30, -45), (20, -45), (20, -45 + t), (30 - t, -45 + t), (30 - t, -t), (-30 + t, -t),
            (-30 + t, -45 + t), (-20, -45 + t), (-20, -45), (-30, -45)]
    ax.add_patch(Polygon([(ox + x * 1.6, oy + y * 1.6) for x, y in prof], closed=True, fc="#dfe6f0", ec=INK, lw=1))
    ax.add_patch(Circle((ox, oy - 25 * 1.6), 13 * 1.6, fill=False, ec="#7a5cd6", lw=1))
    ax.text(ox + 55, oy - 30, "SECTION (scale 1.6:1)\nlamp T8 Ø26, axis 25 from floor\nmirror side INSIDE", fontsize=7)
    ax.text(0, 125, "A1  ARM REFLECTOR CHANNEL   aluminium 1 mm mirror/bright-anodised   qty 4   (flat blank)", fontsize=9, weight="bold")
    save(fig, ax, "A1_arm", ((-30, L + 50), (oy - 90, 135)))


# ------------------------------------------------------------------ A2 end cap
def a2():
    fig, ax = new(1, 1)
    pts = [(-39, -22), (-29, -22), (-29, -32), (29, -32), (29, -22), (39, -22), (39, 22),
           (29, 22), (29, 32), (-29, 32), (-29, 22), (-39, 22)]
    ax.add_patch(Polygon(pts, closed=True, fill=False, ec=INK, lw=1.2))
    for x in (-29, 29):
        bendline(ax, x, -24, x, 24)
    for y in (-22, 22):
        bendline(ax, -31, y, 31, y)
    dim_h(ax, -29, 29, -42, -32, "58")
    dim_h(ax, -39, 39, 40, 32, "78")
    dim_v(ax, -22, 22, -48, -39, "44")
    dim_v(ax, -32, 32, 48, 39, "64")
    ax.text(0, 0, "G13 socket holes\nper purchased socket", ha="center", va="center", fontsize=6.5, color=HID)
    ax.text(-39, 52, "A2  END CAP   aluminium t=1   qty 8   4 flanges 10 bent 90°, rivet M4 to channel", fontsize=8, weight="bold")
    save(fig, ax, "A2_end_cap", ((-60, 60), (-52, 60)))


# ------------------------------------------------------------------ B1 base plate
def b1():
    fig, ax = new(1, 1)
    hx, hy = c.base_x / 2, c.base_y / 2
    rect(ax, -hx, -hy, 2 * hx, 2 * hy)
    fx, fy = c.flange_x / 2 - c.flange_bolt_inset, c.flange_y / 2 - c.flange_bolt_inset
    for sx in (-1, 1):
        for sy in (-1, 1):
            hole(ax, sx * fx, sy * fy, 11)
            cx, cy = sx * (hx - 30), sy * (hy - 30)
            rect(ax, cx - 30, cy - 30, 60, 60, ec=HID, lw=0.5, ls="--")
            for dx in (-22.5, 22.5):
                for dy in (-22.5, 22.5):
                    hole(ax, cx + dx, cy + dy, 9, cross=False)
    rect(ax, -c.flange_x / 2, -c.flange_y / 2, c.flange_x, c.flange_y, ec=HID, lw=0.6, ls="--")
    rect(ax, -c.b2_x / 2, -c.b2_y / 2, c.b2_x, c.b2_y, ec="#e6a23c", lw=0.6, ls=":")
    dim_h(ax, -hx, hx, -hy - 22, -hy)
    dim_v(ax, -hy, hy, hx + 24, hx)
    dim_h(ax, -fx, fx, -fy - 12, -fy, f"{2*fx:g}")
    dim_v(ax, -fy, fy, fx + 14, fx, f"{2*fy:g}")
    dim_h(ax, hx - 52.5, hx - 7.5, hy + 8, hy - 7.5, "45")
    dim_h(ax, hx - 30, hx, hy + 18, hy, "30")
    note(ax, fx + 4, fy + 4, fx + 30, fy + 40, "4x Ø11 (M10) column flange")
    note(ax, hx - 7.5 - 3, -hy + 7.5 + 3, hx - 120, -hy + 45, "16x Ø9 casters (CHECK pattern on real caster)")
    ax.text(0, c.b2_y / 2 - 10, "B2 box outline 460x360", ha="center", fontsize=6.5, color="#e6a23c")
    ax.text(-hx, hy + 30, "B1  BASE PLATE   steel S235 t=6   qty 1   (top view, column centred)", fontsize=9, weight="bold")
    save(fig, ax, "B1_base_plate", ((-hx - 20, hx + 45), (-hy - 35, hy + 40)))


# ------------------------------------------------------------------ C1 flange + gusset
def flange():
    fig, ax = new(1, 1)
    fx, fy = c.flange_x / 2, c.flange_y / 2
    rect(ax, -fx, -fy, 2 * fx, 2 * fy)
    bx, by = fx - c.flange_bolt_inset, fy - c.flange_bolt_inset
    for sx in (-1, 1):
        for sy in (-1, 1):
            hole(ax, sx * bx, sy * by, 11)
    rect(ax, -c.col_x / 2, -c.col_y / 2, c.col_x, c.col_y, ec=INK, lw=0.6, ls="--")
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        w = c.col_x / 2 if ang in (0, 180) else c.col_y / 2
        x0, y0 = w * math.cos(a), w * math.sin(a)
        x1, y1 = (w + c.gusset_l) * math.cos(a), (w + c.gusset_l) * math.sin(a)
        ax.plot([x0, x1], [y0, y1], color=INK, lw=3, alpha=0.35)
    ax.text(0, 0, "column 160x120\nweld all round", ha="center", va="center", fontsize=7)
    dim_h(ax, -fx, fx, -fy - 18, -fy)
    dim_v(ax, -fy, fy, fx + 18, fx)
    dim_h(ax, -bx, bx, fy + 10, by, f"{2*bx:g}")
    dim_v(ax, -by, by, -fx - 10, -bx, f"{2*by:g}")
    dim_h(ax, c.col_x / 2, fx, -fy - 8, -c.col_y / 2, f"{fx - c.col_x/2:g}")
    note(ax, bx + 4, -by - 4, bx + 25, -by - 30, "4x Ø11 (M10)")
    ax.text(-fx, fy + 22, "C1  COLUMN FLANGE   steel S235 t=6   qty 1", fontsize=9, weight="bold")
    # gusset
    gx, gy = fx + 50, -40
    ax.add_patch(Polygon([(gx, gy), (gx + c.gusset_l, gy), (gx, gy + c.gusset_h)], closed=True, fill=False, ec=INK, lw=1.2))
    dim_h(ax, gx, gx + c.gusset_l, gy - 10, gy)
    dim_v(ax, gy, gy + c.gusset_h, gx - 8, gx)
    ax.text(gx, gy + c.gusset_h + 8, "GUSSET t=4  qty 4\n(mid of each face)", fontsize=7.5, weight="bold")
    save(fig, ax, "C1_flange_gusset", ((-fx - 25, gx + c.gusset_l + 25), (-fy - 30, fy + 30)))


# ------------------------------------------------------------------ C1 column (unfolded faces)
def column():
    fig, ax = new(1, 1)
    Hc = c.col_h
    z0 = c.z_col0
    faces = [("FRONT (160)", c.col_x, 0), ("RIGHT (120)", c.col_y, 200), ("BACK (160)", c.col_x, 360), ("LEFT (120)", c.col_y, 560)]
    for name, w, ox in faces:
        rect(ax, ox, 0, w, Hc)
        ax.text(ox + w / 2, Hc + 12, name, ha="center", fontsize=8, weight="bold")
        cx = ox + w / 2
        if "FRONT" in name or "BACK" in name:
            for x, z in c.t1_bolts:
                hole(ax, cx + x, z - z0, 10, cross=False)
            zc = c.z_t1_top - c.t1_h - 25 - z0
            for sx in (-1, 1):
                hole(ax, cx + sx * c.cable_hole_x, zc, 16, cross=False)
            rect(ax, cx - c.t1_w / 2, c.z_t1_top - c.t1_h - z0, c.t1_w, c.t1_h, ec=HID, lw=0.5, ls="--")
        if "BACK" in name:
            rect(ax, cx - 50, c.door_z0 + 10 - z0, 100, c.door_h - 20, ec=INK, lw=1, fc="#f2f5fa", fill=True)
            ax.text(cx, c.door_z0 + c.door_h / 2 - z0, "door\nopening\n100x580", ha="center", va="center", fontsize=6.5)
            dim_v(ax, 0, c.door_z0 + 10 - z0, ox + w + 12, cx + 50, f"{c.door_z0 + 10 - z0:g}")
        if "RIGHT" in name:
            for z in (c.handle_top - 15, c.handle_top - c.handle_len + 15):
                hole(ax, cx, z - z0, 16, cross=False)
            ax.text(cx, c.handle_top - c.handle_len / 2 - z0, "handle\nstandoffs\nØ16", ha="center", fontsize=6.5)
            dim_v(ax, c.handle_top - c.handle_len + 15 - z0, c.handle_top - 15 - z0, ox + w + 12, cx, "270")
            dim_v(ax, 0, c.handle_top - c.handle_len + 15 - z0, ox - 12, cx, f"{c.handle_top - c.handle_len + 15 - z0:g}")
        if "LEFT" in name:
            rect(ax, cx - c.panel_w / 2, c.panel_top - c.panel_h - z0, c.panel_w, c.panel_h, ec=INK, lw=1, fc="#f2f5fa", fill=True)
            ax.text(cx, c.panel_top - c.panel_h / 2 - z0, "panel\nbox C3", ha="center", va="center", fontsize=6.5)
            dim_v(ax, 0, c.panel_top - c.panel_h - z0, ox + w + 12, cx + 55, f"{c.panel_top - c.panel_h - z0:g}")
    zb = c.t1_bolts[0][1] - z0
    zt = c.t1_bolts[-1][1] - z0
    zc = c.z_t1_top - c.t1_h - 25 - z0
    dim_v(ax, 0, Hc, -30, 0)
    dim_v(ax, 0, zb, -14, 25, f"{zb:g}")
    dim_v(ax, zb, zt, 172, 135, f"{zt - zb:g}")
    dim_v(ax, zc, zb, 186, 125, f"{zb - zc:g}")
    ax.text(0, -40, "Heights from column bottom (= top of flange; 112 above floor).  FRONT & BACK: 6x Ø10 for M8 rivet nuts "
            "(mark from T1), 2x Ø16 cable grommets 45 from centre.  Dashed = T1 head plate.", fontsize=7)
    ax.text(0, Hc + 40, "C1  COLUMN   2x U from steel t=1.5 -> box 160x120x1050   (faces unfolded, viewed from outside)",
            fontsize=9, weight="bold")
    save(fig, ax, "C1_column", ((-45, 700), (-55, Hc + 55)))


# ------------------------------------------------------------------ B2 box, C2 door, C3 panel, handle, cap, bush, guard
def small_parts():
    fig, ax = new(1, 1)
    # B2 top view
    rect(ax, 0, 0, 460, 360)
    rect(ax, 230 - 85, 180 - 65, 170, 130)
    dim_h(ax, 0, 460, -14, 0)
    dim_v(ax, 0, 360, -14, 0)
    dim_h(ax, 145, 315, 180 + 75, 180 + 65, "170")
    dim_v(ax, 115, 245, 145 - 10, 145, "130")
    ax.text(230, 60, "height 80, open bottom, sheet t=1.5\nfix to B1 with 4 angle tabs + M5", ha="center", fontsize=7)
    ax.text(0, 372, "B2  BALLAST BOX (top view)  qty 1", fontsize=8.5, weight="bold")
    # C2 door
    ox = 520
    rect(ax, ox, 0, 60, 300)   # drawn at half scale
    for sx in (5, 55):
        for sy in (5, 295):
            ax.add_patch(Circle((ox + sx, sy), 2.1, fill=False, ec=INK, lw=0.8))
    ax.text(ox + 30, 150, "120 x 600\n4x Ø4.2\n10 from edges\n(drawn 1:2)", ha="center", va="center", fontsize=6.5)
    ax.text(ox, 312, "C2  DOOR t=1.2  qty 1", fontsize=8.5, weight="bold")
    # C3 panel box
    ox2 = 620
    rect(ax, ox2, 0, 110, 180)
    rect(ax, ox2 + 115, 0, 60, 180)
    dim_h(ax, ox2, ox2 + 110, -14, 0)
    dim_h(ax, ox2 + 115, ox2 + 175, -14, 0)
    dim_v(ax, 0, 180, ox2 + 190, ox2 + 175)
    ax.text(ox2 + 55, 90, "front face\ncut-outs from\npurchased\ncomponents", ha="center", va="center", fontsize=6.5)
    ax.text(ox2 + 145, 90, "depth", ha="center", va="center", fontsize=6.5, rotation=90)
    ax.text(ox2, 192, "C3  PANEL BOX t=1.2  qty 1 (open to column)", fontsize=8.5, weight="bold")
    # handle
    oy = -170
    rect(ax, 0, oy, 300, 25, fc="#dfe6f0", fill=True)
    for x in (15, 285):
        rect(ax, x - 8, oy - 50, 16, 50)
    dim_h(ax, 0, 300, oy + 36, oy + 25)
    dim_h(ax, 15, 285, oy - 62, oy - 50, "270")
    dim_v(ax, oy - 50, oy, -12, 0, "50")
    ax.text(0, oy + 50, "HANDLE  tube Ø25 L300 + 2 standoffs Ø16 L50 (vertical, right face, top at 1000 from floor)", fontsize=8,
            weight="bold")
    # cap
    ox3 = 380
    rect(ax, ox3, oy - 30, 160, 120)
    dim_h(ax, ox3, ox3 + 160, oy - 42, oy - 30)
    dim_v(ax, oy - 30, oy + 90, ox3 + 172, ox3 + 160)
    ax.text(ox3, oy + 100, "COLUMN CAP t=4  qty 1", fontsize=8.5, weight="bold")
    # bush
    ox4 = 600
    rect(ax, ox4, oy, 10.2, 14, fc="#e8d39a", fill=True)
    ax.text(ox4 + 18, oy + 2, "BRONZE BUSH  bore Ø10 H7 / OD Ø14 h7\nlength 10.2 = channel 1 + bracket 4 + disc 5 + 0.2\n"
            "(bolt clamps the bush, arm turns freely)  qty 4", fontsize=7)
    # guard
    oy2 = -300
    ax.plot([0, 460, 460, 0, 0], [oy2, oy2, oy2 + 25, oy2 + 25, oy2], color=INK, lw=1)
    for x in range(40, 460, 60):
        ax.plot([x, x], [oy2, oy2 + 25], color=INK, lw=0.6)
    ax.text(0, oy2 + 35, "A3  LAMP GUARD  stainless wire Ø3, 50 x 920 (drawn 1:2), cross wires every 120, clip to channel lips  qty 4",
            fontsize=8, weight="bold")
    save(fig, ax, "small_parts", ((-30, 830), (oy2 - 20, 395)))


# ------------------------------------------------------------------ general arrangement
def general():
    fig, ax = new(1, 1)
    z_ax = c.z_axis
    # floor
    ax.plot([-1150, 1150], [0, 0], color=INK, lw=1)
    # casters
    for x in (-220, 220):
        ax.add_patch(Circle((x, 37.5), 37.5, fill=False, ec=INK, lw=0.8))
    rect(ax, -250, c.caster_h, 500, c.base_t, fc="#dfe6f0", fill=True)
    rect(ax, -230, c.z_base_top, 460, c.b2_h)
    rect(ax, -80, c.z_col0, 160, c.col_h)
    rect(ax, -c.t1_w / 2, c.z_t1_top - c.t1_h, c.t1_w, c.t1_h, fc="#eeeeee", fill=True)
    arm_len, e = c.arm_len, c.axis_from_end
    # right arm horizontal, left arm up
    rect(ax, c.hinge_dx - e, z_ax - 30, arm_len, 60, fc="#f0f0ff", fill=True)
    rect(ax, -c.hinge_dx - 30, z_ax - e, 60, arm_len, fc="#f0f0ff", fill=True)
    for s in (-1, 1):
        ax.add_patch(Circle((s * c.hinge_dx, z_ax), c.disc_d / 2, fill=False, ec=INK, lw=0.8))
    # dims
    top = z_ax - e + arm_len
    span = c.hinge_dx - e + arm_len
    dim_v(ax, 0, z_ax, -330, -c.hinge_dx - 30, f"{z_ax:g} hinge axis")
    dim_v(ax, 0, top, -420, -c.hinge_dx - 30, f"{top:g} arms up")
    dim_v(ax, 0, c.caster_h, -280, -250, f"{c.caster_h:g}")
    dim_v(ax, c.z_col0, c.z_col1, 240, 80, f"column {c.col_h:g}")
    dim_h(ax, -span, span, -80, -10, f"span with all arms horizontal {2*span:g}")
    dim_h(ax, -250, 250, -40, 0, "base 500")
    dim_h(ax, -c.hinge_dx, c.hinge_dx, z_ax + 110, z_ax, f"hinges {2*c.hinge_dx:g}")
    dim_h(ax, c.hinge_dx - e, c.hinge_dx - e + arm_len, z_ax + 60, z_ax + 30, f"arm {arm_len:g}")
    ax.plot([-span, -span], [-90, 0], color=DIMC, lw=0.5, ls=":")
    ax.text(-1000, top + 60, "GENERAL ARRANGEMENT - front view (right arm 90°, left arm 180°)", fontsize=10, weight="bold")
    save(fig, ax, "general_arrangement", ((-1050, 1100), (-110, top + 100)))


# ------------------------------------------------------------------ wiring
def wiring():
    fig, ax = new(1, 1)
    blocks = [("PLUG\n230V + PE", 0), ("FUSE\nT2A", 1), ("E-STOP\nNC", 2), ("KEY\nSWITCH", 3), ("TIMER\ndelay-on", 4),
              ("RELAY K1\n(PIR opens)", 5), ("4x BALLAST\n30W T8", 6), ("4x LAMP\nUV-C 30W", 7)]
    for txt, i in blocks:
        x = i * 95
        ax.add_patch(FancyBboxPatch((x, 0), 75, 40, boxstyle="round,pad=2", fc="#e8f1fa", ec="#2265a0", lw=1))
        ax.text(x + 37.5, 20, txt, ha="center", va="center", fontsize=7.5)
        if i < 7:
            ax.annotate("", (x + 93, 20), (x + 77, 20), arrowprops=dict(arrowstyle="->", lw=1))
    ax.add_patch(FancyBboxPatch((5 * 95, 75), 75, 34, boxstyle="round,pad=2", fc="#fff6e6", ec="#e6a23c", lw=1))
    ax.text(5 * 95 + 37.5, 92, "PIR\nsensor", ha="center", va="center", fontsize=7.5)
    ax.annotate("", (5 * 95 + 37.5, 43), (5 * 95 + 37.5, 73), arrowprops=dict(arrowstyle="->", lw=1, color="#e6a23c"))
    for txt, x in (("LED 'UV ON'\n(parallel)", 4 * 95), ("HOUR METER\n(parallel)", 6 * 95)):
        ax.add_patch(FancyBboxPatch((x, -70), 75, 34, boxstyle="round,pad=2", fc="#fdecec", ec="#d0232a", lw=1))
        ax.text(x + 37.5, -53, txt, ha="center", va="center", fontsize=7.5)
        ax.plot([x + 37.5, x + 37.5], [-2, -34], color="#d0232a", lw=1)
    ax.text(0, 130, "WIRING - single line.  PE (earth) to column, base, each arm.  Relay K1 latches OFF: restart only manually.",
            fontsize=8.5, weight="bold")
    save(fig, ax, "wiring", ((-10, 8 * 95), (-85, 145)))


if __name__ == "__main__":
    for f in (general, t1, h2, h1, a1, a2, b1, flange, column, small_parts, wiring):
        f()
    print(sorted(os.listdir(OUT)))
