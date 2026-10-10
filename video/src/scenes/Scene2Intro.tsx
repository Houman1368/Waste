import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Corridor, OldZapper } from "../components/Corridor";
import { PlacedDevice } from "../components/Device";
import { RtlText, TextPanel } from "../components/RtlText";
import { PRODUCT_NAME } from "../config";
import { useLayout } from "../layout";
import { C } from "../theme";
import { clamp } from "../utils";

export const Scene2Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { v, W, H, dev } = useLayout();
  const z = { cx: dev.cx, cy: v ? 430 : 400, s: v ? 1.25 : 1.15 };
  const zapOut = interpolate(frame, [0, 30], [1, 0], clamp);
  const appear = spring({ frame: frame - 28, fps, config: { damping: 200 }, durationInFrames: 40 });
  const ledOn = interpolate(frame, [80, 95], [0, 1], clamp);
  // راهرو در انتهای صحنه کم‌رنگ می‌شود تا صحنهٔ بعد روی زمینهٔ ساده باشد
  const corridor = interpolate(frame, [200, 238], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <Corridor opacity={corridor} />
        <OldZapper cx={z.cx} cy={z.cy} s={z.s} opacity={zapOut} />
        <PlacedDevice
          id="s2"
          {...dev}
          extraScale={0.9 + 0.1 * appear}
          opacity={appear}
          glow={ledOn}
          powerOn={ledOn > 0.5}
        />
      </svg>
      <TextPanel>
        <RtlText size="title" delay={95} color={C.brand} style={{ fontSize: v ? 96 : 84 }}>
          {PRODUCT_NAME}
        </RtlText>
        <RtlText delay={125}>تلهٔ هوشمند حشره، مخصوص محیط‌های درمانی</RtlText>
      </TextPanel>
    </AbsoluteFill>
  );
};
