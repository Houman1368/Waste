import React from "react";
import { AbsoluteFill, Img, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Counter } from "../components/Counter";
import { Fly } from "../components/Fly";
import { CheckIcon, DotIcon, fontFamily, RtlText, TextPanel } from "../components/RtlText";
import { Tick } from "../components/Tick";
import { CONTACT } from "../config";
import { C } from "../theme";
import { angleOf, clamp, ease, fa, flight, Pt } from "../utils";
import { ModelDrawing, placement, toScreen } from "./ModelDrawing";
import { BISMILLAH, COMPANY_FULL, ModelSpec } from "./specs";

type SP = { m: ModelSpec };

// ---------- ابزارهای مشترک ----------

/** نقطه‌های چسبیدن روی فیلم (mm) */
const stickPoints = (m: ModelSpec, n: number, seed: string): Pt[] => {
  const f = m.film;
  const out: Pt[] = [];
  const cols = m.key === "B" ? 2 : 3;
  for (let i = 0; i < n; i++) {
    const cx = f.x0 + ((i % cols) + 0.5) * ((f.x1 - f.x0) / cols);
    const cy = f.y0 + 30 + (Math.floor(i / cols) + 0.5) * ((f.y1 - f.y0 - 60) / Math.ceil(n / cols));
    out.push({
      x: cx + (random(`${seed}x${i}`) - 0.5) * ((f.x1 - f.x0) / cols) * 0.5,
      y: cy + (random(`${seed}y${i}`) - 0.5) * 30,
    });
  }
  return out;
};

const startPoint = (i: number): Pt => {
  const r = random(`start-${i}`);
  const side = i % 3;
  if (side === 0) return { x: -60, y: 150 + r * 800 };
  if (side === 1) return { x: 80 + r * 700, y: -60 };
  return { x: 80 + r * 700, y: 1140 };
};

/** نقطهٔ ورود: برای A لبهٔ پنل، برای B و C جلوی تیغه‌ها */
const entryPoint = (m: ModelSpec, t: Pt, i: number): Pt => {
  if (m.kind === "panel") {
    const s = m.shield!;
    const side = i % 4;
    if (side === 0) return { x: s.x0 - 28, y: t.y };
    if (side === 1) return { x: t.x, y: s.y1 + 28 };
    if (side === 2) return { x: s.x1 + 28, y: t.y };
    return { x: t.x, y: s.y0 - 28 };
  }
  return { x: t.x + 25, y: t.y + 30 };
};

const stuckFly = (p: Pt, i: number, s: number, key: string, filmShift = 0) => (
  <Fly key={key} x={p.x} y={-(p.y - filmShift)} angle={-90 + (random(`a${key}`) - 0.5) * 120} size={1.25 / s} flapping={false} seed={key} />
);

/** گروه فیلم در ModelDrawing مختصات y برعکس دارد: y_svg = H/2 - y */
const FilmFlies: React.FC<{ m: ModelSpec; children: React.ReactNode }> = ({ m, children }) => (
  <g transform={`translate(0 ${m.H / 2})`}>{children}</g>
);

const Stage: React.FC<{ children: React.ReactNode; bg?: string }> = ({ children, bg = C.bg }) => (
  <AbsoluteFill style={{ background: bg }}>
    <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0 }}>
      {children}
    </svg>
  </AbsoluteFill>
);

const ModelBadge: React.FC<{ m: ModelSpec }> = ({ m }) => (
  <div
    style={{
      position: "absolute",
      left: 56,
      bottom: 40,
      fontFamily,
      fontWeight: 700,
      fontSize: 44,
      color: C.brand,
      letterSpacing: 2,
      direction: "ltr",
    }}
  >
    {m.id}
  </div>
);

// ---------- ۰. بسم الله ----------
export const SceneBismillah: React.FC = () => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 25, 95, 118], [0, 1, 1, 0], clamp);
  const line = interpolate(frame, [15, 55], [0, 1], { ...clamp, easing: ease });
  return (
    <AbsoluteFill style={{ background: "#fff", alignItems: "center", justifyContent: "center" }}>
      <div dir="rtl" style={{ fontFamily, fontWeight: 700, fontSize: 104, color: C.brand, opacity: op, transform: `scale(${0.96 + 0.04 * op})` }}>
        {BISMILLAH}
      </div>
      <div style={{ height: 4, width: 520 * line, background: C.brand, opacity: 0.35 * op, marginTop: 36, borderRadius: 2 }} />
    </AbsoluteFill>
  );
};

// ---------- ۱. معرفی ----------
export const SceneIntro: React.FC<SP> = ({ m }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pImg = spring({ frame: frame - 5, fps, config: { damping: 200 }, durationInFrames: 30 });
  const zoom = interpolate(frame, [0, 240], [1.04, 1.12]);
  const logoP = spring({ frame: frame - 15, fps, config: { damping: 200 }, durationInFrames: 25 });
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <div style={{ position: "absolute", left: 60, top: 40, width: 800, height: 1000, borderRadius: 40, overflow: "hidden", opacity: pImg, background: "#EEF2F3" }}>
        <Img src={staticFile(`renders/${m.render}-hero.png`)} style={{ width: "100%", height: "100%", objectFit: "contain", transform: `scale(${zoom})` }} />
      </div>
      <div style={{ position: "absolute", left: 940, top: 70, width: 900, display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 18 }}>
        <div style={{ background: "#fff", borderRadius: 28, padding: "18px 28px", border: `2px solid ${C.bodyEdge}`, opacity: logoP, transform: `translateY(${(1 - logoP) * 20}px)` }}>
          <Img src={staticFile("logo.jpg")} style={{ height: 150, display: "block" }} />
        </div>
        <RtlText size="small" delay={25} color={C.muted}>
          {COMPANY_FULL}
        </RtlText>
        <div style={{ height: 30 }} />
        <RtlText size="title" delay={55} color={C.brand} style={{ fontSize: 120, lineHeight: 1.1, direction: "ltr", justifyContent: "flex-end" }}>
          <span style={{ direction: "ltr", display: "block", textAlign: "right" }}>{m.id}</span>
        </RtlText>
        <RtlText size="title" delay={80}>
          {m.title}
        </RtlText>
        <RtlText delay={115} color={C.muted}>
          {m.tagline}
        </RtlText>
      </div>
    </AbsoluteFill>
  );
};

// ---------- ۲. اجزا ----------
export const SceneParts: React.FC<SP> = ({ m }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = placement(m);
  const n = m.callouts.length;
  const labelY = (i: number) => 300 + i * (560 / Math.max(1, n - 1));
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Stage>
        <ModelDrawing m={m} p={p} id={`parts-${m.key}`} />
        {m.callouts.map((c, i) => {
          const pr = spring({ frame: frame - (40 + i * 45), fps, config: { damping: 200 }, durationInFrames: 20 });
          const a = toScreen(m, p, c.x, c.y);
          const ly = labelY(i);
          const lx = 1000;
          const len = Math.hypot(lx - a.x, ly - a.y) + 60;
          return (
            <g key={i} opacity={pr}>
              <path d={`M ${a.x} ${a.y} L ${a.x + (lx - a.x) * 0.55} ${ly} L ${lx} ${ly}`} fill="none" stroke={C.brand} strokeWidth={3} strokeDasharray={len} strokeDashoffset={len * (1 - pr)} />
              <circle cx={a.x} cy={a.y} r={9} fill="#fff" stroke={C.brand} strokeWidth={4} />
            </g>
          );
        })}
      </Stage>
      <div style={{ position: "absolute", left: 960, right: 80, top: 70 }}>
        <RtlText size="title" delay={8}>
          اجزای اصلی {m.id}
        </RtlText>
      </div>
      {m.callouts.map((c, i) => (
        <div key={i} style={{ position: "absolute", left: 1016, top: labelY(i) - 36, display: "flex", direction: "ltr" }}>
          <RtlText delay={45 + i * 45} weight={700} style={{ width: "auto" }}>
            {c.text}
          </RtlText>
        </div>
      ))}
      <ModelBadge m={m} />
    </AbsoluteFill>
  );
};

// ---------- حشره‌های صحنهٔ جذب (مشترک با صحنهٔ بعد) ----------
const N1 = 8;
const T1 = (i: number) => ({ start: 30 + i * 26, d1: 62, d2: 24 });

const attractFlies = (m: ModelSpec, frame: number) => {
  const p = placement(m);
  const targets = stickPoints(m, N1, `t1${m.key}`);
  const front: React.ReactNode[] = [];
  const behind: React.ReactNode[] = [];
  const stuck: React.ReactNode[] = [];
  targets.forEach((t, i) => {
    const { start, d1, d2 } = T1(i);
    const from = startPoint(i);
    const e = entryPoint(m, t, i);
    const eS = toScreen(m, p, e.x, e.y);
    const tS = toScreen(m, p, t.x, t.y);
    const key = `f${m.key}${i}`;
    if (frame < start) return;
    if (frame < start + d1) {
      const u = (frame - start) / d1;
      const a = flight(key, from, eS, u);
      front.push(<Fly key={key} x={a.x} y={a.y} angle={angleOf(a, flight(key, from, eS, u + 0.02))} size={1.25} seed={key} />);
    } else if (frame < start + d1 + d2) {
      const u = (frame - start - d1) / d2;
      const a = flight(key + "b", eS, tS, u, 0.3);
      // بعد از عبور از لبه/تیغه، حشره پشت پوشش است
      const layer = m.kind === "panel" || u > 0.4 ? behind : front;
      layer.push(<Fly key={key} x={(a.x - p.cx) / p.s} y={(a.y - p.cy) / p.s} angle={angleOf(a, flight(key + "b", eS, tS, u + 0.05, 0.3))} size={1.25 / p.s} seed={key} />);
    } else {
      stuck.push(stuckFly(t, i, p.s, key));
    }
  });
  return { front, behind, stuck, p };
};

// ---------- ۳. جذب ----------
export const SceneAttract: React.FC<SP> = ({ m }) => {
  const frame = useCurrentFrame();
  const { front, behind, stuck, p } = attractFlies(m, frame);
  // کمان‌های نور
  const src = m.kind === "panel" ? toScreen(m, p, 0, m.H / 2) : toScreen(m, p, 0, m.ledBar ? m.ledBar.y0 : (m.window!.y0 + m.window!.y1) / 2);
  const arcs = [0, 1, 2].map((k) => {
    const t = ((frame + k * 40) % 120) / 120;
    const r = 200 + t * 420;
    return <circle key={k} cx={src.x} cy={src.y} r={r} fill="none" stroke={C.uv} strokeWidth={5} strokeDasharray={`${r * 0.8} ${r * 0.5}`} opacity={(1 - t) * 0.5 * interpolate(frame, [0, 20], [0, 1], clamp)} />;
  });
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Stage>
        {arcs}
        <ModelDrawing
          m={m}
          p={p}
          id={`att-${m.key}`}
          behind={<g transform={`translate(0 0)`}>{behind}</g>}
          filmChildren={<FilmFlies m={m}>{stuck}</FilmFlies>}
        />
        {front}
      </Stage>
      <TextPanel>
        <RtlText size="title" delay={10} color={C.uv}>
          جذب حشره با نور UV-A
        </RtlText>
        <RtlText delay={60} icon={<DotIcon size={40} />}>
          {m.attract[0]}
        </RtlText>
        <RtlText delay={170} icon={<DotIcon size={40} color={C.brand} />}>
          {m.attract[1]}
        </RtlText>
      </TextPanel>
      <ModelBadge m={m} />
    </AbsoluteFill>
  );
};

// ---------- ۴. گیر افتادن (نمای برش) ----------
const N2 = 5;
const T2 = (i: number) => ({ start: 70 + i * 34, dur: 50 });

export const SceneCapture: React.FC<SP> = ({ m }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = placement(m);
  const cut = interpolate(frame, [15, 50], [0, 1], { ...clamp, easing: ease });
  const t1 = stickPoints(m, N1, `t1${m.key}`);
  const t2 = stickPoints(m, N2, `t2${m.key}`).map((q, i) => ({ x: q.x + (i % 2 ? 12 : -12), y: q.y + 14 }));
  const stuck = t1.map((t, i) => stuckFly(t, i, p.s, `f${m.key}${i}`));
  const ticks: React.ReactNode[] = [];
  const front: React.ReactNode[] = [];
  let count = N1;
  let last = -100;
  t2.forEach((t, i) => {
    const { start, dur } = T2(i);
    const key = `g${m.key}${i}`;
    const tS = toScreen(m, p, t.x, t.y);
    const from = startPoint(i + 20);
    if (frame >= start + dur) {
      count++;
      last = Math.max(last, start + dur);
      stuck.push(stuckFly(t, i, p.s, key));
      ticks.push(<Tick key={key} x={t.x + 16} y={-(t.y + 16)} since={frame - start - dur} fps={fps} size={1.2 / p.s} />);
    } else if (frame >= start) {
      const u = (frame - start) / dur;
      const a = flight(key, from, tS, u);
      front.push(<Fly key={key} x={a.x} y={a.y} angle={angleOf(a, flight(key, from, tS, u + 0.02))} size={1.25} seed={key} />);
    }
  });
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Stage>
        <ModelDrawing
          m={m}
          p={p}
          cut={cut}
          id={`cap-${m.key}`}
          filmChildren={
            <FilmFlies m={m}>
              {stuck}
              {ticks}
            </FilmFlies>
          }
        />
        {front}
      </Stage>
      <Counter value={count} bumpAt={last} opacity={interpolate(frame, [40, 55], [0, 1], clamp)} />
      <TextPanel>
        <RtlText size="title" delay={10}>
          گیر افتادن روی سطح چسبی
        </RtlText>
        <RtlText delay={55} icon={<CheckIcon size={40} />}>
          {m.capture[0]}
        </RtlText>
        <RtlText delay={165} icon={<CheckIcon size={40} />}>
          {m.capture[1]}
        </RtlText>
      </TextPanel>
      <ModelBadge m={m} />
    </AbsoluteFill>
  );
};

// ---------- ۵. پیچیدن فیلم ----------
const KnobInset: React.FC<{ angle: number; op: number; x: number; y: number }> = ({ angle, op, x, y }) => (
  <g transform={`translate(${x} ${y})`} opacity={op}>
    <circle r={92} fill="#fff" stroke={C.bodyEdge} strokeWidth={3} />
    <g transform={`rotate(${angle})`}>
      <circle r={60} fill={C.brand} />
      {Array.from({ length: 14 }).map((_, i) => {
        const a = (i / 14) * Math.PI * 2;
        return <circle key={i} cx={Math.cos(a) * 60} cy={Math.sin(a) * 60} r={7} fill="#fff" />;
      })}
      <circle cx={0} cy={-34} r={13} fill="#0A4A3A" />
    </g>
    <path d="M 0 -80 A 80 80 0 0 1 75 -27" fill="none" stroke={C.warn} strokeWidth={6} strokeLinecap="round" />
    <path d="M 82 -40 L 76 -16 L 60 -32 Z" fill={C.warn} />
  </g>
);

const MotorInset: React.FC<{ angle: number; op: number; x: number; y: number }> = ({ angle, op, x, y }) => (
  <g transform={`translate(${x} ${y})`} opacity={op}>
    <circle r={92} fill="#fff" stroke={C.bodyEdge} strokeWidth={3} />
    <rect x={-58} y={-24} width={70} height={48} rx={8} fill="#8C9196" />
    <rect x={12} y={-8} width={14} height={16} fill="#6E7378" />
    <g transform={`translate(42 0) rotate(${angle})`}>
      {Array.from({ length: 10 }).map((_, i) => (
        <rect key={i} x={-5} y={-34} width={10} height={14} fill={C.brand} transform={`rotate(${i * 36})`} />
      ))}
      <circle r={24} fill={C.brand} />
      <circle r={7} fill="#fff" />
    </g>
    <path d="M -40 -40 L -28 -60 M -40 -40 L -20 -46" stroke={C.warn} strokeWidth={0} />
  </g>
);

export const SceneRoll: React.FC<SP> = ({ m }) => {
  const frame = useCurrentFrame();
  const p = placement(m);
  const span = m.film.y1 - m.film.y0 + 20;
  const a1 = interpolate(frame, [70, 170], [0, 1], { ...clamp, easing: ease });
  const a2 = interpolate(frame, [270, 350], [0, 1], { ...clamp, easing: ease });
  const filmOffset = (a1 + a2) * span;
  const t1 = stickPoints(m, N1, `t1${m.key}`);
  const t2 = stickPoints(m, N2, `t2${m.key}`).map((q, i) => ({ x: q.x + (i % 2 ? 12 : -12), y: q.y + 14 }));
  const t3 = stickPoints(m, 4, `t3${m.key}`);
  const stuck = [...t1.map((t, i) => stuckFly(t, i, p.s, `f${m.key}${i}`)), ...t2.map((t, i) => stuckFly(t, i, p.s, `g${m.key}${i}`))];
  // دستهٔ تازه بین دو پیشروی
  t3.forEach((t, i) => {
    const st = 195 + i * 14;
    if (frame >= st) stuck.push(stuckFly(t, i, p.s, `h${m.key}${i}`, -span));
  });
  const knobAngle = a1 * 5 * 360;
  const motorAngle = a2 * 4 * 360;
  const knobS = toScreen(m, p, m.knob.x + m.knob.out, m.knob.y);
  const insetX = Math.min(knobS.x + 110, 860);
  const insetY = Math.max(knobS.y - 190, 140);
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Stage>
        <ModelDrawing m={m} p={p} cut={1} filmOffset={filmOffset} roll={0.25 + a1 * 0.3 + a2 * 0.3} knobAngle={knobAngle} id={`roll-${m.key}`} filmChildren={<FilmFlies m={m}>{stuck}</FilmFlies>} />
        <line x1={knobS.x} y1={knobS.y} x2={insetX} y2={insetY} stroke={C.bodyEdge} strokeWidth={3} opacity={Math.max(interpolate(frame, [40, 60, 200, 220], [0, 1, 1, 0], clamp), interpolate(frame, [230, 250], [0, 1], clamp))} />
        <KnobInset angle={knobAngle} op={interpolate(frame, [40, 60, 200, 220], [0, 1, 1, 0], clamp)} x={insetX} y={insetY} />
        <MotorInset angle={motorAngle} op={interpolate(frame, [230, 250], [0, 1], clamp)} x={insetX} y={insetY} />
      </Stage>
      <TextPanel>
        <RtlText size="title" delay={10}>
          پیچیدن فیلم داخل کاست دربسته
        </RtlText>
        <RtlText delay={55} icon={<CheckIcon size={40} />}>
          دستی: با چند دور چرخاندن دستگیره
        </RtlText>
        <RtlText delay={235} icon={<CheckIcon size={40} />}>
          برقی: خودکار با موتور، هر چند ساعت یک بار
        </RtlText>
        <RtlText delay={300} icon={<CheckIcon size={40} color={C.brand} />} weight={700} color={C.brand}>
          حشره‌ها بین لایه‌های فیلم محبوس می‌شوند؛ بدون بو
        </RtlText>
      </TextPanel>
      <ModelBadge m={m} />
    </AbsoluteFill>
  );
};

// ---------- ۶. تعویض کارتریج ----------
export const SceneReplace: React.FC<SP> = ({ m }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = placement(m);
  const f = m.film;
  const span = f.y1 - f.y0 + 20;
  // ۱) پیچیدن کامل
  const wind = interpolate(frame, [20, 110], [0, 1], { ...clamp, easing: ease });
  const filmOffset = wind * span;
  const tail = f.y1 - wind * (span + 10);
  // در A کاست پشت پنل است، پس پنل نیمه‌شفاف می‌ماند تا کارتریج دیده شود
  const cut = interpolate(frame, [0, 10, 115, 140], [1, 1, 1, m.kind === "panel" ? 0.8 : 0], clamp);
  const sealed = spring({ frame: frame - 140, fps, config: { damping: 14 } });
  // ۲) بیرون آمدن
  const OUT = 330;
  const outOld = interpolate(frame, [165, 230], [0, OUT], { ...clamp, easing: ease });
  // ۳) کارتریج نو
  const inNew = interpolate(frame, [250, 320], [OUT, 0], { ...clamp, easing: ease });
  const isNew = frame >= 245;
  const click = frame - 320;
  const casMid = toScreen(m, p, 0, (m.cassette.y0 + m.cassette.y1) / 2);
  const t3 = stickPoints(m, 4, `t3${m.key}`);
  const stuck = t3.map((t, i) => stuckFly({ x: t.x, y: t.y - 60 }, i, p.s, `h${m.key}${i}`));
  const arrowOp = interpolate(frame, [160, 175, 225, 235], [0, 1, 1, 0], clamp);
  const arrowOp2 = interpolate(frame, [250, 262, 312, 320], [0, 1, 1, 0], clamp);
  const arrowX = toScreen(m, p, m.knob.x + m.knob.out + 34, 0).x;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Stage>
        <ModelDrawing
          m={m}
          p={p}
          cut={isNew ? (m.kind === "panel" ? 0.8 : 0) : cut}
          filmOffset={isNew ? 0 : filmOffset}
          filmTail={isNew ? (frame >= 320 ? undefined : f.y0 - 1) : tail}
          roll={isNew ? 0 : 0.85 + wind * 0.15}
          cartridgeOut={isNew ? inNew : outOld}
          sealed={isNew ? 0 : frame >= 140 ? sealed : 0}
          fresh={isNew}
          emptyBay={(!isNew && frame >= 160) || (isNew && frame < 320)}
          id={`rep-${m.key}`}
          filmChildren={<FilmFlies m={m}>{stuck}</FilmFlies>}
        />
        <g opacity={arrowOp}>
          <path d={`M ${arrowX} ${casMid.y - 60} L ${arrowX} ${casMid.y + 140}`} stroke={C.warn} strokeWidth={8} strokeLinecap="round" />
          <path d={`M ${arrowX - 22} ${casMid.y + 120} L ${arrowX} ${casMid.y + 155} L ${arrowX + 22} ${casMid.y + 120}`} fill="none" stroke={C.warn} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" />
        </g>
        <g opacity={arrowOp2}>
          <path d={`M ${arrowX} ${casMid.y + 160} L ${arrowX} ${casMid.y - 40}`} stroke={C.ok} strokeWidth={8} strokeLinecap="round" />
          <path d={`M ${arrowX - 22} ${casMid.y - 20} L ${arrowX} ${casMid.y - 55} L ${arrowX + 22} ${casMid.y - 20}`} fill="none" stroke={C.ok} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" />
        </g>
        {click >= 0 && click < 30 ? (
          <circle cx={casMid.x} cy={casMid.y} r={80 + click * 6} fill="none" stroke={C.ok} strokeWidth={10 - click * 0.3} opacity={interpolate(click, [0, 30], [0.9, 0], clamp)} />
        ) : null}
      </Stage>
      <TextPanel>
        <RtlText size="title" delay={8}>
          تعویض کارتریج بدون تماس
        </RtlText>
        <RtlText delay={25} icon={<StepNum n={1} active={frame < 160} />} weight={frame < 160 ? 700 : 400}>
          فیلم باقی‌مانده کامل داخل کاست پیچیده می‌شود
        </RtlText>
        <RtlText delay={150} icon={<StepNum n={2} active={frame >= 160 && frame < 245} />} weight={frame >= 160 && frame < 245 ? 700 : 400}>
          کارتریج پلمب‌شده از پایین بیرون می‌آید
        </RtlText>
        <RtlText delay={245} icon={<StepNum n={3} active={frame >= 245} />} weight={frame >= 245 ? 700 : 400}>
          کارتریج نو جا زده می‌شود
        </RtlText>
        <RtlText delay={320} size="small" color={C.muted}>
          کارتریج پر همراه پسماند عفونی جمع‌آوری و بی‌خطرسازی می‌شود
        </RtlText>
      </TextPanel>
      <ModelBadge m={m} />
    </AbsoluteFill>
  );
};

const StepNum: React.FC<{ n: number; active: boolean }> = ({ n, active }) => (
  <div
    style={{
      width: 48,
      height: 48,
      borderRadius: 48,
      background: active ? C.brand : "#E3E9EC",
      color: active ? "#fff" : C.muted,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontFamily,
      fontWeight: 700,
      fontSize: 30,
    }}
  >
    {fa(n)}
  </div>
);

// ---------- ۷. مشخصات ----------
export const SceneSpecs: React.FC<SP> = ({ m }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pImg = spring({ frame: frame - 5, fps, config: { damping: 200 }, durationInFrames: 30 });
  const zoom = interpolate(frame, [0, 330], [1.02, 1.1]);
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <div style={{ position: "absolute", left: 60, top: 40, width: 800, height: 1000, borderRadius: 40, overflow: "hidden", opacity: pImg, background: "#EEF2F3" }}>
        <Img src={staticFile(`renders/${m.render}-inside.png`)} style={{ width: "100%", height: "100%", objectFit: "contain", transform: `scale(${zoom})` }} />
      </div>
      <TextPanel>
        <RtlText size="title" delay={8} color={C.brand}>
          <span>مشخصات </span>
          <span style={{ direction: "ltr", unicodeBidi: "isolate" }}>{m.id}</span>
        </RtlText>
        {m.specs.map((s, i) => (
          <RtlText key={i} delay={40 + i * 40} icon={<CheckIcon size={40} />}>
            {s}
          </RtlText>
        ))}
        <RtlText delay={210} weight={700}>
          {m.places}
        </RtlText>
      </TextPanel>
    </AbsoluteFill>
  );
};

// ---------- ۸. پایان ----------
export const SceneOutro: React.FC<SP> = ({ m }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = (d: number) => spring({ frame: frame - d, fps, config: { damping: 200 }, durationInFrames: 22 });
  return (
    <AbsoluteFill style={{ background: C.brand, alignItems: "center", justifyContent: "center" }}>
      <div dir="rtl" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 22, fontFamily, color: "#fff" }}>
        <div style={{ background: "#fff", borderRadius: 32, padding: "22px 36px", opacity: p(5), transform: `scale(${0.9 + 0.1 * p(5)})` }}>
          <Img src={staticFile("logo.jpg")} style={{ height: 210, display: "block" }} />
        </div>
        <div style={{ fontSize: 120, fontWeight: 700, direction: "ltr", opacity: p(30), letterSpacing: 3 }}>{m.id}</div>
        <div style={{ fontSize: 56, opacity: p(50) }}>{COMPANY_FULL}</div>
        <div style={{ fontSize: 48, opacity: p(70) * 0.9 }}>{CONTACT}</div>
      </div>
    </AbsoluteFill>
  );
};
