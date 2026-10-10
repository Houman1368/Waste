import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { PlacedDevice } from "../components/Device";
import { fontFamily } from "../components/RtlText";
import { COMPANY_NAME, CONTACT, PRODUCT_NAME } from "../config";
import { useLayout } from "../layout";
import { C } from "../theme";
import { clamp } from "../utils";

const Icon: React.FC<{ kind: number; size: number }> = ({ kind, size }) => (
  <svg width={size} height={size} viewBox="0 0 40 40">
    <circle cx={20} cy={20} r={19} fill={C.brand} />
    <g stroke="#fff" strokeWidth={2.8} fill="none" strokeLinecap="round" strokeLinejoin="round">
      {kind === 0 ? (
        <>
          <path d="M10 17 H15 L21 12 V28 L15 23 H10 Z" fill="#fff" />
          <path d="M25 16 L31 24 M31 16 L25 24" />
        </>
      ) : kind === 1 ? (
        <>
          <path d="M14 28 Q10 23 14 18 Q18 13 14 9" />
          <path d="M22 28 Q18 23 22 18 Q26 13 22 9" />
          <path d="M9 31 L31 9" />
        </>
      ) : kind === 2 ? (
        <>
          <path d="M15 29 V14 a2.5 2.5 0 0 1 5 0 V21 M20 13 a2.5 2.5 0 0 1 5 0 V21 M25 16 a2.5 2.5 0 0 1 5 0 V24 Q30 31 23 31 H19 Q15 31 13 27 L10 21" />
          <path d="M8 32 L32 8" />
        </>
      ) : (
        <>
          <path d="M11 30 V22 M17 30 V15 M23 30 V19 M29 30 V11" strokeWidth={4} />
        </>
      )}
    </g>
  </svg>
);

const LABELS = ["بی‌صدا", "بدون بو", "بدون تماس", "گزارش‌دهی"];

export const Scene8Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { v, W, H, font } = useLayout();
  const d = v ? { cx: 540, cy: 560, s: 1.05 } : { cx: 960, cy: 500, s: 1.1 };
  const greenBg = interpolate(frame, [100, 130], [0, 1], clamp);
  const fadeOut = 1 - interpolate(frame, [95, 120], [0, 1], clamp);
  const fs = font.small;

  // افقی: دو برچسب چپ و دو برچسب راست دستگاه. عمودی: شبکهٔ ۲×۲ زیر دستگاه
  const chipPos = (i: number): React.CSSProperties => {
    if (v) return { left: i % 2 === 0 ? 540 + 14 : undefined, right: i % 2 === 1 ? 540 + 14 : undefined, top: 1000 + Math.floor(i / 2) * 150 };
    const right = i < 2;
    const top = i % 2 === 0 ? 300 : 560;
    return right ? { left: 1180, top } : { right: W - 740, top };
  };

  const endP = (delay: number) => spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 22 });

  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <AbsoluteFill style={{ background: C.brand, opacity: greenBg }} />
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute", inset: 0, opacity: fadeOut }}>
        <PlacedDevice id="s8" {...d} glow />
      </svg>
      {LABELS.map((l, i) => {
        const p = spring({ frame: frame - (15 + i * 14), fps, config: { damping: 14, stiffness: 160 } });
        return (
          <div
            key={i}
            dir="rtl"
            style={{
              position: "absolute",
              ...chipPos(i),
              display: "flex",
              alignItems: "center",
              gap: 18,
              background: "#fff",
              border: `2px solid ${C.bodyEdge}`,
              borderRadius: 999,
              padding: "14px 34px 14px 20px",
              fontFamily,
              fontSize: fs,
              fontWeight: 700,
              color: C.text,
              opacity: Math.min(1, p) * fadeOut,
              transform: `scale(${0.7 + 0.3 * Math.min(1, p)})`,
              boxShadow: "0 8px 22px rgba(31,42,48,0.08)",
              whiteSpace: "nowrap",
            }}
          >
            <Icon kind={i} size={fs * 1.3} />
            <span>{l}</span>
          </div>
        );
      })}
      {/* متن پایانی روی زمینهٔ برند */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", padding: v ? 56 : 80 }}>
        <div dir="rtl" style={{ fontFamily, color: "#fff", textAlign: "right", maxWidth: W - (v ? 112 : 160) }}>
          <div style={{ fontSize: v ? 110 : 110, fontWeight: 700, lineHeight: 1.3, opacity: endP(125), transform: `translateY(${(1 - endP(125)) * 30}px)` }}>{PRODUCT_NAME}</div>
          <div style={{ fontSize: v ? 60 : 52, lineHeight: 1.5, marginTop: 20, opacity: endP(145) }}>محصول {COMPANY_NAME}</div>
          <div style={{ fontSize: v ? 60 : 52, lineHeight: 1.5, marginTop: 10, opacity: endP(160) * 0.9 }}>{CONTACT}</div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
