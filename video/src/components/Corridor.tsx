import React from "react";
import { C } from "../theme";
import { useLayout } from "../layout";

/** راهروی سادهٔ بیمارستان: دیوار، کف، نردهٔ دیواری، در اتاق بیمار و تخت از دور */
export const Corridor: React.FC<{ opacity?: number }> = ({ opacity = 1 }) => {
  const { v, W, H } = useLayout();
  const floorY = v ? 1010 : 880;
  const railY = v ? 760 : 640;
  const door = v ? { x: 60, w: 220, top: 560 } : { x: 70, w: 230, top: 400 };
  const bed = v ? { x: 760, y: floorY, s: 0.95 } : { x: 760, y: floorY, s: 1 };
  return (
    <g opacity={opacity}>
      <rect x={0} y={0} width={W} height={H} fill={C.wall} />
      <rect x={0} y={floorY} width={W} height={H - floorY} fill={C.floor} />
      <rect x={0} y={floorY - 14} width={W} height={14} fill={C.brand} opacity={0.18} />
      <rect x={0} y={railY} width={W} height={12} rx={6} fill={C.rail} />
      {/* در اتاق بیمار */}
      <g>
        <rect x={door.x - 10} y={door.top - 10} width={door.w + 20} height={floorY - door.top + 10} fill="#E2E8EB" />
        <rect x={door.x} y={door.top} width={door.w} height={floorY - door.top} fill="#D5E6E1" stroke="#B9CBC5" strokeWidth={3} />
        <rect x={door.x + 50} y={door.top + 40} width={door.w - 100} height={110} rx={6} fill="#EEF6FA" stroke="#B9CBC5" strokeWidth={3} />
        <rect x={door.x + door.w - 46} y={door.top + 230} width={30} height={10} rx={5} fill="#8FA3AA" />
        {/* تابلوی اتاق (بدون متن) */}
        <rect x={door.x + door.w / 2 - 34} y={door.top - 70} width={68} height={40} rx={6} fill="#fff" stroke={C.bodyEdge} strokeWidth={2} />
        <rect x={door.x + door.w / 2 - 6} y={door.top - 62} width={12} height={24} fill={C.brand} opacity={0.6} />
        <rect x={door.x + door.w / 2 - 12} y={door.top - 56} width={24} height={12} fill={C.brand} opacity={0.6} />
      </g>
      {/* تخت بیمار از دور */}
      <g transform={`translate(${bed.x} ${bed.y}) scale(${bed.s})`} opacity={0.75}>
        <rect x={0} y={-118} width={14} height={92} rx={5} fill="#B3C0C6" />
        <rect x={176} y={-92} width={12} height={66} rx={5} fill="#B3C0C6" />
        <rect x={6} y={-74} width={176} height={20} rx={8} fill="#CFE1EC" />
        <rect x={10} y={-54} width={168} height={12} rx={4} fill="#B3C0C6" />
        <rect x={20} y={-42} width={8} height={28} fill="#B3C0C6" />
        <rect x={160} y={-42} width={8} height={28} fill="#B3C0C6" />
        <circle cx={24} cy={-10} r={9} fill="#9AA8AE" />
        <circle cx={164} cy={-10} r={9} fill="#9AA8AE" />
        <rect x={12} y={-84} width={44} height={14} rx={7} fill="#fff" />
      </g>
    </g>
  );
};

/** حشره‌کش برقی قدیمی (توری) */
export const OldZapper: React.FC<{ cx: number; cy: number; s: number; opacity?: number; flash?: number }> = ({
  cx,
  cy,
  s,
  opacity = 1,
  flash = 0,
}) => (
  <g transform={`translate(${cx} ${cy}) scale(${s})`} opacity={opacity}>
    <rect x={-160} y={-95} width={320} height={190} rx={16} fill="#8A969C" />
    <rect x={-142} y={-77} width={284} height={154} rx={8} fill="#2A3338" />
    <rect x={-128} y={-40} width={256} height={16} rx={8} fill="#9BB8D3" opacity={0.7 + 0.3 * flash} />
    <rect x={-128} y={20} width={256} height={16} rx={8} fill="#9BB8D3" opacity={0.7 + 0.3 * flash} />
    {Array.from({ length: 23 }).map((_, i) => (
      <line key={i} x1={-132 + i * 12} x2={-132 + i * 12} y1={-77} y2={77} stroke="#B7C2C8" strokeWidth={2} opacity={0.8} />
    ))}
    {/* سینی کثیف زیر دستگاه */}
    <rect x={-150} y={95} width={300} height={16} rx={6} fill="#6E7A80" />
    <circle cx={-90} cy={100} r={3} fill="#1F2A30" />
    <circle cx={-40} cy={102} r={2.5} fill="#1F2A30" />
    <circle cx={30} cy={99} r={3} fill="#1F2A30" />
    <circle cx={100} cy={102} r={2.5} fill="#1F2A30" />
    <rect x={-8} y={-140} width={16} height={45} fill="#8A969C" />
    <rect x={-50} y={-150} width={100} height={14} rx={7} fill="#8A969C" />
  </g>
);
