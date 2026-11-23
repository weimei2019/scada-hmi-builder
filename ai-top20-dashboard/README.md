# GitHub AI 开源项目 Star Top 20 · 数据看板

本看板托管于 `weimei2019/scada-hmi-builder` 仓库的 `ai-top20-dashboard/` 子目录，每日自动抓取 GitHub 上 8 个 AI 相关主题下 Star 数最高的开源项目，经质量筛选后生成 Top 20 排行数据看板（单文件 `index.html`，无外部依赖，可离线打开）。

## 仓库结构

| 文件 | 说明 |
|---|---|
| `index.html` | 数据看板（数据内联，双击即可打开） |
| `build.py` | 抓取 / 筛选 / 排序 / 渲染脚本（每日自动化入口） |
| `template.html` | 看板模板（`build.py` 注入数据后生成 `index.html`） |
| `data/latest.json` | 最新一期 Top 20 结构化数据 |
| `data/history.json` | 每日快照，用于计算 Star 增量（保留最近 60 期） |

原始抓取缓存保留在本地工作区 `data/cache/`，不入库，避免仓库体积膨胀。

## 数据口径

1. **检索**：对 `topic:ai`、`topic:llm`、`topic:machine-learning`、`topic:deep-learning`、`topic:artificial-intelligence`、`topic:generative-ai`、`topic:ai-agents`、`topic:chatgpt` 各按 Star 降序取前 100，按 `full_name` 去重得到候选池。
2. **纳入**：可运行的 AI 软件项目（框架、推理引擎、Agent 工具链、应用平台、生成式内容工具）。
3. **排除**：Awesome 清单、Prompt / 系统提示词合集、课程与教材、面试指南、与 AI 无实质关联的通用基础设施。被排除的高星仓库及原因在 `index.html` 底部"被排除的高星仓库"折叠区可查。
4. **排序**：按 `stargazers_count` 降序取 Top 20，同分按 Fork 次序。

## 本地运行

```bash
python build.py            # 在线抓取并重建看板
python build.py --offline  # 复用最近缓存，不请求网络
```

依赖：Python 3.8+ 与已登录的 `gh` CLI（或具备 `read:packages` 等价权限的 GitHub Token 环境变量）。搜索 API 限额为认证 30 次/分钟，单次运行 8 个请求，余量充足。

## 自动更新

每日 09:00（UTC+8）由 WorkBuddy 自动化任务执行 `build.py` 并将结果提交回 `weimei2019/scada-hmi-builder` 的 `ai-top20-dashboard/` 目录。
