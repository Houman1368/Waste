import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Cassette, DEV, PlacedDevice } from "../components/Device";
import { Hand } from "../components/Hand";
import { RtlText, TextPanel } from "../components/RtlText";
import { useLayout } from "../layout";
import { C } from "../theme";
import { clamp, ease, fa } from "../utils";

const Step: React.FC<{ n: number; active: boolean; children: React.ReactNode; delay: number }> = ({ n, active, children, delay }) => {
  const { font } = useLayout();
  const s = font.small * 1.1;
  return (
    <RtlText
      size="small"
      delay={delay}
      color={active ? C.text : C.muted}
      weight={active ? 700 : 400}
      icon={
        <div
          style={{
            width: s,
            height: s,
            borderRadius: s,
            background: active ? C.brand : "#E3E9EC",
            color: active ? "#fff" : C.muted,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: font.small * 0.75,
            fontWeight: 700,
          }}
        >
          {fa(n)}
        </div>
      }
    >
      {children}
    </RtlText>
  );
};

export const Scene6Service: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { v, W, H, textBox } = useLayout();
  const d = v ? { cx: 540, cy: 520, s: 1.15 } : { cx: 520, cy: 470, s: 1.1 };
  const OUT = 150; // فاصلهٔ بیرون آمدن کاست (واحد دستگاه)
  const OFF = 900; // بیرون از قاب

  const k = (a: number, b: number) => interpolate(frame, [a, b], [0, 1], { ...clamp, easing: ease });
  // کاست قدیمی
  const oldSlide = k(62, 100) * OUT + k(118, 160) * OFF;
  // کاست نو
  const newY = interpolate(frame, [165, 212, 215, 240], [OFF, OUT, OUT, 0], { ...clamp, easing: ease });
  const press = interpolate(frame, [42, 50, 58, 64], [0, 1, 1, 0], clamp);
  const sealed = spring({ frame: frame - 92, fps, config: { damping: 14 } });

  // نوک انگشت در مختصات دستگاه
  const btn = DEV.button;
  let handY: number;
  if (frame < 160) {
    const enter = interpolate(frame, [0, 40], [OFF, 0], { ...clamp, easing: ease });
    handY = btn.y + 8 + enter - press * 4 + oldSlide;
  } else {
    handY = btn.y + 8 + newY + interpolate(frame, [262, 298], [0, OFF], { ...clamp, easing: ease });
  }
  const showNew = frame >= 165;
  const click = frame - 240;
  const ring = click >= 0 && click < 30 ? (
    <circle cx={150} cy={DEV.cassette.y + DEV.cassette.h / 2} r={70 + click * 5} fill="none" stroke={C.ok} strokeWidth={10 - click * 0.3} opacity={interpolate(click, [0, 30], [0.9, 0], clamp)} />
  ) : null;

  const step = frame < 60 ? 1 : frame < 165 ? 2 : 3;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <defs>
          {/* در نسخهٔ عمودی دست و کاست زیر ناحیهٔ متن دیده نشوند */}
          <clipPath id="s6-stage">
            <rect x={0} y={0} width={W} height={v ? textBox.top - 20 : H} />
          </clipPath>
        </defs>
        <PlacedDevice
          id="s6"
          {...d}
          glow
          showCassette={false}
          filmChildren={null}
        />
        <g clipPath="url(#s6-stage)">
        <g transform={`translate(${d.cx} ${d.cy}) scale(${d.s}) translate(-150 -300)`}>
          {!showNew ? (
            <g transform={`translate(0 ${oldSlide})`}>
              <Cassette rollThickness={30} sealed={frame >= 92 ? sealed : 0} buttonPress={press} labelSize={44 / d.s} />
            </g>
          ) : (
            <g transform={`translate(0 ${newY})`}>
              <Cassette fresh />
            </g>
          )}
          {ring}
          <Hand x={btn.x} y={handY} scale={1 / d.s * 1.2} />
        </g>
        </g>
      </svg>
      <TextPanel>
        <RtlText size="title" delay={10}>
          تعویض کاست در کمتر از ۳۰ ثانیه
        </RtlText>
        <RtlText delay={30} color={C.brand} weight={700}>
          بدون تماس با حشره
        </RtlText>
        <Step n={1} active={step === 1} delay={45}>
          فشار دادن ضامن
        </Step>
        <Step n={2} active={step === 2} delay={95}>
          بیرون آوردن کاست پلمب‌شده
        </Step>
        <Step n={3} active={step === 3} delay={170}>
          جا زدن کاست نو
        </Step>
      </TextPanel>
    </AbsoluteFill>
  );
};
