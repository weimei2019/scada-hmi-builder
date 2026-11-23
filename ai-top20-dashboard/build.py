#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub AI 开源项目 Star Top 20 —— 每日抓取 / 筛选 / 排序 / 生成 HTML 看板。

流程：
  1) 对 8 个 AI 主题做 GitHub Search API 检索（按 star 降序，每类 100 条）
  2) 按 full_name 去重，得到候选池
  3) 按「AI 开源软件项目」口径做质量筛选（剔除清单/合集/教程/非 AI 基础设施）
  4) 按 star 降序取 Top 20，写入 data/latest.json 并追加 data/history.json 快照
  5) 用 template.html 渲染 index.html（数据内联，单文件可离线打开）

用法： python build.py [--offline]
  --offline 复用 data/cache 中最近一次抓取结果，不请求网络
"""
import json
import os
import subprocess
import sys
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
TEMPLATE = os.path.join(BASE, "template.html")
OUT_HTML = os.path.join(BASE, "index.html")
OUT_JSON = os.path.join(DATA_DIR, "latest.json")
HISTORY = os.path.join(DATA_DIR, "history.json")

TZ = datetime.timezone(datetime.timedelta(hours=8))
TOPICS = ["ai", "llm", "machine-learning", "deep-learning",
          "artificial-intelligence", "generative-ai", "ai-agents", "chatgpt"]
PER_PAGE = 100
TOP_N = 20
HISTORY_KEEP = 60

# 人工复核的排除清单：仓库 -> 排除原因（口径见 README）
EXCLUDE = {
    "f/prompts.chat": "Prompt 合集，非可运行软件项目",
    "x1xhlol/system-prompts-and-models-of-ai-tools": "系统提示词合集，非软件项目",
    "punkpeye/awesome-mcp-servers": "Awesome 清单，无实际代码实现",
    "Snailclimb/JavaGuide": "Java 面试指南，AI 仅为附带章节",
    "shadcn-ui/ui": "前端 UI 组件库，与 AI 无实质关联",
    "supabase/supabase": "通用 Postgres 平台，与 AI 无实质关联",
    "D4Vinci/Scrapling": "通用爬虫框架，AI 属性弱",
    "Developer-Y/cs-video-courses": "计算机课程合集，非 AI 项目",
    "mlabonne/llm-course": "课程 / 学习路线图",
    "d2l-ai/d2l-zh": "教材，非可运行项目",
    "microsoft/ML-For-Beginners": "教学课程",
    "microsoft/generative-ai-for-beginners": "教学课程",
    "datawhalechina/hello-agents": "教程，非可运行项目",
    "rasbt/LLMs-from-scratch": "教材式教程，非工程可用项目",
    "opencv/opencv": "通用计算机视觉库，非 AI 原生项目",
}

# 分类规则：(分类名, 关键词列表) 命中数最高者胜出
CATEGORY_RULES = [
    ("AI Agent / 编程助手", ["agent", "agentic", "claude-code", "codex", "copilot", "coding-agent",
                             "autonomous", "assistant", "mcp", "skills", "agent-skills"]),
    ("生成式内容", ["diffusion", "image-generation", "stable-diffusion", "video", "voice", "tts",
                    "deepfake", "ai-art", "comfyui", "audiobook", "animation"]),
    ("RAG / 检索与数据", ["rag", "retrieval", "embedding", "vector", "search", "crawler",
                          "scraping", "data-extraction", "crawl"]),
    ("模型框架与推理", ["llm", "transformer", "inference", "pytorch", "tensorflow", "deep-learning",
                        "machine-learning", "finetuning", "training", "vllm", "ollama", "neural-network"]),
    ("工作流 / 自动化", ["workflow", "automation", "orchestration", "low-code", "no-code", "automation-platform"]),
    ("开发工具 / 工程化", ["cli", "developer-tools", "ide", "editor", "spec", "sdk", "plugin"]),
]

AI_TOPICS = {"ai", "llm", "machine-learning", "deep-learning", "artificial-intelligence",
             "generative-ai", "ai-agents", "chatgpt", "agents", "agent", "ai-agent",
             "large-language-models", "deep-neural-networks", "ml", "neural-network",
             "agentic-ai", "llms", "generativeai", "openai", "gpt", "claude", "rag"}


def now_local():
    return datetime.datetime.now(TZ)


def gh_api(path, params):
    cmd = ["gh", "api", "-X", "GET", path]
    for k, v in params.items():
        cmd += ["-f", f"{k}={v}"]
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise RuntimeError(f"GitHub API 调用失败（{path} {params}）：{out.stderr.strip()[:300]}")
    return json.loads(out.stdout)


def fetch_all():
    """抓取所有主题；单主题失败不影响整体，但全部失败则报错。"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    stamp = now_local().strftime("%Y%m%d")
    merged, failed = {}, []
    for topic in TOPICS:
        try:
            d = gh_api("search/repositories",
                       {"q": f"topic:{topic}", "sort": "stars", "order": "desc", "per_page": PER_PAGE})
        except Exception as e:  # noqa: BLE001
            failed.append(f"{topic}: {e}")
            continue
        items = d.get("items", [])
        with open(os.path.join(CACHE_DIR, f"{stamp}_{topic}.json"), "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False)
        for it in items:
            merged[it["full_name"]] = it
        print(f"  topic:{topic:<24} 命中 {d.get('total_count'):>7} / 取回 {len(items)}")
    if not merged:
        raise SystemExit("所有主题抓取均失败：\n" + "\n".join(failed))
    if failed:
        print("  [警告] 部分主题抓取失败：\n   " + "\n   ".join(failed))
    return list(merged.values())


def load_cache():
    files = sorted(f for f in os.listdir(CACHE_DIR) if f.endswith(".json")) if os.path.isdir(CACHE_DIR) else []
    if not files:
        raise SystemExit("无可用的本地缓存，请先在线运行一次。")
    latest_stamp = files[-1].split("_")[0]
    merged = {}
    for f in files:
        if not f.startswith(latest_stamp):
            continue
        with open(os.path.join(CACHE_DIR, f), encoding="utf-8") as fh:
            for it in json.load(fh):
                merged[it["full_name"]] = it
    print(f"  离线模式，复用缓存 {latest_stamp}，共 {len(merged)} 个仓库")
    return list(merged.values())


def categorize(repo):
    hay = " ".join((repo.get("topics") or [])).lower() + " " + (repo.get("description") or "").lower()
    best, best_score = "其他 AI 项目", 0
    for name, kws in CATEGORY_RULES:
        score = sum(1 for kw in kws if kw in hay)
        if score > best_score:
            best, best_score = name, score
    return best


def is_ai(repo):
    topics = {t.lower() for t in (repo.get("topics") or [])}
    if topics & AI_TOPICS:
        return True
    blob = ((repo.get("description") or "") + " " + repo["full_name"]).lower()
    return any(k in blob for k in ("ai", "llm", "gpt", "machine learning", "deep learning", "neural", "agent"))


def select(repos):
    kept, excluded = [], []
    for r in repos:
        name = r["full_name"]
        if name in EXCLUDE:
            excluded.append({"full_name": name, "stars": r["stargazers_count"], "reason": EXCLUDE[name]})
            continue
        if not is_ai(r):
            excluded.append({"full_name": name, "stars": r["stargazers_count"], "reason": "未命中 AI 主题标签"})
            continue
        kept.append(r)
    kept.sort(key=lambda x: (-x["stargazers_count"], -x["forks_count"]))
    excluded.sort(key=lambda x: -x["stars"])
    return kept[:TOP_N], excluded[:12], len(kept)


def load_history():
    if os.path.exists(HISTORY):
        with open(HISTORY, encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def build_deltas(history, repos_for_delta):
    if not history:
        return {}
    prev = history[-1].get("stars", {})
    return {k: (repos_for_delta.get(k) - v if k in repos_for_delta else None) for k, v in prev.items()}


def main():
    offline = "--offline" in sys.argv
    now = now_local()
    print(f"[1/4] 抓取候选池（{'离线缓存' if offline else 'GitHub Search API'}）…")
    raw = load_cache() if offline else fetch_all()
    pool_size = len(raw)

    print("[2/4] 质量筛选与排序…")
    top, excluded, kept_count = select(raw)

    history = load_history()
    stars_now = {r["full_name"]: r["stargazers_count"] for r in raw}
    deltas = build_deltas(history, stars_now)

    repos = []
    for i, r in enumerate(top, 1):
        repos.append({
            "rank": i,
            "full_name": r["full_name"],
            "url": r["html_url"],
            "description": r.get("description") or "",
            "stars": r["stargazers_count"],
            "forks": r["forks_count"],
            "language": r.get("language"),
            "category": categorize(r),
            "topics": (r.get("topics") or [])[:8],
            "pushed_at": r.get("pushed_at"),
            "created_at": r.get("created_at"),
            "avatar": (r.get("owner") or {}).get("avatar_url", ""),
            "delta": deltas.get(r["full_name"]),
        })

    generated_at = now.strftime("%Y-%m-%d %H:%M")
    payload = {
        "meta": {
            "generated_at": now.isoformat(timespec="seconds"),
            "generated_at_display": now.strftime("%Y-%m-%d %H:%M (UTC+8)"),
            "pool_size": pool_size,
            "kept_after_filter": kept_count,
            "top_n": TOP_N,
            "topics": TOPICS,
            "repo": "weimei2019/scada-hmi-builder (ai-top20-dashboard/)",
        },
        "repos": repos,
        "excluded": excluded,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("[3/4] 更新历史快照…")
    history.append({"date": now.strftime("%Y-%m-%d"),
                     "stars": {r["full_name"]: r["stars"] for r in repos}})
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(history[-HISTORY_KEEP:], f, ensure_ascii=False, indent=1)

    print("[4/4] 渲染看板…")
    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    html = html.replace("/*__DATA__*/{}", json.dumps(payload, ensure_ascii=False))
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n完成：候选池 {pool_size} → 筛选后 {kept_count} → Top {len(repos)}")
    for r in repos:
        print(f"  {r['rank']:>2}. {r['full_name']:<42} {r['stars']:>8,}  {r['category']}")
    print(f"\n输出：{OUT_HTML}")


if __name__ == "__main__":
    main()
