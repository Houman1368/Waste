"""نمودار ورود حشره در طرح A (برش افقی و عمودی با ابعاد واقعی مدل) ← entry-a.html
اجرا: python3 make_entry_a.py && node ../../render/shot.mjs entry-a.html entry-a.png 1340"""
import math

R, ZF, T = 900.0, 98.0, 5.0


def shield_z(x):
    return ZF - (R - math.sqrt(R * R - x * x))


FLY = '<g transform="translate({x:.1f} {y:.1f})"><ellipse rx="9" ry="6" fill="#1F2A30"/><ellipse cx="-3" cy="-8" rx="8" ry="4" fill="#C9D1D6" opacity=".8"/></g>'
ARROW = '<path d="{d}" fill="none" stroke="#D85A30" stroke-width="4" stroke-dasharray="10 7" marker-end="url(#ah)" stroke-linecap="round"/>'

# ---------- نمای بالا (برش افقی) ----------
S = 1.55
ZS = 2.6  # بزرگ‌نمایی عمق برای خوانایی
ox, oy = 80 + 280 * S, 40 + 140 * S * ZS


def P(x, z):
    return (ox + x * S, oy - z * S * ZS)


def rect(x0, z0, x1, z1, fill, extra=""):
    a, b = P(x0, z1), P(x1, z0)
    return f'<rect x="{a[0]:.1f}" y="{a[1]:.1f}" width="{b[0]-a[0]:.1f}" height="{b[1]-a[1]:.1f}" fill="{fill}" {extra}/>'


def path(pts, f):
    return "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in (f(*p) for p in pts))


outer = " ".join("{:.1f},{:.1f}".format(*P(x, shield_z(x))) for x in range(-200, 201, 5))
inner = " ".join("{:.1f},{:.1f}".format(*P(x, shield_z(x) - T)) for x in range(200, -201, -5))
top = [
    f'<line x1="20" y1="{oy}" x2="{ox+300*S}" y2="{oy}" stroke="#8FA3AA" stroke-width="6"/>',
    f'<text x="{ox}" y="{oy+38}" class="lbl c">دیوار</text>',
    rect(-180, 0, 180, 34, "#E6ECEF", 'stroke="#B7C2C8" stroke-width="2"'),
    rect(-140, 34, 140, 36.5, "#F2D79E", 'stroke="#BA7517" stroke-width="1.5"'),
    f'<polygon points="{outer} {inner}" fill="#fff" stroke="#9AA8AE" stroke-width="2"/>',
]
for x in (-120, 120):
    top.append(rect(x - 9, 34, x + 9, 76, "#DCE3E7"))
for x in (-176, 172):
    top.append(rect(x, 62, x + 4, 65, "#7F77DD"))
for sx in (-1, 1):
    gx, gz = P(sx * 205, 45)
    top.append(f'<ellipse cx="{gx:.1f}" cy="{gz:.1f}" rx="{38*S:.1f}" ry="{40*S*ZS:.1f}" fill="#AFA9EC" opacity="0.35"/>')
top.append(ARROW.format(d=path([(-265, 125), (-215, 60), (-170, 50), (-100, 42)], P)))
top.append(ARROW.format(d=path([(265, 125), (215, 60), (170, 50), (90, 42)], P)))
for x in (-268, 268):
    top.append(FLY.format(x=P(x, 130)[0], y=P(x, 130)[1]))
a, b = P(0, 36.5), P(0, ZF - T)
top.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#0F6E56" stroke-width="2" marker-start="url(#dm)" marker-end="url(#dm)"/>')
top.append(f'<text x="{a[0]+10}" y="{(a[1]+b[1])/2+8}" class="dim" text-anchor="start">۵.۵ سانتی‌متر</text>')
a, b = P(-160, 36.5), P(-160, shield_z(160) - T)
top.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#0F6E56" stroke-width="2" marker-start="url(#dm)" marker-end="url(#dm)"/>')
top.append(f'<text x="{a[0]+8}" y="{b[1]+26}" class="dim" text-anchor="start">۴</text>')
x, y = P(-65, 62)
top.append(f'<text x="{x}" y="{y}" class="sm c" fill="#55656D">کانال پشت پنل</text>')
x, y = P(0, 104)
top.append(f'<text x="{x}" y="{y}" class="lbl c">پنل جلوی خمیده</text>')
x, y = P(0, 17)
top.append(f'<text x="{x}" y="{y+8}" class="lbl c" fill="#55656D">بدنه + سطح چسبی</text>')
topW, topH = int(ox + 300 * S), int(oy + 60)

# ---------- نمای کنار (برش عمودی) ----------
S2 = 0.95
ox2, oy2 = 60, 110 + 600 * S2


def Q(z, y):
    return (ox2 + z * S2 * 1.6, oy2 - y * S2)


def r2(z0, y0, z1, y1, fill, extra=""):
    a, b = Q(z0, y1), Q(z1, y0)
    return f'<rect x="{a[0]:.1f}" y="{a[1]:.1f}" width="{b[0]-a[0]:.1f}" height="{b[1]-a[1]:.1f}" fill="{fill}" {extra}/>'


side = [
    f'<line x1="{ox2}" y1="20" x2="{ox2}" y2="{oy2+120}" stroke="#8FA3AA" stroke-width="6"/>',
    r2(0, 0, 34, 540, "#E6ECEF", 'stroke="#B7C2C8" stroke-width="2"'),
    r2(34, 120, 36, 445, "#F2D79E", 'stroke="#BA7517" stroke-width="1.5"'),
    r2(4, 8, 38, 112, "#fff", 'stroke="#9AA8AE" stroke-width="2"'),
    r2(93, -4, 98, 544, "#fff", 'stroke="#9AA8AE" stroke-width="2"'),
    r2(62, 0, 65, 4, "#7F77DD"),
    r2(62, 536, 65, 540, "#7F77DD"),
]
for y in (150, 420):
    side.append(r2(34, y - 9, 76, y + 9, "#DCE3E7"))
for y in (-10, 552):
    gx, gy = Q(64, y)
    side.append(f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="{45*S2*1.6:.1f}" ry="{30*S2:.1f}" fill="#AFA9EC" opacity="0.35"/>')
side.append(ARROW.format(d=path([(150, 615), (70, 560), (55, 500), (40, 430)], Q)))
side.append(ARROW.format(d=path([(150, -65), (70, -20), (55, 40), (40, 160)], Q)))
for y in (630, -80):
    side.append(FLY.format(x=Q(150, y)[0], y=Q(150, y)[1]))
x, y = Q(21, 60)
side.append(f'<text x="{x}" y="{y}" class="sm c" fill="#55656D">کاست</text>')
sideW, sideH = int(ox2 + 220 * S2 * 1.6), int(oy2 + 130)

DEFS = """<defs><marker id="ah" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#D85A30"/></marker>
<marker id="dm" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#0F6E56"/></marker></defs>"""

html = f"""<!doctype html><html dir="rtl"><head><meta charset="utf-8"><style>
@font-face{{font-family:V;src:url(vazir-ar.woff2) format("woff2");unicode-range:U+0600-06FF,U+200C-200E,U+FB50-FDFF,U+FE70-FEFF;font-weight:100 900}}
@font-face{{font-family:V;src:url(vazir-lat.woff2) format("woff2");font-weight:100 900}}
body{{margin:0;background:#F7F9FA;font-family:V;color:#1F2A30;width:1340px}}
.wrap{{display:flex;gap:30px;padding:24px 36px 20px;align-items:flex-start}}
.card{{background:#fff;border:2px solid #E3E9EC;border-radius:24px;padding:18px 22px}}
h1{{font-size:44px;margin:30px 36px 0;color:#0F6E56}}
h2{{font-size:30px;margin:0 0 6px}}
.lbl{{font-size:24px;font-family:V}} .sm{{font-size:21px;font-family:V}} .dim{{font-size:22px;font-family:V;fill:#0F6E56;font-weight:700}}
.c{{text-anchor:middle}}
ul{{font-size:27px;line-height:1.75;margin:6px 36px 30px;padding-right:30px}}
.k{{display:inline-block;width:22px;height:22px;border-radius:6px;vertical-align:middle;margin-left:8px}}
</style></head><body>
<h1>طرح A: حشره از کجا وارد می‌شود؟</h1>
<div class="wrap">
<div class="card"><h2>نمای از بالا (برش افقی؛ عمق بزرگ‌نمایی شده)</h2>
<svg direction="ltr" width="{topW}" height="{topH}" viewBox="0 0 {topW} {topH}">{DEFS}{''.join(top)}</svg></div>
<div class="card"><h2>نمای از کنار (برش عمودی)</h2>
<svg direction="ltr" width="{sideW}" height="{sideH}" viewBox="0 0 {sideW} {sideH}">{DEFS}{''.join(side)}</svg></div>
</div>
<ul>
<li><span class="k" style="background:#D85A30"></span>مسیر حشره: از <b>هر چهار لبهٔ</b> پنل (بالا، پایین، چپ، راست) وارد کانال پشت پنل می‌شود.</li>
<li><span class="k" style="background:#AFA9EC"></span>نور UV از نوار LED پشت لبه‌های پنل به دیوار و سطح چسبی می‌تابد و از همین درزها بیرون می‌زند؛ حشره به‌سمت نور می‌آید.</li>
<li><span class="k" style="background:#F2D79E;border:1px solid #BA7517"></span>داخل کانال، نور روی سطح چسبیِ روشن بازتاب می‌شود؛ حشره روی آن می‌نشیند و می‌چسبد.</li>
<li>عرض کانال پشت پنل: حدود ۳.۵ تا ۴ سانتی‌متر نزدیک لبه‌ها و ۵.۵ سانتی‌متر در وسط — برای مگس، پشه و پروانهٔ کوچک کافی است.</li>
</ul></body></html>"""
open("entry-a.html", "w", encoding="utf-8").write(html)
