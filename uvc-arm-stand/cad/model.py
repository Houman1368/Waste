"""Parametric 3D model of the 4-arm UV-C stand (metal parts) - final design.

Coordinates (mm): x = across the front face (500 side of base), y = depth
(front face of column at y = -60), z = up from the floor. Column axis at x=y=0.

Arm angle convention: 0 = arm down beside column (parked), 90 = horizontal,
180 = vertical up. Right arms swing to +x, left arms to -x.
All dimensions live in `Cfg`; change them there and re-run checks.py / export.py.
"""
from dataclasses import dataclass
import math
import cadquery as cq

V = cq.Vector


# ---------------------------------------------------------------- helpers
def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_y(r, y0, y1, x=0.0, z=0.0):
    """Cylinder along y from y0 to y1."""
    lo, hi = min(y0, y1), max(y0, y1)
    return cq.Solid.makeCylinder(r, hi - lo, V(x, lo, z), V(0, 1, 0))


def cyl_x(r, x0, x1, y=0.0, z=0.0):
    lo, hi = min(x0, x1), max(x0, x1)
    return cq.Solid.makeCylinder(r, hi - lo, V(lo, y, z), V(1, 0, 0))


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return cq.Solid.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


def hex_y(af, y0, y1, x=0.0, z=0.0):
    """Hex prism (across-flats af) along y."""
    lo, hi = min(y0, y1), max(y0, y1)
    pl = cq.Plane(origin=(x, lo, z), xDir=(1, 0, 0), normal=(0, 1, 0))
    return cq.Workplane(pl).polygon(6, af / math.cos(math.pi / 6)).extrude(hi - lo).val()


def fuse(*shapes):
    shapes = [s for s in shapes if s is not None]
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.clean()


def cut(base, *tools):
    for t in tools:
        base = base.cut(t)
    return base.clean()


# ---------------------------------------------------------------- design parameters
@dataclass
class Cfg:
    name: str = "UVC_stand"
    caster_h: float = 100.0          # Ø75 swivel caster mounting height (measure the real caster!)
    # base B1 / ballast box B2
    base_x: float = 500.0
    base_y: float = 400.0
    base_t: float = 6.0
    b2_x: float = 460.0
    b2_y: float = 360.0
    b2_h: float = 80.0
    # column C1
    col_x: float = 160.0             # front/back faces are the 160 faces
    col_y: float = 120.0
    col_h: float = 1050.0
    col_t: float = 1.5
    cap_t: float = 4.0
    flange_x: float = 260.0
    flange_y: float = 220.0
    flange_t: float = 6.0
    flange_bolt_inset: float = 25.0  # M10 bolt centre from flange edge
    gusset_h: float = 60.0           # vertical leg (stays under B2 cover)
    gusset_l: float = 50.0           # horizontal leg (= flange margin)
    gusset_t: float = 4.0
    cable_hole_d: float = 16.0       # grommet holes for arm cables, front & back face below T1
    cable_hole_x: float = 45.0
    # head plate T1 (front + back)
    t1_w: float = 250.0
    t1_h: float = 160.0
    t1_t: float = 4.0
    t1_top_above_col: float = 28.0   # T1 stands above the column top -> hinge axis at 1150
    hinge_dx: float = 100.0          # hinge axes 200 apart, outside the column outline
    hinge_from_top: float = 40.0
    # index disc H2 / index plunger H4 (spring loaded, M12x1.5, pin Ø6, with rest position)
    disc_d: float = 130.0
    disc_t: float = 5.0
    index_r: float = 50.0
    index_hole_d: float = 6.2        # Ø6 H8 after reaming -> minimal play
    plunger_beta: float = 0.0        # plunger straight below the hinge axis
    plunger_nut_af: float = 18.0     # M12 weld nut on back of T1
    plunger_knob_d: float = 25.0
    pin_d: float = 6.0
    pin_protrusion: float = 8.0      # pin length in front of T1 face
    teflon_t: float = 1.0
    # bracket H1 (U around back of channel, bolted with 4 x M5 through the side walls)
    br_len: float = 60.0
    br_t: float = 4.0
    br_leg: float = 26.0
    br_edge_from_end: float = 10.0   # hinge axis 40 from the arm end
    br_bolt_dz: float = 18.0         # M5 holes at ±18 along the arm, 13 from channel floor
    # arm A1 (aluminium 1 mm, blank 170 x 950)
    arm_len: float = 950.0
    arm_w: float = 60.0
    arm_d: float = 45.0
    arm_lip: float = 10.0
    arm_t: float = 1.0
    lamp_d: float = 26.0
    lamp_axis_from_floor: float = 25.0
    socket_gap: float = 908.0
    grommet_from_end: float = 90.0   # Ø10 cable grommet in the side wall
    # hinge bolt H3: ISO 7380 M10x30 (head inside channel) + flanged bronze bush + nyloc nut behind T1
    bolt_len: float = 30.0
    bolt_head_h: float = 5.5
    bolt_head_d: float = 17.5
    nut_h: float = 10.0
    # control panel C3 (left side face), push handle (right side face), service door C2 (back face)
    panel_w: float = 110.0
    panel_d: float = 60.0
    panel_h: float = 180.0
    panel_top: float = 990.0
    handle_len: float = 300.0
    handle_top: float = 1000.0
    handle_proj: float = 50.0
    door_w: float = 120.0
    door_h: float = 600.0
    door_z0: float = 300.0

    # derived ---------------------------------------------------------
    @property
    def z_base_top(self):
        return self.caster_h + self.base_t

    @property
    def z_col0(self):
        return self.z_base_top + self.flange_t

    @property
    def z_col1(self):
        return self.z_col0 + self.col_h

    @property
    def z_t1_top(self):
        return self.z_col1 + self.t1_top_above_col

    @property
    def z_axis(self):
        return self.z_t1_top - self.hinge_from_top

    @property
    def y_face(self):  # front column face
        return -self.col_y / 2

    @property
    def y_t1_front(self):
        return self.y_face - self.t1_t

    @property
    def y_disc0(self):
        return self.y_t1_front - self.teflon_t

    @property
    def y_disc1(self):
        return self.y_disc0 - self.disc_t

    @property
    def y_ch_back(self):  # outer face of channel floor
        return self.y_disc1 - self.br_t

    @property
    def axis_from_end(self):
        return self.br_edge_from_end + self.br_len / 2

    @property
    def y_lamp(self):
        return self.y_ch_back - self.lamp_axis_from_floor

    @property
    def t1_bolts(self):
        """Countersunk M8 (flush) into M8 rivet nuts in the column face: (x, z)."""
        z0 = self.z_t1_top - self.t1_h
        return [(x, z0 + 20) for x in (-55, -20, 20, 55)] + [(x, self.z_col1 - 20) for x in (-20, 20)]


C = Cfg()


# ---------------------------------------------------------------- parts
def part_base(c: Cfg):
    hx, hy = c.base_x / 2, c.base_y / 2
    b1 = box(-hx, hx, -hy, hy, c.caster_h, c.z_base_top)
    holes = [cyl_z(5.5, c.caster_h - 1, c.z_base_top + 1, sx * (c.flange_x / 2 - c.flange_bolt_inset),
                   sy * (c.flange_y / 2 - c.flange_bolt_inset)) for sx in (-1, 1) for sy in (-1, 1)]
    return cut(b1, *holes)


def part_casters(c: Cfg):
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (c.base_x / 2 - 30), sy * (c.base_y / 2 - 30)
            out.append(fuse(cq.Solid.makeCylinder(37.5, 28, V(x - 14, y, 37.5), V(1, 0, 0)),
                            box(x - 30, x + 30, y - 30, y + 30, c.caster_h - 25, c.caster_h)))
    return out


def part_b2(c: Cfg):
    hx, hy, t = c.b2_x / 2, c.b2_y / 2, 1.5
    z0, z1 = c.z_base_top, c.z_base_top + c.b2_h
    shell = cut(box(-hx, hx, -hy, hy, z0, z1), box(-hx + t, hx - t, -hy + t, hy - t, z0 - 1, z1 - t))
    hole = box(-c.col_x / 2 - 5, c.col_x / 2 + 5, -c.col_y / 2 - 5, c.col_y / 2 + 5, z1 - 5, z1 + 5)
    return cut(shell, hole)


def part_flange(c: Cfg):
    fx, fy = c.flange_x / 2, c.flange_y / 2
    f = box(-fx, fx, -fy, fy, c.z_base_top, c.z_col0)
    holes = [cyl_z(5.5, c.z_base_top - 1, c.z_col0 + 1, sx * (fx - c.flange_bolt_inset), sy * (fy - c.flange_bolt_inset))
             for sx in (-1, 1) for sy in (-1, 1)]
    return cut(f, *holes)


def part_gussets(c: Cfg):
    """4 triangular gussets at mid-faces, standing on the flange against the column."""
    out = []
    z0 = c.z_col0
    for ang, wall in ((0, c.col_x / 2), (180, c.col_x / 2), (90, c.col_y / 2), (270, c.col_y / 2)):
        pl = cq.Plane(origin=(0, c.gusset_t / 2, 0), xDir=(1, 0, 0), normal=(0, -1, 0))  # local v = +z
        g = (cq.Workplane(pl).polyline([(wall, z0), (wall + c.gusset_l, z0), (wall, z0 + c.gusset_h)]).close()
             .extrude(c.gusset_t).val())
        out.append(g.rotate(V(0, 0, 0), V(0, 0, 1), ang))
    return out


def part_flange_bolt_envelopes(c: Cfg):
    """Ø28 socket-wrench envelope, 40 high, over each M10 flange bolt."""
    fx, fy = c.flange_x / 2, c.flange_y / 2
    return [cyl_z(14, c.z_col0, c.z_col0 + 40, sx * (fx - c.flange_bolt_inset), sy * (fy - c.flange_bolt_inset))
            for sx in (-1, 1) for sy in (-1, 1)]


def part_column(c: Cfg):
    hx, hy, t = c.col_x / 2, c.col_y / 2, c.col_t
    tube = cut(box(-hx, hx, -hy, hy, c.z_col0, c.z_col1), box(-hx + t, hx - t, -hy + t, hy - t, c.z_col0 - 1, c.z_col1 + 1))
    zc = c.z_t1_top - c.t1_h - 25
    holes = [cyl_y(c.cable_hole_d / 2, -hy - 1, hy + 1, sx * c.cable_hole_x, zc) for sx in (-1, 1)]
    holes += [cyl_y(5, -hy - 1, hy + 1, x, z) for x, z in c.t1_bolts]   # Ø10 for M8 rivet nuts
    cap = box(-hx, hx, -hy, hy, c.z_col1, c.z_col1 + c.cap_t)
    return cut(tube, *holes), cap


def part_door(c: Cfg):
    return box(-c.door_w / 2, c.door_w / 2, c.col_y / 2, c.col_y / 2 + 1.2, c.door_z0, c.door_z0 + c.door_h)


def part_panel(c: Cfg):
    """Control panel box on the LEFT side face, open toward the column."""
    z1, z0, t, x0 = c.panel_top, c.panel_top - c.panel_h, 1.2, -c.col_x / 2
    return cut(box(x0 - c.panel_d, x0, -c.panel_w / 2, c.panel_w / 2, z0, z1),
               box(x0 - c.panel_d + t, x0 + 1, -c.panel_w / 2 + t, c.panel_w / 2 - t, z0 + t, z1 - t))


def part_handle(c: Cfg):
    """300 mm vertical push handle (Ø25 bar on two standoffs) on the RIGHT side face."""
    x, z1 = c.col_x / 2 + c.handle_proj, c.handle_top
    z0 = z1 - c.handle_len
    return fuse(cyl_z(12.5, z0, z1, x, 0),
                cyl_x(8, c.col_x / 2, x, 0, z1 - 15),
                cyl_x(8, c.col_x / 2, x, 0, z0 + 15))


def plunger_xz(c: Cfg, side):
    b = math.radians(c.plunger_beta)
    return side * (c.hinge_dx + c.index_r * math.sin(b)), c.z_axis - c.index_r * math.cos(b)


def part_t1(c: Cfg):
    """Front head plate T1 (back one = this rotated 180° about z)."""
    hw = c.t1_w / 2
    z1, z0 = c.z_t1_top, c.z_t1_top - c.t1_h
    p = box(-hw, hw, c.y_t1_front, c.y_face, z0, z1)
    holes = []
    for s in (-1, 1):
        holes.append(cyl_y(5.25, c.y_face + 1, c.y_t1_front - 1, s * c.hinge_dx, c.z_axis))   # M10
        px, pz = plunger_xz(c, s)
        holes.append(cyl_y(6.5, c.y_face + 1, c.y_t1_front - 1, px, pz))                   # pin Ø6 + clearance
    for x, z in c.t1_bolts:
        holes.append(cyl_y(4.5, c.y_face + 1, c.y_t1_front - 1, x, z))                      # Ø9, countersunk
    return cut(p, *holes)


def part_plunger(c: Cfg, side):
    """Index plunger: pin in front of T1; weld nut, threaded body + pull knob behind T1."""
    px, pz = plunger_xz(c, side)
    pin = cyl_y(c.pin_d / 2, c.y_t1_front, c.y_t1_front - c.pin_protrusion, px, pz)
    body = fuse(hex_y(c.plunger_nut_af, c.y_face, c.y_face + 10, px, pz),          # M12 weld nut
                cyl_y(6, c.y_face + 10, c.y_face + 28, px, pz),                      # threaded body
                cyl_y(c.plunger_knob_d / 2, c.y_face + 28, c.y_face + 46, px, pz))   # pull knob
    return pin, body


def part_hinge_fixed(c: Cfg, side):
    """Non-rotating hinge parts: teflon washer, bolt shank, nyloc nut behind T1."""
    x, z = side * c.hinge_dx, c.z_axis
    washer = cut(cyl_y(15, c.y_t1_front, c.y_disc0, x, z), cyl_y(7, c.y_t1_front + 1, c.y_disc0 - 1, x, z))
    head_face = c.y_ch_back - c.arm_t - 2.0          # under-head face (after 2 mm washer) inside channel
    shank = cyl_y(5, head_face, head_face + c.bolt_len, x, z)
    nut = hex_y(17, c.y_face, c.y_face + c.nut_h, x, z)
    return washer, shank, nut


# ---------------------------------------------------------------- arm (rotating)
def arm_canonical(c: Cfg):
    """Right arm at angle 0 (hanging down), hinge axis at x=0, z=0. Returns dict of solids."""
    e = c.axis_from_end
    ztop, zbot = e, e - c.arm_len
    yb = c.y_ch_back
    hw, t = c.arm_w / 2, c.arm_t
    ch = fuse(box(-hw, hw, yb - t, yb, zbot, ztop),
              box(-hw, -hw + t, yb - c.arm_d, yb, zbot, ztop),
              box(hw - t, hw, yb - c.arm_d, yb, zbot, ztop),
              box(-hw, -hw + c.arm_lip, yb - c.arm_d, yb - c.arm_d + t, zbot, ztop),
              box(hw - c.arm_lip, hw, yb - c.arm_d, yb - c.arm_d + t, zbot, ztop))
    y_m5 = yb - 13
    ch = cut(ch, cyl_y(7, yb + 1, yb - t - 1, 0, 0),                                   # Ø14 bush hole
             *[cyl_x(2.75, -hw - 1, hw + 1, y_m5, dz) for dz in (-c.br_bolt_dz, c.br_bolt_dz)],
             cyl_x(5, hw - 2, hw + 1, yb - 22, ztop - c.grommet_from_end))             # cable grommet Ø10
    caps = [box(-hw + t, hw - t, yb - c.arm_d + t, yb - t, ztop - t, ztop),
            box(-hw + t, hw - t, yb - c.arm_d + t, yb - t, zbot, zbot + t)]
    sock_d = (c.arm_len - 2 * t - c.socket_gap) / 2
    sockets = [box(-15, 15, yb - 40, yb - t, ztop - t - sock_d, ztop - t),
               box(-15, 15, yb - 40, yb - t, zbot + t, zbot + t + sock_d)]
    lamp = cq.Solid.makeCylinder(c.lamp_d / 2, c.socket_gap - 4, V(0, c.y_lamp, ztop - t - sock_d - 2), V(0, 0, -1))
    # bracket H1 (U around back of channel)
    bt, bl = c.br_t, c.br_len
    bw = hw + bt
    br = fuse(box(-bw, bw, c.y_disc1 - bt, c.y_disc1, -bl / 2, bl / 2),
              box(-bw, -hw, yb - c.br_leg, yb, -bl / 2, bl / 2),
              box(hw, bw, yb - c.br_leg, yb, -bl / 2, bl / 2))
    br = cut(br, cyl_y(7, c.y_disc1 + 1, yb - 1, 0, 0),
             *[cyl_x(2.75, -bw - 1, bw + 1, y_m5, dz) for dz in (-c.br_bolt_dz, c.br_bolt_dz)])
    # disc H2 with centre hole + 13 index holes
    disc = cyl_y(c.disc_d / 2, c.y_disc0, c.y_disc1)
    holes = [cyl_y(7, c.y_disc0 + 1, c.y_disc1 - 1)]
    for k in range(13):
        g = math.radians(c.plunger_beta - 15 * k)
        holes.append(cyl_y(c.index_hole_d / 2, c.y_disc0 + 1, c.y_disc1 - 1,
                           c.index_r * math.sin(g), -c.index_r * math.cos(g)))
    disc = cut(disc, *holes)
    # button-head bolt + washer inside channel
    head = fuse(cyl_y(10, yb - t, yb - t - 2), cyl_y(c.bolt_head_d / 2, yb - t - 2, yb - t - 2 - c.bolt_head_h))
    return {"channel": ch, "caps": fuse(*caps), "sockets": fuse(*sockets), "lamp": lamp,
            "bracket": br, "disc": disc, "bolt_head": head}


def place_arm(canon: dict, c: Cfg, side: int, alpha: float):
    out = {}
    for k, s in canon.items():
        s2 = s if side == 1 else s.mirror("YZ", V(0, 0, 0))
        s2 = s2.rotate(V(0, 0, 0), V(0, 1, 0), -side * alpha)
        out[k] = s2.translate(V(side * c.hinge_dx, 0, c.z_axis))
    return out


def rot180(s):
    return s.rotate(V(0, 0, 0), V(0, 0, 1), 180)


# ---------------------------------------------------------------- full static set
def static_parts(c: Cfg):
    col, cap = part_column(c)
    p = {
        "B1_base_plate": part_base(c),
        "B2_ballast_box": part_b2(c),
        "C1_column": col,
        "C1_top_cap": cap,
        "C1_flange": part_flange(c),
        "C2_service_door": part_door(c),
        "C3_panel_box": part_panel(c),
        "handle": part_handle(c),
        "T1_head_plate_front": part_t1(c),
        "T1_head_plate_back": rot180(part_t1(c)),
    }
    screws = fuse(*[cyl_y(4.5, c.y_face, c.y_t1_front, x, z) for x, z in c.t1_bolts])   # flush countersunk M8
    p["T1_screws_front"] = screws
    p["T1_screws_back"] = rot180(screws)
    for i, g in enumerate(part_gussets(c)):
        p[f"C1_gusset_{i+1}"] = g
    for i, cs in enumerate(part_casters(c)):
        p[f"B3_caster_{i+1}"] = cs
    return p
