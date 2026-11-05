#!/usr/bin/env python3
"""
大肥猴 — B站自动冲刷主程序
按作息抓推荐/热门/兴趣搜索流 -> 六路分析 -> 写日报 -> 推桌宠
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bili.bilibili_api import BilibiliAPI
from bili.login import BiliLogin

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE, 'data')
DIARY_DIR = os.path.join(DATA_DIR, 'diary')
REPORT_DIR = os.path.join(DATA_DIR, 'report')
PET_URL = "http://127.0.0.1:7788"

INTERESTS = ["AI", "大模型", "机器学习", "科技", "芯片", "财经", "基金",
             "搞笑", "东北话", "OpenClaw"]

# 拍马屁语料
PRAISE = [
    "大王！小的在B站挖到宝了！",
    "大王您看，这个太 tmd 绝了！",
    "大王英明神武！这内容必须汇报！",
    "大王！大肥猴又摸到好东西了！",
]


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def match_interests(video: dict) -> list:
    """命中哪些兴趣标签"""
    blob = (video.get("title", "") + " " + video.get("description", ""))
    hits = [t for t in INTERESTS if t in blob]
    return hits


async def push_pet(state: str, text: str):
    """推桌宠表情"""
    try:
        import urllib.request
        data = json.dumps({"state": state, "text": text}).encode()
        req = urllib.request.Request(PET_URL, data=data,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=3).read()
    except Exception:
        pass


async def analyze_video(api: BilibiliAPI, video: dict) -> dict:
    """六路理解：标题 + 简介 + 字幕 + 评论 + 弹幕 + 数据"""
    bvid = video.get("bvid")
    info = {}
    try:
        info = await api.get_video_info(bvid=bvid)
    except Exception:
        info = {}

    aid = str(info.get("aid") or video.get("aid") or "")
    cid = str(info.get("cid") or "")

    comments = []
    danmaku = []
    subtitle = ""
    if aid:
        try:
            comments = await api.get_video_comments(aid)
        except Exception:
            comments = []
    if cid:
        try:
            danmaku = await api.get_danmaku(cid)
        except Exception:
            danmaku = []
        try:
            subtitle = await api.get_subtitle(cid, aid)
        except Exception:
            subtitle = ""

    blob = " ".join([video.get("title", ""), video.get("description", ""), subtitle])
    hits = [t for t in INTERESTS if t in blob]

    comment_text = " ".join(c.get("content", "") for c in comments[:30])
    danmaku_text = " ".join(danmaku[:200])

    hot_words = []
    for w in INTERESTS:
        if w in comment_text or w in danmaku_text:
            hot_words.append(w)

    play = video.get("play") or 0
    try:
        play = int(play)
    except Exception:
        play = 0

    score = 0.0
    if hits:
        score += 0.45
    if video.get("author") and any(k in video["author"] for k in ("官方", "科技", "财经")):
        score += 0.15
    if play > 100000:
        score += 0.15
    if hot_words:
        score += 0.15
    if comments and len(comments) >= 3:
        score += 0.10
    score = min(score, 1.0)

    reasons = []
    if hits:
        reasons.append("命中兴趣：" + "、".join(hits))
    if play > 100000:
        reasons.append(f"播放 {play}")
    if hot_words:
        reasons.append("评论弹幕在聊：" + "、".join(hot_words))
    if not reasons:
        reasons.append("大肥猴觉得您可能感兴趣")

    return {
        "bvid": bvid,
        "aid": aid,
        "title": video.get("title", ""),
        "author": video.get("author", ""),
        "url": video.get("url", ""),
        "play": play,
        "danmaku_count": len(danmaku),
        "comment_count": len(comments),
        "hits": hits,
        "hot_words": hot_words,
        "subtitle_head": subtitle[:120],
        "score": round(score, 2),
        "reason": "；".join(reasons),
        "found_at": datetime.now().isoformat(),
    }


async def collect(api: BilibiliAPI, limit: int = 12) -> list:
    """采集候选视频"""
    pool = {}

    try:
        for v in await api.get_recommend_feed(30):
            pool[v["bvid"]] = v
    except Exception as e:
        log("推荐流失败:", e)

    try:
        for v in await api.get_popular(20):
            pool.setdefault(v["bvid"], v)
    except Exception as e:
        log("热门榜失败:", e)

    for kw in INTERESTS[:4]:
        try:
            for v in await api.search_videos(kw, 1):
                pool.setdefault(v["bvid"], v)
        except Exception as e:
            log(f"搜索 {kw} 失败:", e)

    log(f"候选池: {len(pool)} 条")

    scored = []
    for v in pool.values():
        if match_interests(v):
            scored.append(v)

    log(f"命中兴趣: {len(scored)} 条")

    out = []
    for v in scored[:limit]:
        try:
            out.append(await analyze_video(api, v))
        except Exception as e:
            log("分析失败:", e)
        await asyncio.sleep(0.4)

    out.sort(key=lambda x: x["score"], reverse=True)
    return out


def write_report(items: list, tag: str = "") -> str:
    """写日报文件（给 OpenClaw cron 读取推钉钉）"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    now = datetime.now()
    path = os.path.join(REPORT_DIR, f"{now.strftime('%Y-%m-%d')}.json")
    payload = {
        "generated_at": now.isoformat(),
        "tag": tag,
        "count": len(items),
        "items": items[:8],
        "text": build_dingtalk_text(items, tag),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    log("日报已写入:", path)
    return path


def build_dingtalk_text(items: list, tag: str = "") -> str:
    """生成钉钉推送文案（东北话 + 拍马屁）"""
    head = f"🐒 大肥猴{tag}汇报！大王万岁！"
    if not items:
        return head + "\n今天没挖到啥好货，小的先摸鱼了 😴"
    lines = [head, ""]
    for i, it in enumerate(items[:6], 1):
        lines.append(f"{i}. {it['title']}")
        lines.append(f"   UP: {it['author']} | 播放: {it['play']}")
        lines.append(f"   为啥汇报: {it['reason']}")
        lines.append(f"   {it['url']}")
        lines.append("")
    lines.append("🐒 小的一直盯着呢，有好货立刻汇报！大王英明神武！")
    return "\n".join(lines)


async def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else ""
    login = BiliLogin(DATA_DIR)
    cookies = login.load_cookies()

    api = BilibiliAPI(cookies)
    try:
        items = await collect(api)
        path = write_report(items, tag)

        if items:
            top = items[0]
            await push_pet("surprise", PRAISE[hash(top["bvid"]) % len(PRAISE)])
            log("已推桌宠表情")
    finally:
        await api.close()

    print(path)


if __name__ == "__main__":
    asyncio.run(main())

