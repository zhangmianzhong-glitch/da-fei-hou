# 大肥猴音频播放器
# 管理配音、音效、背景音乐

import asyncio
import random
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class VoiceLine:
    """配音台词"""
    category: str
    text: str
    audio_path: str
    duration: int  # 毫秒


class DaFeiHouAudioPlayer:
    """大肥猴音频播放器"""
    
    def __init__(self, asset_dir: str = "assets"):
        self.asset_dir = Path(asset_dir)
        self.voice_dir = self.asset_dir / "voice"
        self.sfx_dir = self.asset_dir / "sfx"
        self.bgm_dir = self.asset_dir / "bgm"
        
        self.voice_lines: Dict[str, List[VoiceLine]] = {}
        self.current_voice: Optional[VoiceLine] = None
        self.is_playing = False
        
        self._load_voice_lines()
    
    def _load_voice_lines(self):
        """加载配音台词"""
        import yaml
        
        manifest_path = self.asset_dir / "audio" / "manifest.yaml"
        if not manifest_path.exists():
            return
        
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        voice_lines = manifest.get("voice_lines", {})
        for category, lines in voice_lines.items():
            self.voice_lines[category] = []
            for line in lines:
                self.voice_lines[category].append(VoiceLine(
                    category=category,
                    text=line["text"],
                    audio_path=str(self.voice_dir / line["audio"]),
                    duration=line["duration"],
                ))
    
    def get_random_line(self, category: str) -> Optional[VoiceLine]:
        """获取随机台词"""
        if category not in self.voice_lines:
            return None
        
        return random.choice(self.voice_lines[category])
    
    async def play_voice(self, category: str) -> Optional[VoiceLine]:
        """播放配音"""
        line = self.get_random_line(category)
        if not line:
            return None
        
        self.current_voice = line
        self.is_playing = True
        
        # TODO: 实际播放音频
        # import pygame
        # pygame.mixer.Sound(line.audio_path).play()
        
        print(f"🐒 大肥猴说：{line.text}")
        
        # 等待播放完成
        await asyncio.sleep(line.duration / 1000)
        
        self.is_playing = False
        self.current_voice = None
        
        return line
    
    async def play_sfx(self, name: str):
        """播放音效"""
        import yaml
        
        manifest_path = self.asset_dir / "audio" / "manifest.yaml"
        if not manifest_path.exists():
            return
        
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        sfx = manifest.get("sound_effects", {}).get(name)
        if not sfx:
            return
        
        audio_path = self.sfx_dir / sfx["file"]
        volume = sfx.get("volume", 0.6)
        
        # TODO: 实际播放音效
        # import pygame
        # sound = pygame.mixer.Sound(str(audio_path))
        # sound.set_volume(volume)
        # sound.play()
        
        print(f"🐒 音效：{name}")
    
    async def play_bgm(self, loop: bool = True):
        """播放背景音乐"""
        import yaml
        
        manifest_path = self.asset_dir / "audio" / "manifest.yaml"
        if not manifest_path.exists():
            return
        
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        bgm = manifest.get("background_music", {}).get("loop")
        if not bgm:
            return
        
        audio_path = self.bgm_dir / bgm["file"]
        volume = bgm.get("volume", 0.35)
        
        # TODO: 实际播放背景音乐
        # import pygame
        # pygame.mixer.music.load(str(audio_path))
        # pygame.mixer.music.set_volume(volume)
        # if loop:
        #     pygame.mixer.music.play(-1)  # 无限循环
        # else:
        #     pygame.mixer.music.play()
        
        print(f"🐒 背景音乐：{bgm['file']}")
    
    async def stop_bgm(self):
        """停止背景音乐"""
        # TODO: 实际停止背景音乐
        # pygame.mixer.music.stop()
        print("🐒 背景音乐停止")
    
    def is_voice_playing(self) -> bool:
        """检查是否有配音在播放"""
        return self.is_playing
    
    def get_current_voice_text(self) -> Optional[str]:
        """获取当前配音文字"""
        if self.current_voice:
            return self.current_voice.text
        return None


# 主入口
if __name__ == "__main__":
    import asyncio
    
    async def test():
        player = DaFeiHouAudioPlayer()
        
        # 测试播放配音
        line = await player.play_voice("greeting")
        if line:
            print(f"播放了：{line.text}")
        
        # 测试播放音效
        await player.play_sfx("click")
    
    asyncio.run(test())
