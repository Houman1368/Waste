import React from "react";
import { AbsoluteFill, Html5Audio, Sequence, staticFile } from "remotion";
import { Scene1Problem } from "./scenes/Scene1Problem";
import { Scene2Intro } from "./scenes/Scene2Intro";
import { Scene3UvAttract } from "./scenes/Scene3UvAttract";
import { Scene4Stick } from "./scenes/Scene4Stick";
import { Scene5Roll } from "./scenes/Scene5Roll";
import { Scene6Service } from "./scenes/Scene6Service";
import { Scene7Cycle } from "./scenes/Scene7Cycle";
import { Scene8Outro } from "./scenes/Scene8Outro";
import { C, SCENES } from "./theme";

export type VideoProps = { hasVoiceover: boolean; hasMusic: boolean };

const LIST: { key: keyof typeof SCENES; C: React.FC }[] = [
  { key: "s1", C: Scene1Problem },
  { key: "s2", C: Scene2Intro },
  { key: "s3", C: Scene3UvAttract },
  { key: "s4", C: Scene4Stick },
  { key: "s5", C: Scene5Roll },
  { key: "s6", C: Scene6Service },
  { key: "s7", C: Scene7Cycle },
  { key: "s8", C: Scene8Outro },
];

export const Video: React.FC<VideoProps> = ({ hasVoiceover, hasMusic }) => (
  <AbsoluteFill style={{ background: C.bg }}>
    {LIST.map(({ key, C: Scene }) => (
      <Sequence key={key} name={key} from={SCENES[key].from} durationInFrames={SCENES[key].dur} premountFor={30}>
        <Scene />
      </Sequence>
    ))}
    {hasVoiceover ? <Html5Audio src={staticFile("voiceover.mp3")} /> : null}
    {hasMusic ? <Html5Audio src={staticFile("music.mp3")} volume={0.2} /> : null}
  </AbsoluteFill>
);
