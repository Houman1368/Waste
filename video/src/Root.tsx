import React from "react";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import { FPS, TOTAL_FRAMES } from "./theme";
import { Video, VideoProps } from "./Video";

// فایل‌های صوتی اختیاری‌اند: اگر در public/ نباشند ویدیو بی‌صدا ساخته می‌شود.
const exists = async (file: string) => {
  try {
    const res = await fetch(staticFile(file), { method: "HEAD" });
    return res.ok;
  } catch {
    return false;
  }
};

const calculateMetadata: CalculateMetadataFunction<VideoProps> = async ({ props }) => ({
  props: { ...props, hasVoiceover: await exists("voiceover.mp3"), hasMusic: await exists("music.mp3") },
});

const defaultProps: VideoProps = { hasVoiceover: false, hasMusic: false };

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Video16x9" component={Video} durationInFrames={TOTAL_FRAMES} fps={FPS} width={1920} height={1080} defaultProps={defaultProps} calculateMetadata={calculateMetadata} />
    <Composition id="Video9x16" component={Video} durationInFrames={TOTAL_FRAMES} fps={FPS} width={1080} height={1920} defaultProps={defaultProps} calculateMetadata={calculateMetadata} />
  </>
);
