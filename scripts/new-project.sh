#!/usr/bin/env bash
# 一键起一个新的组态项目：bash new-project.sh <目录> [页面名，默认 index]
# 复制引擎 / 外壳样式 / 示例页面 / 导出器，装依赖。
set -e
SK="$(cd "$(dirname "$0")/.." && pwd)/assets"; DST="${1:?用法: new-project.sh <目录> [页面名]}"; PAGE="${2:-index}"
mkdir -p "$DST/js" "$DST/css" "$DST/tools/pack" "$DST/exports"
cp "$SK"/engine/*.js "$DST/js/"; cp "$SK/shell/style.css" "$DST/css/"
cp "$SK/starter/index.html" "$DST/$PAGE.html"; cp "$SK/starter/css/app.css" "$DST/css/"; cp "$SK"/starter/js/*.js "$DST/js/"
cp "$SK/starter/serve.py" "$SK/starter/package.json" "$DST/"
cp "$SK/pack/export.html" "$SK/pack/build-pack.mjs" "$SK/pack/make-zips.py" "$SK/pack/README.md" "$DST/tools/pack/"
cd "$DST" && { [ -d node_modules/three ] || npm install --no-audit --no-fund; }
echo "已创建 $DST。运行：cd $DST && python3 serve.py 8080  → http://localhost:8080/$PAGE.html"
echo "改 js/plant.js（三维布局）、js/sim.js（台账 + 仿真）、js/main.js（界面驱动）；素材包导出配置见 tools/pack/export.html 顶部。"
