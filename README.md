# SCADA 2.5D Builder

用于构建浏览器 2.5D SCADA / HMI 组态演示的 Claude Code / Codex / WorkBuddy 通用 skill，包含共享可视化框架、可运行示例、工艺仿真与素材包导出工具。

## 功能

- 从工艺图、P&ID、设备清单等资料建立设备台账和三维场景。
- 设备状态、备用泵自动切换、报警、联锁和工艺仿真。
- 参数面板、设备详情、分区视角、场景全屏和 PNG 导出。
- 按需导出 GLB、PNG 图标、SVG、设备坐标和点位清单。

## 安装 skill

### Claude Code

```bash
git clone https://github.com/Howe829/scada-25d-builder.git ~/.claude/skills/scada-25d-builder
```

在对话中使用 `/scada-25d-builder` 或直接描述组态需求。

### Codex

用户级安装：

```bash
git clone https://github.com/Howe829/scada-25d-builder.git ~/.agents/skills/scada-25d-builder
```

也可以在目标项目根目录安装到 `.agents/skills/scada-25d-builder`。在 Codex 中使用 `$scada-25d-builder`，或从 `/skills` 选择；未显示时重启 Codex。同名 skill 只保留一份安装，避免重复显示。

### WorkBuddy

从 [Releases](https://github.com/Howe829/scada-25d-builder/releases) 下载 `scada-25d-builder-workbuddy.zip`，在 WorkBuddy 技能页选择「添加技能 → 上传技能」，导入 ZIP 并启用。然后在对话中说：“使用 scada-25d-builder，制作一个带备用泵切换和报警的污水处理组态演示。”

也可在仓库根目录自行生成导入包（仅需 Python 3）：

```bash
python3 scripts/package-skill.py --target workbuddy
```

输出为 `dist/scada-25d-builder-workbuddy.zip`。专用包会补齐 WorkBuddy 展示元数据；Codex 和 Claude Code 继续使用仓库中的标准 `SKILL.md`。

以上是格式与安装方式适配；WorkBuddy 客户端中的实际导入与完整交互尚未实测。

安装依据：[Codex 官方文档](https://learn.chatgpt.com/docs/build-skills)、[WorkBuddy 技能结构](https://open.workbuddy.cn/docs/skill)、[WorkBuddy 导入说明](https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills)。完整流程见 [SKILL.md](SKILL.md)。

## 运行示例

需要 Bash、Node.js 18+、npm 和 Python 3（Windows 可用 WSL）；截图和素材导出工具还需要 Google Chrome（默认路径 `/usr/bin/google-chrome`）。

```bash
cd <skill安装目录>
bash scripts/new-project.sh ~/work/my-scada
cd ~/work/my-scada
python3 serve.py 8080
```

打开 http://localhost:8080/index.html 。修改 `js/plant.js` 配置场景、`js/sim.js` 配置台账与仿真、`js/main.js` 配置界面交互。

示例使用浏览器仿真数据，连接真实 PLC 需要自行实现数据接入层。

## 目录

- `SKILL.md`：skill 入口与工作流程。
- `references/`：图纸解析、场景、仿真、界面和交付参考。
- `assets/engine/`：基于 Three.js 的组态可视化框架。
- `assets/starter/`：可运行示例。
- `assets/shell/`：界面公共样式。
- `assets/pack/`：素材导出工具。
- `scripts/new-project.sh`：新项目初始化脚本。

## 许可证

Copyright (C) 2026 HowardChan (Howe829).

本仓库原创文档、代码和模板采用 **GNU Affero General Public License version 3 only**（`AGPL-3.0-only`），详见 [LICENSE](LICENSE)。允许在该许可证条件下使用、修改和再分发；不提供任何担保。

分发包含本项目代码的衍生作品时，应遵守 AGPLv3 的源码提供要求；修改版本支持网络交互时，应按第 13 条向远程交互用户提供对应源码。AGPLv3 允许商用。

初始化脚本会复制本仓库的框架和模板代码到新项目，因此生成项目中这些代码仍受 AGPLv3 约束。发布此类项目时，请保留版权和许可声明，并附上本仓库的 LICENSE；脚本不会自动复制许可证。

通过 npm 安装的第三方依赖保留各自的许可证，本仓库的许可声明不替代其许可条件。
