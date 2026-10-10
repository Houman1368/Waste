import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { fontFamily } from "../fonts";
import { C } from "../theme";
import { useLayout } from "../layout";
import { clamp } from "../utils";

export { fontFamily };

type Size = "title" | "body" | "small";

export const RtlText: React.FC<{
  children: React.ReactNode;
  size?: Size;
  color?: string;
  weight?: 400 | 700;
  delay?: number;
  icon?: React.ReactNode;
  style?: React.CSSProperties;
  /** اگر داده شود، متن در این فریم محو می‌شود */
  outAt?: number;
}> = ({ children, size = "body", color = C.text, weight, delay = 0, icon, style, outAt }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { font } = useLayout();
  const p = spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 22 });
  const out = outAt === undefined ? 1 : interpolate(frame, [outAt, outAt + 12], [1, 0], clamp);
  const fs = font[size];
  return (
    <div
      dir="rtl"
      style={{
        fontFamily,
        fontSize: fs,
        fontWeight: weight ?? (size === "title" ? 700 : 400),
        lineHeight: 1.45,
        textAlign: "right",
        color,
        width: "100%",
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        gap: fs * 0.4,
        opacity: p * out,
        transform: `translateY(${(1 - p) * 24}px)`,
        ...style,
      }}
    >
      {icon ? <div style={{ flexShrink: 0, display: "flex" }}>{icon}</div> : null}
      <div style={{ flex: 1, minWidth: 0 }}>{children}</div>
    </div>
  );
};

/** ناحیهٔ متن استاندارد هر صحنه؛ در نسخهٔ افقی سمت راست، در نسخهٔ عمودی زیر تصویر */
export const TextPanel: React.FC<{
  children: React.ReactNode;
  card?: boolean;
  opacity?: number;
  justify?: "center" | "flex-start";
}> = ({ children, card = true, opacity = 1, justify }) => {
  const { textBox, v } = useLayout();
  return (
    <div
      style={{
        position: "absolute",
        left: textBox.left,
        top: textBox.top,
        width: textBox.width,
        height: textBox.height,
        display: "flex",
        flexDirection: "column",
        justifyContent: justify ?? (v ? "flex-start" : "center"),
        opacity,
      }}
    >
      <div
        dir="rtl"
        style={{
          display: "flex",
          flexDirection: "column",
          gap: v ? 26 : 22,
          padding: card ? (v ? "44px 52px" : "48px 56px") : 0,
          background: card ? "rgba(255,255,255,0.94)" : "transparent",
          borderRadius: 32,
          border: card ? `2px solid ${C.bodyEdge}` : "none",
          boxShadow: card ? "0 10px 30px rgba(31,42,48,0.06)" : "none",
        }}
      >
        {children}
      </div>
    </div>
  );
};

// آیکون‌های ساده برای فهرست‌ها
export const CrossIcon: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 40 40">
    <circle cx={20} cy={20} r={19} fill={C.warn} />
    <path d="M13 13 L27 27 M27 13 L13 27" stroke="#fff" strokeWidth={4.5} strokeLinecap="round" />
  </svg>
);

export const CheckIcon: React.FC<{ size: number; color?: string }> = ({ size, color = C.ok }) => (
  <svg width={size} height={size} viewBox="0 0 40 40">
    <circle cx={20} cy={20} r={19} fill={color} />
    <path d="M11 21 L17.5 27.5 L29 14" stroke="#fff" strokeWidth={4.5} fill="none" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const DotIcon: React.FC<{ size: number; color?: string }> = ({ size, color = C.uv }) => (
  <svg width={size} height={size} viewBox="0 0 40 40">
    <circle cx={20} cy={20} r={10} fill={color} />
    <circle cx={20} cy={20} r={17} fill="none" stroke={color} strokeOpacity={0.35} strokeWidth={4} />
  </svg>
);
