// رندر نماهای مختلف مدل با three.js در Chromium بی‌سر
import { chromium } from "playwright";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const types = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".stl": "application/octet-stream" };
const server = createServer(async (req, res) => {
  try {
    const p = path.join(root, decodeURIComponent(new URL(req.url, "http://x").pathname));
    const body = await readFile(p);
    res.writeHead(200, { "content-type": types[path.extname(p)] || "application/octet-stream" });
    res.end(body);
  } catch { res.writeHead(404); res.end(); }
}).listen(0);
const port = server.address().port;

const views = process.argv.slice(2).length ? process.argv.slice(2) : ["hero", "front", "cutaway", "service", "side"];
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
page.on("console", (m) => m.type() === "error" && console.error(m.text()));
for (const v of views) {
  await page.goto(`http://localhost:${port}/render/index.html?view=${v}`);
  await page.waitForFunction(() => window.__done === true, null, { timeout: 120000 });
  await page.locator("canvas").screenshot({ path: path.join(root, "render", "out", `${v}.png`) });
  console.log("rendered", v);
}
await browser.close();
server.close();
