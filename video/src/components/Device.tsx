import React from "react";
import { useCurrentFrame } from "remotion";
import { C } from "../theme";
import { fontFamily } from "./RtlText";

// هندسهٔ دستگاه در مختصات داخلی 300×600
export const DEV = {
  w: 300,
  h: 600,
  panel: { x: 60, y: 110, w: 180, h: 330 },
  cassette: { x: 30, y: 446, w: 240, h: 126 },
  rollCy: 509,
  button: { x: 150, y: 556 },
};

export type DeviceProps = {
  /** نمای برش؛ true/false یا عدد بین ۰ و ۱ برای انیمیشن */
  cutaway?: boolean | number;
  /** میزان حرکت فیلم چسبی به پایین (واحد دستگاه) */
  filmOffset?: number;
  /** نیم‌ضخامت قرقرهٔ جمع‌کننده */
  rollThickness?: number;
  /** روشن بودن LED؛ true/false یا شدت ۰ تا ۱ */
  glow?: boolean | number;
  /** محتوای روی فیلم (حشره‌های چسبیده) در مختصات دستگاه؛ همراه فیلم پایین می‌رود */
  filmChildren?: React.ReactNode;
  /** شفافیت فلش چرخش کنار قرقره */
  rotateArrow?: number;
  /** اگر false باشد کاست داخلی کشیده نمی‌شود و جای خالی‌اش دیده می‌شود */
  showCassette?: boolean;
  /** نشانگر سبز «روشن» */
  powerOn?: boolean;
  id: string;
};

const num = (v: boolean | number | undefined, d: number) =>
  v === undefined ? d : typeof v === "boolean" ? (v ? 1 : 0) : v;

export const Cassette: React.FC<{
  cutaway?: number;
  rollThickness?: number;
  filmOffset?: number;
  sealed?: number;
  buttonPress?: number;
  fresh?: boolean;
  labelSize?: number;
}> = ({ cutaway = 0, rollThickness = 18, filmOffset = 0, sealed = 0, buttonPress = 0, fresh = false, labelSize = 36 }) => {
  const { x, y, w, h } = DEV.cassette;
  const r = rollThickness;
  const cy = DEV.rollCy;
  const stripes = [];
  const phase = (filmOffset * 0.6) % 9;
  for (let k = -2; k < 16; k++) {
    const yy = cy - r + k * 9 + phase;
    if (yy > cy - r + 2 && yy < cy + r - 2) stripes.push(yy);
  }
  return (
    <g>
      <rect x={x} y={y} width={w} height={h} rx={18} fill={fresh ? "#6E6D68" : C.cassette} />
      <rect x={x + 6} y={y + 6} width={w - 12} height={8} rx={4} fill="#000" opacity={0.15} />
      {/* شیار دست‌گیره */}
      <rect x={x + 30} y={y + h - 22} width={w - 60} height={6} rx={3} fill="#000" opacity={0.18} />
      {/* پنجرهٔ نمای برش */}
      <g opacity={cutaway}>
        <rect x={x + 16} y={y + 18} width={w - 32} height={h - 46} rx={10} fill={C.cassetteDark} />
        <rect x={DEV.panel.x} y={y + 18} width={DEV.panel.w} height={cy - r - (y + 18)} fill={C.film} opacity={0.9} />
        <rect x={50} y={cy - r} width={200} height={r * 2} rx={Math.min(r, 14)} fill={C.film} stroke={C.filmEdge} strokeWidth={3} />
        {stripes.map((yy, i) => (
          <line key={i} x1={56} x2={244} y1={yy} y2={yy} stroke={C.filmEdge} strokeOpacity={0.45} strokeWidth={1.6} />
        ))}
        <rect x={44} y={cy - 6} width={10} height={12} rx={3} fill="#8E8C86" />
        <rect x={246} y={cy - 6} width={10} height={12} rx={3} fill="#8E8C86" />
      </g>
      {/* دکمهٔ آزادسازی */}
      <rect
        x={DEV.button.x - 22}
        y={DEV.button.y - 7 + buttonPress * 3}
        width={44}
        height={14 - buttonPress * 3}
        rx={6}
        fill={buttonPress > 0.5 ? C.ok : "#8E8C86"}
      />
      {/* برچسب پلمب */}
      {sealed > 0 ? (
        <g opacity={sealed} transform={`translate(150 ${y + 52}) scale(${0.85 + 0.15 * sealed})`}>
          <rect x={-112} y={-32} width={224} height={64} rx={12} fill="#fff" stroke={C.warn} strokeWidth={3} />
          {/* قفل */}
          <g transform="translate(-86 0)">
            <rect x={-12} y={-6} width={24} height={20} rx={4} fill={C.warn} />
            <path d="M-7 -6 V-12 A7 7 0 0 1 7 -12 V-6" fill="none" stroke={C.warn} strokeWidth={3.5} />
          </g>
          <text
            x={18}
            y={labelSize * 0.34}
            fontFamily={fontFamily}
            fontWeight={700}
            fontSize={labelSize}
            fill={C.warn}
            textAnchor="middle"
            direction="rtl"
          >
            پلمب‌شده
          </text>
        </g>
      ) : null}
    </g>
  );
};

export const Device: React.FC<DeviceProps> = ({
  cutaway,
  filmOffset = 0,
  rollThickness = 18,
  glow,
  filmChildren,
  rotateArrow = 0,
  showCassette = true,
  powerOn = true,
  id,
}) => {
  const frame = useCurrentFrame();
  const c = num(cutaway, 0);
  const g = num(glow, 1);
  const pulse = 0.6 + 0.4 * Math.sin((frame / 60) * Math.PI * 2); // دورهٔ ۲ ثانیه
  const { panel } = DEV;
  const supply = Math.max(10, 52 - rollThickness);
  const lineGap = 30;
  const lines = [];
  for (let k = -1; k < panel.h / lineGap + 1; k++) {
    lines.push(panel.y + lineGap / 2 + k * lineGap + (filmOffset % lineGap));
  }
  const clipId = `${id}-film`;
  const blurId = `${id}-blur`;
  return (
    <g>
      <defs>
        <clipPath id={clipId}>
          <rect x={panel.x} y={panel.y} width={panel.w} height={panel.h} />
        </clipPath>
        <filter id={blurId} x="-50%" y="-200%" width="200%" height="500%">
          <feGaussianBlur stdDeviation={14} />
        </filter>
      </defs>
      {/* سایهٔ نرم روی دیوار */}
      <rect x={10} y={14} width={300} height={600} rx={30} fill="#1F2A30" opacity={0.06} />
      {/* بدنه */}
      <rect x={0} y={0} width={300} height={600} rx={30} fill={C.body} stroke={C.bodyEdge} strokeWidth={4} />
      <rect x={40} y={70} width={220} height={376} rx={14} fill="#EEF2F4" />
      {/* هالهٔ LED */}
      <ellipse cx={150} cy={44} rx={150} ry={34} fill={C.uvHalo} opacity={0.4 * g * (0.55 + 0.45 * pulse)} filter={`url(#${blurId})`} />
      {/* نوار LED */}
      <rect x={30} y={24} width={240} height={40} rx={20} fill="#ECEAF7" stroke={C.bodyEdge} strokeWidth={2} />
      <rect x={42} y={33} width={216} height={22} rx={11} fill={g > 0.05 ? C.uv : "#D4D1EC"} opacity={0.35 + 0.65 * g} />
      <rect x={56} y={37} width={188} height={5} rx={2.5} fill="#fff" opacity={0.35 * g} />
      {/* نشانگر روشن */}
      <circle cx={280} cy={90} r={7} fill={powerOn ? C.ok : "#B9C3C8"} />
      {powerOn ? <circle cx={280} cy={90} r={12} fill="none" stroke={C.ok} strokeOpacity={0.3 + 0.2 * pulse} strokeWidth={3} /> : null}
      {/* رول فیلم نو */}
      <rect x={52} y={91 - supply / 2} width={196} height={supply} rx={Math.min(supply / 2, 14)} fill={C.film} stroke={C.filmEdge} strokeWidth={3} />
      <line x1={64} x2={236} y1={91 - supply / 4} y2={91 - supply / 4} stroke="#fff" strokeOpacity={0.7} strokeWidth={2.5} />
      <rect x={44} y={85} width={10} height={12} rx={3} fill="#AEB8BD" />
      <rect x={246} y={85} width={10} height={12} rx={3} fill="#AEB8BD" />
      {/* سطح چسبی */}
      <rect x={panel.x} y={panel.y} width={panel.w} height={panel.h} fill={C.film} stroke={C.filmEdge} strokeWidth={3} />
      <g clipPath={`url(#${clipId})`}>
        {lines.map((yy, i) => (
          <line key={i} x1={panel.x} x2={panel.x + panel.w} y1={yy} y2={yy} stroke={C.filmEdge} strokeOpacity={0.16} strokeWidth={2} />
        ))}
        <g transform={`translate(0 ${filmOffset})`}>{filmChildren}</g>
      </g>
      {/* جای کاست */}
      <rect x={DEV.cassette.x} y={DEV.cassette.y} width={DEV.cassette.w} height={DEV.cassette.h} rx={18} fill="#2C2B29" />
      {showCassette ? <Cassette cutaway={c} rollThickness={rollThickness} filmOffset={filmOffset} /> : null}
      {/* محافظ مشبک جلو */}
      <g opacity={1 - c}>
        {Array.from({ length: 12 }).map((_, i) => (
          <line key={`v${i}`} x1={62 + i * 16} x2={62 + i * 16} y1={106} y2={444} stroke={C.bodyEdge} strokeWidth={2} />
        ))}
        {Array.from({ length: 16 }).map((_, i) => (
          <line key={`h${i}`} x1={56} x2={244} y1={112 + i * 22} y2={112 + i * 22} stroke={C.bodyEdge} strokeWidth={1.4} opacity={0.8} />
        ))}
        <rect x={54} y={104} width={192} height={342} rx={8} fill="none" stroke="#B7C2C8" strokeWidth={4} />
      </g>
      {/* فلش چرخش کنار قرقره */}
      {rotateArrow > 0 ? (
        <g opacity={rotateArrow} transform={`translate(-38 ${DEV.rollCy}) rotate(${(filmOffset * 2) % 360})`}>
          <path d="M 0 -22 A 22 22 0 1 1 -21 7" fill="none" stroke={C.brand} strokeWidth={6} strokeLinecap="round" />
          <path d="M -30 0 L -21 14 L -10 2 Z" fill={C.brand} />
        </g>
      ) : null}
    </g>
  );
};

export const PlacedDevice: React.FC<DeviceProps & { cx: number; cy: number; s: number; opacity?: number; extraScale?: number }> = ({
  cx,
  cy,
  s,
  opacity = 1,
  extraScale = 1,
  ...rest
}) => (
  <g opacity={opacity} transform={`translate(${cx} ${cy}) scale(${s * extraScale}) translate(-150 -300)`}>
    <Device {...rest} />
  </g>
);
