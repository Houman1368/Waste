import { useVideoConfig } from "remotion";
import { Pt } from "./utils";

export type DevicePlacement = { cx: number; cy: number; s: number };

// دستگاه در مختصات خودش 300×600 است؛ این تابع نقطهٔ دستگاه را به مختصات قاب می‌برد.
export const devToWorld = (d: DevicePlacement, p: Pt): Pt => ({
  x: d.cx + (p.x - 150) * d.s,
  y: d.cy + (p.y - 300) * d.s,
});

export const useLayout = () => {
  const { width, height } = useVideoConfig();
  const v = height > width;
  return {
    v,
    W: width,
    H: height,
    // جایگاه اصلی دستگاه (صحنه‌های ۲ تا ۵)
    dev: (v ? { cx: 540, cy: 590, s: 1.3 } : { cx: 520, cy: 555, s: 1.25 }) as DevicePlacement,
    font: v ? { title: 74, body: 58, small: 56 } : { title: 64, body: 48, small: 44 },
    // ناحیهٔ متن: افقی ← سمت راست قاب؛ عمودی ← زیر دستگاه
    textBox: v
      ? { left: 56, top: 1090, width: 968, height: 770 }
      : { left: 960, top: 90, width: 880, height: 900 },
  };
};
