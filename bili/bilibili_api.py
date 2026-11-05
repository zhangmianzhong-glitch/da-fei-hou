#!/usr/bin/env python3
"""
大肥猴 — B站 API 封装（真实实现）
- WBI 签名（搜索等接口需要）
- buvid 指纹（大部分接口需要）
- 视频详情 / 评论 / 弹幕 / 字幕 / 搜索 / 推荐 / 热门
"""

import asyncio
import hashlib
import json
import time
import urllib.parse

import aiohttp

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

API = "https://api.bilibili.com"

# WBI 混淆表（B 站前端公开算法）
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]


def get_mixin_key(raw: str) -> str:
    """由 img_key + sub_key 生成 mixin key"""
    return "".join(raw[i] for i in MIXIN_KEY_ENC_TAB[:32])


def enc_wbi(params: dict, img_key: str, sub_key: str) -> dict:
    """对参数做 WBI 签名"""
    mixin_key = get_mixin_key(img_key + sub_key)
    params = dict(params)
    params["wts"] = str(int(time.time()))

    params = dict(sorted(params.items()))
    params = {k: "".join(ch for ch in str(v) if ch not in "!'()*")
              for k, v in params.items()}

    query = urllib.parse.urlencode(params)
    params["w_rid"] = hashlib.md5((query + mixin_key).encode()).hexdigest()
    return params


class BilibiliAPI:
    """B站 API 客户端"""

    def __init__(self, cookies: dict = None):
        self.cookies = dict(cookies or {})
        self.img_key = None
        self.sub_key = None
        self.session = None

    # ---------- 底层 ----------
    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                cookies=self.cookies,
                headers={
                    "User-Agent": UA,
                    "Referer": "https://www.bilibili.com/",
                    "Origin": "https://www.bilibili.com",
                },
                timeout=aiohttp.ClientTimeout(total=20),
            )
        return self.session

    async def _get(self, url, params=None, need_wbi=False, referer=None):
        sess = await self._ensure_session()
        if need_wbi:
            await self._ensure_wbi()
            params = enc_wbi(params or {}, self.img_key, self.sub_key)
        headers = {"Referer": referer} if referer else {}
        async with sess.get(url, params=params, headers=headers) as resp:
            try:
                return await resp.json()
            except Exception:
                return {"code": -1, "message": "非 JSON 响应"}

    async def _post(self, url, data=None, headers=None):
        sess = await self._ensure_session()
        async with sess.post(url, data=data or {}, headers=headers or {}) as resp:
            try:
                return await resp.json()
            except Exception:
                return {"code": -1, "message": "非 JSON 响应"}

    async def _ensure_wbi(self):
        if self.img_key and self.sub_key:
            return
        data = await self._get(f"{API}/x/web-interface/nav")
        wbi = (data.get("data") or {}).get("wbi_img") or {}
        img = wbi.get("img_url", "").rsplit("/", 1)[-1].split(".")[0]
        sub = wbi.get("sub_url", "").rsplit("/", 1)[-1].split(".")[0]
        self.img_key = img
        self.sub_key = sub

    async def _ensure_buvid(self):
        if "buvid3" in self.cookies:
            return
        data = await self._get(f"{API}/x/frontend/finger/spi")
        b = data.get("data") or {}
        if b.get("b_3"):
            self.cookies["buvid3"] = b["b_3"]
        if b.get("b_4"):
            self.cookies["buvid4"] = b["b_4"]
        if self.session is not None:
            self.session.cookie_jar.update_cookies(self.cookies)

    async def close(self):
        if self.session is not None and not self.session.closed:
            await self.session.close()
            self.session = None

    # ---------- 对外接口 ----------
    async def get_recommend_feed(self, size: int = 20) -> list:
        """推荐视频流"""
        await self._ensure_buvid()
        data = await self._get(
            f"{API}/x/web-interface/index/top/rcmd",
            params={"ps": size, "fresh_idx": 1, "fresh_type": 3,
                    "feed_version": "V8", "homepage_ver": 1,
                    "web_location": "1430654"},
            referer="https://www.bilibili.com/")
        items = (data.get("data") or {}).get("item") or []
        return [self._norm_video(it) for it in items if it.get("bvid")]

    async def get_popular(self, ps: int = 20, pn: int = 1) -> list:
        """热门榜"""
        await self._ensure_buvid()
        data = await self._get(f"{API}/x/web-interface/popular",
                               params={"ps": ps, "pn": pn},
                               referer="https://www.bilibili.com/")
        items = (data.get("data") or {}).get("list") or []
        return [self._norm_video(it) for it in items if it.get("bvid")]

    async def search_videos(self, keyword: str, page: int = 1) -> list:
        """搜索视频（需 WBI 签名）"""
        await self._ensure_buvid()
        data = await self._get(
            f"{API}/x/web-interface/wbi/search/type",
            params={"search_type": "video", "keyword": keyword,
                    "page": page, "order": "totalrank"},
            need_wbi=True,
            referer="https://search.bilibili.com/")
        items = (data.get("data") or {}).get("result") or []
        out = []
        for it in items:
            if not it.get("bvid"):
                continue
            out.append({
                "bvid": it.get("bvid"),
                "aid": it.get("aid"),
                "title": _strip_em(it.get("title", "")),
                "author": it.get("author"),
                "mid": it.get("mid"),
                "play": it.get("play"),
                "danmaku": it.get("video_review"),
                "like": it.get("like"),
                "duration": it.get("duration"),
                "pubdate": it.get("pubdate"),
                "url": "https://www.bilibili.com/video/" + it.get("bvid", ""),
                "cover": it.get("pic", ""),
                "description": it.get("description", ""),
            })
        return out

    async def get_video_info(self, bvid: str = "", aid: str = "") -> dict:
        """视频详情（不需要签名）"""
        params = {"bvid": bvid} if bvid else {"aid": aid}
        data = await self._get(f"{API}/x/web-interface/view", params=params,
                               referer="https://www.bilibili.com/")
        return data.get("data") or {}

    async def get_video_comments(self, oid: str, pn: int = 1, ps: int = 20,
                                sort: int = 2) -> list:
        """评论列表。sort=2 按热度（分析用），sort=0 按时间（查自己刚发的）"""
        await self._ensure_buvid()
        data = await self._get(
            f"{API}/x/v2/reply",
            params={"oid": oid, "type": 1, "pn": pn, "ps": ps, "sort": sort},
            referer="https://www.bilibili.com/")
        replies = (data.get("data") or {}).get("replies") or []
        return [{
            "rpid": r.get("rpid"),
            "mid": r.get("mid"),
            "user": ((r.get("member") or {}).get("uname")),
            "level": ((r.get("member") or {}).get("level")),
            "like": r.get("like"),
            "content": (r.get("content") or {}).get("message", ""),
            "ctime": r.get("ctime"),
        } for r in replies]

    async def get_danmaku(self, cid: str) -> list:
        """弹幕（XML）"""
        sess = await self._ensure_session()
        async with sess.get(f"https://comment.bilibili.com/{cid}.xml",
                             headers={"Referer": "https://www.bilibili.com/"}) as resp:
            xml = await resp.text()
        out = []
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml)
            for d in root.iter("d"):
                out.append(d.text or "")
        except Exception:
            pass
        return out

    async def get_subtitle(self, cid: str, aid: str = "") -> str:
        """字幕文本"""
        data = await self._get(
            f"{API}/x/player/wbi/v2",
            params={"cid": cid, "aid": aid}, need_wbi=True,
            referer="https://www.bilibili.com/")
        subs = (data.get("data") or {}).get("subtitle", {}).get("subtitles") or []
        if not subs:
            return ""
        url = subs[0].get("subtitle_url", "")
        if not url:
            return ""
        if url.startswith("//"):
            url = "https:" + url
        sess = await self._ensure_session()
        async with sess.get(url, headers={"Referer": "https://www.bilibili.com/"}) as resp:
            body = await resp.json()
        lines = [x.get("content", "") for x in (body.get("body") or [])]
        return "\n".join(lines)

    async def get_up_videos(self, mid: str, ps: int = 30, pn: int = 1) -> list:
        """UP 主投稿列表"""
        await self._ensure_buvid()
        data = await self._get(
            f"{API}/x/space/wbi/arc/search",
            params={"mid": mid, "ps": ps, "pn": pn, "order": "pubdate"},
            need_wbi=True,
            referer=f"https://space.bilibili.com/{mid}/video")
        vlist = ((data.get("data") or {}).get("list") or {}).get("vlist") or []
        return [{
            "bvid": v.get("bvid"),
            "aid": v.get("aid"),
            "title": v.get("title"),
            "play": v.get("play"),
            "comment": v.get("comment"),
            "created": v.get("created"),
            "length": v.get("length"),
            "url": "https://www.bilibili.com/video/" + (v.get("bvid") or ""),
        } for v in vlist if v.get("bvid")]

    async def like_video(self, bvid: str) -> bool:
        """点赞"""
        await self._ensure_buvid()
        data = await self._get(f"{API}/x/web-interface/archive/has/like",
                               params={"bvid": bvid},
                               referer="https://www.bilibili.com/")
        return data.get("code") == 0

    async def coin_video(self, bvid: str, num: int = 1) -> bool:
        """投币。网页端风控要求：先访问视频页建会话、用 aid 而非 bvid、带 Origin 和 sp_from_id"""
        await self._ensure_buvid()
        sess = await self._ensure_session()

        # 1) 先访问视频页建立会话（风控要求）
        try:
            async with sess.get(f"https://www.bilibili.com/video/{bvid}",
                                 headers={"Referer": "https://www.bilibili.com/"}) as resp:
                await resp.text()
        except Exception:
            pass

        # 2) 拿 aid
        aid = ""
        try:
            info = await self.get_video_info(bvid=bvid)
            aid = str(info.get("aid") or "")
        except Exception:
            pass

        payload = {
            "multiply": num,
            "select_like": 1,
            "csrf": self.cookies.get("bili_jct", ""),
            "sp_from_id": "333.1387.0.0",
        }
        if aid:
            payload["aid"] = aid
        else:
            payload["bvid"] = bvid

        data = await self._post(f"{API}/x/web-interface/coin/add", data=payload)
        if data.get("code") != 0:
            log_msg = data.get("message", "")
            print("投币失败:", data.get("code"), log_msg)
            return False
        return True

    async def comment_video(self, oid: str, content: str) -> bool:
        """发表评论"""
        await self._ensure_buvid()
        data = await self._post(
            f"{API}/x/v2/reply/add",
            data={"oid": oid, "type": 1, "message": content, "plat": 1,
                  "csrf": self.cookies.get("bili_jct", "")})
        return data.get("code") == 0

    def _norm_video(self, it: dict) -> dict:
        """把不同接口的条目统一成同一结构"""
        return {
            "bvid": it.get("bvid"),
            "aid": it.get("aid"),
            "title": _strip_em(it.get("title", "")),
            "author": (it.get("owner") or {}).get("name") or it.get("author"),
            "mid": (it.get("owner") or {}).get("mid") or it.get("mid"),
            "play": it.get("play") or it.get("stat", {}).get("view"),
            "danmaku": it.get("danmaku") or it.get("stat", {}).get("danmaku"),
            "like": it.get("like") or it.get("stat", {}).get("like"),
            "duration": it.get("duration"),
            "pubdate": it.get("pubdate"),
            "url": "https://www.bilibili.com/video/" + (it.get("bvid") or ""),
            "cover": it.get("pic") or it.get("cover") or "",
            "description": it.get("desc") or it.get("description") or "",
        }


def _strip_em(text: str) -> str:
    """去掉 B 站标题里的 <em class="keyword"> 高亮标签"""
    import re
    return re.sub(r"<[^>]+>", "", text or "")

