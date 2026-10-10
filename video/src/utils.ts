import { Easing, interpolate, random } from "remotion";

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const fa = (n: number | string) =>
  String(n).replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[Number(d)]);

export type Pt = { x: number; y: number };

export const ease = Easing.inOut(Easing.cubic);

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// مسیر پرواز با نویز سینوسی (مارپیچ طبیعی)؛ نویز در دو سر مسیر صفر است.
export const flight = (seed: string, from: Pt, to: Pt, t: number, wobbleScale = 1): Pt => {
  const tt = Math.min(1, Math.max(0, t));
  const e = ease(tt);
  const amp = (30 + random(seed + "-a") * 50) * wobbleScale;
  const freq = 1.5 + random(seed + "-f") * 2;
  const ph = random(seed + "-p") * Math.PI * 2;
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const len = Math.max(1, Math.hypot(dx, dy));
  const nx = -dy / len;
  const ny = dx / len;
  const env = Math.sin(Math.PI * tt);
  const w = env * (amp * Math.sin(tt * freq * Math.PI * 2 + ph) + amp * 0.3 * Math.sin(tt * 11 + ph * 2));
  return { x: lerp(from.x, to.x, e) + nx * w, y: lerp(from.y, to.y, e) + ny * w };
};

// پرسه‌زدن کوچک دور یک نقطه
export const hover = (seed: string, c: Pt, frame: number, r = 1): Pt => {
  const ph = random(seed + "-h") * Math.PI * 2;
  return {
    x: c.x + r * (22 * Math.sin(frame * 0.085 + ph) + 9 * Math.sin(frame * 0.21 + ph * 3)),
    y: c.y + r * (16 * Math.cos(frame * 0.105 + ph) + 6 * Math.sin(frame * 0.27 + ph)),
  };
};

export const angleOf = (a: Pt, b: Pt, fallback = 0) => {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  if (Math.hypot(dx, dy) < 0.01) return fallback;
  return (Math.atan2(dy, dx) * 180) / Math.PI;
};

export const fadeIn = (frame: number, start: number, dur = 15) =>
  interpolate(frame, [start, start + dur], [0, 1], clamp);
