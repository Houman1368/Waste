import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";
import { Corridor, OldZapper } from "../components/Corridor";
import { Fly } from "../components/Fly";
import { CrossIcon, RtlText, TextPanel } from "../components/RtlText";
import { useLayout } from "../layout";
import { C } from "../theme";
import { angleOf, clamp, flight, Pt } from "../utils";

const HITS = [
  { start: 10, dur: 55, from: { x: -0.03, y: 0.22 }, hit: { x: -60, y: -20 } },
  { start: 45, dur: 60, from: { x: 1.1, y: -0.1 }, hit: { x: 50, y: 10 } },
  { start: 85, dur: 55, from: { x: -0.1, y: 0.9 }, hit: { x: -10, y: 40 } },
  { start: 120, dur: 60, from: { x: 0.6, y: 1.1 }, hit: { x: 90, y: -40 } },
  { start: 155, dur: 50, from: { x: -0.05, y: 0.2 }, hit: { x: -100, y: 30 } },
];

export const Scene1Problem: React.FC = () => {
  const frame = useCurrentFrame();
  const { v, W, H, dev, font } = useLayout();
  const z = { cx: dev.cx, cy: v ? 430 : 400, s: v ? 1.25 : 1.15 };
  const iconSize = font.body * 0.9;

  const flies: React.ReactNode[] = [];
  const effects: React.ReactNode[] = [];
  let lastHit = -999;
  HITS.forEach((h, i) => {
    const from: Pt = { x: h.from.x * W, y: h.from.y * H };
    const to: Pt = { x: z.cx + h.hit.x * z.s, y: z.cy + h.hit.y * z.s };
    const end = h.start + h.dur;
    if (frame >= h.start && frame < end) {
      const t = (frame - h.start) / h.dur;
      const p = flight(`s1-${i}`, from, to, t);
      const p2 = flight(`s1-${i}`, from, to, t + 0.01);
      flies.push(<Fly key={i} x={p.x} y={p.y} angle={angleOf(p, p2)} size={1.4} seed={`s1-${i}`} />);
    }
    const since = frame - end;
    if (since >= 0) lastHit = Math.max(lastHit, end);
    if (since >= 0 && since < 60) {
      // جرقه
      const sp = interpolate(since, [0, 4, 10], [0, 1, 0], clamp);
      effects.push(
        <g key={`spark${i}`} transform={`translate(${to.x} ${to.y})`} opacity={sp}>
          <circle r={26} fill="#FFE08A" opacity={0.7} />
          {Array.from({ length: 8 }).map((_, k) => {
            const a = (k / 8) * Math.PI * 2;
            return (
              <line key={k} x1={Math.cos(a) * 12} y1={Math.sin(a) * 12} x2={Math.cos(a) * 44} y2={Math.sin(a) * 44} stroke={k % 2 ? C.warn : "#F2B33D"} strokeWidth={5} strokeLinecap="round" />
            );
          })}
        </g>,
      );
      // ذرات پخش‌شده
      for (let k = 0; k < 14; k++) {
        const a = random(`p${i}-${k}`) * Math.PI * 2;
        const sp2 = 2 + random(`ps${i}-${k}`) * 5;
        const t = since;
        const px = to.x + Math.cos(a) * sp2 * t;
        const py = to.y + Math.sin(a) * sp2 * t + 0.06 * t * t;
        effects.push(
          <circle key={`pt${i}-${k}`} cx={px} cy={py} r={2.5 + random(`pr${i}-${k}`) * 3} fill={k % 3 === 0 ? C.warn : C.insect} opacity={interpolate(t, [0, 55], [0.9, 0], clamp)} />,
        );
      }
    }
  });

  // خطوط موج‌دار «بو»
  const firstHit = HITS[0].start + HITS[0].dur;
  const smellOn = lastHit < 0 ? 0 : interpolate(frame, [firstHit, firstHit + 20], [0, 1], clamp);
  const smell = [-70, 0, 70].map((dx, i) => {
    const cyc = ((frame + i * 25) % 75) / 75;
    const baseY = z.cy - 120 * z.s - cyc * 160;
    const d = Array.from({ length: 13 })
      .map((_, k) => {
        const yy = baseY - k * 9;
        const xx = z.cx + dx * z.s + Math.sin(k * 0.9 + frame * 0.15 + i) * 12;
        return `${k === 0 ? "M" : "L"} ${xx} ${yy}`;
      })
      .join(" ");
    return <path key={i} d={d} fill="none" stroke={C.warn} strokeWidth={6} strokeLinecap="round" opacity={smellOn * Math.sin(cyc * Math.PI) * 0.8} />;
  });

  const flash = effects.length > 0 ? 1 : 0;

  return (
    <AbsoluteFill>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <Corridor />
        <OldZapper cx={z.cx} cy={z.cy} s={z.s} flash={flash} />
        {smell}
        {effects}
        {flies}
      </svg>
      <TextPanel>
        <RtlText size="title" delay={8}>
          حشره‌کش‌های فعلی در بیمارستان…
        </RtlText>
        <RtlText delay={75} icon={<CrossIcon size={iconSize} />} color={C.warn} weight={700}>
          بوی بد
        </RtlText>
        <RtlText delay={115} icon={<CrossIcon size={iconSize} />} color={C.warn} weight={700}>
          پخش ذرات حشره
        </RtlText>
        <RtlText delay={155} icon={<CrossIcon size={iconSize} />} color={C.warn} weight={700}>
          تماس مستقیم هنگام تمیزکاری
        </RtlText>
      </TextPanel>
    </AbsoluteFill>
  );
};
