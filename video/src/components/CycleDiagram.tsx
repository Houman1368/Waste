import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { useLayout } from "../layout";
import { C } from "../theme";
import { clamp, fa } from "../utils";
import { fontFamily } from "./RtlText";

export const STATIONS = [
  "نصب در بیمارستان",
  "سرویس دوره‌ای و تعویض کاست",
  "جمع‌آوری کاست‌ها همراه پسماند عفونی",
  "بی‌خطرسازی با اتوکلاو",
];

type Rect = { x: number; y: number; w: number; h: number };

// زمان ظاهر شدن ایستگاه‌ها و رسم فلش‌ها
const ST = (i: number) => 15 + i * 55;
const AR = (i: number) => ({ start: ST(i) + 25, dur: 28 });

const Arrow: React.FC<{ d: string; len: number; progress: number }> = ({ d, len, progress }) => (
  <g opacity={progress > 0 ? 1 : 0}>
    <path d={d} fill="none" stroke={C.brand} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - progress)} markerEnd={progress > 0.97 ? "url(#arrowhead)" : undefined} />
  </g>
);

export const CycleDiagram: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { v, W, H, font } = useLayout();

  let rects: Rect[];
  let arrows: { d: string; len: number }[];
  if (v) {
    const x = 170, w = 854, h = 168, gap = 56, y0 = 350;
    rects = [0, 1, 2, 3].map((i) => ({ x, y: y0 + i * (h + gap), w, h }));
    const cx = x + w / 2;
    arrows = [0, 1, 2].map((i) => {
      const a = rects[i].y + h + 8;
      const b = rects[i + 1].y - 14;
      return { d: `M ${cx} ${a} L ${cx} ${b}`, len: b - a };
    });
    const y4 = rects[3].y + h / 2;
    const y1 = rects[0].y + h / 2;
    arrows.push({ d: `M ${x - 8} ${y4} L ${x - 70} ${y4} L ${x - 70} ${y1} L ${x - 20} ${y1}`, len: 62 + (y4 - y1) + 50 });
  } else {
    const w = 500, h = 200;
    const xr = 1340, xl = 760, yt = 270, yb = 640;
    rects = [
      { x: xr, y: yt, w, h },
      { x: xl, y: yt, w, h },
      { x: xl, y: yb, w, h },
      { x: xr, y: yb, w, h },
    ];
    const my = (r: Rect) => r.y + r.h / 2;
    const mx = (r: Rect) => r.x + r.w / 2;
    arrows = [
      { d: `M ${xr - 8} ${my(rects[0])} L ${xl + w + 14} ${my(rects[0])}`, len: xr - xl - w - 22 },
      { d: `M ${mx(rects[1])} ${yt + h + 8} L ${mx(rects[1])} ${yb - 14}`, len: yb - yt - h - 22 },
      { d: `M ${xl + w + 8} ${my(rects[2])} L ${xr - 14} ${my(rects[2])}`, len: xr - xl - w - 22 },
      { d: `M ${mx(rects[3])} ${yb - 8} L ${mx(rects[3])} ${yt + h + 14}`, len: yb - yt - h - 22 },
    ];
  }

  const fs = v ? font.small : font.small;
  return (
    <>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <marker id="arrowhead" viewBox="0 0 10 10" refX={3} refY={5} markerWidth={4} markerHeight={4} orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={C.brand} />
          </marker>
        </defs>
        {arrows.map((a, i) => (
          <Arrow key={i} d={a.d} len={a.len} progress={interpolate(frame, [AR(i).start, AR(i).start + AR(i).dur], [0, 1], clamp)} />
        ))}
      </svg>
      {rects.map((r, i) => {
        const p = spring({ frame: frame - ST(i), fps, config: { damping: 200 }, durationInFrames: 20 });
        const badge = fs * 1.3;
        return (
          <div
            key={i}
            dir="rtl"
            style={{
              position: "absolute",
              left: r.x,
              top: r.y,
              width: r.w,
              height: r.h,
              boxSizing: "border-box",
              background: "#fff",
              border: `3px solid ${i === 3 ? C.brand : C.bodyEdge}`,
              borderRadius: 28,
              display: "flex",
              alignItems: "center",
              gap: 20,
              padding: "0 30px",
              fontFamily,
              fontSize: fs,
              fontWeight: 700,
              lineHeight: 1.3,
              color: C.text,
              textAlign: "right",
              opacity: p,
              transform: `scale(${0.92 + 0.08 * p})`,
              boxShadow: "0 8px 22px rgba(31,42,48,0.06)",
            }}
          >
            <div
              style={{
                flexShrink: 0,
                width: badge,
                height: badge,
                borderRadius: badge,
                background: C.brand,
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: fs * 0.85,
              }}
            >
              {fa(i + 1)}
            </div>
            <div style={{ flex: 1 }}>{STATIONS[i]}</div>
          </div>
        );
      })}
    </>
  );
};
