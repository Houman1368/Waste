import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { useLayout } from "../layout";
import { C } from "../theme";
import { clamp, ease, fa } from "../utils";
import { fontFamily } from "./RtlText";

const DATA = [
  { label: "اورژانس", value: 12 },
  { label: "آشپزخانه", value: 27 },
  { label: "بخش داخلی", value: 8 },
];

/** کارت داشبورد: تعداد حشره در هفته به تفکیک بخش */
export const MiniDashboard: React.FC<{ delay: number; box: { left: number; top: number; width: number; height: number } }> = ({ delay, box }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { font } = useLayout();
  const p = spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 22 });
  const max = 30;
  const fs = font.small;
  return (
    <div
      dir="rtl"
      style={{
        position: "absolute",
        ...box,
        boxSizing: "border-box",
        background: "#fff",
        border: `2px solid ${C.bodyEdge}`,
        borderRadius: 32,
        padding: "36px 40px",
        fontFamily,
        color: C.text,
        opacity: p,
        transform: `translateY(${(1 - p) * 30}px)`,
        display: "flex",
        flexDirection: "column",
        gap: 20,
        boxShadow: "0 10px 30px rgba(31,42,48,0.06)",
      }}
    >
      <div style={{ fontSize: fs, fontWeight: 700, lineHeight: 1.35, textAlign: "right" }}>گزارش برای کمیتهٔ کنترل عفونت</div>
      <div style={{ fontSize: fs, color: C.muted, lineHeight: 1.35, textAlign: "right" }}>تعداد حشره در هفته به تفکیک بخش</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 22, marginTop: 10, flex: 1, justifyContent: "center" }}>
        {DATA.map((d, i) => {
          const g = interpolate(frame, [delay + 20 + i * 10, delay + 55 + i * 10], [0, 1], { ...clamp, easing: ease });
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 18 }}>
              <div style={{ width: fs * 5, flexShrink: 0, fontSize: fs, textAlign: "right", whiteSpace: "nowrap" }}>{d.label}</div>
              <div style={{ flex: 1, height: fs * 0.9, background: "#EEF2F4", borderRadius: 10, position: "relative" }}>
                <div
                  style={{
                    position: "absolute",
                    right: 0,
                    top: 0,
                    bottom: 0,
                    width: `${(d.value / max) * 100 * g}%`,
                    background: i === 1 ? C.warn : C.brand,
                    borderRadius: 10,
                  }}
                />
              </div>
              <div style={{ width: fs * 1.4, flexShrink: 0, fontSize: fs, fontWeight: 700, textAlign: "right", opacity: g }}>{fa(Math.round(d.value * g))}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
