import React from "react";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import { LOGO_CANDIDATES } from "./config";
import { FPS, TOTAL_FRAMES } from "./theme";
import { Video, VideoProps } from "./Video";
import { ModelVideo, ModelVideoProps } from "./models/ModelVideo";
import { MTOTAL } from "./models/specs";

// فایل‌های صوتی اختیاری‌اند: اگر در public/ نباشند ویدیو بی‌صدا ساخته می‌شود.
const exists = async (file: string) => {
  try {
    const res = await fetch(staticFile(file), { method: "HEAD" });
    return res.ok;
  } catch {
    return false;
  }
};

const findLogo = async () => {
  for (const f of LOGO_CANDIDATES) if (await exists(f)) return f;
  return null;
};

const calculateMetadata: CalculateMetadataFunction<VideoProps> = async ({ props }) => ({
  props: {
    ...props,
    hasVoiceover: await exists("voiceover.mp3"),
    hasMusic: await exists("music.mp3"),
    logoFile: await findLogo(),
  },
});

const defaultProps: VideoProps = { hasVoiceover: false, hasMusic: false, logoFile: null };

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Video16x9" component={Video} durationInFrames={TOTAL_FRAMES} fps={FPS} width={1920} height={1080} defaultProps={defaultProps} calculateMetadata={calculateMetadata} />
    {(["A", "B", "C"] as const).map((k) => (
      <Composition
        key={k}
        id={`RTH-${k}`}
        component={ModelVideo}
        durationInFrames={MTOTAL}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{ model: k, hasMusic: false } as ModelVideoProps}
        calculateMetadata={async ({ props }) => ({ props: { ...props, hasMusic: await exists("music.mp3") } })}
      />
    ))}
    <Composition id="Video9x16" component={Video} durationInFrames={TOTAL_FRAMES} fps={FPS} width={1080} height={1920} defaultProps={defaultProps} calculateMetadata={calculateMetadata} />
  </>
);
