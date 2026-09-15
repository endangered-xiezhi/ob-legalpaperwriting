import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const serverEntry = path.join(root, "dist", "server", "index.js");
const clientDir = path.join(root, "dist", "client");

console.log("⚡ 正在执行云端静态渲染 (Pre-rendering for Vercel / Cloud Static)...");

if (!fs.existsSync(serverEntry)) {
  console.error("❌ 未找到服务端入口:", serverEntry);
  process.exit(1);
}

try {
  const { default: worker } = await import(serverEntry);
  const response = await worker.fetch(
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
    }
  );

  if (response.status !== 200) {
    throw new Error(`渲染响应状态异常: ${response.status}`);
  }

  const html = await response.text();
  const indexPath = path.join(clientDir, "index.html");
  const notFoundPath = path.join(clientDir, "404.html");

  fs.writeFileSync(indexPath, html, "utf-8");
  fs.writeFileSync(notFoundPath, html, "utf-8");

  console.log(`✓ 成功生成 ${indexPath} (${html.length} 字节)`);
  console.log(`✓ 成功生成 ${notFoundPath} (SPA Fallback)`);
} catch (err) {
  console.error("❌ 预渲染失败:", err);
  process.exit(1);
}
