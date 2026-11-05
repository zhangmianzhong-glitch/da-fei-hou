#!/usr/bin/env python3
"""
大肥猴 — 视频分析器
真 AI 分析走 MiniMax（Anthropic 兼容端点），失败回退关键词。
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bili.ai_analyzer import AIAnalyzer


class DaFeiHouVideoAnalyzer:
    """大肥猴视频分析器"""

    INTERESTS = [
        "AI", "大模型", "机器学习", "科技", "芯片",
        "财经", "基金", "搞笑", "东北话", "OpenClaw",
    ]

    def __init__(self, api_key=None):
        self.ai = AIAnalyzer()
        self.ai.enabled = bool(api_key) or self.ai.enabled

    async def analyze(self, video, comments, danmaku, subtitle):
        """六路分析：标题/简介 + 字幕 + 评论 + 弹幕 + 数据 + AI 语义"""
        ai_result = {}
        if self.ai.enabled:
            ai_result = await self.ai.analyze(video, comments, danmaku, subtitle)

        hits = [t for t in self.INTERESTS
                if t in (video.get("title", "") + video.get("description", ""))]
        hot_words = []
        blob = " ".join([c.get("content", "") for c in comments[:30]] +
                        list(danmaku[:200]))
        for t in self.INTERESTS:
            if t in blob:
                hot_words.append(t)

        play = video.get("play") or 0
        try:
            play = int(play)
        except Exception:
            play = 0

        # AI 给了分就直接用，否则回退关键词打分
        if ai_result and ai_result.get("score") is not None:
            score = float(ai_result.get("score", 0))
            reason = ai_result.get("reason", "")
        else:
            score = 0.0
            if hits:
                score += 0.45
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
            reason = "；".join(reasons) or "大肥猴觉得您可能感兴趣"

        return {
            "aid": video.get("aid"),
            "bvid": video.get("bvid"),
            "title": video.get("title", ""),
            "author": video.get("author", ""),
            "url": video.get("url", ""),
            "play": play,
            "danmaku_count": len(danmaku),
            "comment_count": len(comments),
            "hits": hits,
            "hot_words": hot_words,
            "summary": ai_result.get("summary", ""),
            "key_points": ai_result.get("key_points", []),
            "sentiment": ai_result.get("sentiment", "neutral"),
            "keywords": ai_result.get("keywords", []),
            "ai_used": bool(ai_result),
            "score": round(score, 2),
            "reason": reason,
        }
