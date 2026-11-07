# 共享引擎与设备库（搭场景用）

## 一、`createEngine(opts)`（`js/engine.js`）

返回 `engine`：`scene camera controls renderer HOME pipeHolder`，以及：

| 方法 | 用途 |
|---|---|
| `optimize(selectables)` | 把静态网格按材质合并（性能）；可选设备各自合并并**克隆材质**；管道单独合并。标 `userData.dynamic` 的组不合并 |
| `addLabels(list, makeEl?)` | 三维标签；默认 4 种 `kind`：`name`（蓝色铭牌，`sm` 小号）、`tag`（图标 + 深色数值 + 单位，`data-k` / `key`）、`pump`（圆点 + 编号 + A/M 模式）、`flow`（箭头 + 文字）；`dx/dy` 屏幕像素偏移；可传第二参数自定义（返回 DOM） |
| `enableHover(selectables, html)` | 悬停提示；`selectables = [{ group, title, rows(), ... }]`，`html(s)` 返回提示 HTML |
| `onClick((selectable, event) => …)` | 点击；空白处传 `null` |
| `flyTo({target,dist,polar,azim,offset}, ms)` / `home()` / `setView` / `getView` | 镜头；`offset` 是画面偏移（给侧边面板让位） |
| `onFrame((t,dt)=>…)` / `onTheme(name=>…)` / `onAfterRender` | 钩子 |
| `highlight(selectable, on, color)` | 悬停 / 选中描边；材质 `userData.keepEmissive` 的不受影响 |
| `project(vec3)` | 世界 → 舞台坐标 |
| `tween(ms, fn, ease)` + `ease.inOut/out/back` | 补间 |
| `toast(msg, ms)` / `exportPNG(scale)` / `setTheme('light'|'dark')` / `idle()` / `removeLabel` | 杂项 |

选项：`fill`（铺满窗口，不留白边；舞台尺寸读 `engine.size`）、`bg fog groundSize sun hemi ao bloom themes view{fov near far target dist polar azim offset limits}`、`ao:false`（整页关 AO）。按钮 id 约定：`btn-reset`（复位视角）、`btn-export`（导出 PNG）、`btn-fullscreen`（全屏，F 键也行）、`demo-toggle` 等由页面自己接。时钟元素 id：`clock-text`、`sb-time`、`clock-date`、`aclock`（模拟表盘）。

## 二、设备与管道（`js/factory.js`，单位米）

- 地台 / 池体：`platform(w,d,h,cell)`、`rectTank(w,d,h,{water,dividers,rail,wall,waterInset,waters})`（`waters` 可给每个分格不同水色）、`vTank(r,h,{top,bottom,legs,mat,rail,ladderSide,open,water})`（`open + water` 做敞口圆池 / 罐）、`clarifier`、`railing`、`ringRailing`、`ladder`。
- 动设备：`pump({scale})`（进口在 +x 侧：局部 `(1.15,0.62,0)`，出口 `(0.62,1.45,0)`）、`mixer({shaft})`（桨叶自转，挂在 `animated`）、`blowerCabinet / boiler / scrubber / centrifugalFan` 等行业件。
- 水面：`waterMaterial({deep,light,foam,bubbles,round,size,speed})`（着色器，按世界坐标，有波纹 / 泡沫 / 曝气气泡）。
- **管道**：`pipe(pts, {kind,r,flow,speed,bend,dash,seg})` 折线点 → 圆角管 + 端头法兰 + 流动贴图层；`userData` 带 `curve len r kind pts`；`kind` 对应 `PIPE_COLORS`（`Object.assign(F.PIPE_COLORS, {…})` 加自己的介质）。`flow:false` 不画流动（汇管 / 吸水短管）。`arrowHead(kind,r)` 做出口箭头。`valve(axis)` 红手轮阀门。
- `M`：共享材质（`steel steelD white rail walk pump pumpD red base glass …`）。
- `textTex(lines,{logo})`：文字 / Logo 贴图（罐身标牌）。

## 三、对象配合约定

- **给设备记接口**：`userData.nozzles = { in: Vector3, out: … }`（局部坐标，接口端面中心），用 `wv(obj,key)` 换成世界坐标，管线从那里开始画——挪动设备时管线跟着重算，不要手填绝对坐标。
- **泵朝向**：`rot` 决定进出口方向。`rot=π`：进口朝 −x；`rot=π/2`：进口朝 −z；`rot=−π/2`：进口朝 +z；`rot=0`：进口朝 +x。管线从进口端面起、出口端面立管起。
- **并联泵组**写一个 `pumpSet({id,x,zs,rot,H,labels,suction})`：每台泵 + 出口立管 + 汇管，返回出口 x、汇管高度、各进口，上层再接。
- **可选设备**：`sel(group,title,rows,ids,{tank,nolamp,…})`，`ids` 是该设备组包含的台账设备（驱动状态灯 / 详情卡里的启停），`nolamp` 表示不补状态灯，`tank` 关联储罐液位。
- **静态 / 动态**：旋转件 / 动画 / 要显隐的东西 `userData.dynamic = true`；同组里多台泵想分别选中，把每台泵单独 `sel`。
- **管线动画只在设备运行时流动**：给 `pipe(..., {act: '<设备或阀门id>'})`，刷新时 `f.mesh.visible = 介质开关 && (!act || 该设备在运行)`（按介质先判断总开关，再看指定设备）。
- **标签防重叠**：同一世界点上的多块牌用 `dx/dy` 错开；`name` 的 y 抬到设备顶上；流向文字放在管线中段偏上，反向箭头给 `rev:true`（CSS 里 `scaleX(-1)`）。

## 四、典型管线几何

- 管道走“上-横-下”：先抬到统一的管廊高度（互不相交的几个高度层），沿 x / z 走直线，最后下到接口；不同介质用不同高度或平行偏移 0.6–1.0 m，避免穿模。
- 过墙 / 穿池壁用直线进出，并在池体内部终止于水面以下（`y` 略低于水面）。
- 多根同向管并排时，各自的拐弯点错开，拐弯半径 `bend` 用管径的 3 倍上限。
- 画好后**多个角度看**：俯视检查平面位置，特写检查立管 / 法兰是否穿设备。

## 五、特效（`js/fx.js`，科技模式用）

`tempColor(t)`（温度色带）、`FlowParticles(pipeMeta)`（沿管线的发光粒子，颜色 / 速度可按管设置）、`scanFloor(w,d)`、`holoBase(w,d)`、`beacon(color,h)`（故障光柱 + 脉冲环）、`edgeOverlay(root)`（设备描边）。HDR 输出（> 1）交给引擎辉光；深色主题辉光容易过曝，自发光要压低。
