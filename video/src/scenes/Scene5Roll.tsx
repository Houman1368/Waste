import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame, useVideoConfig } from "remotion";
import { PlacedDevice } from "../components/Device";
import { Fly } from "../components/Fly";
import { CheckIcon, fontFamily, RtlText, TextPanel } from "../components/RtlText";
import { STICK_ANGLE, STICK_DEV, SWARM_N } from "../components/Swarm";
import { Tick } from "../components/Tick";
import { devToWorld, useLayout } from "../layout";
import { C } from "../theme";
import { angleOf, clamp, ease, flight, Pt } from "../utils";

const ADV = 340; // طول هر پیشروی فیلم (بیشتر از ارتفاع سطح چسبی)
const ADV1 = { start: 45, dur: 60 };
const ADV2 = { start: 225, dur: 60 };

const BATCH2: Pt[] = [
  { x: 110, y: 180 },
  { x: 195, y: 250 },
  { x: 90, y: 300 },
  { x: 175, y: 370 },
  { x: 130, y: 410 },
];
const B2 = (i: number) => ({ start: 112 + i * 14, dur: 48 });

const Clock: React.FC<{ size: number }> = ({ size }) => {
  const frame = useCurrentFrame();
  const a = frame * 6;
  return (
    <svg width={size} height={size} viewBox="0 0 40 40">
      <circle cx={20} cy={20} r={17} fill="#fff" stroke={C.brand} strokeWidth={3.5} />
      <line x1={20} y1={20} x2={20} y2={10} stroke={C.text} strokeWidth={3} strokeLinecap="round" transform={`rotate(${a / 12} 20 20)`} />
      <line x1={20} y1={20} x2={20} y2={6} stroke={C.brand} strokeWidth={2.4} strokeLinecap="round" transform={`rotate(${a} 20 20)`} />
      <circle cx={20} cy={20} r={2.5} fill={C.text} />
    </svg>
  );
};

export const Scene5Roll: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { v, W, H, dev, font } = useLayout();
  const a1 = interpolate(frame, [ADV1.start, ADV1.start + ADV1.dur], [0, 1], { ...clamp, easing: ease });
  const a2 = interpolate(frame, [ADV2.start, ADV2.start + ADV2.dur], [0, 1], { ...clamp, easing: ease });
  const filmOffset = (a1 + a2) * ADV;
  const roll = 18 + a1 * 6 + a2 * 6;
  const moving = (frame >= ADV1.start - 5 && frame <= ADV1.start + ADV1.dur + 10) || (frame >= ADV2.start - 5 && frame <= ADV2.start + ADV2.dur + 10);
  const arrowOp = moving ? 1 : 0;
  const flySize = 1.3;

  const filmFlies: React.ReactNode[] = [];
  // دستهٔ اول: حشره‌های صحنهٔ ۴
  for (let i = 0; i < SWARM_N; i++) {
    const p = STICK_DEV[i];
    filmFlies.push(<Fly key={`a${i}`} x={p.x} y={p.y} angle={STICK_ANGLE(i)} size={flySize / dev.s} flapping={false} seed={`sw-${i}`} />);
  }
  // دستهٔ دوم: مگس‌های تازه
  const flying: React.ReactNode[] = [];
  BATCH2.forEach((p, i) => {
    const b = B2(i);
    const end = b.start + b.dur;
    if (frame >= end) {
      filmFlies.push(<Fly key={`b${i}`} x={p.x} y={p.y - ADV} angle={-90 + (random(`b2a${i}`) - 0.5) * 100} size={flySize / dev.s} flapping={false} seed={`b2-${i}`} />);
      filmFlies.push(<Tick key={`t${i}`} x={p.x + 20} y={p.y - ADV - 18} since={frame - end} fps={fps} size={1.3 / dev.s} />);
    } else if (frame >= b.start) {
      const from: Pt = i % 2 === 0 ? { x: -60, y: H * (0.2 + 0.15 * i) } : { x: W * (0.15 + 0.1 * i), y: -60 };
      const to = devToWorld(dev, p);
      const t = (frame - b.start) / b.dur;
      const q = flight(`b2-${i}`, from, to, t);
      flying.push(<Fly key={`f${i}`} x={q.x} y={q.y} angle={angleOf(q, flight(`b2-${i}`, from, to, t + 0.02))} size={flySize} seed={`b2-${i}`} />);
    }
  });

  const iconSize = font.body * 0.85;
  const chipOp = interpolate(frame, [5, 20], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <PlacedDevice id="s5" {...dev} glow cutaway filmOffset={filmOffset} rollThickness={roll} rotateArrow={arrowOp} filmChildren={filmFlies} />
        {flying}
      </svg>
      {/* ساعت: هر چند ساعت یک بار */}
      <div
        dir="rtl"
        style={{
          position: "absolute",
          top: v ? 48 : 44,
          ...(v ? { right: 56 } : { left: 56 }),
          display: "flex",
          alignItems: "center",
          gap: 16,
          fontFamily,
          fontSize: font.small,
          color: C.text,
          background: "#fff",
          border: `2px solid ${C.bodyEdge}`,
          borderRadius: 24,
          padding: "10px 28px",
          opacity: chipOp,
        }}
      >
        <Clock size={font.small * 1.2} />
        <span style={{ whiteSpace: "nowrap" }}>هر چند ساعت، یا با پر شدن سطح</span>
      </div>
      <TextPanel>
        <RtlText size="title" delay={15}>
          حشره‌ها خودکار داخل کاست دربسته پیچیده می‌شوند
        </RtlText>
        <RtlText delay={125} icon={<CheckIcon size={iconSize} />}>
          سطح چسبی همیشه تمیز ← کارایی همیشه بالا
        </RtlText>
        <RtlText delay={240} icon={<CheckIcon size={iconSize} />}>
          بدون بو، بدون دیدن حشره‌ها
        </RtlText>
      </TextPanel>
    </AbsoluteFill>
  );
};
