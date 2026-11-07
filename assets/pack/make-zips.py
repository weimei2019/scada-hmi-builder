# 把素材包打成 zip：python3 tools/pack/make-zips.py "<项目名>"
# 用 Python 的 zipfile，中文文件名会带 UTF-8 标志（Windows 资源管理器 / macOS 都能正确显示）
import json, os, shutil, sys, zipfile
PROJECT = sys.argv[1] if len(sys.argv) > 1 else '示例项目'
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'exports')
PACK, STATES = (os.path.join(ROOT, f'{PROJECT}_{x}') for x in ('素材包', '状态版'))
SVG, CLEAN = (os.path.join(ROOT, f'{PROJECT}_{x}') for x in ('网页视角SVG', '设备模型'))

def zipdir(d, out):
    if os.path.exists(out): os.remove(out)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, _, fs in os.walk(d):
            for f in sorted(fs):
                p = os.path.join(r, f); z.write(p, os.path.join(os.path.basename(d), os.path.relpath(p, d)))

L = json.load(open(os.path.join(PACK, 'layout.json'), encoding='utf-8'))
shutil.rmtree(SVG, ignore_errors=True); os.makedirs(SVG)
for e in L['equipment'] + L['parts']:
    src = os.path.join(PACK, e['svg']['page']); shutil.copy(src, os.path.join(SVG, os.path.basename(src)))
zipdir(PACK, PACK + '.zip'); zipdir(SVG, SVG + '.zip')
if os.path.isdir(STATES): zipdir(STATES, STATES + '.zip')
# 设备模型（无状态灯、无状态变体）：工段 / 设备 / 文件
shutil.rmtree(CLEAN, ignore_errors=True); n = 0
for kind, group in (('equipment', None), ('parts', '通用小件')):
    for e in L[kind]:
        file = os.path.basename(e['model'])[:-4]
        d = os.path.join(CLEAN, group or e['area'], file); os.makedirs(d, exist_ok=True)
        for src, ext in ((e['model'], 'glb'), (e['sprite'], 'png'), (e['svg']['page'], 'svg')):
            shutil.copy(os.path.join(PACK, src), os.path.join(d, f'{file}.{ext}')); n += 1
open(os.path.join(CLEAN, '说明.txt'), 'w', encoding='utf-8').write(
    f'{PROJECT} · 设备模型（无状态灯）\n目录：工段 / 设备 / 设备.glb（三维）· .png（图标）· .svg（网页视角矢量）\n'
    '设备保持原色；GLB 带搅拌桨 / 刮泥桥等旋转动画；水面为烘焙贴图（静止）。\n单位米，Y 向上；每个模型以设备底面中心为原点，设备在整厂里的坐标见素材包的 layout.json。\n')
zipdir(CLEAN, CLEAN + '.zip')
print(len(os.listdir(SVG)), 'svg;', n, 'files in 设备模型')
