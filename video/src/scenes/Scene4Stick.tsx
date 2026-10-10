import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Counter } from "../components/Counter";
import { PlacedDevice } from "../components/Device";
import { Fly } from "../components/Fly";
import { CheckIcon, RtlText, TextPanel } from "../components/RtlText";
import { LAND, STICK_ANGLE, STICK_DEV, SWARM_N, swarmPos } from "../components/Swarm";
import { Tick } from "../components/Tick";
import { useLayout } from "../layout";
import { C } from "../theme";
import { clamp, ease } from "../utils";
import { zoomOrigin } from "./Scene3UvAttract";

export const Scene4Stick: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { W, H, dev, font } = useLayout();
  const zoom = interpolate(frame, [0, 35], [1.4, 1], { ...clamp, easing: ease });
  const cut = interpolate(frame, [20, 50], [0, 1], clamp);
  const o = zoomOrigin(dev);
  const flySize = 1.3;

  const flying: React.ReactNode[] = [];
  const stuck: React.ReactNode[] = [];
  const ticks: React.ReactNode[] = [];
  let count = 0;
  let lastLand = -100;
  for (let i = 0; i < SWARM_N; i++) {
    const s = swarmPos(dev, i, frame + 300, W, H);
    const landEnd = LAND(i).start + LAND(i).dur;
    if (s.stuck) {
      count++;
      lastLand = Math.max(lastLand, landEnd);
      const p = STICK_DEV[i];
      stuck.push(<Fly key={i} x={p.x} y={p.y} angle={STICK_ANGLE(i)} size={flySize / dev.s} flapping={false} seed={`sw-${i}`} />);
      ticks.push(<Tick key={i} x={p.x + 20} y={p.y - 18} since={frame - landEnd} fps={fps} size={1 / dev.s * 1.3} />);
    } else {
      flying.push(<Fly key={i} x={s.p.x} y={s.p.y} angle={s.angle} size={flySize} seed={`sw-${i}`} />);
    }
  }
  const iconSize = font.body * 0.85;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <g transform={`translate(${o.x} ${o.y}) scale(${zoom}) translate(${-o.x} ${-o.y})`}>
          <PlacedDevice
            id="s4"
            {...dev}
            glow
            cutaway={cut}
            filmChildren={
              <>
                {stuck}
                {ticks}
              </>
            }
          />
          {flying}
        </g>
      </svg>
      <Counter value={count} bumpAt={lastLand} opacity={interpolate(frame, [30, 45], [0, 1], clamp)} />
      <TextPanel>
        <RtlText size="title" delay={60}>
          گیر افتادن روی سطح چسبی
        </RtlText>
        <RtlText delay={90} icon={<CheckIcon size={iconSize} />}>
          بدون برق‌گرفتگی
        </RtlText>
        <RtlText delay={120} icon={<CheckIcon size={iconSize} />}>
          بدون سوختن
        </RtlText>
        <RtlText delay={150} icon={<CheckIcon size={iconSize} />}>
          بدون ذرات معلق
        </RtlText>
      </TextPanel>
    </AbsoluteFill>
  );
};
