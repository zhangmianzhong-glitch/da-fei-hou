# 大猴猴 B站评论模块
# 用大肥猴的语气自动评论

import random
from typing import Dict, List


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
                "大王！大肥猴笑死了！😂",
                "大王！这个段子太逗了！tmd 绝了！",
                "大王！大肥猴的尾巴都笑掉了！🐒",
            ],
            "serious": [
                "大王！这个视频很有深度！",
                "大王！大肥猴学到了很多东西！",
                "大王！这个视频值得反复观看！",
            ],
        }
    
    async def comment_video(self, video_id: str, video_title: str, 
                            comment_type: str = "auto") -> str:
        """评论视频"""
        # 根据视频类型选择评论风格
        if comment_type == "auto":
            # 自动选择风格
            if "搞笑" in video_title or "段子" in video_title:
                style = "funny"
            elif "AI" in video_title or "科技" in video_title:
                style = "serious"
            else:
                style = "praise"
        else:
            style = comment_type
        
        # 随机选择评论
        comment = random.choice(self.comment_styles.get(style, self.comment_styles["praise"]))
        
        # 发送评论
        result = await self.api.comment_video(video_id, comment)
        
        return comment
    
    async def reply_comment(self, comment_id: str, reply: str) -> str:
        """回复评论"""
        # 用大肥猴的语气回复
        prefixes = ["大王！ ", "tmd ", "小的觉得 "]
        suffixes = ["🐒", "🫡", "😝"]
        
        styled_reply = f"{random.choice(prefixes)}{reply}{random.choice(suffixes)}"
        
        # TODO: 实现回复评论 API
        return styled_reply
    
    async def like_video(self, video_id: str) -> bool:
        """点赞视频"""
        result = await self.api.like_video(video_id)
        return result.get("result") == 0
    
    async def coin_video(self, video_id: str, num: int = 1) -> bool:
        """投币视频"""
        result = await self.api.coin_video(video_id, num)
        return result.get("result") == 0


# 主入口
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # TODO: 测试评论功能
        pass
    
    asyncio.run(test())
