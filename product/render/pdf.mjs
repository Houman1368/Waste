// تبدیل HTML محلی به PDF: node pdf.mjs <in.html> <out.pdf>
import { chromium } from "playwright";
import path from "node:path";
const [, , input, output] = process.argv;
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const page = await browser.newPage();
await page.goto("file://" + path.resolve(input));
await page.evaluate(() => document.fonts.ready);
await page.waitForLoadState("networkidle");
await page.pdf({ path: output, format: "A4", printBackground: true, preferCSSPageSize: true });
await browser.close();
