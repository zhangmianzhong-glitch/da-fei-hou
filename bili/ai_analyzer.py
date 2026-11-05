#!/usr/bin/env python3
"""
大肥猴 — 真 AI 视频分析
用 MiniMax 的 Anthropic 兼容端点（~/.openclaw/.env 里的 MINIMAX_API_KEY）
对字幕 + 评论 + 弹幕做真正的语义理解，替代关键词匹配。
"""

import json
import os
import re

import aiohttp

ENV_PATH = os.path.expanduser("~/.openclaw/.env")
BASE_URL = "https://api.minimaxi.com/anthropic"
MODEL = "MiniMax-M3"


def load_api_key() -> str:
    """从 OpenClaw 的 .env 读 key，不打印明文"""
    if not os.path.exists(ENV_PATH):
        return ""
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("MINIMAX_API_KEY"):
                _, _, val = line.partition("=")
                return val.strip().strip('"').strip("'")
    return ""


PROMPT = """你是大肥猴，一个贼兮兮的马屁精助手。下面给你一个 B站视频的内容素材，
请用中文分析它，判断值不值得报告给你的主人大王，并给出理由。

严格输出 JSON（不要任何多余文字）：
{
  "score": 0.0-1.0 的浮点数,
  "reason": "一句话说明为什么值得报告，用东北话+拍马屁语气",
  "summary": "视频讲了什么，60字内",
  "key_points": ["关键点1", "关键点2"],
  "sentiment": "positive/neutral/negative",
  "keywords": ["提取的关键词"]
}"
"""


class AIAnalyzer:
    """调用 MiniMax 分析视频"""

    def __init__(self):
        self.api_key = load_api_key()
        self.enabled = bool(self.api_key)

    async def analyze(self, video: dict, comments: list, danmaku: list,
                       subtitle: str) -> dict:
        """真 AI 分析；失败则返回空 dict 让调用方回退关键词"""
        if not self.enabled:
            return {}

        parts = []
        parts.append("标题：" + video.get("title", ""))
        if video.get("description"):
            parts.append("简介：" + video["description"][:300])
        if subtitle:
            parts.append("字幕节选：" + subtitle[:3000])
        if comments:
            ctext = " | ".join(c.get("content", "") for c in comments[:20])
            parts.append("热门评论：" + ctext[:1500])
        if danmaku:
            dtext = " ".join(danmaku[:150])
            parts.append("弹幕采样：" + dtext[:1000])

        user_text = "\n\n".join(parts)

        payload = {
            "model": MODEL,
            "max_tokens": 800,
            "messages": [
                {"role": "user", "content": PROMPT + "\n\n" + user_text}
            ],
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.post(BASE_URL + "/v1/messages", json=payload,
                                     headers=headers,
                                     timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200:
                        print("AI 分析 HTTP", resp.status)
                        return {}
                    body = await resp.json()
        except Exception as e:
            print("AI 分析失败:", e)
            return {}

        try:
            text = "".join(
                blk.get("text", "")
                for blk in body.get("content", [])
                if blk.get("type") == "text"
            )
            m = re.search(r"\{.*\}", text, re.S)
            if not m:
                return {}
            return json.loads(m.group(0))
        except Exception as e:
            print("AI 结果解析失败:", e)
            return {}
