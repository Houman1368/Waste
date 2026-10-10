import { continueRender, delayRender, staticFile } from "remotion";
import { getInfo, loadFont } from "@remotion/google-fonts/Vazirmatn";

// پیش‌فرض: فونت Vazirmatn از Google Fonts با @remotion/google-fonts.
// اگر مرورگر رندر به Google Fonts دسترسی نداشته باشد، با REMOTION_LOCAL_FONTS=1
// همان فایل‌ها از public/fonts خوانده می‌شوند (npm run fonts:download).
const useLocal = process.env.REMOTION_LOCAL_FONTS === "1";

const loadLocal = () => {
  const info = getInfo();
  const handle = delayRender("Loading local Vazirmatn");
  const jobs: Promise<unknown>[] = [];
  for (const weight of ["400", "700"] as const) {
    for (const subset of ["arabic", "latin"] as const) {
      const url = info.fonts.normal[weight][subset];
      const file = staticFile(`fonts/${url.split("/").pop()}`);
      const face = new FontFace(info.fontFamily, `url(${file}) format('woff2')`, {
        weight,
        style: "normal",
        unicodeRange: info.unicodeRanges[subset],
      });
      document.fonts.add(face);
      jobs.push(face.load());
    }
  }
  Promise.all(jobs)
    .then(() => continueRender(handle))
    .catch((err) => {
      throw err;
    });
  return { fontFamily: info.fontFamily };
};

export const { fontFamily } = useLocal
  ? loadLocal()
  : loadFont("normal", { weights: ["400", "700"], subsets: ["arabic", "latin"] });
