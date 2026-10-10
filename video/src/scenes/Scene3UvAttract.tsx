import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { PlacedDevice } from "../components/Device";
import { Fly } from "../components/Fly";
import { DotIcon, RtlText, TextPanel } from "../components/RtlText";
import { SWARM_N, swarmPos } from "../components/Swarm";
import { devToWorld, useLayout } from "../layout";
import { C } from "../theme";
import { clamp, ease } from "../utils";

export const zoomOrigin = (dev: { cx: number; cy: number; s: number }) => devToWorld(dev, { x: 150, y: 200 });

export const Scene3UvAttract: React.FC = () => {
  const frame = useCurrentFrame();
  const { W, H, dev, font } = useLayout();
  const zoom = interpolate(frame, [0, 300], [1, 1.4], { ...clamp, easing: ease });
  const o = zoomOrigin(dev);
  const led = devToWorld(dev, { x: 150, y: 44 });
  const arcs = [0, 1, 2, 3].map((k) => {
    const t = ((frame + k * 30) % 120) / 120;
    const r = 60 + t * 520;
    const op = interpolate(frame, [10, 30], [0, 1], clamp) * (1 - t) * 0.7;
    return (
      <g key={k} opacity={op}>
        <circle cx={led.x} cy={led.y} r={r} fill="none" stroke={C.uv} strokeWidth={6} strokeDasharray={`${r * 0.9} ${r * 0.35}`} transform={`rotate(${-20 + k * 13} ${led.x} ${led.y})`} />
      </g>
    );
  });
  const flies = Array.from({ length: SWARM_N }).map((_, i) => {
    const s = swarmPos(dev, i, frame, W, H);
    if (!s.visible) return null;
    return <Fly key={i} x={s.p.x} y={s.p.y} angle={s.angle} size={1.3} seed={`sw-${i}`} />;
  });
  const iconSize = font.body * 0.8;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <g transform={`translate(${o.x} ${o.y}) scale(${zoom}) translate(${-o.x} ${-o.y})`}>
          {arcs}
          <PlacedDevice id="s3" {...dev} glow />
          {flies}
        </g>
      </svg>
      <TextPanel>
        <RtlText size="title" delay={15} color={C.uv}>
          نور LED یووی-A (حدود ۳۶۵ نانومتر)
        </RtlText>
        <RtlText delay={90} icon={<DotIcon size={iconSize} />}>
          جذاب برای حشره، بی‌خطر برای انسان در کاربرد معمول
        </RtlText>
        <RtlText delay={165} icon={<DotIcon size={iconSize} color={C.brand} />}>
          مصرف برق کم، بدون جیوه
        </RtlText>
      </TextPanel>
    </AbsoluteFill>
  );
};
