"""Parametric 3D model of the 4-arm UV-C stand (metal parts).

Coordinates (mm): x = across the front face (500 side of base), y = depth
(front face of column at y = -60), z = up from the floor. Column axis at x=y=0.

Arm angle convention (from the plan): 0 = arm down beside column (parked),
90 = horizontal, 180 = vertical up. Right arms swing to +x, left arms to -x.

Two configurations:
  V1 - exactly as the PDF plan (with the one consistent reading where needed)
  V2 - corrected design that passes all fit checks
"""
from dataclasses import dataclass, field, replace
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


# ---------------------------------------------------------------- config
@dataclass
class Cfg:
    name: str
    caster_h: float = 100.0          # Ø75 swivel caster mounting height (assumed)
    base_x: float = 500.0
    base_y: float = 400.0
    base_t: float = 6.0
    b2_x: float = 460.0
    b2_y: float = 360.0
    b2_h: float = 80.0
    col_x: float = 160.0             # front/back faces are the 160 faces
    col_y: float = 120.0
    col_h: float = 1050.0
    col_t: float = 1.5
    cap_t: float = 4.0
    flange_x: float = 200.0
    flange_y: float = 160.0
    flange_t: float = 6.0
    flange_bolt_inset: float = 10.0  # bolt centre from flange edge
    gusset_h: float = 100.0          # vertical leg
    gusset_l: float = 100.0          # horizontal leg
    gusset_t: float = 4.0
    # head plate T1
    t1_w: float = 220.0
    t1_h: float = 160.0
    t1_t: float = 4.0
    t1_top_above_col: float = 0.0    # T1 top relative to column body top
    hinge_dx: float = 70.0           # hinge axis x from column centre (140 apart)
    hinge_from_top: float = 40.0
    # index disc H2 / plunger H4
    disc_d: float = 110.0
    disc_t: float = 5.0
    index_r: float = 40.0
    index_hole_d: float = 6.5
    plunger_beta: float = 0.0        # plunger direction from hinge (arm-angle convention)
    plunger_behind: bool = True      # plunger body/knob behind T1 (only option with disc in front)
    pin_d: float = 6.0
    pin_protrusion: float = 8.0      # pin length in front of T1 face
    teflon_t: float = 1.0
    # bracket H1
    br_len: float = 60.0
    br_t: float = 4.0
    br_leg: float = 26.0
    br_edge_from_end: float = 50.0
    br_chamfer: float = 0.0
    # arm A1
    arm_len: float = 950.0
    arm_w: float = 60.0
    arm_d: float = 45.0
    arm_lip: float = 10.0
    arm_t: float = 1.0
    lamp_d: float = 26.0
    lamp_axis_from_floor: float = 25.0
    socket_gap: float = 908.0
    # hinge bolt
    bolt: str = "M10x60 hex, head inside channel, nut behind T1"
    bolt_len: float = 60.0
    bolt_head_h: float = 6.4
    bolt_head_af: float = 16.0
    nut_h: float = 10.0
    weld_nut_relief: float = 0.0     # Ø of relief hole in column wall behind hinge (0 = none)
    # panel / handle (C3)
    panel_face: str = "front"
    panel_w: float = 110.0
    panel_d: float = 60.0
    panel_h: float = 180.0
    panel_top: float = 1050.0
    handle_face: str = "front"
    handle_len: float = 300.0
    handle_proj: float = 50.0
    # service door C2 (back face)
    door_z0: float = 300.0
    notes: list = field(default_factory=list)

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


V1 = Cfg(name="V1_as_drawn")

V2 = replace(
    V1,
    name="V2_corrected",
    flange_x=260.0, flange_y=220.0, flange_bolt_inset=25.0,
    gusset_h=60.0, gusset_l=50.0,
    hinge_dx=95.0,                    # hinges outside the column outline -> nut & plunger reachable from the side
    t1_w=240.0, t1_top_above_col=1150.0 + 40.0 - V1.z_col1,  # T1 stands 28 above column top -> axis at 1150
    disc_d=130.0, index_r=50.0,
    plunger_beta=0.0,
    br_edge_from_end=10.0,
    bolt="ISO 7380 M10x30 button head inside channel + nyloc nut behind T1 (outside column)",
    bolt_len=30.0, bolt_head_h=5.5, bolt_head_af=17.5, nut_h=10.0,
    panel_face="right", panel_top=990.0,
    handle_face="right",
)


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
    """M10 nut (17 AF, h8) on flange + Ø28 socket-wrench envelope 40 high."""
    fx, fy = c.flange_x / 2, c.flange_y / 2
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (fx - c.flange_bolt_inset), sy * (fy - c.flange_bolt_inset)
            out.append(cyl_z(14, c.z_col0, c.z_col0 + 40, x, y))
    return out


def part_column(c: Cfg):
    hx, hy, t = c.col_x / 2, c.col_y / 2, c.col_t
    tube = cut(box(-hx, hx, -hy, hy, c.z_col0, c.z_col1), box(-hx + t, hx - t, -hy + t, hy - t, c.z_col0 - 1, c.z_col1 + 1))
    if c.weld_nut_relief:
        for side in (1, -1):
            for sx in (-1, 1):
                tube = tube.cut(cyl_y(c.weld_nut_relief / 2, -side * (hy + 1), -side * (hy - t - 1), sx * c.hinge_dx, c.z_axis))
    cap = box(-hx, hx, -hy, hy, c.z_col1, c.z_col1 + c.cap_t)
    return tube.clean(), cap


def part_door(c: Cfg):
    return box(-70, 70, c.col_y / 2, c.col_y / 2 + 1.2, c.door_z0, c.door_z0 + 600)


def part_panel(c: Cfg):
    z1, z0 = c.panel_top, c.panel_top - c.panel_h
    t = 1.2  # sheet box, open toward the column
    if c.panel_face == "front":
        return cut(box(-c.panel_w / 2, c.panel_w / 2, c.y_face - c.panel_d, c.y_face, z0, z1),
                   box(-c.panel_w / 2 + t, c.panel_w / 2 - t, c.y_face - c.panel_d + t, c.y_face + 1, z0 + t, z1 - t))
    return cut(box(c.col_x / 2, c.col_x / 2 + c.panel_d, -c.panel_w / 2, c.panel_w / 2, z0, z1),
               box(c.col_x / 2 - 1, c.col_x / 2 + c.panel_d - t, -c.panel_w / 2 + t, c.panel_w / 2 - t, z0 + t, z1 - t))


def part_handle(c: Cfg):
    """300 mm push handle (Ø25 bar on two standoffs) below the panel."""
    z = c.panel_top - c.panel_h - 40
    if c.handle_face == "front":
        L = c.handle_len / 2
        return fuse(cq.Solid.makeCylinder(12.5, c.handle_len, V(-L, c.y_face - c.handle_proj, z), V(1, 0, 0)),
                    cyl_y(8, c.y_face, c.y_face - c.handle_proj, -L + 15, z),
                    cyl_y(8, c.y_face, c.y_face - c.handle_proj, L - 15, z))
    x = c.col_x / 2 + c.handle_proj
    return fuse(cyl_z(12.5, z - c.handle_len, z, x, 0),
                cq.Solid.makeCylinder(8, c.handle_proj, V(c.col_x / 2, 0, z - 15), V(1, 0, 0)),
                cq.Solid.makeCylinder(8, c.handle_proj, V(c.col_x / 2, 0, z - c.handle_len + 15), V(1, 0, 0)))


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
        holes.append(cyl_y(5.25, c.y_face + 1, c.y_t1_front - 1, s * c.hinge_dx, c.z_axis))
        px, pz = plunger_xz(c, s)
        holes.append(cyl_y(3.4, c.y_face + 1, c.y_t1_front - 1, px, pz))       # M8 tap / pin hole
    for x in (-55, -20, 20, 55):  # 4 x Ø9 mounting holes, 20 from bottom edge
        holes.append(cyl_y(4.5, c.y_face + 1, c.y_t1_front - 1, x, z0 + 20))
    return cut(p, *holes)


def part_t1_bolts(c: Cfg):
    z0 = c.z_t1_top - c.t1_h
    return [cyl_y(6.5, c.y_t1_front, c.y_t1_front - 5.3, x, z0 + 20) for x in (-55, -20, 20, 55)]


def part_plunger(c: Cfg, side):
    """Index plunger: pin in front of T1, threaded body + knob behind T1 (toward column)."""
    px, pz = plunger_xz(c, side)
    pin = cyl_y(c.pin_d / 2, c.y_t1_front, c.y_t1_front - c.pin_protrusion, px, pz)
    body = fuse(hex_y(13, c.y_face, c.y_face + 8, px, pz),          # M8 weld nut
                cyl_y(4, c.y_face + 8, c.y_face + 22, px, pz),       # plunger body
                cyl_y(10, c.y_face + 22, c.y_face + 37, px, pz))     # pull knob
    return pin, body


def part_hinge_fixed(c: Cfg, side):
    """Parts of the hinge that do not rotate: teflon washer, nut/weld-nut behind T1, bolt shank."""
    x, z = side * c.hinge_dx, c.z_axis
    washer = cut(cyl_y(15, c.y_t1_front, c.y_disc0, x, z), cyl_y(7, c.y_t1_front + 1, c.y_disc0 - 1, x, z))
    head_face = c.y_ch_back - c.arm_t - 2.0          # under-head face (after 2 mm washer) inside channel
    shank_end = head_face + c.bolt_len               # toward +y (column)
    shank = cyl_y(5, head_face, shank_end, x, z)
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
    ch = ch.cut(cyl_y(7, yb + 1, yb - t - 1, 0, 0))
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
    br = br.cut(cyl_y(7, c.y_disc1 + 1, yb - 1, 0, 0))
    # disc H2 with centre hole + 13 index holes
    disc = cyl_y(c.disc_d / 2, c.y_disc0, c.y_disc1)
    holes = [cyl_y(7, c.y_disc0 + 1, c.y_disc1 - 1)]
    for k in range(13):
        g = math.radians(c.plunger_beta - 15 * k)
        holes.append(cyl_y(c.index_hole_d / 2, c.y_disc0 + 1, c.y_disc1 - 1,
                           c.index_r * math.sin(g), -c.index_r * math.cos(g)))
    disc = cut(disc, *holes)
    # bolt head + washer inside channel
    head = fuse(cyl_y(10, yb - t, yb - t - 2), hex_y(c.bolt_head_af, yb - t - 2, yb - t - 2 - c.bolt_head_h))
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
    for i, g in enumerate(part_gussets(c)):
        p[f"C1_gusset_{i+1}"] = g
    for i, cs in enumerate(part_casters(c)):
        p[f"B3_caster_{i+1}"] = cs
    return p
