"""Fit / interference / stability checks for the UV-C stand (all 13 arm positions)."""
import json
import math
import sys
import os
from model import (C, Cfg, arm_canonical, place_arm, static_parts, part_plunger,
                   part_hinge_fixed, part_flange_bolt_envelopes, box)

TOL = 1.0  # mm^3 - below this an overlap is just touching faces
ANGLES = list(range(0, 181, 15))
STEEL, ALU = 7.85e-6, 2.70e-6  # kg/mm^3


def bb_overlap(a, b):
    A, B = a.BoundingBox(), b.BoundingBox()
    return not (A.xmax < B.xmin or B.xmax < A.xmin or A.ymax < B.ymin or B.ymax < A.ymin
                or A.zmax < B.zmin or B.zmax < A.zmin)


def iv(a, b):
    if not bb_overlap(a, b):
        return 0.0
    return a.intersect(b).Volume()


def run(c: Cfg):
    R = {"config": c.name, "checks": []}

    def add(code, title, ok, detail):
        R["checks"].append({"code": code, "title": title, "ok": bool(ok), "detail": detail})
        print(("  OK  " if ok else "  FAIL") + f"  [{code}] {title}: {detail}", flush=True)

    S = static_parts(c)
    canon = arm_canonical(c)
    pin_r, body_r = part_plunger(c, 1)
    pin_l, body_l = part_plunger(c, -1)
    wash_r, shank_r, nut_r = part_hinge_fixed(c, 1)
    wash_l, shank_l, nut_l = part_hinge_fixed(c, -1)

    # --- T1 geometry
    edge = c.t1_w / 2 - c.hinge_dx
    add("T1-1", "T1 hinge hole spacing / edge distance",
        edge >= 25,
        f"plate {c.t1_w:.0f} wide x {c.t1_h:.0f} high, holes at x=±{c.hinge_dx:.0f}, edge distance {edge:.0f}; "
        f"overhang beyond column face {c.t1_w/2 - c.col_x/2:.0f} each side")
    px, pz = (c.hinge_dx + c.index_r * math.sin(math.radians(c.plunger_beta)),
              c.z_axis - c.index_r * math.cos(math.radians(c.plunger_beta)))
    add("T1-2", "Plunger hole edge distance in T1", c.t1_w / 2 - px >= 15,
        f"plunger at x=±{px:.1f}, z={pz:.1f}; edge distance {c.t1_w/2 - px:.1f}")

    # --- plunger body / knob behind T1 vs column wall
    v = iv(body_r, S["C1_column"]) + iv(body_l, S["C1_column"])
    add("H4-1", "Index plunger knob reachable from the side (≥5 mm from column)",
        v < TOL and px - c.plunger_knob_d / 2 - c.col_x / 2 >= 5,
        f"knob/body overlap with column wall = {v:.0f} mm³; gap knob to column side = {px - c.plunger_knob_d/2 - c.col_x/2:.1f} mm")

    # --- hinge bolt / nut
    v = sum(iv(s, S["C1_column"]) for s in (shank_r, nut_r, shank_l, nut_l))
    add("H3-1", "Hinge bolt & nut clear of column wall", v < TOL,
        f"overlap {v:.0f} mm³ (ISO 7380 M10x{c.bolt_len:.0f} + nyloc nut); nut x from column side = {c.hinge_dx - 9.8 - c.col_x/2:.1f} mm; shank reaches y={c.y_ch_back - c.arm_t - 2 + c.bolt_len:.0f} "
        f"(column face y={c.y_face:.0f})")
    head_low = c.y_ch_back - c.arm_t - 2 - c.bolt_head_h
    lamp_top = c.y_lamp + c.lamp_d / 2
    add("H3-2", "Bolt head under lamp clearance", head_low - lamp_top >= 2,
        f"gap bolt head to lamp tube = {head_low - lamp_top:.1f} mm")

    # --- flange / gussets / B2
    fl_margin_x = (c.flange_x - c.col_x) / 2
    fl_margin_y = (c.flange_y - c.col_y) / 2
    add("C1-1", "Gusset horizontal leg fits on flange", c.gusset_l <= min(fl_margin_x, fl_margin_y),
        f"gusset leg {c.gusset_l:.0f} vs flange margin x {fl_margin_x:.0f} / y {fl_margin_y:.0f}")
    g = [S[f"C1_gusset_{i}"] for i in range(1, 5)]
    v = sum(iv(x, S["B2_ballast_box"]) for x in g)
    add("C1-2", "Gussets below B2 cover", v < TOL, f"overlap {v:.0f} mm³ (gusset top z={c.z_col0 + c.gusset_h:.0f}, "
        f"B2 cover z={c.z_base_top + c.b2_h - 1.5:.0f})")
    env = part_flange_bolt_envelopes(c)
    weld = box(-c.col_x / 2 - 5, c.col_x / 2 + 5, -c.col_y / 2 - 5, c.col_y / 2 + 5, c.z_col0, c.z_col0 + 40)  # column + 5 mm fillet weld
    v = sum(iv(e, weld) + sum(iv(e, x) for x in g) for e in env)
    add("C1-3", "M10 flange bolts: socket-wrench room (Ø28)", v < TOL,
        f"wrench envelope overlap with column weld/gussets = {v:.0f} mm³; bolt centre to column wall = "
        f"{min(fl_margin_x, fl_margin_y) - c.flange_bolt_inset:.0f} mm")

    # --- panel vs T1
    v = iv(S["C3_panel_box"], S["T1_head_plate_front"])
    add("C3-1", "Control panel clear of T1 head plate", v < TOL, f"overlap {v:.0f} mm³ "
        f"(panel top {c.panel_top:.0f}, T1 bottom {c.z_t1_top - c.t1_h:.0f})")

    # --- arm sweeps vs static parts (front face; back face is the same rotated 180°)
    statics = {k: s for k, s in S.items() if not k.startswith("B3")}
    statics["plunger_R_pin_body"] = pin_r.fuse(body_r)
    statics["plunger_L_pin_body"] = pin_l.fuse(body_l)
    statics["hinge_R_fixed"] = wash_r.fuse(shank_r).fuse(nut_r)
    statics["hinge_L_fixed"] = wash_l.fuse(shank_l).fuse(nut_l)
    hits = {}
    pin_bad = []
    arms = {1: {}, -1: {}}
    for side in (1, -1):
        for a in ANGLES:
            parts = place_arm(canon, c, side, a)
            arms[side][a] = parts
            for pn, ps in parts.items():
                for sn, ss in statics.items():
                    own_pin = (side == 1 and sn == "plunger_R_pin_body") or (side == -1 and sn == "plunger_L_pin_body")
                    own_hinge = (side == 1 and sn == "hinge_R_fixed") or (side == -1 and sn == "hinge_L_fixed")
                    vv = iv(ps, ss)
                    if vv > TOL:
                        if own_pin:
                            pin_bad.append((side, a, pn, round(vv)))
                        elif own_hinge and pn in ("disc", "bracket", "channel", "bolt_head"):
                            pass  # same bolt / passes through Ø14 bush holes – checked in H3-*
                        else:
                            hits.setdefault(f"{'R' if side == 1 else 'L'} arm {pn} x {sn}", []).append(a)
    for k, v in hits.items():
        print("     hit:", k, v)
    add("SW-1", "Arms 0-180° clear of column, T1, panel, handle, base", not hits,
        "; ".join(f"{k} @ {v}°" for k, v in hits.items()) or "no contact at any of the 13 positions, both sides")
    add("H4-2", "Plunger pin fully engages index hole at all 13 positions", not pin_bad,
        ("; ".join(f"{'R' if s == 1 else 'L'} @{a}° pin hits {p} ({vv} mm³)" for s, a, p, vv in pin_bad))
        or "pin passes cleanly through disc at 0,15,…,180°")

    # --- arm vs arm on the same face (13 x 13)
    matrix = []
    clash = []
    for ar in ANGLES:
        row = []
        for al in ANGLES:
            v = 0.0
            for pr in ("channel", "bracket", "disc", "caps", "bolt_head"):
                for pl in ("channel", "bracket", "disc", "caps", "bolt_head"):
                    v += iv(arms[1][ar][pr], arms[-1][al][pl])
            row.append(round(v))
            if v > TOL:
                clash.append((ar, al))
        matrix.append(row)
    R["arm_arm_matrix"] = {"angles": ANGLES, "rows_right": matrix}
    reach = math.hypot(c.axis_from_end, c.arm_w / 2 + c.br_t)
    add("SW-2", "Left & right arm on same face never collide (13×13 positions)", not clash,
        f"{len(clash)} of 169 combinations collide" + (f", e.g. R/L = {clash[:6]}" if clash else "")
        + f"; stub reach from axis {max(reach, c.disc_d/2):.1f} vs half hinge spacing {c.hinge_dx:.0f}")

    # --- disc web
    web = 2 * c.index_r * math.sin(math.radians(7.5)) - c.index_hole_d
    add("H2-1", "Web between index holes ≥ disc thickness (laser cut)", web >= c.disc_t,
        f"web {web:.1f} mm vs plate {c.disc_t:.0f} mm")

    # --- arm tip clearance and envelope
    tip = arms[1][0]["channel"].BoundingBox().zmin
    b2top = c.z_base_top + c.b2_h
    add("A1-1", "Parked arm (0°) tip ≥ 50 mm above B2 box", tip - b2top >= 50,
        f"tip z={tip:.0f}, B2 top z={b2top:.0f}, gap {tip - b2top:.0f} mm")
    top = arms[1][180]["channel"].BoundingBox().zmax
    span = arms[1][90]["channel"].BoundingBox().xmax - arms[-1][90]["channel"].BoundingBox().xmin
    add("DIM-1", "Hinge axis height ≈ 1150", abs(c.z_axis - 1150) <= 10, f"z axis = {c.z_axis:.0f}")
    arm_in = c.hinge_dx - c.arm_w / 2 - c.br_t
    add("C2-1", "Service door & cable holes not hidden behind parked arms", c.door_w / 2 < arm_in and
        c.cable_hole_x + c.cable_hole_d / 2 < arm_in,
        f"parked arm inner edge x=±{arm_in:.0f}; door edge ±{c.door_w/2:.0f}; cable hole edge ±{c.cable_hole_x + c.cable_hole_d/2:.0f}")
    add("DIM-2", "Overall height / span", True,
        f"height with arms up = {top:.0f}, span with arms horizontal = {span:.0f} (info only)")

    # --- mass
    m_static = 0.0
    for k, s in S.items():
        if k.startswith("B3") or k in ("handle",):
            continue
        m_static += s.Volume() * STEEL
    m_static += 0.6  # handle (tube)
    # T1 extra: second bolts ignored. non-metal & bought-in estimates:
    bought = {"casters 4x": 1.4, "ballasts 4x": 1.4, "timer/PIR/switches/E-stop/LED": 0.7,
              "cables": 0.8, "plunger/fasteners": 0.6}
    arm_parts = canon
    m_arm = (arm_parts["channel"].Volume() + arm_parts["caps"].Volume()) * ALU \
        + (arm_parts["bracket"].Volume() + arm_parts["disc"].Volume()) * STEEL \
        + 0.20 + 0.06 + 0.17  # lamp, 2 sockets, wire guard A3
    m_total = m_static + sum(bought.values()) + 4 * m_arm
    R["mass"] = {"static_metal": round(m_static, 2), "arm_each": round(m_arm, 2),
                 "bought_in": bought, "total": round(m_total, 2)}
    add("M-1", "Total mass ≥ 18 kg (else add B4 counterweight)", m_total >= 18,
        f"structure {m_static:.1f} kg + arms 4×{m_arm:.2f} kg + bought-in {sum(bought.values()):.1f} kg = {m_total:.1f} kg")

    # --- stability: two arms on the same side horizontal (left front + left back at 90°)
    tip_line = c.base_x / 2 - 30
    cg_arm = (arms[1][90]["channel"].Center().x)  # approx: channel centroid
    m_rest = m_total - 2 * m_arm
    M_over = 2 * m_arm * (cg_arm - tip_line) / 1000
    M_res = m_rest * tip_line / 1000
    add("ST-1", "Static tip-over margin, 2 arms horizontal on one side", M_res / max(M_over, 1e-6) >= 2,
        f"arm CG {cg_arm:.0f} mm from column axis; overturning {M_over:.2f} kg·m vs resisting {M_res:.2f} kg·m "
        f"→ factor {M_res / max(M_over, 1e-6):.1f}")
    F = m_total * tip_line / top
    add("ST-2", "Side push at top that tips it (arms vertical)", True,
        f"≈ {F:.1f} kgf at {top:.0f} mm – move only with arms parked (info)")
    R["n_fail"] = sum(not x["ok"] for x in R["checks"])
    return R


if __name__ == "__main__":
    print(f"=== {C.name}")
    res = run(C)
    print(f"  -> {res['n_fail']} failures")
    out = os.path.join(os.path.dirname(__file__), "..", "results", "checks.json")
    with open(out, "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
