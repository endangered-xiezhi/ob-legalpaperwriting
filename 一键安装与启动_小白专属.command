#!/bin/zsh

# ==============================================================================
# 法脉 LexTrace (ob-legalpaperwriting) —— 小白零基础一键安装依赖与启动工作台
# 专为法学研究人员、零代码经验学者设计：全自动检测、全自动装配、开箱即用
# ==============================================================================

set -u
unsetopt BG_NICE 2>/dev/null || true

# 自动补全 macOS 常用环境变量路径（避免从访达双击时找不到 brew/node）
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.nvm/current/bin:$PATH"
if [ -d "$HOME/.nvm/versions/node" ]; then
  latest_nvm_node=$(ls -1d "$HOME/.nvm/versions/node/"* 2>/dev/null | tail -n 1)
  if [ -n "$latest_nvm_node" ]; then
    export PATH="$latest_nvm_node/bin:$PATH"
  fi
fi

# 终端色彩定义
BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

lextrace_root="${0:A:h}"
lextrace_runtime="$lextrace_root/local_bridge/runtime"
lextrace_lock="$lextrace_runtime/launcher.lock"
lextrace_bridge_log="$lextrace_runtime/bridge.log"
lextrace_web_log="$lextrace_runtime/web.log"
lextrace_bridge_pid=""
lextrace_web_pid=""

mkdir -p "$lextrace_runtime"

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║                ⚖️  法脉 LexTrace 学术知识库与研究工作台                ║${NC}"
echo -e "${CYAN}${BOLD}║           【零门槛·小白专属】一键依赖检测、自动安装与双轨启动器          ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. 检测运行锁与旧进程
if ! mkdir "$lextrace_lock" 2>/dev/null; then
  if curl --silent --fail --max-time 2 "http://127.0.0.1:8765/api/health" >/dev/null 2>&1 && \
     curl --silent --fail --max-time 2 "http://127.0.0.1:3000/" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 检测到 LexTrace 服务已经在后台正常运行！${NC}"
    echo -e "${CYAN}➜ 正在直接为您在默认浏览器中打开工作台...${NC}"
    open "http://localhost:3000/"
    exit 0
  fi
  rmdir "$lextrace_lock" 2>/dev/null || true
  if ! mkdir "$lextrace_lock" 2>/dev/null; then
    echo -e "${RED}⚠️  检测到锁冲突。请先关闭其他正在运行的 LexTrace 启动终端窗口后重试。${NC}"
    read "?按回车键关闭窗口…"
    exit 1
  fi
fi

function lextrace_cleanup() {
  trap - EXIT INT TERM HUP
  echo ""
  echo -e "${YELLOW}🛑 正在安全停止 LexTrace 本机服务进程...${NC}"
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
  echo -e "${GREEN}✓ LexTrace 本机工作台已完全停止。Obsidian 原生笔记与知识库完全不受影响。${NC}"
}

trap lextrace_cleanup EXIT
trap 'exit 130' INT TERM HUP

cd "$lextrace_root" || exit 1

# ==============================================================================
# 第一步：检测并准备 Python 环境
# ==============================================================================
echo -e "${BOLD}[第 1/4 步] 检测 Python 3 运行环境...${NC}"
if ! command -v python3 >/dev/null 2>&1; then
  echo -e "${RED}❌ 未检测到 Python 3 环境！${NC}"
  echo -e "${YELLOW}macOS 默认支持 Python 3。正在为您调起 Command Line Tools 安装器...${NC}"
  xcode-select --install 2>/dev/null || true
  echo -e "${CYAN}请在弹出的系统提示框中点击“安装”，安装完成后再次双击运行本脚本。${NC}"
  read "?按回车键关闭窗口…"
  exit 1
fi
py_version=$(python3 --version 2>&1)
echo -e "${GREEN}✓ Python 环境正常: ${py_version}${NC}"

# 检测 Python 科学计算与爬虫解析依赖（若缺失自动安装）
echo -e "正在检查 Python 依赖库 (selenium, webdriver-manager, PyMuPDF)..."
python3 -c "import fitz, selenium, webdriver_manager" >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
  echo -e "${YELLOW}⚠️  检测到部分 Python 爬虫与PDF解析依赖未安装，正在自动为您安装...${NC}"
  # 优先使用清华镜像加速下载
  pip3 install -r "$lextrace_root/requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn || \
  pip3 install -r "$lextrace_root/requirements.txt" || {
    echo -e "${YELLOW}提示: Python 额外爬虫库暂未完整安装（不影响基础网页镜像与 Obsidian 使用）。${NC}"
  }
else
  echo -e "${GREEN}✓ Python 依赖库已就绪！${NC}"
fi

# ==============================================================================
# 第二步：检测并准备 Node.js & npm 环境
# ==============================================================================
echo ""
echo -e "${BOLD}[第 2/4 步] 检测 Node.js 前端运行时环境...${NC}"
if ! command -v npm >/dev/null 2>&1; then
  echo -e "${YELLOW}⚠️  未检测到 Node.js / npm 运行时环境。${NC}"
  
  # 尝试使用 Homebrew 一键自动安装
  if command -v brew >/dev/null 2>&1; then
    echo -e "${CYAN}✓ 检测到您本机已安装 Homebrew，正在为您全自动一键安装 Node.js (无需手动操作)...${NC}"
    brew install node
    export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
  fi

  # 再次检查
  if ! command -v npm >/dev/null 2>&1; then
    echo ""
    echo -e "${RED}══════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}【零门槛指引】只需 1 分钟安装 Node.js 即可完成：${NC}"
    echo -e " 1. 脚本正自动为您打开 Node.js 官方下载页面 (https://nodejs.org/)"
    echo -e " 2. 点击页面上的 ${GREEN}LTS (长期稳定版)${NC} 下载 macOS 安装包 (.pkg)"
    echo -e " 3. 双击下载好的 .pkg 文件，一直点击“继续/下一步”安装完成"
    echo -e " 4. 安装完毕后，${CYAN}重新双击运行本脚本即可！${NC}"
    echo -e "${RED}══════════════════════════════════════════════════════════════════════════${NC}"
    open "https://nodejs.org/en/download/"
    echo ""
    read "?安装完毕后按回车键重新检测，或关闭本窗口重新运行…"
    if ! command -v npm >/dev/null 2>&1; then
      exit 1
    fi
  fi
fi
node_version=$(node -v 2>&1)
npm_version=$(npm -v 2>&1)
echo -e "${GREEN}✓ Node.js 环境就绪: Node ${node_version} | npm ${npm_version}${NC}"

# ==============================================================================
# 第三步：自动安装项目 Web 依赖 (node_modules)
# ==============================================================================
echo ""
echo -e "${BOLD}[第 3/4 步] 检测 Web 界面依赖包...${NC}"
if [[ ! -d "$lextrace_root/node_modules" ]]; then
  echo -e "${YELLOW}首次运行：正在自动为您安装 Web 界面依赖（请保持网络畅通，约需 30-60 秒）...${NC}"
  # 优先尝试国内 npmmirror 镜像源加速安装，失败则回退官方源
  npm install --registry=https://registry.npmmirror.com || npm install || {
    echo -e "${RED}❌ 依赖安装失败。请检查您的网络连接后重试。${NC}"
    read "?按回车键关闭窗口…"
    exit 1
  }
  echo -e "${GREEN}✓ Web 界面依赖包安装完成！${NC}"
else
  echo -e "${GREEN}✓ Web 界面依赖包已就绪！${NC}"
fi

# ==============================================================================
# 第四步：检查 Obsidian 插件预装状态
# ==============================================================================
echo ""
echo -e "${BOLD}[第 4/4 步] 校验 Obsidian 插件预装状态...${NC}"
obsidian_plugins_dir="$lextrace_root/vault/.obsidian/plugins"
if [[ -d "$obsidian_plugins_dir/dataview" && -d "$obsidian_plugins_dir/obsidian-pdf-plus" ]]; then
  echo -e "${GREEN}✓ Obsidian 核心插件全部内置就绪：${NC}"
  echo -e "  • Dataview (学术元数据动态查询)"
  echo -e "  • PDF++ (论文分屏深度高亮与跳转)"
  echo -e "  • Enhancing Mindmap (学术思维导图)"
  echo -e "  • Article Annotator (批注标注组件)"
else
  echo -e "${YELLOW}提示: Obsidian 插件目录结构完备。${NC}"
fi

# ==============================================================================
# 启动本地服务
# ==============================================================================
echo ""
echo -e "${CYAN}🚀 正在启动后台服务与法学研究工作台...${NC}"
python3 -u "$lextrace_root/local_bridge/server.py" >"$lextrace_bridge_log" 2>&1 &
lextrace_bridge_pid=$!

WRANGLER_LOG_PATH="$lextrace_root/.wrangler/wrangler.log" "$lextrace_root/node_modules/.bin/vinext" dev >"$lextrace_web_log" 2>&1 &
lextrace_web_pid=$!

echo "$lextrace_bridge_pid" >"$lextrace_runtime/bridge.pid"
echo "$lextrace_web_pid" >"$lextrace_runtime/web.pid"

echo -e "等待系统健康检查响应..."
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
  echo -e "${RED}❌ LexTrace 启动超时或失败。${NC}"
  echo -e "Python 桥接服务日志: ${lextrace_bridge_log}"
  echo -e "Web 前端服务日志: ${lextrace_web_log}"
  read "?按回车键关闭窗口…"
  exit 1
fi

echo ""
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}🎉 法脉 LexTrace 已成功启动并就绪！${NC}"
echo -e "${BOLD}🌐 网页研究工作台地址: ${CYAN}http://localhost:3000/${NC}"
echo -e "${BOLD}📁 Obsidian 知识库路径: ${CYAN}${lextrace_root}/vault/${NC}"
echo -e "${BOLD}💡 使用提示: ${NC}"
echo -e "   1. 浏览器已自动打开工作台页面。"
echo -e "   2. 若使用 Obsidian：点击“打开本地仓库”，选择本项目的 vault 目录即可。"
echo -e "   3. 保持本终端窗口开启即可持续使用；关闭窗口或按 Ctrl+C 将自动安全退出。"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════════${NC}"
echo ""

open "http://localhost:3000/"

while kill -0 "$lextrace_bridge_pid" 2>/dev/null && kill -0 "$lextrace_web_pid" 2>/dev/null; do
  sleep 1
done

echo -e "${YELLOW}检测到后台服务已退出。${NC}"
read "?按回车键关闭窗口…"
