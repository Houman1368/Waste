// رندر نمونهٔ اولیهٔ RTH-C: node render-proto.mjs ← prototype-rth-c/images/*.png
import { chromium } from "playwright";
import { createServer } from "node:http";
import { readFile, mkdir } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const types = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json", ".jpg": "image/jpeg" };
const server = createServer(async (req, res) => {
  try {
    const p = path.join(root, decodeURIComponent(new URL(req.url, "http://x").pathname));
    const body = await readFile(p);
    res.writeHead(200, { "content-type": types[path.extname(p)] || "application/octet-stream" });
    res.end(body);
  } catch { res.writeHead(404); res.end(); }
}).listen(0);
const port = server.address().port;
const outDir = path.join(root, "prototype-rth-c", "images");
await mkdir(outDir, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const page = await browser.newPage({ viewport: { width: 1600, height: 1300 } });
page.on("pageerror", (e) => console.error(e));
for (const v of (process.env.VIEWS || "hero,front,inside,exploded").split(",")) {
  await page.goto(`http://localhost:${port}/render/concepts.html?dir=../prototype-rth-c/render-data/&view=${v}&w=1600&h=1300`);
  await page.waitForFunction(() => window.__done === true, null, { timeout: 300000 });
  await page.locator("canvas").screenshot({ path: path.join(outDir, `${v}.png`) });
  console.log("rendered", v);
}
await browser.close();
server.close();
