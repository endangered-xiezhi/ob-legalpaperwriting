#!/bin/zsh

# 获取脚本所在绝对目录
script_dir="${0:A:h}"
cd "$script_dir" || exit 1

echo "============================================================"
echo "          正在启动知网学术论文采集器 (CNKI Spider)          "
echo "============================================================"
echo "工作目录：$script_dir"
echo ""

# 检查 Python 环境
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ 错误：未检测到 python3，请先安装 Python 3 环境。"
    read "?按回车键退出…"
    exit 1
fi

# 检查 Python 基础依赖库
python3 -c "import selenium, webdriver_manager, fitz" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️ 首次检测：部分依赖包未安装，正在自动安装所需依赖……"
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败，请检查网络或在终端手动运行：pip3 install -r requirements.txt"
        read "?按回车键退出…"
        exit 1
    fi
fi

# 启动爬虫主交互程序
python3 run_spider.py

exit_code=$?
echo ""
echo "============================================================"
echo "知网采集器已退出（状态码: $exit_code）。"
echo "所有下载的 PDF、分页 TXT 与元数据已保存在对应目录下。"
echo "============================================================"
read "?按回车键关闭本窗口…"
