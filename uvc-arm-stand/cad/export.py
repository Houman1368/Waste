"""Export STEP assemblies / parts (open in SolidWorks), DXF laser profiles and PNG renders."""
import json
import math
import os
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from model import V1, V2, Cfg, arm_canonical, place_arm, static_parts, part_plunger, part_hinge_fixed, rot180

OUT = os.path.join(os.path.dirname(__file__), "..")
STEP_DIR, DXF_DIR, IMG_DIR = (os.path.join(OUT, d) for d in ("step", "dxf", "images"))
for d in (STEP_DIR, DXF_DIR, IMG_DIR):
    os.makedirs(d, exist_ok=True)

COL = {"steel": (0.55, 0.57, 0.6), "alu": (0.82, 0.84, 0.88), "lamp": (0.6, 0.45, 0.95),
       "panel": (0.25, 0.45, 0.75), "black": (0.2, 0.2, 0.2), "red": (0.85, 0.2, 0.2), "brass": (0.8, 0.65, 0.3)}


def color_of(name):
    if "lamp" in name:
        return COL["lamp"]
    if any(k in name for k in ("channel", "caps")):
        return COL["alu"]
    if "C3" in name or "handle" in name:
        return COL["panel"]
    if "caster" in name or "sockets" in name:
        return COL["black"]
    if "plunger" in name:
        return COL["red"]
    if "hinge" in name or "bolt" in name:
        return COL["brass"]
    return COL["steel"]


def full_assembly(c: Cfg, pose=None):
    """pose = {('F',1): angle, ('F',-1): ..., ('B',1): ..., ('B',-1): ...}"""
    pose = pose or {("F", 1): 90, ("F", -1): 45, ("B", 1): 180, ("B", -1): 0}
    parts = dict(static_parts(c))
    canon = arm_canonical(c)
    for face in ("F", "B"):
        for side in (1, -1):
            tag = f"{face}{'R' if side == 1 else 'L'}"
            arm = place_arm(canon, c, side, pose[(face, side)])
            pin, body = part_plunger(c, side)
            w, sh, n = part_hinge_fixed(c, side)
            extra = {"plunger": pin.fuse(body), "hinge_fixed": w.fuse(sh).fuse(n)}
            for k, s in {**arm, **extra}.items():
                parts[f"{tag}_{k}"] = s if face == "F" else rot180(s)
    return parts


def export_step(c: Cfg, parts, fname):
    asm = cq.Assembly(name=c.name)
    for k, s in parts.items():
        r, g, b = color_of(k)
        asm.add(cq.Workplane().add(s), name=k, color=cq.Color(r, g, b))
    asm.save(os.path.join(STEP_DIR, fname), "STEP")


# ------------------------------------------------------------------ DXF (V2 laser parts)
def dxf_parts(c: Cfg):
    W = cq.Workplane
    out = {}
    # T1 head plate, origin = plate centre-bottom
    t1 = W("XY").rect(c.t1_w, c.t1_h, centered=(True, False))
    t1 = t1.pushPoints([(s * c.hinge_dx, c.t1_h - c.hinge_from_top) for s in (-1, 1)]).circle(5.25)
    t1 = t1.pushPoints([(s * c.hinge_dx, c.t1_h - c.hinge_from_top - c.index_r) for s in (-1, 1)]).circle(3.4)
    t1 = t1.pushPoints([(x, 20) for x in (-55, -20, 20, 55)]).circle(4.5)
    out["T1_head_plate_4mm_x2"] = t1
    # H2 index disc
    pts = [(c.index_r * math.sin(math.radians(c.plunger_beta - 15 * k)),
            -c.index_r * math.cos(math.radians(c.plunger_beta - 15 * k))) for k in range(13)]
    h2 = W("XY").circle(c.disc_d / 2).moveTo(0, 0).circle(7).pushPoints(pts).circle(c.index_hole_d / 2)
    out["H2_index_disc_5mm_x4_(mirror_2)"] = h2
    # B1 base plate
    bx, by = c.base_x / 2, c.base_y / 2
    fb = [(sx * (c.flange_x / 2 - c.flange_bolt_inset), sy * (c.flange_y / 2 - c.flange_bolt_inset)) for sx in (-1, 1) for sy in (-1, 1)]
    cast = [(sx * (bx - 30) + dx, sy * (by - 30) + dy) for sx in (-1, 1) for sy in (-1, 1) for dx in (-22.5, 22.5) for dy in (-22.5, 22.5)]
    b1 = W("XY").rect(c.base_x, c.base_y).pushPoints(fb).circle(5.5).pushPoints(cast).circle(4.5)
    out["B1_base_plate_6mm"] = b1
    # column flange with column outline as reference square hole? (solid plate, column welded on top)
    fl = W("XY").rect(c.flange_x, c.flange_y).pushPoints(fb).circle(5.5)
    out["C1_flange_6mm"] = fl
    gu = W("XY").polyline([(0, 0), (c.gusset_l, 0), (0, c.gusset_h)]).close()
    out["C1_gusset_4mm_x4"] = gu
    # H1 bracket flat blank (60 wide, developed length 120) with Ø14 bush hole and 4 x M5 holes
    h1 = W("XY").rect(120, c.br_len).moveTo(0, 0).circle(7).pushPoints([(-22, -20), (-22, 20), (22, -20), (22, 20)]).circle(2.75)
    out["H1_bracket_blank_4mm_x4"] = h1
    # A1 arm blank 170 x 950 (bend lines: 10/45/60/45/10), Ø14 hinge hole, bracket M5 holes
    e = c.axis_from_end
    a1 = (W("XY").rect(c.arm_len, 170, centered=(False, True)).moveTo(e, 0).circle(7)
          .pushPoints([(e - 20, -22), (e + 20, -22), (e - 20, 22), (e + 20, 22)]).circle(2.75))
    out["A1_arm_blank_1mm_x4"] = a1
    for k, w in out.items():
        cq.exporters.export(w, os.path.join(DXF_DIR, f"{k}.dxf"))
    return list(out)


# ------------------------------------------------------------------ renders (VTK, offscreen)
def _polydata(shape, tol=0.4):
    import vtk
    v, t = shape.tessellate(tol, 0.25)
    pts = vtk.vtkPoints()
    for p in v:
        pts.InsertNextPoint(p.x, p.y, p.z)
    cells = vtk.vtkCellArray()
    for a, b, c in t:
        cells.InsertNextCell(3)
        for k in (a, b, c):
            cells.InsertCellPoint(k)
    pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetPolys(cells)
    nf = vtk.vtkPolyDataNormals(); nf.SetInputData(pd); nf.SetFeatureAngle(35); nf.Update()
    return nf.GetOutput()


def render(parts, fname, view=(-1, -1.4, 0.7), focal=None, height=None, title=None, highlight=None, size=(1000, 1100),
           up=(0, 0, 1)):
    """view = direction from focal point to camera; height = visible height in mm (parallel projection)."""
    import vtk
    ren = vtk.vtkRenderer(); ren.SetBackground(1, 1, 1)
    for k, sh in parts.items():
        m = vtk.vtkPolyDataMapper(); m.SetInputData(_polydata(sh))
        a = vtk.vtkActor(); a.SetMapper(m)
        col = COL["red"] if highlight and k in highlight else color_of(k)
        a.GetProperty().SetColor(*col); a.GetProperty().SetSpecular(0.25); a.GetProperty().SetSpecularPower(20)
        ren.AddActor(a)
    if title:
        tx = vtk.vtkTextActor(); tx.SetInput(title); tx.GetTextProperty().SetFontSize(22)
        tx.GetTextProperty().SetColor(0.1, 0.1, 0.1); tx.SetPosition(15, size[1] - 40); ren.AddActor2D(tx)
    win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.AddRenderer(ren); win.SetSize(*size)
    cam = ren.GetActiveCamera(); cam.ParallelProjectionOn()
    ren.ResetCamera()
    if focal is None:
        focal = cam.GetFocalPoint()
    d = np.array(view, float); d /= np.linalg.norm(d)
    cam.SetFocalPoint(*focal); cam.SetPosition(*(np.array(focal) + 6000 * d)); cam.SetViewUp(*up)
    ren.ResetCameraClippingRange()
    if height:
        cam.SetParallelScale(height / 2)
    else:
        ren.ResetCamera(); cam.Zoom(1.05)
    win.Render()
    f = vtk.vtkWindowToImageFilter(); f.SetInput(win); f.Update()
    w = vtk.vtkPNGWriter(); w.SetFileName(os.path.join(IMG_DIR, fname)); w.SetInputConnection(f.GetOutputPort()); w.Write()


def matrix_plot(res):
    fig, axs = plt.subplots(1, 2, figsize=(11, 5), dpi=110)
    for ax, key in zip(axs, ("V1", "V2")):
        m = np.array(res[key]["arm_arm_matrix"]["rows_right"]) > 1
        ang = res[key]["arm_arm_matrix"]["angles"]
        ax.imshow(m, cmap="RdYlGn_r", vmin=0, vmax=1, origin="lower")
        ax.set_xticks(range(13)); ax.set_xticklabels(ang, fontsize=7)
        ax.set_yticks(range(13)); ax.set_yticklabels(ang, fontsize=7)
        ax.set_xlabel("left arm angle (deg)"); ax.set_ylabel("right arm angle (deg)")
        ax.set_title(f"{key}: {int(m.sum())} / 169 colliding (red)")
    fig.tight_layout()
    fig.savefig(os.path.join(IMG_DIR, "arm_vs_arm_collision_matrix.png"))
    plt.close(fig)


if __name__ == "__main__":
    for c in (V1, V2):
        parts = full_assembly(c)
        export_step(c, parts, f"{c.name}_assembly.step")
        print("STEP", c.name, len(parts), "solids")
    # individual V2 parts
    p2 = full_assembly(V2)
    canon = arm_canonical(V2)
    singles = {"B1_base_plate": p2["B1_base_plate"], "B2_ballast_box": p2["B2_ballast_box"],
               "C1_column_tube": p2["C1_column"], "C1_top_cap": p2["C1_top_cap"], "C1_flange": p2["C1_flange"],
               "C1_gusset": p2["C1_gusset_1"], "C2_service_door": p2["C2_service_door"],
               "C3_panel_box": p2["C3_panel_box"], "T1_head_plate": p2["T1_head_plate_front"],
               "A1_arm_channel": canon["channel"], "A2_end_caps": canon["caps"], "H1_bracket": canon["bracket"],
               "H2_index_disc": canon["disc"]}
    for k, s in singles.items():
        cq.exporters.export(cq.Workplane().add(s), os.path.join(STEP_DIR, "V2_parts", f"{k}.step"))
    print("DXF", dxf_parts(V2))

    res = json.load(open(os.path.join(OUT, "results", "checks_V1_V2.json")))
    matrix_plot(res)
    render(full_assembly(V2), "V2_iso.png", title="V2 (corrected) - arms at 90, 45, 180, 0 deg")
    render(full_assembly(V1), "V1_iso.png", title="V1 (as drawn) - same pose")
    for c in (V1, V2):
        z = c.z_axis
        render(full_assembly(c, {("F", 1): 90, ("F", -1): 90, ("B", 1): 0, ("B", -1): 0}),
               f"{c.name}_hinge_front_both90.png", view=(0, -1, 0), focal=(0, 0, z - 40), height=420,
               title=f"{c.name}: both front arms at 90 deg (front view)", size=(1100, 800))
        render(full_assembly(c, {("F", 1): 0, ("F", -1): 0, ("B", 1): 0, ("B", -1): 0}), f"{c.name}_parked.png",
               view=(-0.6, -1, 0.35), title=f"{c.name}: all arms parked (0 deg)")
        render(full_assembly(c, {("F", 1): 45, ("F", -1): 0, ("B", 1): 0, ("B", -1): 0}), f"{c.name}_hinge_side.png",
               view=(1, -0.25, 0.25), focal=(c.hinge_dx, -40, z - 30), height=330,
               title=f"{c.name}: right side of hinge zone (plunger knob / nut behind T1)", size=(1000, 800))
    print("renders done")
