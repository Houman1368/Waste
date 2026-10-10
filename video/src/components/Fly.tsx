import React from "react";
import { random, useCurrentFrame } from "remotion";
import { C } from "../theme";

export const Fly: React.FC<{
  x: number;
  y: number;
  angle?: number;
  size?: number;
  flapping?: boolean;
  opacity?: number;
  seed?: string;
}> = ({ x, y, angle = 0, size = 1, flapping = true, opacity = 1, seed = "fly" }) => {
  const frame = useCurrentFrame();
  const ph = random(seed + "-wing") * 6;
  // بال‌زدن سریع؛ وقتی می‌چسبد ثابت می‌ماند
  const flap = flapping ? 0.25 + 0.75 * Math.abs(Math.sin(frame * 1.7 + ph)) : 1;
  const wingAngle = flapping ? 20 + 25 * flap : 38;
  return (
    <g transform={`translate(${x} ${y}) rotate(${angle}) scale(${size})`} opacity={opacity}>
      {!flapping ? (
        <g stroke={C.insect} strokeWidth={1.4} strokeLinecap="round">
          <line x1={2} y1={3} x2={6} y2={10} />
          <line x1={-2} y1={3} x2={-4} y2={10} />
          <line x1={-6} y1={3} x2={-11} y2={9} />
          <line x1={2} y1={-3} x2={6} y2={-10} />
          <line x1={-2} y1={-3} x2={-4} y2={-10} />
          <line x1={-6} y1={-3} x2={-11} y2={-9} />
        </g>
      ) : null}
      <g transform={`rotate(${-wingAngle})`}>
        <ellipse cx={-8} cy={-1} rx={10} ry={4.5 * (flapping ? 0.5 + 0.5 * flap : 1)} fill="#DCE3EA" fillOpacity={0.6} stroke={C.insect} strokeOpacity={0.6} strokeWidth={0.9} />
      </g>
      <g transform={`rotate(${wingAngle})`}>
        <ellipse cx={-8} cy={1} rx={10} ry={4.5 * (flapping ? 0.5 + 0.5 * flap : 1)} fill="#DCE3EA" fillOpacity={0.6} stroke={C.insect} strokeOpacity={0.6} strokeWidth={0.9} />
      </g>
      <ellipse cx={-2} cy={0} rx={9} ry={5.2} fill={C.insect} />
      <circle cx={8} cy={0} r={4.3} fill={C.insect} />
      <circle cx={9.5} cy={-2.2} r={1.5} fill="#7A2E1E" />
      <circle cx={9.5} cy={2.2} r={1.5} fill="#7A2E1E" />
    </g>
  );
};
