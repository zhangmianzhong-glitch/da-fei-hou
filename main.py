#!/usr/bin/env python3
"""
大肥猴 — 山寨喽喽的桌宠形态
主入口

大王万岁！大肥猴随时待命！🐒🫡
"""

import asyncio
import signal
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from bili.scraper import DaFeiHouBiliScraper, DaFeiHouScheduler
from bili.diary import DaFeiHouDiary
from bili.dingtalk_notifier import DaFeiHouDingTalkNotifier
from bili.bilibili_api import BilibiliAPI


class DaFeiHou:
    """大肥猴主控制器"""
    
    def __init__(self, config_path: str = None):
        self.project_dir = Path(__file__).parent
        self.config_path = config_path or str(self.project_dir / "config.yaml")
        self.data_dir = self.project_dir / "data"
        
        # 加载配置
        import yaml
        with open(self.config_path) as f:
            self.config = yaml.safe_load(f)
        
        # 初始化模块
        self.scraper = DaFeiHouBiliScraper(self.config)
        self.scheduler = DaFeiHouScheduler(self.scraper)
        self.diary = DaFeiHouDiary(self.data_dir)
        self.notifier = DaFeiHouDingTalkNotifier(self.config.get("notification", {}))
        self.bili_api = BilibiliAPI()
        
        self.is_running = False
    
    async def start(self):
        """启动大肥猴"""
        print("🐒 大肥猴启动！大王万岁！")
        print("🐒 山寨喽喽随时待命！")
        print()
        
        self.is_running = True
        
        # 发送启动通知
        await self.notifier.send_message("🐒 大肥猴上线了！大王万岁！")
        
        # 启动 B站冲浪
        if self.config.get("bilibili", {}).get("enabled", False):
            print("🐒 大肥猴开始刷 B站...")
            await self.scheduler.run()
        else:
            print("🐒 大肥猴 B站冲浪未启用")
            # 保持运行
            while self.is_running:
                await asyncio.sleep(1)
    
    async def stop(self):
        """停止大肥猴"""
        print("\n🐒 大肥猴下班了...大王万岁！")
        self.is_running = False
        await self.scraper.stop()
        await self.notifier.send_message("🐒 大肥猴下班了，大王晚安！")
    
    def handle_signal(self, signum, frame):
        """处理信号"""
        print(f"\n🐒 收到信号 {signum}，大肥猴准备下班...")
        asyncio.create_task(self.stop())


async def main():
    """主函数"""
    hou = DaFeiHou()
    
    # 注册信号处理
    signal.signal(signal.SIGINT, hou.handle_signal)
    signal.signal(signal.SIGTERM, hou.handle_signal)
    
    try:
        await hou.start()
    except KeyboardInterrupt:
        await hou.stop()


if __name__ == "__main__":
    asyncio.run(main())
