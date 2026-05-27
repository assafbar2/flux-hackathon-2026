import { createRequire } from "node:module";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { spawn } from "node:child_process";
import path from "node:path";

const require = createRequire("/tmp/flux-video/package.json");
const { chromium } = require("playwright");

const BASE_URL = "https://flux-153593352872.us-central1.run.app";
const CHROME_BETA = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta";
const FFMPEG = "/private/tmp/flux-video/node_modules/@ffmpeg-installer/darwin-arm64/ffmpeg";
const VIDEO_DIR = path.resolve("docs/video");
const TMP_DIR = path.join(VIDEO_DIR, "tmp");
const MOV_PATH = path.join(TMP_DIR, "flux-demo-chrome-beta.mov");
const MP4_PATH = path.join(VIDEO_DIR, "flux-demo-chrome-beta.mp4");
const PROFILE_DIR = path.join(TMP_DIR, "chrome-beta-profile");
const CAPTURE_RECT = "0,50,1512,850";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function run(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: "pipe", ...options });
    let stdout = "";
    let stderr = "";
    child.stdout?.on("data", (data) => {
      stdout += data.toString();
    });
    child.stderr?.on("data", (data) => {
      stderr += data.toString();
    });
    child.on("close", (code) => {
      if (code === 0) resolve({ stdout, stderr });
      else reject(new Error(`${command} exited ${code}\n${stdout}\n${stderr}`));
    });
  });
}

async function launchCleanChromeBeta() {
  await run("/usr/bin/pkill", ["-f", `${PROFILE_DIR}`]).catch(() => {});
  return chromium.launchPersistentContext(PROFILE_DIR, {
    headless: false,
    executablePath: CHROME_BETA,
    viewport: null,
    chromiumSandbox: true,
    args: [
      "--test-type",
      "--no-first-run",
      "--no-default-browser-check",
      "--disable-session-crashed-bubble",
      "--window-position=0,50",
      "--window-size=1512,850",
    ],
  });
}

async function setWindowBounds(context, page) {
  const session = await context.newCDPSession(page);
  const { windowId } = await session.send("Browser.getWindowForTarget");
  await session.send("Browser.setWindowBounds", {
    windowId,
    bounds: {
      left: 0,
      top: 50,
      width: 1512,
      height: 850,
      windowState: "normal",
    },
  });
}

function cardHtml({ title, eyebrow, bullets, footer }) {
  const items = bullets.map((item) => `<li>${item}</li>`).join("");
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>${eyebrow}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { color: #fffaf0; background: #143c37; font-family: "Avenir Next", "Segoe UI", sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: #143c37; }
    main { min-height: 100vh; display: grid; align-content: center; padding: 90px 140px; }
    .eyebrow { color: #f0b09a; font-size: 18px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }
    h1 { max-width: 1150px; margin: 18px 0 30px; font-family: Georgia, "Times New Roman", serif; font-size: 90px; line-height: .95; font-weight: 500; }
    ul { display: grid; gap: 14px; max-width: 1100px; padding: 0; margin: 0; list-style: none; color: #f8efe2; font-size: 28px; line-height: 1.35; }
    li::before { content: "•"; color: #f0b09a; margin-right: 14px; }
    footer { margin-top: 52px; color: #d9d2c1; font-size: 22px; }
    code { color: #fffaf0; background: rgb(255 250 240 / 12%); padding: 2px 6px; border-radius: 5px; }
  </style>
</head>
<body>
  <main>
    <div class="eyebrow">${eyebrow}</div>
    <h1>${title}</h1>
    <ul>${items}</ul>
    <footer>${footer}</footer>
  </main>
</body>
</html>`;
}

async function installClickMarker(page) {
  await page.addInitScript(() => {
    window.addEventListener("DOMContentLoaded", () => {
      const style = document.createElement("style");
      style.textContent = `@keyframes fluxClick { from { opacity: .95; transform: scale(.6); } to { opacity: 0; transform: scale(1.8); } }`;
      document.head.appendChild(style);
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
  await sleep(2500);
}

async function createCardPage(context, options) {
  const page = await context.newPage();
  await page.setContent(cardHtml(options), { waitUntil: "domcontentloaded" });
  return page;
}

function startCapture() {
  return spawn("/usr/sbin/screencapture", [
    "-v",
    "-k",
    `-R${CAPTURE_RECT}`,
    MOV_PATH,
  ], { stdio: "ignore" });
}

async function stopCapture(process) {
  if (process.exitCode !== null) return;
  process.kill("SIGINT");
  await new Promise((resolve) => process.once("close", resolve));
}

async function main() {
  await mkdir(TMP_DIR, { recursive: true });
  await rm(PROFILE_DIR, { recursive: true, force: true });
  await rm(MOV_PATH, { force: true });
  await rm(MP4_PATH, { force: true });

  let context;
  let capture;
  try {
    context = await launchCleanChromeBeta();
    context.setDefaultTimeout(120_000);

    const livePage = context.pages()[0] || await context.newPage();
    await livePage.waitForLoadState("domcontentloaded").catch(() => {});
    for (const page of context.pages()) {
      if (page !== livePage) await page.close().catch(() => {});
    }
    await setWindowBounds(context, livePage);
    await installClickMarker(livePage);
    await livePage.goto(BASE_URL, { waitUntil: "networkidle" });
    await livePage.bringToFront();

    const gitlabPage = await createCardPage(context, {
    eyebrow: "GitLab issue",
    title: "billing/#412 is the first real task.",
    bullets: [
      "Source project: <code>assafbar-group/flux-demo</code>",
      "Flux reads issues through GitLab MCP",
      "The final action assigns this issue after confirmation",
    ],
    footer: "The assignment happens live during the demo through glab_issue_update.",
  });

    const notionPage = await createCardPage(context, {
    eyebrow: "Notion guide",
    title: "The human context comes from the team guide.",
    bullets: [
      "Who's on leave",
      "What not to touch this week",
      "How shipping actually works",
      "Which unwritten rules matter",
    ],
    footer: "Flux combines this guide with GitLab activity before answering.",
  });

    const cloudPage = await createCardPage(context, {
    eyebrow: "Cloud Run proof",
    title: "The production service is live.",
    bullets: [
      "Cloud Run service: <code>flux</code>",
      "Health: <code>/api/health</code> returns <code>mode: live</code>",
      "Google ADK <code>LlmAgent</code> + <code>Runner</code> orchestrate Gemini",
      "GitLab MCP is registered as an ADK toolset",
    ],
    footer: "Public repo links to the exact proof file and Cloud Logging command.",
  });

    await livePage.bringToFront();
    await sleep(1000);
    capture = startCapture();
    await sleep(2500);

    for (const page of [livePage, gitlabPage, notionPage, cloudPage]) {
      await page.bringToFront();
      await sleep(5000);
    }

    await livePage.bringToFront();
    await sleep(1200);
    await clickButton(livePage, "Generate link");
    const link = livePage.locator(".result a").first();
    await link.waitFor({ state: "visible" });
    await sleep(1500);
    await moveAndClick(livePage, link);

    await livePage.getByText("New hire brief").waitFor({ state: "visible" });
    await livePage.getByText("Live ADK + MCP").waitFor({ state: "visible" });
    await livePage.getByText("SSO migration", { exact: false }).first().waitFor({ state: "visible" });
    await sleep(3000);
    await livePage.mouse.wheel(0, 360);
    await sleep(1800);
    await livePage.mouse.wheel(0, -260);
    await sleep(1000);

    await sendPrompt(livePage, "Who owns auth?");
    await sendPrompt(livePage, "How do I ship fast?");
    await sendPrompt(livePage, "Anything I shouldn't say in standup?");

    await clickButton(livePage, "Assign issue #412 to me");
    await livePage.getByText("Confirm assignment").waitFor({ state: "visible" });
    await sleep(1800);
    const [confirmResponse] = await Promise.all([
      livePage.waitForResponse(
        (response) => response.url().includes("/api/action/confirm"),
        { timeout: 120_000 },
      ),
      moveAndClick(livePage, livePage.getByRole("button", { name: "Confirm assignment" }).first()),
    ]);
    if (!confirmResponse.ok()) {
      throw new Error(`Assignment failed with HTTP ${confirmResponse.status()}`);
    }
    await livePage.locator(".action-result").last().waitFor({ state: "visible" });
    await sleep(3500);

    await gitlabPage.setContent(cardHtml({
    eyebrow: "GitLab issue",
    title: "billing/#412 is assigned.",
    bullets: [
      "Confirmed in the app after explicit user approval",
      "Write path: <code>GitLab MCP -> glab_issue_update</code>",
      "Assigned to <code>assafbar</code>",
    ],
    footer: "This is the move-beyond-chat moment: the agent takes a controlled action.",
  }), { waitUntil: "domcontentloaded" });
    await gitlabPage.bringToFront();
    await sleep(5000);

    await cloudPage.bringToFront();
    await sleep(6000);

    await stopCapture(capture);
    capture = null;
    await context.close();
    context = null;
  } finally {
    if (capture) await stopCapture(capture).catch(() => {});
    if (context) await context.close().catch(() => {});
    await run("/usr/bin/pkill", ["-f", `${PROFILE_DIR}`]).catch(() => {});
  }

  if (!existsSync(MOV_PATH)) {
    throw new Error("Screen capture did not create a .mov file");
  }
  await run(FFMPEG, [
    "-y",
    "-i",
    MOV_PATH,
    "-vf",
    "scale=1920:1080",
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-movflags",
    "+faststart",
    MP4_PATH,
  ]);
  await writeFile(path.join(TMP_DIR, "latest-chrome-beta-recording.txt"), `${MP4_PATH}\n`);
  console.log(MP4_PATH);
}

main().catch(async (error) => {
  console.error(error);
  process.exitCode = 1;
});
