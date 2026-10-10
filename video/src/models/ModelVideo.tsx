import React from "react";
import { AbsoluteFill, Html5Audio, Sequence, staticFile } from "remotion";
import { C } from "../theme";
import {
  SceneAttract,
  SceneBismillah,
  SceneCapture,
  SceneIntro,
  SceneOutro,
  SceneParts,
  SceneReplace,
  SceneRoll,
  SceneSpecs,
} from "./ModelScenes";
import { MODELS, ModelKey, MSCENES } from "./specs";

export type ModelVideoProps = { model: ModelKey; hasMusic: boolean };

/** ویدیوی معرفی یک مدل (RTH-A / RTH-B / RTH-C) */
export const ModelVideo: React.FC<ModelVideoProps> = ({ model, hasMusic }) => {
  const m = MODELS[model];
  const comps: Record<(typeof MSCENES)[number]["key"], React.ReactNode> = {
    bismillah: <SceneBismillah />,
    intro: <SceneIntro m={m} />,
    parts: <SceneParts m={m} />,
    attract: <SceneAttract m={m} />,
    capture: <SceneCapture m={m} />,
    roll: <SceneRoll m={m} />,
    replace: <SceneReplace m={m} />,
    specs: <SceneSpecs m={m} />,
    outro: <SceneOutro m={m} />,
  };
  let from = 0;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      {MSCENES.map((s) => {
        const el = (
          <Sequence key={s.key} name={s.key} from={from} durationInFrames={s.dur} premountFor={30}>
            {comps[s.key]}
          </Sequence>
        );
        from += s.dur;
        return el;
      })}
      {hasMusic ? <Html5Audio src={staticFile("music.mp3")} volume={0.2} /> : null}
    </AbsoluteFill>
  );
};
