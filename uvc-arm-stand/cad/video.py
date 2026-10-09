"""Animated clip: step-by-step assembly of V2, then arm motion (locks every 15°)."""
import math
import os
import subprocess
import sys
import numpy as np
import vtk
from model import V2, arm_canonical, static_parts, part_plunger, part_hinge_fixed, rot180
from export import _polydata, color_of, COL

c = V2
FPS = 24
W, H = 1280, 720
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "video")
FRAMES = os.path.join("/tmp", "uvc_frames")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FRAMES, exist_ok=True)

ren = vtk.vtkRenderer()
ren.SetBackground(0.97, 0.97, 0.98)
ren.SetBackground2(0.82, 0.85, 0.9)
ren.GradientBackgroundOn()
win = vtk.vtkRenderWindow()
win.SetOffScreenRendering(1)
win.AddRenderer(ren)
win.SetSize(W, H)
win.SetMultiSamples(8)

label = vtk.vtkTextActor()
label.GetTextProperty().SetFontSize(30)
label.GetTextProperty().SetColor(0.12, 0.12, 0.15)
label.GetTextProperty().BoldOn()
label.SetPosition(30, H - 60)
ren.AddActor2D(label)
sub = vtk.vtkTextActor()
sub.GetTextProperty().SetFontSize(20)
sub.GetTextProperty().SetColor(0.3, 0.3, 0.35)
sub.SetPosition(30, H - 95)
ren.AddActor2D(sub)


def make_actor(shape, name):
    m = vtk.vtkPolyDataMapper()
    m.SetInputData(_polydata(shape))
    a = vtk.vtkActor()
    a.SetMapper(m)
    p = a.GetProperty()
    p.SetColor(*color_of(name))
    p.SetSpecular(0.3)
    p.SetSpecularPower(25)
    a.VisibilityOff()
    ren.AddActor(a)
    return a


# ---------------------------------------------------------------- build actors
S = static_parts(c)
groups = []  # (title, subtitle, [(actor, base_transform_fn, offset_vec)])


def static_group(title, subtitle, keys, offset):
    groups.append((title, subtitle, [(make_actor(S[k], k), None, offset) for k in keys]))


static_group("1. Casters", "4 x swivel casters D75 (2 with brake)", [k for k in S if k.startswith("B3")], (0, 0, -400))
static_group("2. Base plate B1", "steel 6 mm, 500 x 400", ["B1_base_plate"], (0, 0, 600))
static_group("3. Column flange + gussets", "flange 260 x 220 x 6, 4 x M10 to base", ["C1_flange"] + [k for k in S if "gusset" in k], (0, 0, 600))
static_group("4. Column C1", "1.5 mm box 160 x 120 x 1050 + top cap", ["C1_column", "C1_top_cap"], (0, 0, 1400))
static_group("5. Ballast box B2", "covers ballasts, fuse, terminals", ["B2_ballast_box"], (0, 0, 1500))
static_group("6. Panel C3, handle, service door", "panel + handle on right side, door on back", ["C3_panel_box", "handle", "C2_service_door"], (500, 0, 0))
static_group("7. Head plates T1 (front + back)", "4 mm, 240 x 160, axis at 1150 mm", ["T1_head_plate_front", "T1_head_plate_back"], (0, 0, 700))

canon = arm_canonical(c)
hinge_items, arm_items = [], []
ARM_ACTORS = {}  # (face, side) -> list of actors
for face in ("F", "B"):
    for side in (1, -1):
        pin, body = part_plunger(c, side)
        w, sh, n = part_hinge_fixed(c, side)
        for nm, s in (("plunger", pin.fuse(body)), ("hinge_fixed", w.fuse(sh).fuse(n))):
            s = s if face == "F" else rot180(s)
            hinge_items.append((make_actor(s, nm), None, (0, (-300 if face == "F" else 300), 0)))
        acts = []
        for k, s in canon.items():
            s2 = s if side == 1 else s.mirror("YZ")
            a = make_actor(s2, k)
            acts.append(a)
            arm_items.append((a, (face, side), (0, (-700 if face == "F" else 700), 0)))
        ARM_ACTORS[(face, side)] = acts
groups.append(("8. Index plungers + hinge bolts", "M8 index plunger, teflon washer, M10 bolt + bronze bush", hinge_items))
groups.append(("9. Four arms A1 (with H1 bracket + H2 disc)", "aluminium reflector channel, UV-C T8 30 W lamp", arm_items))


def arm_transform(face, side, alpha, offset=(0, 0, 0)):
    t = vtk.vtkTransform()
    t.PostMultiply()
    t.RotateY(-side * alpha)
    t.Translate(side * c.hinge_dx, 0, c.z_axis)
    if face == "B":
        t.RotateZ(180)
    t.Translate(*offset)
    return t


def set_pose(pose, offsets=None):
    for (face, side), acts in ARM_ACTORS.items():
        off = (offsets or {}).get((face, side), (0, 0, 0))
        for a in acts:
            a.SetUserTransform(arm_transform(face, side, pose[(face, side)], off))


cam = ren.GetActiveCamera()
FOCAL = np.array([0, 0, 1050.0])


def set_camera(azim_deg, elev_deg=18, scale=1250):
    a, e = math.radians(azim_deg), math.radians(elev_deg)
    d = np.array([math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)])
    cam.SetFocalPoint(*FOCAL)
    cam.SetPosition(*(FOCAL + 8000 * d))
    cam.SetViewUp(0, 0, 1)
    cam.ParallelProjectionOn()
    cam.SetParallelScale(scale)
    ren.ResetCameraClippingRange()


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


frame_no = [0]


def snap():
    win.Render()
    f = vtk.vtkWindowToImageFilter()
    f.SetInput(win)
    f.Update()
    w = vtk.vtkPNGWriter()
    w.SetFileName(os.path.join(FRAMES, f"f{frame_no[0]:05d}.png"))
    w.SetInputConnection(f.GetOutputPort())
    w.Write()
    frame_no[0] += 1


# ---------------------------------------------------------------- 1) assembly
PARK = {k: 0.0 for k in ARM_ACTORS}
set_pose(PARK)
STEP = 22
azim = -35.0
for title, subtitle, items in groups:
    label.SetInput(title)
    sub.SetInput(subtitle)
    for a, *_ in items:
        a.VisibilityOn()
    for i in range(STEP + 6):
        k = 1 - ease(i / STEP)
        for a, armkey, off in items:
            o = tuple(k * v for v in off)
            if armkey:
                a.SetUserTransform(arm_transform(*armkey, 0.0, o))
            else:
                t = vtk.vtkTransform()
                t.Translate(*o)
                a.SetUserTransform(t)
        set_camera(azim, 20, 1150)
        azim += 0.25
        snap()
label.SetInput("Assembled - all arms parked (0 deg)")
sub.SetInput("move the stand only in this position")
for i in range(30):
    set_camera(azim, 20, 1150)
    azim += 0.25
    snap()


# ---------------------------------------------------------------- 2) arm motion (stepwise, 15 deg locks)
def stepped(a0, a1, x):
    """Move a0->a1 in 15° steps; each step = 70 % motion, 30 % locked pause."""
    n = int(round(abs(a1 - a0) / 15))
    if n == 0:
        return a0
    pos = min(max(x, 0.0), 1.0) * n
    i = min(int(pos), n - 1)
    frac = ease(min((pos - i) / 0.7, 1.0))
    return a0 + math.copysign(15, a1 - a0) * (i + frac)


moves = [
    ("Front arms -> 90 deg (horizontal)", "pull plunger knob, rotate, release: locks every 15 deg",
     {("F", 1): (0, 90), ("F", -1): (0, 90), ("B", 1): (0, 0), ("B", -1): (0, 0)}, 110),
    ("Back arms -> 135 / 90 deg, front right -> 180", "each arm is fully independent",
     {("F", 1): (90, 180), ("F", -1): (90, 45), ("B", 1): (0, 135), ("B", -1): (0, 90)}, 120),
    ("Working position", "4 x 30 W UV-C - room must be empty (PIR + start delay)",
     {k: (v, v) for k, v in {("F", 1): 180, ("F", -1): 45, ("B", 1): 135, ("B", -1): 90}.items()}, 90),
    ("Back to park (0 deg)", "", {("F", 1): (180, 0), ("F", -1): (45, 0), ("B", 1): (135, 0), ("B", -1): (90, 0)}, 130),
]
for title, subtitle, spec, n in moves:
    label.SetInput(title)
    sub.SetInput(subtitle)
    for i in range(n):
        x = i / (n - 1)
        set_pose({k: stepped(a0, a1, x) for k, (a0, a1) in spec.items()})
        set_camera(azim, 16, 1250)
        azim += 0.6
        snap()
for i in range(24):
    set_camera(azim, 16, 1250)
    snap()

print("frames:", frame_no[0])
mp4 = os.path.join(OUT_DIR, "UV-C_stand_V2_assembly_and_motion.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "f%05d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-movflags", "+faststart", mp4], check=True)
print(mp4, os.path.getsize(mp4))
