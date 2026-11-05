# 大肥猴 AI 视频分析
# 六路理解：画面 + 音频 + 字幕 + 评论 + 弹幕 + 简介

import asyncio
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class VideoAnalysis:
    """视频分析结果"""
    aid: str
    title: str
    up_name: str
    score: float  # 兴趣评分 0-1
    reason: str  # 推荐理由
    categories: List[str]  # 分类标签
    sentiment: str  # 情感分析
    summary: str  # 内容摘要
    key_moments: List[Dict]  # 关键时间点
    comment_sentiment: str  # 评论情感
    danmaku_hot_words: List[str]  # 弹幕热词


class DaFeiHouVideoAnalyzer:
    """大肥猴视频分析器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.interests = [
            "AI", "机器学习", "深度学习", "大语言模型",
            "科技", "芯片", "半导体",
            "财经", "基金", "股票",
            "搞笑", "段子", "东北话",
        ]
    
    async def analyze(self, video: Dict, comments: List[Dict], 
                      danmaku: List[str], subtitle: str) -> VideoAnalysis:
        """六路分析视频"""
        # 1. 简介分析（标题 + UP主 + 简介）
        title_score = self._analyze_title(video.get("title", ""))
        
        # 2. 字幕分析（AI 理解视频内容）
        subtitle_analysis = await self._analyze_subtitle(subtitle) if subtitle else {}
        
        # 3. 评论分析
        comment_analysis = self._analyze_comments(comments)
        
        # 4. 弹幕分析
        danmaku_analysis = self._analyze_danmaku(danmaku)
        
        # 5. 综合评分
        score = self._calculate_score(title_score, subtitle_analysis, 
                                       comment_analysis, danmaku_analysis)
        
        # 6. 生成推荐理由
        reason = self._generate_reason(score, title_score, comment_analysis)
        
        return VideoAnalysis(
            aid=video.get("aid"),
            title=video.get("title"),
            up_name=video.get("up_name"),
            score=score,
            reason=reason,
            categories=title_score.get("categories", []),
            sentiment=subtitle_analysis.get("sentiment", "neutral"),
            summary=subtitle_analysis.get("summary", ""),
            key_moments=subtitle_analysis.get("key_moments", []),
            comment_sentiment=comment_analysis.get("sentiment", "neutral"),
            danmaku_hot_words=danmaku_analysis.get("hot_words", []),
        )
    
    def _analyze_title(self, title: str) -> Dict:
        """分析标题"""
        categories = []
        score = 0.0
        
        for interest in self.interests:
            if interest in title:
                categories.append(interest)
                score += 0.2
        
        # 标题长度评分（太短或太长都不好）
        if 10 < len(title) < 50:
            score += 0.1
        
        return {
            "score": min(score, 1.0),
            "categories": categories,
        }
    
    async def _analyze_subtitle(self, subtitle: str) -> Dict:
        """分析字幕（AI 理解）"""
        # TODO: 调用 AI API 分析
        # 使用 OpenAI API 或本地模型
        
        if not subtitle or len(subtitle) < 10:
            return {}
        
        # 简单关键词匹配
        keywords = []
        for interest in self.interests:
            if interest in subtitle:
                keywords.append(interest)
        
        return {
            "sentiment": "positive" if keywords else "neutral",
            "summary": subtitle[:200] + "..." if len(subtitle) > 200 else subtitle,
            "key_moments": [],
            "keywords": keywords,
        }
    
    def _analyze_comments(self, comments: List[Dict]) -> Dict:
        """分析评论"""
        if not comments:
            return {"sentiment": "neutral", "hot_words": []}
        
        # 提取评论中的热词
        all_text = " ".join(c.get("content", "") for c in comments[:20])
        hot_words = self._extract_keywords(all_text)
        
        # 情感分析（简单版）
        positive_words = ["好", "棒", "绝", "厉害", "牛", "赞", "有趣"]
        negative_words = ["差", "烂", "水", "无聊", "垃圾"]
        
        pos_count = sum(1 for w in positive_words if w in all_text)
        neg_count = sum(1 for w in negative_words if w in all_text)
        
        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "hot_words": hot_words[:10],
        }
    
    def _analyze_danmaku(self, danmaku: List[str]) -> Dict:
        """分析弹幕"""
        if not danmaku:
            return {"sentiment": "neutral", "hot_words": []}
        
        all_text = " ".join(danmaku[:100])
        hot_words = self._extract_keywords(all_text)
        
        return {
            "sentiment": "positive",  # 弹幕通常比较正面
            "hot_words": hot_words[:10],
        }
    
    def _calculate_score(self, title_score: Dict, subtitle_analysis: Dict,
                          comment_analysis: Dict, danmaku_analysis: Dict) -> float:
        """计算综合评分"""
        score = 0.0
        
        # 标题权重 40%
        score += title_score.get("score", 0) * 0.4
        
        # 字幕分析权重 30%
        if subtitle_analysis.get("keywords"):
            score += 0.3
        
        # 评论情感权重 20%
        if comment_analysis.get("sentiment") == "positive":
            score += 0.2
        
        # 弹幕热词权重 10%
        if danmaku_analysis.get("hot_words"):
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_reason(self, score: float, title_score: Dict, 
                          comment_analysis: Dict) -> str:
        """生成推荐理由"""
        reasons = []
        
        categories = title_score.get("categories", [])
        if categories:
            reasons.append(f"涉及大王感兴趣的领域：{', '.join(categories)}")
        
        if comment_analysis.get("sentiment") == "positive":
            reasons.append("评论反响很好")
        
        if score > 0.7:
            reasons.append("大肥猴觉得大王一定会感兴趣！")
        elif score > 0.5:
            reasons.append("大肥猴觉得可能有点意思...")
        else:
            reasons.append("大肥猴觉得一般般...")
        
        return "；".join(reasons)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简单版）"""
        # TODO: 使用更复杂的 NLP 方法
        words = []
        for word in self.interests:
            if word in text:
                words.append(word)
        return words


# 主入口
if __name__ == "__main__":
    import asyncio
    
    analyzer = DaFeiHouVideoAnalyzer()
    
    async def test():
        video = {
            "aid": "123456",
            "title": "AI 大模型最新进展！大王必看！",
            "up_name": "科技前沿",
        }
        comments = [
            {"content": "太厉害了！大王必看！"},
            {"content": "AI 发展真快"},
        ]
        danmaku = ["牛！", "666", "AI", "大王万岁"]
        subtitle = "本期视频介绍 AI 大模型的最新进展..."
        
        result = await analyzer.analyze(video, comments, danmaku, subtitle)
        print(f"🐒 大肥猴分析结果：")
        print(f"  评分：{result.score}")
        print(f"  原因：{result.reason}")
        print(f"  分类：{result.categories}")
    
    asyncio.run(test())
