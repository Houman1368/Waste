"""Animated vertical clip: step-by-step assembly, then arm motion (locks every 15°)."""
import math
import os
import subprocess
import sys
import numpy as np
import vtk
from model import C, arm_canonical, static_parts, part_plunger, part_hinge_fixed, rot180
from export import _polydata, color_of, COL

c = C
FPS = 24
W, H = 1080, 1920  # vertical (portrait) clip
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "video")
FRAMES = os.path.join("/tmp", "uvc_frames")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FRAMES, exist_ok=True)  # render with: python video.py  [--compose-only]

ren = vtk.vtkRenderer()
ren.SetBackground(0.97, 0.97, 0.98)
ren.SetBackground2(0.82, 0.85, 0.9)
ren.GradientBackgroundOn()
win = vtk.vtkRenderWindow()
win.SetOffScreenRendering(1)
win.AddRenderer(ren)
win.SetSize(W, H)
win.SetMultiSamples(8)

CAPTIONS = []  # per frame: (step_no, title_fa, sub_fa)
CUR = {"step": 0, "title": "", "sub": ""}


def caption(step, title, sub=""):
    CUR.update(step=step, title=title, sub=sub)


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


static_group("چرخ‌ها (B3)", "۴ چرخ گردان Ø۷۵ با روکش PU — دو چرخ ترمزدار در یک قطر", [k for k in S if k.startswith("B3")], (0, 0, -400))
static_group("صفحهٔ پایه (B1)", "ورق فولادی ۶ میلی‌متر، ۵۰۰ × ۴۰۰", ["B1_base_plate"], (0, 0, 600))
static_group("فلنج و لچکی‌های ستون", "فلنج ۲۶۰ × ۲۲۰ × ۶ با ۴ پیچ M10 به صفحهٔ پایه", ["C1_flange"] + [k for k in S if "gusset" in k], (0, 0, 600))
static_group("ستون (C1)", "باکس ورق ۱٫۵ میلی‌متر، ۱۶۰ × ۱۲۰ × ۱۰۵۰ با درپوش بالا", ["C1_column", "C1_top_cap"], (0, 0, 1400))
static_group("جعبهٔ باالست (B2)", "باالست‌ها، فیوز و ترمینال — وزن پایین، پایداری بیشتر", ["B2_ballast_box"], (0, 0, 1500))
static_group("پنل کنترل، دستهٔ هل‌دادن و درب سرویس", "پنل روی وجه چپ، دسته روی وجه راست، درب سرویس پشت ستون", ["C3_panel_box", "handle", "C2_service_door"], (500, 0, 0))
static_group("صفحه‌های سر (T1) جلو و پشت", "ورق ۴ میلی‌متر، ۲۵۰ × ۱۶۰ با ۶ پیچ خزینه M8 — محور لولا در ارتفاع ۱۱۵۰", ["T1_head_plate_front", "T1_head_plate_back", "T1_screws_front", "T1_screws_back"], (0, 0, 700))

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
groups.append(("پین‌های قفل و محور لولا", "پین فنری M12 با پین Ø۶ و حالت استراحت، واشر تفلونی، پیچ M10 با بوش برنجی", hinge_items))
groups.append(("چهار بازوی لامپ (A1)", "ناودانی رفلکتور آلومینیومی، لامپ UV-C T8 سی‌وات، دیسک تقسیم H2", arm_items))


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
FOCAL = np.array([0, 0, 980.0])


def set_camera(azim_deg, elev_deg=18, scale=1250, zc=None):
    """zc = height (mm) shown at the centre of the free band between header and footer overlays."""
    a, e = math.radians(azim_deg), math.radians(elev_deg)
    if zc is not None:
        FOCAL[2] = zc - 94 * (2 * scale / H)  # band centre is 94 px above the frame centre
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


SKIP_RENDER = "--compose-only" in sys.argv  # reuse existing f*.png frames, only redo overlays


def snap():
    if SKIP_RENDER:
        CAPTIONS.append(dict(CUR))
        frame_no[0] += 1
        return
    win.Render()
    f = vtk.vtkWindowToImageFilter()
    f.SetInput(win)
    f.Update()
    w = vtk.vtkPNGWriter()
    w.SetFileName(os.path.join(FRAMES, f"f{frame_no[0]:05d}.png"))
    w.SetInputConnection(f.GetOutputPort())
    w.Write()
    CAPTIONS.append(dict(CUR))
    frame_no[0] += 1


# ---------------------------------------------------------------- 1) assembly
PARK = {k: 0.0 for k in ARM_ACTORS}
set_pose(PARK)
STEP = 22
azim = -35.0
for gi, (title, subtitle, items) in enumerate(groups):
    caption(gi + 1, title, subtitle)
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
        set_camera(azim, 20, 1500, 600)
        azim += 0.25
        snap()
caption(10, "مونتاژ کامل — بازوها در حالت پارک (۰ درجه)", "جابه‌جایی دستگاه فقط در این حالت")
for i in range(30):
    set_camera(azim, 20, 1500, 600)
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
    ("بازوهای جلو تا ۹۰ درجه (افقی)", "دستهٔ پین را بکشید، بچرخانید، رها کنید — قفل هر ۱۵ درجه",
     {("F", 1): (0, 90), ("F", -1): (0, 90), ("B", 1): (0, 0), ("B", -1): (0, 0)}, 110),
    ("تنظیم مستقل هر چهار بازو", "۰ تا ۱۸۰ درجه، ۱۳ موقعیت قفل برای هر بازو",
     {("F", 1): (90, 180), ("F", -1): (90, 45), ("B", 1): (0, 135), ("B", -1): (0, 90)}, 120),
    ("حالت کار", "۴ × ۳۰ وات UV-C — فقط در اتاق خالی (سنسور PIR و تأخیر شروع)",
     {k: (v, v) for k, v in {("F", 1): 180, ("F", -1): 45, ("B", 1): 135, ("B", -1): 90}.items()}, 90),
    ("بازگشت به حالت پارک", "همهٔ بازوها به ۰ درجه، آمادهٔ جابه‌جایی", {("F", 1): (180, 0), ("F", -1): (45, 0), ("B", 1): (135, 0), ("B", -1): (90, 0)}, 130),
]
for mi, (title, subtitle, spec, n) in enumerate(moves):
    caption(11 + mi, title, subtitle)
    for i in range(n):
        x = i / (n - 1)
        set_pose({k: stepped(a0, a1, x) for k, (a0, a1) in spec.items()})
        set_camera(azim, 16, 1750, 1030)
        azim += 0.6
        snap()
for i in range(24):
    set_camera(azim, 16, 1750, 1030)
    snap()

print("frames:", frame_no[0])
from overlay import compose_all
compose_all(FRAMES, CAPTIONS, W, H)
mp4 = os.path.join(OUT_DIR, "UV-C_stand_Rayateb_vertical.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "o%05d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-movflags", "+faststart", mp4], check=True)
print(mp4, os.path.getsize(mp4))
