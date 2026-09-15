#!/bin/zsh

set -u
unsetopt BG_NICE 2>/dev/null || true

# 自动补全 macOS 环境变量路径
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.nvm/current/bin:$PATH"
if [ -d "$HOME/.nvm/versions/node" ]; then
  latest_nvm_node=$(ls -1d "$HOME/.nvm/versions/node/"* 2>/dev/null | tail -n 1)
  if [ -n "$latest_nvm_node" ]; then
    export PATH="$latest_nvm_node/bin:$PATH"
  fi
fi

lextrace_root="${0:A:h}"
lextrace_runtime="$lextrace_root/local_bridge/runtime"
lextrace_lock="$lextrace_runtime/launcher.lock"
lextrace_bridge_log="$lextrace_runtime/bridge.log"
lextrace_web_log="$lextrace_runtime/web.log"
lextrace_bridge_pid=""
lextrace_web_pid=""

mkdir -p "$lextrace_runtime"

if ! mkdir "$lextrace_lock" 2>/dev/null; then
  if curl --silent --fail --max-time 2 "http://127.0.0.1:8765/api/health" >/dev/null 2>&1 && \
     curl --silent --fail --max-time 2 "http://127.0.0.1:3000/" >/dev/null 2>&1; then
    echo "LexTrace 已经在运行，正在打开现有页面。"
    open "http://localhost:3000/"
    exit 0
  fi
  rmdir "$lextrace_lock" 2>/dev/null || true
  if ! mkdir "$lextrace_lock" 2>/dev/null; then
    echo "无法取得启动锁。请关闭旧的 LexTrace 启动窗口后重试。"
    read "?按回车关闭窗口…"
    exit 1
  fi
fi

function lextrace_cleanup() {
  trap - EXIT INT TERM HUP
  if [[ -n "$lextrace_web_pid" ]] && kill -0 "$lextrace_web_pid" 2>/dev/null; then
    kill "$lextrace_web_pid" 2>/dev/null || true
  fi
  if [[ -n "$lextrace_bridge_pid" ]] && kill -0 "$lextrace_bridge_pid" 2>/dev/null; then
    kill "$lextrace_bridge_pid" 2>/dev/null || true
  fi
  wait "$lextrace_web_pid" 2>/dev/null || true
  wait "$lextrace_bridge_pid" 2>/dev/null || true
  rmdir "$lextrace_lock" 2>/dev/null || true
  command rm -f "$lextrace_runtime/bridge.pid" "$lextrace_runtime/web.pid"
  echo "LexTrace 本机工作台已停止。Obsidian 原生导航不受影响。"
}

trap lextrace_cleanup EXIT
trap 'exit 130' INT TERM HUP

cd "$lextrace_root" || exit 1

if ! command -v npm >/dev/null 2>&1; then
  echo "未找到 Node.js / npm，无法启动网页镜像。"
  echo "你仍可直接使用 Obsidian 中的 00_知识产权研究导航。"
  read "?按回车关闭窗口…"
  exit 1
fi

if [[ ! -d "$lextrace_root/node_modules" ]]; then
  echo "首次运行：正在安装网页依赖。"
  npm install || {
    echo "依赖安装失败。请检查网络后重试。"
    read "?按回车关闭窗口…"
    exit 1
  }
fi

echo "正在启动 Obsidian 本机桥接和法学研究工作台…"
python3 -u "$lextrace_root/local_bridge/server.py" >"$lextrace_bridge_log" 2>&1 &
lextrace_bridge_pid=$!
WRANGLER_LOG_PATH="$lextrace_root/.wrangler/wrangler.log" "$lextrace_root/node_modules/.bin/vinext" dev >"$lextrace_web_log" 2>&1 &
lextrace_web_pid=$!

echo "$lextrace_bridge_pid" >"$lextrace_runtime/bridge.pid"
echo "$lextrace_web_pid" >"$lextrace_runtime/web.pid"

lextrace_ready=0
for lextrace_attempt in {1..80}; do
  if curl --silent --fail --max-time 2 "http://127.0.0.1:8765/api/health" >/dev/null 2>&1 && \
     curl --silent --fail --max-time 2 "http://127.0.0.1:3000/" >/dev/null 2>&1; then
    lextrace_ready=1
    break
  fi
  if ! kill -0 "$lextrace_bridge_pid" 2>/dev/null || ! kill -0 "$lextrace_web_pid" 2>/dev/null; then
    break
  fi
  sleep 0.5
done

if [[ "$lextrace_ready" -ne 1 ]]; then
  echo "LexTrace 启动失败。"
  echo "桥接日志：$lextrace_bridge_log"
  echo "网页日志：$lextrace_web_log"
  read "?按回车关闭窗口…"
  exit 1
fi

echo ""
echo "LexTrace 已启动：http://localhost:3000/"
echo "目录将每10秒检查一次 Obsidian 更新。"
echo "采集器只会创建新论文待审核样板，不会改写现有论文笔记。"
echo "请保持本窗口开启；关闭或按 Ctrl+C 即停止网页镜像。"
open "http://localhost:3000/"

while kill -0 "$lextrace_bridge_pid" 2>/dev/null && kill -0 "$lextrace_web_pid" 2>/dev/null; do
  sleep 1
done

echo "检测到服务退出，请查看 runtime 日志。"
read "?按回车关闭窗口…"
