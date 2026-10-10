// اسکرین‌شات فریم‌های کلیدی ویدیوهای RTH: node scripts/stills-rth.mjs [A B C] ← out/stills/RTH-*.png
import path from "node:path";
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";

const keys = process.argv.slice(2).length ? process.argv.slice(2) : ["A", "B", "C"];
const frames = (process.env.FRAMES || "60,250,500,800,1100,1450,1700,1950,2250,2560,2700").split(",").map(Number);
const browserExecutable = process.env.REMOTION_BROWSER_EXECUTABLE || null;
const envVariables = Object.fromEntries(Object.entries(process.env).filter(([k]) => k.startsWith("REMOTION_")));
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
for (const k of keys) {
  const composition = await selectComposition({ serveUrl, id: `RTH-${k}`, browserExecutable, envVariables });
  for (const frame of frames) {
    const output = `out/stills/RTH-${k}-${frame}.png`;
    await renderStill({ composition, serveUrl, output, frame, browserExecutable, envVariables, overwrite: true });
    console.log(output);
  }
}
