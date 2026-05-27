import { createRequire } from "node:module";
import { mkdir, rename } from "node:fs/promises";
import path from "node:path";

const require = createRequire("/tmp/flux-video/package.json");
const { chromium } = require("playwright");

const BASE_URL = "https://flux-153593352872.us-central1.run.app";
const CHROME_BETA = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta";
const VIDEO_DIR = path.resolve("docs/video");
const RAW_DIR = path.join(VIDEO_DIR, "raw");
const FINAL_VIDEO = path.join(VIDEO_DIR, "flux-demo-visual-track.webm");

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function cardHtml({ title, eyebrow, bullets, footer }) {
  const items = bullets.map((item) => `<li>${item}</li>`).join("");
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { color: #fffaf0; background: #143c37; font-family: "Avenir Next", "Segoe UI", sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: #143c37; }
    .chrome { height: 76px; display: flex; align-items: end; gap: 8px; padding: 12px 20px 0; background: #ece7dc; color: #39362e; }
    .dot { width: 14px; height: 14px; border-radius: 50%; margin: 0 2px 18px 0; }
    .red { background: #dd625b; } .yellow { background: #e0b84f; } .green { background: #56b96b; }
    .tab { min-width: 190px; height: 40px; display: flex; align-items: center; padding: 0 16px; border-radius: 8px 8px 0 0; background: #d6cfbd; font-size: 14px; font-weight: 700; }
    .tab.active { background: #fffaf0; color: #143c37; }
    main { min-height: calc(100vh - 76px); display: grid; align-content: center; padding: 90px 140px; }
    .eyebrow { color: #f0b09a; font-size: 18px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }
    h1 { max-width: 1150px; margin: 18px 0 30px; font-family: Georgia, "Times New Roman", serif; font-size: 92px; line-height: .95; font-weight: 500; }
    ul { display: grid; gap: 14px; max-width: 960px; padding: 0; margin: 0; list-style: none; color: #f8efe2; font-size: 28px; line-height: 1.35; }
    li::before { content: "•"; color: #f0b09a; margin-right: 14px; }
    footer { margin-top: 52px; color: #d9d2c1; font-size: 22px; }
    .cursor { position: fixed; z-index: 999999; width: 22px; height: 22px; pointer-events: none; transform: translate(-3px,-3px); }
    .cursor::before { content: ""; position: absolute; width: 0; height: 0; border-left: 16px solid #9c3f2f; border-top: 10px solid transparent; border-bottom: 10px solid transparent; transform: rotate(-35deg); filter: drop-shadow(0 2px 2px rgb(0 0 0 / 30%)); }
  </style>
</head>
<body>
  <div class="chrome">
    <span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span>
    <div class="tab active">Flux live app</div>
    <div class="tab">GitLab issue</div>
    <div class="tab">Notion guide</div>
    <div class="tab">Cloud Run proof</div>
  </div>
  <main>
    <div class="eyebrow">${eyebrow}</div>
    <h1>${title}</h1>
    <ul>${items}</ul>
    <footer>${footer}</footer>
  </main>
</body>
</html>`;
}

async function installCursor(page) {
  await page.addInitScript(() => {
    window.addEventListener("DOMContentLoaded", () => {
      const cursor = document.createElement("div");
      cursor.id = "flux-demo-cursor";
      cursor.style.cssText = [
        "position:fixed",
        "z-index:2147483647",
        "width:22px",
        "height:22px",
        "pointer-events:none",
        "left:120px",
        "top:120px",
        "transform:translate(-3px,-3px)",
      ].join(";");
      cursor.innerHTML = `<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 3L22 15L13 17L9 25L4 3Z" fill="#9c3f2f" stroke="#fffaf0" stroke-width="2" />
      </svg>`;
      document.body.appendChild(cursor);
      window.addEventListener("mousemove", (event) => {
        cursor.style.left = `${event.clientX}px`;
        cursor.style.top = `${event.clientY}px`;
      });
      window.addEventListener("click", (event) => {
        const ring = document.createElement("div");
        ring.style.cssText = [
          "position:fixed",
          "z-index:2147483646",
          `left:${event.clientX - 18}px`,
          `top:${event.clientY - 18}px`,
          "width:36px",
          "height:36px",
          "border:3px solid #9c3f2f",
          "border-radius:999px",
          "pointer-events:none",
          "animation:fluxClick .55s ease-out forwards",
        ].join(";");
        document.body.appendChild(ring);
        setTimeout(() => ring.remove(), 650);
      });
      const style = document.createElement("style");
      style.textContent = `@keyframes fluxClick { from { opacity: .95; transform: scale(.6); } to { opacity: 0; transform: scale(1.8); } }`;
      document.head.appendChild(style);
    });
  });
}

async function moveAndClick(page, locator) {
  await locator.scrollIntoViewIfNeeded();
  const box = await locator.boundingBox();
  if (!box) throw new Error("Cannot click invisible element");
  const x = box.x + box.width / 2;
  const y = box.y + box.height / 2;
  await page.mouse.move(x, y, { steps: 24 });
  await sleep(250);
  await page.mouse.click(x, y);
}

async function clickText(page, text) {
  await moveAndClick(page, page.getByText(text, { exact: true }).first());
}

async function clickButton(page, name) {
  await moveAndClick(page, page.getByRole("button", { name }).first());
}

async function sendPrompt(page, text) {
  const before = await page.locator(".message.assistant").count();
  await clickButton(page, text);
  await page.waitForFunction(
    (count) => document.querySelectorAll(".message.assistant").length > count,
    before,
    { timeout: 120_000 },
  );
  await sleep(2800);
}

async function main() {
  await mkdir(RAW_DIR, { recursive: true });

  let browser;
  let context;
  const browserInstance = await chromium.launch({
    executablePath: CHROME_BETA,
    headless: true,
  });
  browser = browserInstance;
  try {
    context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      recordVideo: {
        dir: RAW_DIR,
        size: { width: 1920, height: 1080 },
      },
    });
    const page = await context.newPage();
    page.setDefaultTimeout(120_000);
    await installCursor(page);

    await page.goto(`data:text/html,${encodeURIComponent(cardHtml({
      eyebrow: "Flux demo track",
      title: "The org as it runs, not as it is drawn.",
      bullets: [
        "Live app",
        "GitLab issue action",
        "Notion team guide",
        "Cloud Run + ADK/Gemini proof",
      ],
      footer: "Silent 16:9 visual track for voiceover",
    }))}`);
    await page.mouse.move(320, 170, { steps: 24 });
    await sleep(6500);

    await page.goto(BASE_URL, { waitUntil: "networkidle" });
    await sleep(1800);
    await page.mouse.move(430, 640, { steps: 30 });
    await sleep(800);
    await clickButton(page, "Generate link");

    const link = page.locator(".result a").first();
    await link.waitFor({ state: "visible" });
    await sleep(1800);
    await moveAndClick(page, link);

    await page.getByText("New hire brief").waitFor({ state: "visible" });
    await page.getByText("Live ADK + MCP").waitFor({ state: "visible" });
    await page.getByText("SSO migration", { exact: false }).first().waitFor({ state: "visible" });
    await sleep(3000);
    await page.mouse.wheel(0, 360);
    await sleep(2200);
    await page.mouse.wheel(0, -260);
    await sleep(1200);

    await sendPrompt(page, "Who owns auth?");
    await sendPrompt(page, "How do I ship fast?");
    await sendPrompt(page, "Anything I shouldn't say in standup?");

    await clickButton(page, "Assign issue #412 to me");
    await page.getByText("Confirm assignment").waitFor({ state: "visible" });
    await sleep(2400);
    const confirmButton = page.getByRole("button", { name: "Confirm assignment" }).first();
    const [confirmResponse] = await Promise.all([
      page.waitForResponse(
        (response) => response.url().includes("/api/action/confirm"),
        { timeout: 120_000 },
      ),
      moveAndClick(page, confirmButton),
    ]);
    if (!confirmResponse.ok()) {
      throw new Error(`Assignment failed with HTTP ${confirmResponse.status()}`);
    }
    await page.locator(".action-result").last().waitFor({ state: "visible" });
    await sleep(4500);

    await page.goto(`data:text/html,${encodeURIComponent(cardHtml({
      eyebrow: "Implementation proof",
      title: "Cloud Run + Gemini + ADK + GitLab MCP",
      bullets: [
        "Public Cloud Run app with /api/health mode: live",
        "Google ADK LlmAgent + Runner orchestrates Gemini",
        "GitLab MCP registered through McpToolset and glab mcp serve",
        "Confirmed assignment writes through glab_issue_update",
      ],
      footer: "Source and proof notes are in the public GitHub repo",
    }))}`);
    await page.mouse.move(460, 420, { steps: 30 });
    await sleep(9000);

    const video = page.video();
    await context.close();
    context = null;

    const rawPath = await video.path();
    await rename(rawPath, FINAL_VIDEO);
    console.log(FINAL_VIDEO);
  } finally {
    if (context) await context.close().catch(() => {});
    await browser.close().catch(() => {});
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
