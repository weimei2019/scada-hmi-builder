---
name: scada-25d-builder
description: 做任意行业的「2.5D 三维组态（SCADA / HMI）演示页」的通用流程：从 P&ID / 工艺图 / DWG 竣工图 / 设备采购单 / 客户修改建议出发，用共享引擎搭三维工艺场景（设备、管线、水面、标签、仪表数值牌），配设备台账 + 工艺仿真 + 联锁 / 备用泵 / 报警 + 设备状态（正常 / 异常 / 离线），再加右侧参数卡、设备详情、分区视角、只显示场景的全屏、导出 PNG，并按需导出组态素材包（GLB / PNG 图标 / SVG / 坐标 / 点位清单 / 状态版）。用户提到组态、SCADA、HMI、工艺流程画面、P&ID 转三维、做某个工艺的监控页面 / 三维画面、按图纸做组态、把组态素材打包导出、解析 DWG / 图纸 / 采购单来改组态页面时，都要使用这个 skill，即使用户没有说“skill”。具体工艺（如换热站）有专门 skill 时一起用。
---

# 通用 2.5D 组态页制作流程

本 skill 适用于 Claude Code、Codex 和 WorkBuddy。用随包共享框架制作各行业的浏览器组态演示：纯前端、无后端、数据是浏览器里的工艺仿真，接真实 PLC 时替换数据层。一页 = 场景（几何）+ 台账与仿真（数据）+ 界面（HTML 面板）。

## 宿主与路径

- **资源定位**：以当前加载的 `SKILL.md` 所在目录为 skill 根目录，以下 `references/`、`assets/`、`scripts/` 都相对它解析；不要相对用户工作目录查找，也不要假定安装在 `~/.claude/skills`。
- **执行**：用宿主提供的终端 / Shell 工具运行脚本，用文件读取和图片查看工具查看资料与截图；不依赖某个工具的专用名称。先确定用户的目标项目目录，再在该目录生成产物。
- **初始化**：`bash "<skill根目录>/scripts/new-project.sh" "<目标项目目录>"`。Windows 需在 WSL 或已具备 Node.js、Python 3 的 Bash 环境执行；不可用时按脚本中的目录映射复制模板并安装依赖，说明未能验证的步骤。
- **项目约定**：遵循宿主实际加载的项目指令。交付文档优先更新项目已有说明：Codex 常用 `AGENTS.md`，Claude Code 常用 `CLAUDE.md`，WorkBuddy 沿用其项目现有说明；没有时使用项目 README。记忆功能仅在宿主提供时使用。
- **可选资料**：`docs/组态行业图谱.md`、`heat-exchange-station` 等项目或外部 skill 仅在实际存在时参考；本包自身包含启动示例，不依赖它们。

## 一、总流程（按这个顺序，别跳步）

1. **读懂输入**：图纸 / 采购单 / 修改建议 / 竣工图（`references/drawings-to-scene.md`）。图纸读不清的地方**当场列成待确认清单**，不要凭印象补；补的内容必须在回复里标明“这是我补的”。
2. **建台账**：设备唯一编号 / 位号 / 名称 / 型号 / 参数 / 数量 / 变频 / 功率 / 联锁说明，数据来源以采购单为准（`references/ledger-sim-alarm.md`）。
3. **搭场景**：先用**展开式布局**把流程摆清楚，再接管线、放标签（`references/engine-and-kit.md`）。
4. **接仿真**：工艺模型 + 控制（备用泵、PID、顺序控制）+ 报警，**跑 30–50 分钟虚拟时间确认不发散**。
5. **做界面**：参数卡、详情卡、报警条、视角条、全屏、导出（`references/ui-patterns.md`）。
6. **验证**：无头 Chrome 截图（默认 / 特写 / 详情 / 故障 / 离线）逐张看，点交互走一遍（`references/delivery-qa.md`）。
7. **交付**：给出打开地址、截图路径、需要确认的假设；需要时导出素材包（`references/asset-pack-export.md`）；按上面的宿主约定更新项目说明与可用记忆。

## 二、八条原则（都是被用户反馈出来的）

1. **风格以“已有页面”为准**：用户说“和某某项目一样的风格”时，指的是共享引擎的 2.5D 三维 + 名称牌 / 数值牌 / 泵状态牌 + 蓝白玻璃面板。第一版不要自作主张做成二维图纸；二维图纸版可以作为附加视图保留。
2. **清晰优先于比例精确**：竣工图 1:1 的设备区往往只有十几米见方，放到屏幕上标签会叠成一团，用户的反馈是“还不如原来清晰”。图纸用来校正**工艺流向、设备配置、相对位置关系**，布局要展开到每个设备 / 标签有空间；真实比例版可以留作 `?layout=` 对照。
3. **介质要有真实颜色**：废水是浑浊的灰黄绿，达标出水才是清澈的蓝，药剂、污泥、清水各一色；水面着色器的 `deep / light` 跟着介质变，池内沿流程逐格变清也很有说服力。
4. **设备不整体染色，状态用灯 / 点表示**：名称牌前的圆点（绿正常 / 红闪异常 / 灰离线），没有名称牌的设备补一盏小灯；离线时搅拌 / 旋转件停转、水面冻结、数值显示 `--`。
5. **控制联动要“真”**：备用泵故障自动切换并写一条信息事件；压滤机等顺序设备要受阀门 / 泵状态约束（阀没开就不进料）；手动模式下才允许点启停；离线时按钮禁用。
6. **标签要分级**：全景只显示名称牌和关键数值，泵牌 / 流向箭头 / 次要数值只在放大后出现；再给**分区视角条**（点一下镜头飞过去），不要让用户靠放大找东西。
7. **全屏 = 只显示模型场景**：隐藏顶栏 / 导航 / 参数卡 / 报警条，镜头拉近，右上角留一个半透明“退出全屏”；Esc / F 也能退。
8. **项目名 / 位号 / 参数以资料为准**：用户口头说的名字可能是同音字（输入法），资料里的写法要核对并和用户确认；外设（客户已有设备、利旧）要标“利旧，不在采购范围，参数以现场铭牌为准”。

## 三、目录与命名约定

| 类型 | 位置 |
|---|---|
| 页面 | `<name>.html` + `js/<name>.js`（界面 + 驱动）+ `js/<name>-plant.js`（三维布局）+ `js/<name>-sim.js`（台账 + 仿真，**不依赖画面**，方便换成真实点位）+ `css/<name>.css` |
| 共享 | `js/engine.js`（引擎）、`js/factory.js`（通用设备 / 管道 / 水面）、`js/fx.js`（粒子 / 扫描线 / 光柱等特效）、`css/style.css`（外壳：顶栏、导航、玻璃卡、标签、底部三块） |
| 截图 / 成片 | `exports/<项目名>_<页面>[_<场景>].png` |
| 素材包 | `tools/pack/`（导出页 + 构建脚本 + 打 zip），输出 `exports/<项目名>_素材包/` 等 |

页面参数约定：`?demo=0`（模拟通信失败 / 离线）、`?sel=<设备>`（预选）、`?fault=1`（预置故障）、`?freeze=1`（不推进仿真，截图用）、`?warm=<秒>`（预热）、`?view=<视角>`、`?layout=<版式>`、`?theme=dark|light`、`?ao=0` `?fx=0`（排查渲染问题）。

## 四、新页面的最小骨架（完整可运行版本见第六节 `assets/starter/`）

```html
<!-- 外壳：header / nav / 左上图例 / 右上参数卡 / footer(报警+快捷操作+用户时钟) / #tooltip / #toast；画布 #gl + 标签层 #labels -->
<script type="module" src="js/<name>.js"></script>
```

```js
import { createEngine } from './engine.js';
const engine = createEngine({ fill: true, view: { fov: 19, target: [..], dist: .., polar: 0.86, offset: [14, -46], limits: {..} }, exportName: () => '<项目名>_工艺流程' });
const plant = buildPlant(engine.scene);          // 返回 { labels, selectables, pumps }
engine.optimize(plant.selectables);              // 静态合并（之后改材质要先打 userData 标记）
engine.addLabels(plant.labels);  engine.enableHover(plant.selectables, html);  engine.onClick(select);
engine.start();
```

## 五、什么时候读哪份参考

- 动手搭场景 / 写设备 / 接管线 → `references/engine-and-kit.md`
- 拿到图纸、采购单、DWG、修改建议 → `references/drawings-to-scene.md`
- 写台账、联锁、仿真、报警、状态 → `references/ledger-sim-alarm.md`
- 做面板、视角、全屏、详情卡、标签分级 → `references/ui-patterns.md`
- 要导出 GLB / 图标 / SVG / 点位 → `references/asset-pack-export.md`
- 截图验证、交付说明、踩坑排查 → `references/delivery-qa.md`

## 六、自带可运行的引擎 / 示例 / 导出器（`assets/`，不依赖任何现有仓库）

| 路径 | 内容 |
|---|---|
| `assets/engine/` | `engine.js`（引擎）、`factory.js`（设备 / 管道 / 水面）、`fx.js`（特效），基于 three.js 0.170 的自研组态框架（引擎 ≈ 485 行，不是从零写的渲染器） |
| `assets/shell/style.css` | 外壳样式（顶栏、导航、玻璃卡、标签、底部三块、提示 / toast、状态点） |
| `assets/starter/` | **可直接运行的示例页**：`index.html` + `css/app.css` + `js/{plant,sim,main}.js`（调节池 → 一用一备提升泵 → 反应罐：台账、备用泵自动切换、报警、参数卡折叠、视角条、只显示场景的全屏、离线、模拟异常 / 复位）+ `serve.py`（禁缓存 + Range）+ `package.json` |
| `assets/pack/` | 素材包导出器：`export.html`（顶部配置 `SLUG / AREA_OF / EXTRA_TAGS`）、`build-pack.mjs`、`make-zips.py`、`README.md` 模板 |
| `scripts/new-project.sh` | 一键起新项目：`bash "<skill根目录>/scripts/new-project.sh" "<目录>"`（复制以上全部 + `npm install`） |

**起新项目**：`bash "<skill根目录>/scripts/new-project.sh" "<目标项目目录>"` → `cd` 进去 `python3 serve.py 8080` → 打开 `http://localhost:8080/index.html` 就是示例页；然后把 `plant.js / sim.js` 换成自己的工艺。需要 Node ≥ 18 和 `/usr/bin/google-chrome`（截图 / 导出用）。

**导出素材包**：编辑 `tools/pack/export.html` 顶部的 `SLUG / AREA_OF / EXTRA_TAGS`（设备标题 = `plant.js` 里 `sel(group, title, …)` 的 title），然后 `node tools/pack/build-pack.mjs "<项目名>"` → `python3 tools/pack/make-zips.py "<项目名>"`；产物在 `exports/`。导出器约定 `js/plant.js`（导出 `buildPlant(scene)`，返回 `{labels, selectables, pumps}`）和 `js/sim.js`（导出 `DEV`）。

**已验证**：在空目录里按上述步骤起项目，示例页能运行（故障 → 备用泵自动投运 → 报警 → 复位、折叠、分区视角、仅场景全屏、离线），导出器能出 GLB / 图标 / 4 视角 SVG / 状态版 / 点位 / 4 个 zip。

**对外措辞**：把它称作“自研组态可视化框架（基于开源三维库）”，不要说“自研三维引擎”；对外画面 / 文案不出现 three.js / WebGL 等技术名词。
