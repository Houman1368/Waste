// رندر سه طرح مفهومی: node render-concepts.mjs [a b c] ← render/out/concepts/<c>-<view>.png
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
const keys = process.argv.slice(2).length ? process.argv.slice(2) : ["a", "b", "c"];
const views = ["hero", "front", "inside"];
await mkdir(path.join(root, "render", "out", "concepts"), { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const page = await browser.newPage({ viewport: { width: 1200, height: 1500 } });
page.on("console", (m) => m.type() === "error" && !m.text().includes("404") && console.error(m.text()));
page.on("pageerror", (e) => console.error(e));
for (const k of keys) for (const v of views) {
  await page.goto(`http://localhost:${port}/render/concepts.html?c=${k}&view=${v}`);
  await page.waitForFunction(() => window.__done === true, null, { timeout: 180000 });
  await page.locator("canvas").screenshot({ path: path.join(root, "render", "out", "concepts", `${k}-${v}.png`) });
  console.log("rendered", k, v);
}
await browser.close();
server.close();
