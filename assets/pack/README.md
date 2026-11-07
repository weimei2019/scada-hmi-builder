# {{PROJECT}} · 组态素材包

由 ZUTAI LAB 的 2.5D 工艺流程页面拆出。所有模型由基本几何体拼成，无第三方版权素材。

## 目录

| 路径 | 内容 |
|---|---|
| `models/equipment/*.glb` | 每台设备一个 GLB，已按“底面中心”归零 |
| `models/parts/*.glb` | 通用小件（离心泵、搅拌机、阀门横 / 立、管道箭头） |
| `models/pipes_all.glb` | 全部管线，每种介质一种材质（`pipe_<介质>`） |
| `models/plant_full.glb` | 整厂（设备 + 平台 + 管线），保持原位置 |
| `sprites/*.png` | 每件设备的 512px 透明底 2.5D 图标；`_overview.png` 为整厂总览 |
| `svg/page|iso|front|top/*.svg` | 4 个视角的矢量图标（`page` = 网页里的俯拍视角），透明底 |
| `layout.json` | 每台设备的世界坐标 / 尺寸 / 所属工段；管线折线点（含管径 / 介质）；三维标签；泵编号 |
| `tags.csv` / `tags.json` | 点位清单（AI 模拟量 / DI 开关量 / STRING 字符串） |

## 约定

- 单位米，Y 向上，右手系（glTF 标准）。`layout.json` 里 `position` 是设备底面中心的世界坐标。
- 水面是着色器实时算的，这里**烘焙成静止贴图**（俯视渲染，材质不受光）；搅拌桨 / 刮泥桥等旋转件作为 glTF 动画带进 GLB；**管道流动、水面波纹无法导出**，需要在目标编辑器里自己做。
- 点位值是演示用的，没有接真实 PLC；报警限 / 联锁说明在页面源码的台账里，不在素材包内。

## 状态版（另附 `{{PROJECT}}_状态版/`）

目录：`工段 / 设备 / 状态 / 文件`。**不带状态灯**：正常 = 原色；异常 = 整体变红（保留明暗，水面也变红）；离线 = 整体变灰，GLB 不带任何动画。在组态编辑器里按设备状态切换对应文件即可。

## 重新生成

```bash
node tools/pack/build-pack.mjs "{{PROJECT}}"      # 输出到 exports/{{PROJECT}}_素材包 与 _状态版
python3 tools/pack/make-zips.py "{{PROJECT}}"     # 打成 zip
```
