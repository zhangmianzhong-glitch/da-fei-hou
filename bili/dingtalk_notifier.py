# 钉钉通知模块
# 大肥猴通过钉钉向大王汇报

import json
import time
from typing import Optional, Dict, List
from datetime import datetime


class DaFeiHouDingTalkNotifier:
    """大肥猴钉钉通知器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.client_id = config.get("client_id", "dinginhyci8m2jm0ilgw")
        self.base_url = "https://oapi.dingtalk.com"
        
    async def send_message(self, message: str, msg_type: str = "text"):
        """发送钉钉消息"""
        # TODO: 调用钉钉 API
        print(f"🐒 大肥猴钉钉消息：{message}")
    
    async def send_video_report(self, videos: List[dict], report_type: str = "早报"):
        """推送视频报告"""
        message = f"🐒 大肥猴{report_type}\n\n"
        for i, video in enumerate(videos[:5], 1):
            message += f"{i}. {video['title']}\n"
            message += f"   原因：{video.get('reason', '大王可能会感兴趣')}\n"
            message += f"   链接：{video.get('url', '')}\n\n"
        
        message += "🐒 大王万岁！小的给大王请安了！"
        
        await self.send_message(message)
    
    async def send_task_notification(self, task_name: str, status: str, details: str = ""):
        """发送任务通知"""
        status_emoji = {
            "start": "🤔",
            "complete": "🎉",
            "error": "😢",
        }
        
        emoji = status_emoji.get(status, "🐒")
        message = f"{emoji} 大肥猴汇报：\n\n"
        message += f"任务：{task_name}\n"
        message += f"状态：{status}\n"
        if details:
            message += f"详情：{details}\n"
        
        message += "\n🐒 大王万岁！"
        
        await self.send_message(message)
    
    async def send_diary_summary(self, diary: dict):
        """发送日记汇总"""
        message = "🐒 大肥猴今日日记\n\n"
        message += f"看了 {diary.get('videos_watched', 0)} 个视频\n"
        message += f"发现 {diary.get('interesting_videos', 0)} 个有意思的\n"
        message += f"评论了 {diary.get('comments_made', 0)} 次\n\n"
        
        for video in diary.get('interesting_videos', [])[:3]:
            message += f"- {video['title']}\n"
        
        message += "\n🐒 大王万岁！小的明天继续努力！"
        
        await self.send_message(message)
    
    async def send_bilibili_discovery(self, video: dict):
        """发送B站发现"""
        message = f"🐒 大肥猴发现好东西！\n\n"
        message += f"{video['title']}\n"
        message += f"UP主：{video.get('up_name', '未知')}\n"
        message += f"播放：{video.get('play_count', 0)}\n"
        message += f"弹幕：{video.get('danmaku_count', 0)}\n"
        message += f"链接：{video.get('url', '')}\n\n"
        message += f"原因：{video.get('reason', '大王可能会感兴趣')}\n\n"
        message += "🐒 大王快看！tmd 太绝了！"
        
        await self.send_message(message)
    
    async def send_error_notification(self, error: str, context: str = ""):
        """发送错误通知"""
        message = f"😢 大肥猴出错了...\n\n"
        message += f"错误：{error}\n"
        if context:
            message += f"上下文：{context}\n"
        message += "\n大王...小的错了...🙏"
        
        await self.send_message(message)


# 主入口
if __name__ == "__main__":
    import asyncio
    
    config = {"client_id": "dinginhyci8m2jm0ilgw"}
    notifier = DaFeiHouDingTalkNotifier(config)
    
    async def test():
        await notifier.send_message("大王！大肥猴测试通知！🐒")
    
    asyncio.run(test())
