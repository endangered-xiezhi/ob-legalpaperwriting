import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

const templateRoot = new URL("../", import.meta.url);

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the LexTrace Obsidian guide", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>LexTrace｜Obsidian 法学研究工作台<\/title>/i);
  assert.match(html, /Obsidian Research Workbench/);
  assert.match(html, /研究导航/);
  assert.match(html, /采集与待处理/);
  assert.match(html, /关系工作台/);
  assert.match(html, /引注中心/);
  assert.match(html, /Agent 任务单/);
  assert.match(html, /从采集到引注/);
  assert.match(html, /10秒自动检查/);
  assert.doesNotMatch(
    html,
    /codex-preview|Your site is taking shape|react-loading-skeleton/i,
  );
});

test("removes starter preview code and exposes product metadata", async () => {
  const [page, layout, packageJson, workbench, bridge] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../app/obsidian-workbench.tsx", import.meta.url), "utf8"),
    readFile(new URL("../local_bridge/server.py", import.meta.url), "utf8"),
  ]);

  assert.match(page, /ObsidianWorkbench/);
  assert.match(layout, /Obsidian 法学研究工作台/);
  assert.match(layout, /og\.png/);
  assert.match(workbench, /api\/vault\/version/);
  assert.match(workbench, /10_000/);
  assert.doesNotMatch(workbench, /api\/agent\/chat|api\/settings\/api|apiKey/);
  assert.match(bridge, /readOnly/);
  assert.match(bridge, /\/api\/vault\/navigation/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
  await Promise.all([
    assert.rejects(
      access(new URL("app/_sites-preview/SkeletonPreview.tsx", templateRoot)),
    ),
    assert.rejects(
      access(new URL("app/_sites-preview/preview.css", templateRoot)),
    ),
  ]);
});
