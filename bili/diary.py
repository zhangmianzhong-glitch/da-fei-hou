# 大猴猴日记系统
# 两本日记：刷站日记 + 汇报日记

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DaFeiHouDiary:
    """大肥猴日记系统"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.diary_dir = data_dir / "diary"
        self.memory_dir = data_dir / "memory"
        self.diary_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def today(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_diary_path(self, date: Optional[str] = None) -> Path:
        return self.diary_dir / f"{date or self.today()}.json"
    
    def get_memory_path(self, date: Optional[str] = None) -> Path:
        return self.memory_dir / f"{date or self.today()}.json"
    
    def load_diary(self, date: Optional[str] = None) -> Dict:
        """加载日记"""
        path = self.get_diary_path(date)
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return self._empty_diary()
    
    def save_diary(self, diary: Dict, date: Optional[str] = None):
        """保存日记"""
        path = self.get_diary_path(date)
        with open(path, "w") as f:
            json.dump(diary, f, ensure_ascii=False, indent=2)
    
    def load_memory(self, date: Optional[str] = None) -> Dict:
        """加载记忆"""
        path = self.get_memory_path(date)
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return self._empty_memory()
    
    def save_memory(self, memory: Dict, date: Optional[str] = None):
        """保存记忆"""
        path = self.get_memory_path(date)
        with open(path, "w") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    
    def add_video(self, video: Dict, date: Optional[str] = None):
        """添加观看记录"""
        diary = self.load_diary(date)
        diary["videos_watched"].append({
            "title": video.get("title"),
            "aid": video.get("aid"),
            "up_name": video.get("up_name"),
            "play_count": video.get("play_count"),
            "watched_at": datetime.now().isoformat(),
        })
        self.save_diary(diary, date)
    
    def add_interesting(self, video: Dict, reason: str, date: Optional[str] = None):
        """添加感兴趣视频"""
        diary = self.load_diary(date)
        diary["interesting_videos"].append({
            "title": video.get("title"),
            "aid": video.get("aid"),
            "url": video.get("url"),
            "reason": reason,
            "found_at": datetime.now().isoformat(),
        })
        self.save_diary(diary, date)
    
    def add_comment(self, comment: Dict, date: Optional[str] = None):
        """添加评论记录"""
        diary = self.load_diary(date)
        diary["comments_made"].append({
            "video_title": comment.get("video_title"),
            "content": comment.get("content"),
            "commented_at": datetime.now().isoformat(),
        })
        self.save_diary(diary, date)
    
    def add_memory(self, memory: str, date: Optional[str] = None):
        """添加记忆"""
        mem = self.load_memory(date)
        if "memories" not in mem:
            mem["memories"] = []
        mem["memories"].append({
            "content": memory,
            "created_at": datetime.now().isoformat(),
        })
        self.save_memory(mem, date)
    
    def get_summary(self, date: Optional[str] = None) -> str:
        """获取日记汇总"""
        diary = self.load_diary(date)
        summary = f"🐒 大肥猴{date or self.today()}日记\n\n"
        summary += f"看了 {len(diary['videos_watched'])} 个视频\n"
        summary += f"发现 {len(diary['interesting_videos'])} 个有意思的\n"
        summary += f"评论了 {len(diary['comments_made'])} 次\n"
        return summary
    
    def _empty_diary(self) -> Dict:
        return {
            "date": self.today(),
            "videos_watched": [],
            "interesting_videos": [],
            "comments_made": [],
        }
    
    def _empty_memory(self) -> Dict:
        return {
            "date": self.today(),
            "memories": [],
        }


# 主入口
if __name__ == "__main__":
    diary = DaFeiHouDiary(Path(__file__).parent.parent / "data")
    
    # 测试
    diary.add_video({
        "title": "大王万岁！大肥猴来了！",
        "aid": "123456",
        "up_name": "山寨喽喽",
        "play_count": 999999,
    })
    
    diary.add_interesting({
        "title": "大王英明神武！tmd 绝了！",
        "aid": "789012",
        "url": "https://www.bilibili.com/video/BV123",
    }, "大王可能会感兴趣")
    
    print(diary.get_summary())
