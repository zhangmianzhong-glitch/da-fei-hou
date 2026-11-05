#!/usr/bin/env python3
"""
大肥猴 — 钉钉推送
通过 openclaw message send CLI 走本机 Gateway 发钉钉（无需自己持有钉钉凭据）。
"""

import shutil
import subprocess
import sys

CHANNEL = "dingtalk-connector"
TARGET = "user:265707340624258391"


class DaFeiHouDingTalkNotifier:
    """用 OpenClaw CLI 推钉钉"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.channel = self.config.get("channel", CHANNEL)
        self.target = self.config.get("target", TARGET)
        self.cli = shutil.which("openclaw")

    def available(self) -> bool:
        return bool(self.cli)

    def send(self, message: str, title: str = "") -> bool:
        """发一条钉钉消息"""
        if not self.cli:
            print("找不到 openclaw CLI，改用 cron 代发")
            return False
        text = message
        if title:
            text = title + "\n" + message
        try:
            r = subprocess.run(
                [self.cli, "message", "send",
                 "--channel", self.channel,
                 "--target", self.target,
                 "--message", text],
                capture_output=True, text=True, timeout=60)
            ok = r.returncode == 0
            print("钉钉推送:", "成功 ✅" if ok else "失败 ❌", r.stdout.strip()[:120])
            return ok
        except Exception as e:
            print("钉钉推送异常:", e)
            return False

    def send_video_report(self, videos: list, report_type: str = "早报") -> bool:
        lines = [f"🐒 大肥猴{report_type}！大王万岁！", ""]
        for i, v in enumerate(videos[:6], 1):
            lines.append(f"{i}. {v.get('title','')}")
            lines.append(f"   UP: {v.get('author','')} | 播放: {v.get('play','')}")
            lines.append(f"   为啥汇报: {v.get('reason','')}")
            lines.append(f"   {v.get('url','')}")
            lines.append("")
        lines.append("🐒 小的一直盯着呢！大王英明神武！")
        return self.send("\n".join(lines))

    def send_bilibili_discovery(self, video: dict) -> bool:
        msg = (f"🐒 大肥猴发现好东西！\n\n{video.get('title','')}\n"
               f"UP: {video.get('author','')}\n"
               f"播放: {video.get('play','')}\n"
               f"{video.get('url','')}\n\n"
               f"原因: {video.get('reason','')}\n\n"
               "🐒 大王快看！tmd 太绝了！")
        return self.send(msg)


if __name__ == '__main__':
    n = DaFeiHouDingTalkNotifier()
    print('openclaw CLI:', n.cli or '未找到')
    n.send('🐒 大肥猴测试推送！大王万岁！')
