# 界面模式（面板 / 详情 / 视角 / 全屏 / 导出）

页面是 1920×1080 的舞台等比缩放，三维画布铺底，HTML 面板叠上去。样式来自 `css/style.css`（顶栏、导航、`.glass` 卡、`.card-hd`、`.badge`、`.lbl.*`、底部三块 `#footer`）。

## 一、固定外壳（所有页面共用的版式）

- **顶栏**：品牌 + PLC / CPU 状态胶囊 | 蓝色梯形标题牌 | 时钟 + 用户。离线时 PLC 胶囊红“通信失败”，在线绿“通信正常”。
- **导航**：工艺流程等菜单（没接页面的就是占位）+ 右侧工具（演示数据开关、模拟异常、复位视角、**全屏**、导出 PNG）。菜单多时把 `#nav a` 宽度压到 112 px，工具按钮 `white-space: nowrap`。
- **左上两条图例**：管线图例（介质色）、设备状态图例（正常 / 异常 / 离线）。注意 id 与 `style.css` 里已有 id 冲突（`#legend` 是绝对定位的），自己的容器换个 id。
- **右上参数卡**：反应器 / 机组的运行参数表（深色数值块 + 单位）。**加展开 / 收起按钮**（标题栏右侧圆形箭头，收起后只剩一行摘要，状态存 `localStorage`，用 try/catch 包）——参数卡会遮挡右上角的设备。
- **底部**：报警信息表 | 快捷操作 | 用户 + 表盘时钟。

## 二、标签与分级

- 标签类型见 engine-and-kit.md。全景只保留 `name` 和关键 `tag`；次要 `tag`（流量、压力、液位）加 class `sec`，泵牌 `.lbl.pump`、流向 `.lbl.flow` 在“远景”隐藏：

```js
engine.onFrame(() => { const far = engine.getView().dist > FAR; stage.classList.toggle('far', far); });
```
```css
#stage.far .lbl.pump, #stage.far .lbl.flow, #stage.far .lbl.tag.sec { display: none !important; }   /* placeLabels 每帧写 display，必须 !important */
```

- **默认视距下标签应基本不重叠**；如果还重叠，是布局太挤，先挪设备（见 SKILL 原则 2），而不是调 LOD 阈值。
- 三点料位这类“多灯一体”的牌自定义 `kind`（如 `lvl3`），用 `addLabels(list, l => el)` 工厂创建。

## 三、分区视角条

左下一排药丸按钮（全景 / 调节池·提升泵 / 反应器 / 沉淀池·排放 / 污泥·压滤 / 药剂…），点击 `engine.flyTo({target, dist, polar, azim, offset}, 1400)`，当前项高亮；`?view=<键>` 直接 `setView`（截图用）。每个视角 `dist` 130–190，`target` 取该区中心偏后一点，`offset` 沿用全景的。布局版式不同时视角表也要换一套。

## 四、设备详情卡

点击 3D 设备 → 卡片出现（右侧或左侧，设备在画面右半边就放左边，别挡住设备；参数卡收起时位置上移），内容：
- 标题：位号 chip + 名称 + 状态胶囊。
- **设备**区：该组每台泵 / 阀一行：状态胶囊、A/M 模式按钮、启 / 停（阀：开 / 关）、复位。**只有手动模式才能启停**；离线禁用；故障可复位；压滤机给“启动周期 / 中止”。
- **实时数据**区：`rows()`，每秒刷新（内容没变不重绘，避免点击途中按钮被替换；点击事件用 `pointerdown`）。
- **铭牌参数**区：台账 `spec`；底部 `lock` 联锁说明。内容多时卡内滚动（`max-height = 884 − top`），不要盖到底部报警条。

## 五、全屏 = 只显示模型场景

```js
document.addEventListener('fullscreenchange', () => {
  const on = !!document.fullscreenElement;
  stage.classList.toggle('only', on);
  if (on) { saved = engine.getView(); engine.flyTo({ ...saved, dist: saved.dist * 0.7, offset: [0, 10] }, 700); }
  else if (saved) engine.flyTo(saved, 700);
});
```
```css
#stage.only #header, #stage.only #nav, #stage.only #footer, #stage.only .card /* 参数卡/详情卡/图例/视角条 */ { display: none !important; }
#fs-exit { display: none; position: absolute; right: 22px; top: 18px; opacity: .55; … }   #stage.only #fs-exit { display: inline-flex; }
```

引擎已有全屏按钮 / F 键逻辑，页面只需要 `#btn-fullscreen`（含 `<span>` 文字与 `<svg>`）和上面的类切换。不要把“全屏”理解成浏览器全屏而保留界面。开 `fill:true`，全屏时场景才铺满。

## 六、其它

- **PID 图纸视图**（可选，作为附加页）：SVG 手绘流程图 + 实时数据，便于和图纸逐点对照；三维页导航里放入口，两边互链。
- **导出 PNG**：引擎自带（`html-to-image`，期间 `#stage.exporting` 去毛玻璃）；批量截图用无头 Chrome（见 delivery-qa.md）。
- **持久化**：只存个人偏好（参数卡折叠、主题），读写都用 try/catch；不要把业务状态放 localStorage。
- 提示 / toast 文案简短，写在 `engine.toast`。
- 页面文案不出现“Three.js / WebGL”等技术名词，写“实时三维渲染”。
