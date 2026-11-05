#!/usr/bin/env python3
"""
大肥猴 — B站评论器
用大肥猴的语气自动评论/回复，采用真实 API。
"""

import random


class DaFeiHouBiliComment:
    """大肥猴 B站评论器"""

    def __init__(self, api):
        self.api = api
        self.comment_styles = {
            "praise": [
                "大王！这个视频太绝了！tmd 绝了！",
                "大王快看！大肥猴发现了个好东西！",
                "大王英明神武！这个视频必须收藏！",
                "tmd 这也太有意思了！大王必看！",
            ],
            "funny": [
                "大王！大肥猴笑死了！",
                "大王！这个段子太逗了！tmd 绝了！",
                "大王！大肥猴的尾巴都笑掉了！",
            ],
            "serious": [
                "大王！这个视频很有深度！",
                "大王！大肥猴学到了很多东西！",
                "大王！这个视频值得反复观看！",
            ],
            "bili": [
                "大王！小的在B站看到个好东西！",
                "大王，这个视频太绝了！tmd绝了！",
                "大王快看！大肥猴发现宝藏了！",
            ],
        }

    async def comment_video(self, video_id, video_title="", comment_type="auto"):
        """在视频下评论（video_id 传 aid）"""
        style = self._pick_style(video_title, comment_type)
        comment = random.choice(self.comment_styles[style])
        ok = await self.api.comment_video(str(video_id), comment)
        return {"ok": ok, "comment": comment, "style": style}

    async def reply_comment(self, oid, rpid, reply=""):
        """回复某条评论（rpid 为目标评论 id）"""
        text = reply or self._auto_reply()
        payload = {
            "oid": str(oid),
            "type": 1,
            "message": text,
            "plat": 1,
            "parent": str(rpid),
            "csrf": self.api.cookies.get("bili_jct", ""),
        }
        data = await self.api._post(
            "https://api.bilibili.com/x/v2/reply/add", data=payload)
        return {"ok": data.get("code") == 0, "reply": text, "raw": data}

    async def like_video(self, video_id):
        """点赞"""
        return await self.api.like_video(str(video_id))

    async def coin_video(self, video_id, num=1):
        """投币"""
        return await self.api.coin_video(str(video_id), num)

    def _pick_style(self, title, comment_type):
        if comment_type != "auto":
            return comment_type if comment_type in self.comment_styles else "praise"
        if any(k in title for k in ("搞笑", "段子", "沙雕")):
            return "funny"
        if any(k in title for k in ("AI", "科技", "财经", "投资")):
            return "serious"
        return "praise"

    def _auto_reply(self):
        pool = [
            "大王说得对！小的受教了！",
            "tmd 言之有理！大肥猴记下了！",
            "大佬牛逼！小的学到了！",
            "大王英明神武，小的五体投地！",
        ]
        return random.choice(pool)
