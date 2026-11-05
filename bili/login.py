#!/usr/bin/env python3
"""
大肥猴 — B站扫码登录
生成二维码 PNG（发给大王用钉钉扫），轮询登录状态，保存 cookies。
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta

import aiohttp

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

QR_GENERATE = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
QR_POLL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"

CODE = {
    0: "登录成功",
    86038: "二维码已过期，请重新生成",
    86090: "已扫码，等待手机确认",
    86101: "已扫码，等待确认",
}


class BiliLogin:
    """B站扫码登录管理器"""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.cookies_dir = os.path.join(data_dir, "cookies")
        os.makedirs(self.cookies_dir, exist_ok=True)
        self.cookies_file = os.path.join(self.cookies_dir, "bilibili.json")

    def load_cookies(self) -> dict:
        """读取已保存的 cookies"""
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, encoding="utf-8") as f:
                cookies = json.load(f)
            if self._expired(cookies):
                print("cookies 已过期，需要重新登录")
                return {}
            return cookies
        return {}

    def save_cookies(self, cookies: dict):
        """保存 cookies"""
        cookies["expire_time"] = (
            datetime.now() + timedelta(days=30)).isoformat()
        with open(self.cookies_file, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print("cookies 已保存:", self.cookies_file)

    def _expired(self, cookies: dict) -> bool:
        exp = cookies.get("expire_time")
        if not exp:
            return True
        try:
            return datetime.fromisoformat(exp) < datetime.now()
        except Exception:
            return True

    async def generate_qr(self, png_path: str) -> tuple:
        """生成登录二维码，返回 (qrcode_key, url)"""
        async with aiohttp.ClientSession(headers={
                "User-Agent": UA,
                "Referer": "https://passport.bilibili.com/login",
        }) as sess:
            async with sess.get(QR_GENERATE) as resp:
                data = await resp.json()
        if data.get("code") != 0:
            raise RuntimeError("生成二维码失败: " + str(data.get("message")))

        payload = data.get("data") or {}
        url = payload.get("url")
        key = payload.get("qrcode_key")

        # 存 PNG，方便钉钉发图给大王扫
        try:
            import qrcode
            img = qrcode.make(url)
            img.save(png_path)
            print("二维码已保存:", png_path)
        except Exception as e:
            print("二维码图片生成失败（终端仍可扫码）:", e)

        return key, url

    async def poll_login(self, qrcode_key: str, timeout: int = 300) -> dict:
        """轮询登录状态"""
        deadline = time.time() + timeout
        async with aiohttp.ClientSession(headers={
                "User-Agent": UA,
                "Referer": "https://passport.bilibili.com/login",
        }) as sess:
            while time.time() < deadline:
                async with sess.get(QR_POLL,
                                   params={"qrcode_key": qrcode_key}) as resp:
                    data = await resp.json()
                code = (data.get("data") or {}).get("code")
                msg = CODE.get(code, str(data.get("message")))

                if code == 0:
                    # B站现版本用 Set-Cookie 下发登录态，cookie jar 才是真身
                    jar = {c.key: c.value for c in sess.cookie_jar}
                    # 老版本字段兜底
                    for c in ((data.get("data") or {}).get("cookies") or []):
                        n = c.get("name")
                        v = c.get("value")
                        if n and v and n not in jar:
                            jar[n] = v
                    if "SESSDATA" not in jar:
                        print("警告：没拿到 SESSDATA，可能需要重新扫码")
                    else:
                        print("登录成功！已拿到:", [k for k in jar if k in ("SESSDATA", "bili_jct", "DedeUserID")])
                    return jar

                print("状态:", msg)
                if code in (86038,):
                    return {}
                await asyncio.sleep(3)
        print("登录超时")
        return {}


async def main():
    import sys
    base = "/Users/zmz/.openclaw/workspace/da-fei-hou"
    data_dir = os.path.join(base, "data")
    png = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bili_qr.png"

    login = BiliLogin(data_dir)
    existing = login.load_cookies()
    if existing:
        print("已有有效 cookies:", list(existing.keys()))
        return

    key, url = await login.generate_qr(png)
    print("请用 B站 APP 扫码，链接:", url)
    cookies = await login.poll_login(key)
    if cookies:
        login.save_cookies(cookies)


if __name__ == "__main__":
    asyncio.run(main())

