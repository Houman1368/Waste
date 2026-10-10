// تصویر جدا از هر قطعهٔ پرینتی: node render-proto-parts.mjs ← prototype-rth-c/images/parts/*.png
import { chromium } from "playwright";
import { createServer } from "node:http";
import { readFile, mkdir } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const server = createServer(async (req, res) => {
  try {
    const p = path.join(root, decodeURIComponent(new URL(req.url, "http://x").pathname));
    const body = await readFile(p);
    res.writeHead(200, { "content-type": p.endsWith(".html") ? "text/html" : p.endsWith(".js") ? "text/javascript" : "application/octet-stream" });
    res.end(body);
  } catch { res.writeHead(404); res.end(); }
}).listen(0);
const port = server.address().port;
const parts = ["side_upper_L", "side_upper_R", "side_lower_L", "side_lower_R", "head_1", "head_2", "head_3", "slats_L", "slats_R", "cassette_L", "cassette_R", "knob", "cap_supply_L", "cap_takeup_R"];
const outDir = path.join(root, "prototype-rth-c", "images", "parts");
await mkdir(outDir, { recursive: true });
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const page = await browser.newPage({ viewport: { width: 600, height: 500 } });
for (const p of parts) {
  await page.goto(`http://localhost:${port}/render/concepts.html?dir=../prototype-rth-c/render-data/&only=${p}&w=600&h=500`);
  await page.waitForFunction(() => window.__done === true, null, { timeout: 120000 });
  await page.locator("canvas").screenshot({ path: path.join(outDir, `${p}.png`) });
}
console.log("parts", parts.length);
await browser.close();
server.close();
