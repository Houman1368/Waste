// اسکرین‌شات یک صفحهٔ HTML محلی: node shot.mjs <input.html> <output.png> [width]
import { chromium } from "playwright";
import path from "node:path";
const [, , input, output, width = "1340"] = process.argv;
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const page = await browser.newPage({ viewport: { width: +width, height: 800 }, deviceScaleFactor: 1.5 });
await page.goto("file://" + path.resolve(input));
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: output, fullPage: true });
await browser.close();
