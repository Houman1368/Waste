import React from "react";
import { Img, staticFile, useCurrentFrame } from "remotion";
import { fontFamily } from "../components/RtlText";
import { C } from "../theme";
import { ModelSpec, Rect } from "./specs";

export type Placement = { cx: number; cy: number; s: number };

/** تبدیل مختصات مدل (mm، y رو به بالا) به مختصات قاب */
export const toScreen = (m: ModelSpec, p: Placement, x: number, y: number) => ({
  x: p.cx + x * p.s,
  y: p.cy - (y - m.H / 2) * p.s,
});

/** جاگذاری پیش‌فرض: دستگاه سمت چپ قاب، متن سمت راست */
export const placement = (m: ModelSpec, cx = 480, cy = 560, maxH = 860): Placement => ({
  cx,
  cy,
  s: Math.min(maxH / m.H, 640 / 420),
});

// مستطیل در مختصات داخلی گروه (y برعکس)
const R: React.FC<{ box: Rect; H: number } & React.SVGProps<SVGRectElement>> = ({ box: r, H, ...rest }) => (
  <rect x={r.x0} y={H / 2 - r.y1} width={r.x1 - r.x0} height={r.y1 - r.y0} rx={r.r ?? 0} {...rest} />
);

/** لوگو داخل SVG با <Img> ریموشن (منتظر بارگذاری تصویر می‌ماند) */
const Logo: React.FC<{ m: ModelSpec; opacity: number }> = ({ m, opacity }) => (
  <foreignObject x={m.logo.x - m.logo.w / 2} y={m.H / 2 - m.logo.y - m.logo.h / 2} width={m.logo.w} height={m.logo.h} opacity={opacity}>
    <Img src={staticFile("logo.jpg")} style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }} />
  </foreignObject>
);

export type DrawingProps = {
  m: ModelSpec;
  p: Placement;
  /** ۰ = بسته، ۱ = نمای برش (پنل یا تیغه‌ها شفاف) */
  cut?: number;
  /** میزان حرکت فیلم به پایین (mm) */
  filmOffset?: number;
  /** ۰ تا ۱: پر شدن قرقرهٔ جمع‌کننده */
  roll?: number;
  /** شدت نور UV */
  glow?: number;
  /** زاویهٔ دستگیره (درجه) */
  knobAngle?: number;
  /** فاصلهٔ بیرون آمدن کارتریج (mm، رو به پایین) */
  cartridgeOut?: number;
  /** انتهای فیلم (y mm)؛ بالاتر از آن فیلمی نیست (برای پیچیدن کامل) */
  filmTail?: number;
  /** فیلم و رول‌ها کلاً نباشند (کارتریج بیرون است) */
  emptyBay?: boolean;
  sealed?: number;
  fresh?: boolean;
  /** حشره‌های چسبیده، در مختصات فیلم (mm) */
  filmChildren?: React.ReactNode;
  /** حشره‌هایی که پشت پنل/تیغه‌اند (مختصات قاب) */
  behind?: React.ReactNode;
  /** حشره‌های جلوی دستگاه (مختصات قاب) */
  front?: React.ReactNode;
  id: string;
};

export const ModelDrawing: React.FC<DrawingProps> = ({
  m,
  p,
  cut = 0,
  filmOffset = 0,
  roll = 0,
  glow = 1,
  knobAngle = 0,
  cartridgeOut = 0,
  filmTail,
  emptyBay = false,
  sealed = 0,
  fresh = false,
  filmChildren,
  behind,
  front,
  id,
}) => {
  const frame = useCurrentFrame();
  const pulse = 0.65 + 0.35 * Math.sin((frame / 60) * Math.PI * 2);
  const H = m.H;
  const Y = (y: number) => H / 2 - y;
  const g = glow * pulse;
  const f = m.film;
  const tail = filmTail ?? f.y1;
  const takeR = 20 + roll * 10;
  const supplyR = Math.max(13, 25 - roll * 10);
  const clipId = `${id}-clip`;
  const blur = `${id}-blur`;
  const cas = m.cassette;
  const lineGap = 30;
  const lines: number[] = [];
  for (let k = -1; k < (f.y1 - f.y0) / lineGap + 2; k++) lines.push(f.y0 + k * lineGap - (filmOffset % lineGap));

  const coverOpacity = 1 - cut * 0.85;

  const filmLayer = emptyBay ? null : (
    <g>
      <rect x={f.x0} y={Y(Math.min(f.y1, tail))} width={f.x1 - f.x0} height={Math.max(0, Math.min(f.y1, tail) - f.y0)} fill={C.film} stroke={C.filmEdge} strokeWidth={2} />
      <g clipPath={`url(#${clipId})`}>
        {lines.map((yy, i) => (yy < tail ? <line key={i} x1={f.x0} x2={f.x1} y1={Y(yy)} y2={Y(yy)} stroke={C.filmEdge} strokeOpacity={0.15} strokeWidth={1.5} /> : null))}
        <g transform={`translate(0 ${filmOffset})`}>{filmChildren}</g>
      </g>
    </g>
  );

  const rollShape = (y: number, r: number, len: number, op: number) => (
    <g opacity={op}>
      <rect x={-len / 2} y={Y(y) - r} width={len} height={r * 2} rx={Math.min(r, 10)} fill="#F2D79E" stroke={C.filmEdge} strokeWidth={2} />
      <line x1={-len / 2 + 8} x2={len / 2 - 8} y1={Y(y) - r * 0.45} y2={Y(y) - r * 0.45} stroke="#fff" strokeOpacity={0.6} strokeWidth={2} />
    </g>
  );

  // کارتریج: کاست + رول جمع‌کننده (همراه هم بیرون می‌آیند)
  const cartridge = (
    <g transform={`translate(0 ${cartridgeOut})`}>
      <R box={cas} H={H} fill={fresh ? "#F3F6F7" : "#fff"} stroke={C.bodyEdge} strokeWidth={3} opacity={1 - cut * 0.55} />
      <rect x={cas.x0 + 4} y={Y(cas.y1) - 3} width={cas.x1 - cas.x0 - 8} height={4} fill={C.brand} opacity={m.kind === "panel" ? 0 : 1} />
      {rollShape(m.takeupY, takeR, m.rollLen, cut)}
      {m.kind === "slats" ? <Logo m={m} opacity={1 - cut * 0.8} /> : null}
      {sealed > 0 ? (
        <g transform={`translate(0 ${Y((cas.y0 + cas.y1) / 2)}) scale(${0.85 + 0.15 * sealed})`} opacity={sealed}>
          <rect x={-Math.min(110, (cas.x1 - cas.x0) / 2 - 8)} y={-26} width={Math.min(220, cas.x1 - cas.x0 - 16)} height={52} rx={10} fill="#fff" stroke={C.warn} strokeWidth={3} />
          <text x={0} y={12} textAnchor="middle" fontFamily={fontFamily} fontWeight={700} fontSize={Math.min(34, (cas.x1 - cas.x0) / 6)} fill={C.warn}>
            پلمب‌شده
          </text>
        </g>
      ) : null}
    </g>
  );

  // دستگیره (از روبه‌رو، لبهٔ آن دیده می‌شود؛ شیارها با چرخش جابه‌جا می‌شوند)
  const k = m.knob;
  const ridges = [];
  for (let i = 0; i < 9; i++) {
    const a = ((i * 40 + knobAngle) % 360) * (Math.PI / 180);
    const yy = Y(k.y) + Math.cos(a) * k.r;
    if (Math.sin(a) > 0) ridges.push(<line key={i} x1={k.x + 4} x2={k.x + k.out - 2} y1={yy} y2={yy} stroke="#0A4A3A" strokeWidth={2.5} opacity={0.35 + 0.65 * Math.sin(a)} />);
  }
  const knob = (
    <g>
      <rect x={k.x - 4} y={Y(k.y) - k.r} width={k.out} height={k.r * 2} rx={6} fill={C.brand} />
      {ridges}
      <rect x={k.x + k.out - 4} y={Y(k.y) - 6 + Math.sin((knobAngle * Math.PI) / 180) * k.r * 0.55} width={14} height={12} rx={5} fill={C.brand} />
    </g>
  );

  return (
    <g transform={`translate(${p.cx} ${p.cy}) scale(${p.s})`}>
      <defs>
        <clipPath id={clipId}>
          <rect x={f.x0} y={Y(Math.min(f.y1, tail))} width={f.x1 - f.x0} height={Math.max(0, Math.min(f.y1, tail) - f.y0)} />
        </clipPath>
        <filter id={blur} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation={18} />
        </filter>
      </defs>
      {/* سایه روی دیوار */}
      <R box={m.shield ?? m.body} H={H} fill="#1F2A30" opacity={0.07} transform="translate(10 14)" />

      {m.kind === "panel" ? (
        <>
          {/* هالهٔ نور UV روی دیوار دور پنل */}
          <R box={{ ...m.shield!, x0: m.shield!.x0 - 30, x1: m.shield!.x1 + 30, y0: m.shield!.y0 - 30, y1: m.shield!.y1 + 30 }} H={H} fill="none" stroke={C.uvHalo} strokeWidth={40} opacity={0.55 * g} filter={`url(#${blur})`} />
          <R box={m.body} H={H} fill="#E6ECEF" stroke={C.bodyEdge} strokeWidth={3} />
          {filmLayer}
          {rollShape(m.supplyY, supplyR, m.rollLen, cut)}
          {cartridgeOut > 0 ? <R box={cas} H={H} fill="#C9D1D6" /> : null}
          {cartridge}
          {behind}
          {knob}
          {/* پنل جلو */}
          <g opacity={coverOpacity}>
            <R box={m.shield!} H={H} fill="#fff" stroke={C.bodyEdge} strokeWidth={2} />
            <Logo m={m} opacity={1} />
          </g>
          <R box={m.shield!} H={H} fill="none" stroke={C.uv} strokeWidth={6} opacity={0.5 + 0.5 * g} />
          <circle cx={m.status.x} cy={Y(m.status.y)} r={5} fill={C.ok} />
        </>
      ) : (
        <>
          <R box={m.body} H={H} fill="#fff" stroke={C.bodyEdge} strokeWidth={3} />
          <R box={m.window!} H={H} fill="#DCE3E7" />
          {filmLayer}
          {rollShape(m.supplyY, supplyR, m.rollLen, cut)}
          {behind}
          {/* تیغه‌ها */}
          <g opacity={coverOpacity}>
            {(() => {
              const w = m.window!;
              const out = [];
              for (let y = w.y0 + m.slatPitch! / 2; y < w.y1 - 4; y += m.slatPitch!) {
                out.push(<rect key={y} x={w.x0 + 2} y={Y(y) - 3.5} width={w.x1 - w.x0 - 4} height={7} fill="#F4F6F7" />);
                out.push(<rect key={`s${y}`} x={w.x0 + 2} y={Y(y) + 3.5} width={w.x1 - w.x0 - 4} height={3} fill="#9590C9" opacity={0.55} />);
              }
              return out;
            })()}
          </g>
          {(m.uvStrips ?? []).map((u, i) => (
            <R key={i} box={u} H={H} fill={C.uv} opacity={0.6 + 0.4 * g} />
          ))}
          <R box={m.window!} H={H} fill={C.uvHalo} opacity={0.12 * g} />
          {m.ledBar ? (
            <>
              <R box={{ ...m.ledBar, x0: m.ledBar.x0 - 20, x1: m.ledBar.x1 + 20, y0: m.ledBar.y0 - 18, y1: m.ledBar.y1 + 18 }} H={H} fill={C.uvHalo} opacity={0.5 * g} filter={`url(#${blur})`} />
              <R box={m.ledBar} H={H} fill={C.uv} />
            </>
          ) : null}
          {cartridgeOut > 0 ? <R box={cas} H={H} fill="#C9D1D6" /> : null}
          {cartridge}
          {knob}
          <circle cx={m.status.x} cy={Y(m.status.y)} r={5} fill={C.ok} />
        </>
      )}
      {front}
    </g>
  );
};
