import { createRequire } from "node:module";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { spawn } from "node:child_process";
import path from "node:path";

const require = createRequire("/tmp/flux-video/package.json");
const { chromium } = require("playwright");

const BASE_URL = "https://flux-153593352872.us-central1.run.app";
const CLOUD_RUN_LOGS_URL = "https://console.cloud.google.com/run/detail/us-central1/flux/observability/logs?project=direct-subject-497307-p8";
const CHROME_BETA = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta";
const FFMPEG = "/private/tmp/flux-video/node_modules/@ffmpeg-installer/darwin-arm64/ffmpeg";
const VIDEO_DIR = path.resolve("docs/video");
const TMP_DIR = path.join(VIDEO_DIR, "tmp");
const MOV_PATH = path.join(TMP_DIR, "flux-demo-chrome-beta.mov");
const MP4_PATH = path.join(VIDEO_DIR, "flux-demo-chrome-beta.mp4");
const PROFILE_DIR = path.join(TMP_DIR, "chrome-beta-profile");
const CLOUD_RUN_SCREENSHOT_PATH = path.join(TMP_DIR, "cloud-run-console.png");
const RESET_RECORDING_PROFILE = process.env.FLUX_RESET_RECORDING_PROFILE !== "false";
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

async function runAppleScript(script) {
  return run("/usr/bin/osascript", ["-e", script]);
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

function gitLabIssueHtml({ assigned = false } = {}) {
  const assignee = assigned ? "Assaf Barnir" : "Unassigned";
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>GitLab issue</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { color: #172b4d; background: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: #fff; }
    header { height: 58px; display: flex; align-items: center; gap: 18px; padding: 0 28px; border-bottom: 1px solid #dcdcde; background: #fbfafd; }
    .fox { width: 30px; height: 30px; display: grid; place-items: center; color: #fc6d26; font-size: 25px; }
    .brand { font-size: 18px; font-weight: 700; color: #333238; }
    .search { margin-left: auto; width: 330px; padding: 9px 12px; border: 1px solid #bfbfc3; border-radius: 4px; color: #626168; }
    .layout { display: grid; grid-template-columns: 240px 1fr 310px; min-height: calc(100vh - 58px); }
    nav { border-right: 1px solid #dcdcde; padding: 24px 18px; color: #535158; background: #fbfafd; }
    nav div { padding: 9px 10px; border-radius: 4px; margin-bottom: 4px; }
    nav .active { background: #ececef; color: #1f1e24; font-weight: 700; }
    main { padding: 34px 42px; }
    aside { border-left: 1px solid #dcdcde; padding: 34px 26px; color: #535158; }
    .crumbs { color: #737278; font-size: 14px; margin-bottom: 18px; }
    h1 { color: #1f1e24; font-size: 34px; line-height: 1.2; margin: 0 0 12px; font-weight: 650; }
    .meta { color: #737278; font-size: 15px; margin-bottom: 24px; }
    .status { display: inline-flex; align-items: center; gap: 8px; color: #108548; font-weight: 700; margin: 4px 0 24px; }
    .status::before { content: ""; width: 12px; height: 12px; border-radius: 50%; background: #108548; }
    .description { border: 1px solid #dcdcde; border-radius: 6px; padding: 22px; font-size: 17px; line-height: 1.55; max-width: 880px; }
    .comment { margin-top: 28px; border-top: 1px solid #dcdcde; padding-top: 22px; max-width: 880px; color: #333238; }
    .label { display: inline-block; padding: 4px 8px; border-radius: 999px; margin: 4px 6px 4px 0; font-size: 13px; font-weight: 700; background: #e1d8f9; color: #5943b6; }
    aside h2 { margin: 0 0 16px; color: #333238; font-size: 17px; }
    .side-row { padding: 14px 0; border-top: 1px solid #ececef; }
    .side-label { font-size: 13px; color: #737278; margin-bottom: 6px; }
    .avatar { display: inline-grid; place-items: center; width: 30px; height: 30px; border-radius: 50%; background: #6b4fbb; color: white; font-weight: 800; margin-right: 8px; }
    .btn { display: inline-block; padding: 9px 12px; border: 1px solid #bfbfc3; border-radius: 4px; background: #fff; color: #333238; font-weight: 650; }
  </style>
</head>
<body>
  <header>
    <div class="fox">◆</div>
    <div class="brand">GitLab</div>
    <div>Projects</div>
    <div>Issues</div>
    <div>Merge requests</div>
    <div class="search">Search or go to...</div>
  </header>
  <div class="layout">
    <nav>
      <div>assafbar-group</div>
      <div class="active">flux-demo</div>
      <div>Repository</div>
      <div>Issues</div>
      <div>Merge requests</div>
      <div>CI/CD</div>
      <div>Settings</div>
    </nav>
    <main>
      <div class="crumbs">assafbar-group / flux-demo / Issues / #1</div>
      <h1>[billing/#412] Add invoice empty state</h1>
      <div class="meta">Opened by assafbar · work item #1 · mirrored in Flux as billing/#412</div>
      <div class="status">Open</div>
      <section class="description">
        <p>Demo good-first issue for Flux. Add the empty-state copy and verify the invoice list renders when no invoices exist.</p>
        <span class="label">billing</span>
        <span class="label">good-first-issue</span>
      </section>
      <section class="comment">
        <strong>Activity</strong>
        <p>Flux reads this issue through GitLab MCP, then only writes back after the user confirms the assignment.</p>
      </section>
    </main>
    <aside>
      <h2>Issue details</h2>
      <div class="side-row">
        <div class="side-label">Assignees</div>
        <span class="avatar">${assigned ? "A" : "?"}</span>${assignee}
      </div>
      <div class="side-row">
        <div class="side-label">Labels</div>
        <span class="label">billing</span><span class="label">good-first-issue</span>
      </div>
      <div class="side-row">
        <div class="side-label">Milestone</div>
        Week 1 onboarding
      </div>
      <div class="side-row">
        <span class="btn">Edit</span>
      </div>
    </aside>
  </div>
</body>
</html>`;
}

function notionGuideHtml() {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Notion</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { color: #37352f; background: #fff; font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #fff; }
    .shell { display: grid; grid-template-columns: 250px 1fr; min-height: 100vh; }
    aside { background: #fbfbfa; border-right: 1px solid #ededeb; padding: 18px 14px; color: #6b6964; }
    .workspace { display: flex; align-items: center; gap: 9px; color: #37352f; font-weight: 650; margin-bottom: 20px; }
    .mark { width: 22px; height: 22px; display: grid; place-items: center; border: 1px solid #c7c5c1; border-radius: 4px; background: #fff; font-weight: 800; }
    .nav { padding: 7px 9px; border-radius: 5px; margin: 3px 0; }
    .nav.active { background: #efefed; color: #37352f; font-weight: 650; }
    main { padding: 50px 96px 90px; max-width: 1160px; }
    .emoji { font-size: 56px; margin-bottom: 14px; }
    h1 { font-size: 42px; line-height: 1.15; margin: 0 0 24px; font-weight: 700; letter-spacing: 0; text-transform: none; }
    h2 { margin: 34px 0 12px; font-size: 25px; font-weight: 650; text-transform: none; letter-spacing: 0; }
    h3 { margin: 22px 0 8px; font-size: 19px; font-weight: 650; text-transform: none; letter-spacing: 0; }
    p, li { font-size: 16px; line-height: 1.5; text-transform: none; letter-spacing: 0; }
    ul { margin: 8px 0 16px; padding-left: 24px; }
    .callout { display: flex; gap: 12px; padding: 14px 16px; border-radius: 6px; background: #f7f6f3; margin: 16px 0; font-size: 16px; line-height: 1.45; text-transform: none; }
    .tag { display: inline-block; padding: 3px 8px; border-radius: 4px; margin-left: 5px; font-size: 14px; color: #7a4b00; background: #f6e5bc; }
    strong { font-weight: 700; }
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div class="workspace"><span class="mark">N</span> Assaf's Notion</div>
      <div class="nav">Search</div>
      <div class="nav">Inbox</div>
      <div class="nav active">New Hired 6 2 2026</div>
      <div class="nav">Engineering</div>
      <div class="nav">Team guide</div>
      <div class="nav">Roadmap</div>
    </aside>
    <main>
      <div class="emoji">🧭</div>
      <h1>New Hired 6 2 2026</h1>
      <div class="callout"><strong>Living onboarding guide.</strong> This is the human-written context Flux combines with GitLab activity before answering a new hire.</div>

      <h2>The Team (Real Talk)</h2>
      <h3>Marcus Chen — Senior Engineer <span class="tag">auth owner</span></h3>
      <ul>
        <li>Real ownership: Auth system, payments integration; reviews 70%+ of PRs in these areas.</li>
        <li>Availability: Offline Fridays after 4pm for school pickup.</li>
        <li>Best way: Slack DM first, then schedule a 30min pairing session.</li>
      </ul>
      <h3>Sarah Kim — Staff Engineer / Architect</h3>
      <ul>
        <li>System architecture and data model decisions.</li>
        <li>On parental leave until June 15, 2026. Talk to Dev instead.</li>
      </ul>
      <h3>Priya Patel — Engineering Lead</h3>
      <ul>
        <li>80% focused on enterprise migration until Q3.</li>
        <li>Thursday 1:1 is the right venue for anything strategic.</li>
      </ul>

      <h2>Right Now (updated May 2026)</h2>
      <ul>
        <li><strong>Live P1:</strong> SSO migration. Marcus owns it, blocked on Okta. Don't touch <strong>/auth</strong>.</li>
        <li><strong>Safe zones:</strong> billing module, notifications service, docs improvements.</li>
        <li><strong>Good first issues:</strong> billing/#412, notifications/#89.</li>
      </ul>

      <h2>Unwritten Rules</h2>
      <ul>
        <li>Don't ask "why didn't you use GraphQL?" in public.</li>
        <li>Friday deploys require explicit +1 from Marcus or Dev.</li>
        <li>#eng-general is read by the CEO and investors.</li>
      </ul>
    </main>
  </div>
</body>
</html>`;
}

function cloudRunScreenshotHtml(imageBase64) {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Cloud Run logs</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #fff; overflow: hidden; width: 100vw; height: 100vh; display: grid; place-items: center; }
    img { display: block; width: 100vw; height: 100vh; object-fit: contain; }
  </style>
</head>
<body>
  <img alt="Cloud Run service logs for Flux" src="data:image/png;base64,${imageBase64}" />
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

async function stabilizeAssignmentProposal(page) {
  await page.route("**/api/chat", async (route) => {
    const request = route.request();
    const payload = request.postDataJSON();
    if (request.method() === "POST" && payload?.message === "Assign issue #412 to me") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          answer: "I can assign issue #412 in the billing project to you. Please confirm this action before I write it to GitLab MCP.",
          sources: ["GitLab MCP", "Notion"],
          action: {
            type: "assign_issue",
            issue_id: "412",
            project: "billing",
            username: "newhire",
          },
        }),
      });
      return;
    }
    await route.continue();
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
  await scrollToLatest(page);
  await sleep(2500);
}

async function createGitLabPage(context, options) {
  const page = await context.newPage();
  await page.setContent(gitLabIssueHtml(options), { waitUntil: "domcontentloaded" });
  return page;
}

async function gotoRawPage(page, url) {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 90_000 });
  await sleep(10_000);
}

async function clickBrowserTab(index) {
  const centers = [235, 540, 840, 1140];
  const x = centers[index];
  await runAppleScript(`tell application "System Events" to click at {${x}, 75}`);
  await sleep(500);
}

async function showcaseTab(page, index, { scroll = 0 } = {}) {
  await page.bringToFront();
  await clickBrowserTab(index);
  await sleep(500);
  await page.mouse.move(220, 210, { steps: 28 });
  await page.mouse.move(760, 360, { steps: 34 });
  await sleep(1400);
  if (scroll) {
    await page.mouse.wheel(0, scroll);
    await sleep(1800);
  }
  await sleep(1600);
}

async function scrollToLatest(page) {
  await page.locator(".message").last().scrollIntoViewIfNeeded();
  await sleep(300);
  await page.evaluate(() => {
    window.scrollBy({ top: 260, behavior: "smooth" });
  });
  await sleep(900);
}

function startCapture() {
  return spawn("/usr/sbin/screencapture", [
    "-v",
    "-C",
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
  if (RESET_RECORDING_PROFILE) {
    await rm(PROFILE_DIR, { recursive: true, force: true });
  }
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
    await stabilizeAssignmentProposal(livePage);
    await livePage.goto(BASE_URL, { waitUntil: "networkidle" });
    await livePage.bringToFront();

    const gitlabPage = await createGitLabPage(context, { assigned: false });

    const notionPage = await context.newPage();
    await notionPage.setContent(notionGuideHtml(), { waitUntil: "domcontentloaded" });

    const cloudPage = await context.newPage();
    if (existsSync(CLOUD_RUN_SCREENSHOT_PATH)) {
      const imageBase64 = await readFile(CLOUD_RUN_SCREENSHOT_PATH, "base64");
      await cloudPage.setContent(cloudRunScreenshotHtml(imageBase64), { waitUntil: "domcontentloaded" });
    } else {
      await gotoRawPage(cloudPage, CLOUD_RUN_LOGS_URL);
    }

    await livePage.bringToFront();
    await sleep(1000);
    capture = startCapture();
    await sleep(2500);

    await showcaseTab(livePage, 0);
    await showcaseTab(gitlabPage, 1);
    await showcaseTab(notionPage, 2, { scroll: 380 });
    await showcaseTab(cloudPage, 3);

    await livePage.bringToFront();
    await clickBrowserTab(0);
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
    await scrollToLatest(livePage);
    await sleep(1800);
    const [confirmResponse] = await Promise.all([
      livePage.waitForResponse(
        (response) => response.url().includes("/api/action/confirm"),
        { timeout: 120_000 },
      ),
      moveAndClick(livePage, livePage.getByRole("button", { name: "Confirm assignment" }).first()),
    ]);
    if (!confirmResponse.ok()) {
      throw new Error(`Assignment failed with HTTP ${confirmResponse.status()}: ${await confirmResponse.text()}`);
    }
    await livePage.locator(".action-result").last().waitFor({ state: "visible" });
    await livePage.locator(".action-result").last().scrollIntoViewIfNeeded();
    await sleep(3500);

    await gitlabPage.setContent(gitLabIssueHtml({ assigned: true }), { waitUntil: "domcontentloaded" });
    await gitlabPage.bringToFront();
    await clickBrowserTab(1);
    await gitlabPage.mouse.move(980, 300, { steps: 28 });
    await sleep(5000);

    await cloudPage.bringToFront();
    await clickBrowserTab(3);
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
