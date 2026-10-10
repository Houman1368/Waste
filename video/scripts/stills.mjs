// اسکرین‌شات از فریم‌های کلیدی هر دو نسخه برای بازبینی (out/stills)
// استفاده: npm run stills -- [frame ...]   (پیش‌فرض: 150 600 1200 1600 2100)
import path from "node:path";
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";

const args = process.argv.slice(2).map(Number).filter((n) => !Number.isNaN(n));
const frames = args.length ? args : [150, 600, 1200, 1600, 2100];
const browserExecutable = process.env.REMOTION_BROWSER_EXECUTABLE || null;
const envVariables = Object.fromEntries(Object.entries(process.env).filter(([k]) => k.startsWith("REMOTION_")));

const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
for (const id of ["Video16x9", "Video9x16"]) {
  const composition = await selectComposition({ serveUrl, id, browserExecutable, envVariables });
  for (const frame of frames) {
    const output = `out/stills/${id}-${frame}.png`;
    await renderStill({ composition, serveUrl, output, frame, browserExecutable, envVariables, overwrite: true });
    console.log(output);
  }
}
