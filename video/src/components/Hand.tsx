import React from "react";
import { C } from "../theme";

/** دست کارتونی با دستکش آبی؛ مبدأ = نوک انگشت اشاره، انگشت رو به بالا */
export const Hand: React.FC<{ x: number; y: number; scale?: number; rotate?: number; opacity?: number }> = ({
  x,
  y,
  scale = 1,
  rotate = 0,
  opacity = 1,
}) => (
  <g transform={`translate(${x} ${y}) rotate(${rotate}) scale(${scale})`} opacity={opacity}>
    {/* آستین */}
    <rect x={-50} y={176} width={112} height={900} rx={20} fill={C.sleeve} />
    {/* مچ دستکش */}
    <rect x={-44} y={146} width={100} height={46} rx={14} fill={C.gloveDark} />
    {/* انگشت‌های جمع‌شده */}
    <rect x={12} y={58} width={26} height={52} rx={13} fill={C.glove} stroke={C.gloveDark} strokeWidth={3} />
    <rect x={32} y={66} width={24} height={48} rx={12} fill={C.glove} stroke={C.gloveDark} strokeWidth={3} />
    {/* کف دست */}
    <rect x={-40} y={70} width={94} height={92} rx={30} fill={C.glove} stroke={C.gloveDark} strokeWidth={3} />
    {/* شست */}
    <rect x={-62} y={92} width={30} height={60} rx={15} fill={C.glove} stroke={C.gloveDark} strokeWidth={3} transform="rotate(-28 -47 122)" />
    {/* انگشت اشاره */}
    <rect x={-13} y={0} width={27} height={96} rx={13.5} fill={C.glove} stroke={C.gloveDark} strokeWidth={3} />
    <path d="M-5 14 Q1 10 7 14" stroke="#fff" strokeOpacity={0.5} strokeWidth={3} fill="none" strokeLinecap="round" />
  </g>
);
