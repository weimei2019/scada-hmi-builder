# 验证 · 交付 · 踩坑

## 一、无头 Chrome 截图（每次改完都做）

```js
chromium.launch({ executablePath: '/usr/bin/google-chrome',
  args: ['--no-sandbox', '--use-angle=vulkan', '--enable-features=Vulkan', '--ignore-gpu-blocklist', '--enable-gpu'] })   // --use-angle=gl 不可用
page = await browser.newPage({ viewport: { width: 1920, height: 1080 } })    // 特写要放大加 deviceScaleFactor: 2 + clip
await page.goto('http://localhost:8090/<page>.html?freeze=1&…'); await page.waitForTimeout(4000~5000)
await page.screenshot({ path })           // 同时收集 pageerror / console error（404 favicon 可忽略）
```

- 页面被代理端口屏蔽时另起一个静态服务（`python3 serve.py 8090`；开发服务器 8080 给用户用，别占用）。
- 截图后**用宿主提供的图片查看工具看图**；每一轮改动至少看：全景、一个特写视角、详情卡、故障联动、离线（`?demo=0`）。
- 交互测试用 Playwright：`page.click`、`mouse.click(engine.project(...))`（世界坐标 → 舞台坐标）、`#btn-fault`、`#btn-reset-fault`；断言状态（`document.querySelector(...)`）而不只看图。**全屏**要用 `--start-fullscreen` 或真实点击测试。
- 看不到更新时先 `curl localhost:8080/js/<file>.js | grep <新内容>` 确认服务器返回的是新版，再告诉用户“Ctrl+F5 强制刷新”。
- 大图 / 特写批量出：脚本参数化 `out、scale、clip、query`，别手写十几个脚本。

## 二、常见问题与排查

| 现象 | 原因 / 办法 |
|---|---|
| 整个地台变**黑** | 用 `await import()` 动态加载场景模块会让贴图变黑（原因未查清）；**一律静态 `import`**，用查询参数选版式即可 |
| 页面停在初始状态（数值全 0、无三维） | 模块语法错误：`node --check --input-type=module < file.js`；多半是一行代码后面加了 `//` 注释吞掉了 `}` |
| 黑方块 / 辉光爆 | 着色器 `pow()` 底数 ≤ 0 → NaN；`?fx=0` 能确认；`pow(x,2.0)` 改 `x*x` |
| 物体合并后不动 / 材质改不了 | `optimize` 合并 + 克隆材质：动态件标 `userData.dynamic`；要改材质先打标记 |
| 标签叠成一团 | 布局太挤（见 SKILL 原则 2）；先挪设备，再用 `dx/dy`，最后才考虑 LOD |
| 管线穿设备 | 多角度看；管线只用 `nozzles` 世界坐标起止，拐点在设备之外 |
| 点击没反应 | 重绘 DOM 把按钮替换了（用 `pointerdown`，内容没变不重绘） |
| 详情卡盖住设备 | 设备在右半边放左边；内容多时卡内滚动 |
| 菜单 / 按钮字被换行 | `white-space: nowrap` + 压窄菜单宽度 |
| id 冲突导致样式错乱 | 先 `grep -n "#<id>" css/*.css`，`#legend` 等已被外壳占用 |
| `backdrop-filter` 太卡 | 只给侧边卡 / 详情卡加；标签不加 |

## 三、交付清单（回复用户时）

1. **一句话结论**：做了什么、在哪看（`http://<本机IP>:8080/<page>.html`）。
2. **截图路径**（完整路径，一个一个列）。
3. **和资料的对应**（修改建议逐条表 / 采购单修正了哪些参数）。
4. **我补的 / 推断的 / 暂定的**：报警限、主出水去向、读不清的小字、建筑位置——**逐条列**，请用户确认。
5. **没做的**：例如某路管没画，问是否要补。
6. 如何刷新 / 怎么复现（`Ctrl+F5`、`?view=`、`?layout=`）。
7. 能复用的脚本命令（重新出包、重新截图）。

## 四、沟通与迭代习惯

- 用户给的反馈要**先复述理解**再改：“你说得对，X 不该是 Y”；改完说“改了什么、没改什么”。
- 不确定的业务事实（进水来源、出水去向、型号）**问一句**，用户常常一句话就能给；用户给的口径一经确认，同步到台账 / 联锁 / 素材包 / 截图 / 文档。
- 多轮迭代里的返工代价很高：布局类大改之前，先做 1 张全景草图截图发用户确认再扩展。
- 长任务中途要回一句“我在做什么”（用户看不到工具输出），不要沉默。
- 每次大改后同步：项目已有说明文件（如 `AGENTS.md`、`CLAUDE.md` 或 README：结构、坑、命令）、宿主可用的记忆（用户偏好 / 已确认的事实）、素材包与截图。

## 五、宣传片 / 演示视频（需要时）

虚拟时间逐帧录制：注入脚本接管 `performance.now / Date / 定时器 / rAF / CSS 动画 / Math.random`，录制脚本**每帧单独调用一次** `__vt.step(dt)` 再 CDP 截图，ffmpeg 合成；配乐用代码合成卡点；字幕条 / 片头片尾 / 模拟鼠标是注入的叠加层。分镜里调页面异步函数**不要等返回值**（会死锁）；预览模式也要读回画面。对外画面不出现技术栈名词。如果已安装 `heat-exchange-station` skill，可参考其 `references/promo-video.md`；未安装时无需读取该外部文件。
