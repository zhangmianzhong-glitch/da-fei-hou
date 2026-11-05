#!/usr/bin/env python3
"""
大肥猴 — B站搜索（热门榜 / UP主投稿 / 关键词），委托给 bilibili_api 真实实现
"""

import asyncio

from bili.bilibili_api import BilibiliAPI


class DaFeiHouBiliSearch:
    """B站搜索器"""

    def __init__(self, api: BilibiliAPI = None):
        self.api = api
        self.own_api = api is None
        self.history = []
        self.bookmarks = []

    async def _get_api(self) -> BilibiliAPI:
        if self.api is None:
            self.api = BilibiliAPI()
        return self.api

    async def keyword(self, kw: str, page: int = 1) -> list:
        """关键词搜索视频"""
        api = await self._get_api()
        res = await api.search_videos(kw, page)
        self.history.append({'kw': kw, 'count': len(res)})
        return res

    async def popular(self, ps: int = 20, pn: int = 1) -> list:
        """热门榜"""
        api = await self._get_api()
        return await api.get_popular(ps, pn)

    async def up_videos(self, mid: str, ps: int = 30, pn: int = 1) -> list:
        """UP 主投稿列表"""
        api = await self._get_api()
        return await api.get_up_videos(mid, ps, pn)

    async def recommend(self, size: int = 20) -> list:
        """推荐流"""
        api = await self._get_api()
        return await api.get_recommend_feed(size)

    async def bookmark(self, video: dict):
        """收藏"""
        self.bookmarks.append(video)

    async def close(self):
        if self.own_api and self.api is not None:
            await self.api.close()
