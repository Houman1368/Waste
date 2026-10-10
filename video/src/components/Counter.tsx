import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { useLayout } from "../layout";
import { C } from "../theme";
import { fa } from "../utils";
import { fontFamily } from "./RtlText";

export const Counter: React.FC<{ value: number; bumpAt: number; opacity?: number }> = ({ value, bumpAt, opacity = 1 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { v, font } = useLayout();
  const bump = 1 + 0.12 * (1 - spring({ frame: frame - bumpAt, fps, config: { damping: 10 } }));
  return (
    <div
      dir="rtl"
      style={{
        position: "absolute",
        top: v ? 48 : 44,
        ...(v ? { right: 56 } : { left: 56 }),
        fontFamily,
        fontSize: font.small,
        color: C.text,
        background: "#fff",
        border: `2px solid ${C.bodyEdge}`,
        borderRadius: 24,
        padding: "12px 30px",
        display: "flex",
        gap: 14,
        alignItems: "center",
        opacity,
        boxShadow: "0 8px 24px rgba(31,42,48,0.06)",
      }}
    >
      <span>حشره‌های گرفته‌شده:</span>
      <span style={{ fontWeight: 700, color: C.brand, display: "inline-block", minWidth: font.small * 0.8, textAlign: "center", transform: `scale(${bump})` }}>
        {fa(value)}
      </span>
    </div>
  );
};
