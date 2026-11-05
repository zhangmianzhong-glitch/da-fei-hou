# 大肥猴 TTS 语音合成
# 用东北话+天津话给大肥猴配音

import asyncio
import os
import hashlib
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class TTSConfig:
    """TTS 配置"""
    provider: str = "edge-tts"  # edge-tts, openai, local
    voice: str = "zh-CN-YunxiNeural"  # 东北话男声
    rate: str = "+10%"  # 语速
    pitch: str = "+5Hz"  # 音调
    output_dir: str = "assets/voice"


class DaFeiHouTTS:
    """大肥猴 TTS 语音合成"""
    
    def __init__(self, config: TTSConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, text: str) -> Path:
        """获取缓存路径"""
        hash_key = hashlib.md5(text.encode()).hexdigest()[:16]
        return self.output_dir / f"{hash_key}.mp3"
    
    async def synthesize(self, text: str, output_path: Optional[str] = None) -> str:
        """合成语音"""
        cache_path = self._get_cache_path(text)
        
        if cache_path.exists():
            # 使用缓存
            return str(cache_path)
        
        if self.config.provider == "edge-tts":
            audio_path = await self._edge_tts(text, cache_path)
        elif self.config.provider == "openai":
            audio_path = await self._openai_tts(text, cache_path)
        else:
            # 本地 TTS
            audio_path = await self._local_tts(text, cache_path)
        
        return audio_path
    
    async def _edge_tts(self, text: str, output_path: Path) -> str:
        """Edge TTS（免费）"""
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(
                text,
                self.config.voice,
                rate=self.config.rate,
                pitch=self.config.pitch,
            )
            
            await communicate.save(str(output_path))
            return str(output_path)
        
        except ImportError:
            print("🐒 需要安装 edge-tts: pip install edge-tts")
            return ""
    
    async def _openai_tts(self, text: str, output_path: Path) -> str:
        """OpenAI TTS"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = await client.audio.speech.create(
                model="tts-1",
                voice="alloy",  # OpenAI 不支持中文方言
                input=text,
            )
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            return str(output_path)
        
        except ImportError:
            print("🐒 需要安装 openai: pip install openai")
            return ""
    
    async def _local_tts(self, text: str, output_path: Path) -> str:
        """本地 TTS（使用 pyttsx3）"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()
            
            return str(output_path)
        
        except ImportError:
            print("🐒 需要安装 pyttsx3: pip install pyttsx3")
            return ""
    
    async def batch_synthesize(self, lines: Dict[str, str]) -> Dict[str, str]:
        """批量合成语音"""
        results = {}
        
        for name, text in lines.items():
            audio_path = await self.synthesize(text)
            results[name] = audio_path
        
        return results
    
    async def clear_cache(self):
        """清空缓存"""
        for file in self.output_dir.glob("*.mp3"):
            file.unlink()
        print("🐒 TTS 缓存已清空")


# 主入口
if __name__ == "__main__":
    import asyncio
    
    async def test():
        config = TTSConfig()
        tts = DaFeiHouTTS(config)
        
        # 测试合成
        lines = {
            "greeting": "大王！小的大肥猴在呢！大王万岁！",
            "thinking": "tmd 这任务有点意思...让小的想想...",
            "happy": "大王夸奖！小的太开心了！大王英明神武！",
        }
        
        results = await tts.batch_synthesize(lines)
        for name, path in results.items():
            print(f"🐒 {name}: {path}")
    
    asyncio.run(test())
