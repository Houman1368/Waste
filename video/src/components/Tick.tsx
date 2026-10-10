import React from "react";
import { interpolate, spring } from "remotion";
import { C } from "../theme";
import { clamp } from "../utils";

/** تیک سبز کوچکی که لحظه‌ای کنار حشرهٔ گرفته‌شده ظاهر می‌شود */
export const Tick: React.FC<{ x: number; y: number; since: number; fps: number; size?: number }> = ({ x, y, since, fps, size = 1 }) => {
  if (since < 0 || since > 40) return null;
  const pop = spring({ frame: since, fps, config: { damping: 12, stiffness: 200 } });
  const op = interpolate(since, [28, 40], [1, 0], clamp);
  return (
    <g transform={`translate(${x} ${y}) scale(${pop * size})`} opacity={op}>
      <circle r={13} fill={C.ok} />
      <path d="M-6 0 L-2 5 L7 -5" stroke="#fff" strokeWidth={3.2} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </g>
  );
};
