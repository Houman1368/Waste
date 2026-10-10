// دانلود فایل‌های Vazirmatn (لایسنس OFL) در public/fonts برای رندر آفلاین
import { mkdirSync, writeFileSync } from "node:fs";
import { getInfo } from "@remotion/google-fonts/Vazirmatn";

const info = getInfo();
mkdirSync("public/fonts", { recursive: true });
const urls = new Set();
for (const w of ["400", "700"]) for (const s of ["arabic", "latin"]) urls.add(info.fonts.normal[w][s]);
for (const url of urls) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  writeFileSync(`public/fonts/${url.split("/").pop()}`, Buffer.from(await res.arrayBuffer()));
  console.log("saved", url.split("/").pop());
}
