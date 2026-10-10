import { random } from "remotion";
import { DevicePlacement, devToWorld } from "../layout";
import { angleOf, flight, hover, Pt } from "../utils";

// مگس‌های صحنهٔ ۳ و ۴: از لبهٔ قاب می‌آیند، جلوی دستگاه پرسه می‌زنند و یکی‌یکی می‌چسبند.
export const SWARM_N = 9;

// نقطهٔ پرسه در مختصات دستگاه
const HOVER_DEV: Pt[] = [
  { x: -70, y: 150 },
  { x: 370, y: 190 },
  { x: -40, y: 330 },
  { x: 380, y: 360 },
  { x: 90, y: -50 },
  { x: 230, y: -40 },
  { x: -80, y: 470 },
  { x: 360, y: 520 },
  { x: 150, y: 660 },
];

// جای چسبیدن روی سطح چسبی (مختصات دستگاه)
export const STICK_DEV: Pt[] = [
  { x: 95, y: 160 },
  { x: 190, y: 205 },
  { x: 120, y: 265 },
  { x: 205, y: 300 },
  { x: 85, y: 340 },
  { x: 160, y: 365 },
  { x: 210, y: 400 },
  { x: 140, y: 150 },
  { x: 100, y: 410 },
];

export const STICK_ANGLE = (i: number) => -90 + (random(`stick-${i}`) - 0.5) * 120;

const startPoint = (i: number, W: number, H: number): Pt => {
  const side = i % 4;
  const r = random(`edge-${i}`);
  if (side === 0) return { x: -60, y: H * (0.15 + r * 0.6) };
  if (side === 1) return { x: W * (0.1 + r * 0.4), y: -60 };
  if (side === 2) return { x: W * (0.05 + r * 0.4), y: H + 60 };
  return { x: W * 0.55, y: -60 + r * 0 };
};

export const ARRIVE = (i: number) => ({ start: 30 + i * 16, dur: 90 + Math.round(random(`dur-${i}`) * 30) });
export const LAND = (i: number) => ({ start: 50 + i * 24, dur: 22 });

const hoverWorld = (dev: DevicePlacement, i: number) => devToWorld(dev, HOVER_DEV[i]);

/** موقعیت مگس i در فریم t (t از ابتدای صحنهٔ ۳ شمرده می‌شود). */
export const swarmPos = (
  dev: DevicePlacement,
  i: number,
  t: number,
  W: number,
  H: number,
): { p: Pt; angle: number; stuck: boolean; visible: boolean } => {
  const a = ARRIVE(i);
  const l = LAND(i);
  const landStart = 300 + l.start;
  const landEnd = landStart + l.dur;
  const seed = `sw-${i}`;
  const at = (tt: number): Pt => {
    if (tt < a.start) return startPoint(i, W, H);
    if (tt < a.start + a.dur) {
      const target = hover(seed, hoverWorld(dev, i), a.start + a.dur);
      return flight(seed, startPoint(i, W, H), target, (tt - a.start) / a.dur);
    }
    if (tt < landStart) return hover(seed, hoverWorld(dev, i), tt);
    const from = hover(seed, hoverWorld(dev, i), landStart);
    return flight(seed + "-l", from, devToWorld(dev, STICK_DEV[i]), (tt - landStart) / l.dur, 0.4);
  };
  const p = at(t);
  const stuck = t >= landEnd;
  return {
    p,
    angle: angleOf(p, at(t + 1), -90),
    stuck,
    visible: t >= a.start,
  };
};
