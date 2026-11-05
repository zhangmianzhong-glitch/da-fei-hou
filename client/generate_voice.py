#!/usr/bin/env python3
"""
大肥猴 TTS 配音生成脚本
使用 Edge TTS（免费微软 TTS）批量生成所有配音

Edge TTS 优势：
- 完全免费，无需 API key
- 支持中文语音（云希、晓晓等）
- 可以调语速、音调
- 音质好，接近真人

安装：pip install edge-tts
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, List


# 大肥猴的配音台词库
VOICE_LINES = {
    "greeting": [
        "大王！小的大肥猴在呢！",
        "大王万岁！山寨喽喽随时待命！",
        "大王来啦！小的给您磕头了！",
        "大王！大肥猴想死您了！",
        "大王英明神武！小的给您请安了！",
    ],
    "thinking": [
        "t m d 这任务有点意思...",
        "让小的想想...大王英明神武！",
        "大王放心，小的马上搞定！",
        "t m d 大王这主意绝了！",
    ],
    "happy": [
        "大王夸奖！小的太开心了！",
        "大王英明！小的拍马屁时间到！",
        "大王万岁！小的给您唱首歌！",
        "t m d 大王太厉害了！",
    ],
    "sad": [
        "大王骂我了...小的难过...",
        "小的错了...大王别生气...",
        "大王...小的不是故意的...",
    ],
    "angry": [
        "别戳了！再戳小的大王万岁都不喊了！",
        "t m d 再戳我试试！...大王我开玩笑的！",
        "大王！小的要生气了！...哎呀还是不敢...",
    ],
    "surprise": [
        "卧槽！大王这也太厉害了！",
        "t m d 这任务小的是真没想到！",
        "大王！大肥猴惊了！",
    ],
    "sleeping": [
        "z z z...大王...z z z...万岁...z z z...",
        "z z z...摸鱼...z z z...",
        "z z z...大王...给钱...z z z...",
    ],
    "wave": [
        "大王好！小的给您挥手！",
        "大王回来啦！小的等您好久了！",
    ],
    "singing": [
        "大王万岁~万岁~万万岁~",
        "山寨喽喽~永远忠于大王~",
        "大肥猴~大肥猴~大王的好喽喽~",
    ],
    "basin": [
        "哐——嗡——（敲盆）",
        "大王骂我了...顶个盆防弹...",
    ],
    "eating": [
        "大王，小的吃饭去了！",
        "剩饭等于缓存，外包摸鱼等于 a g e n t 调用！",
        "大王！小的去吃饭，测完告诉我就行！",
    ],
    "fishing": [
        "t m d 摸鱼时间到...打哈欠...",
        "大王不在，小的偷偷看个 B 站...",
        "大王！小的在摸鱼...啊不对！在努力工作！",
    ],
    "bilibili": [
        "大王！小的在 B 站看到个好东西！",
        "大王，这个视频太绝了！t m d 绝了！",
        "大王快看！大肥猴发现宝藏了！",
    ],
    "patting": [
        "大王万岁！大王永远是对的！",
        "大王的话就是圣旨！",
        "大王的决策英明神武！",
        "大王的眼光独到大气！",
        "大王的气质威震四方！",
        "大王的智慧深不可测！",
    ],
}


class DaFeiHouTTS:
    """大肥猴 TTS 配音生成器"""
    
    def __init__(self, output_dir: str = "assets/voice"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Edge TTS 语音配置
        # 东北话男声 - 云希（比较符合大肥猴的人设）
        self.voice = "zh-CN-YunxiNeural"
        self.rate = "+10%"  # 语速稍快
        self.pitch = "+5Hz"  # 音调稍高
        self.volume = "+20%"  # 音量稍大
    
    async def synthesize(self, text: str, output_path: Path) -> bool:
        """合成单个语音"""
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(
                text,
                self.voice,
                rate=self.rate,
                pitch=self.pitch,
                volume=self.volume,
            )
            
            await communicate.save(str(output_path))
            return True
        
        except ImportError:
            print("❌ 需要安装 edge-tts: pip install edge-tts")
            return False
        except Exception as e:
            print(f"❌ 合成失败：{e}")
            return False
    
    async def batch_synthesize(self):
        """批量合成所有配音"""
        print("🐒 大肥猴开始批量生成配音...")
        print(f" 使用语音：{self.voice}")
        print(f"📁 输出目录：{self.output_dir}")
        print()
        
        total = 0
        success = 0
        
        for category, lines in VOICE_LINES.items():
            print(f"📢 生成 {category} 类别...")
            category_dir = self.output_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            for i, line in enumerate(lines, 1):
                # 文件名：category_01.mp3
                filename = f"{category}_{i:02d}.mp3"
                output_path = category_dir / filename
                
                # 处理文本（去掉 t m d 中的空格）
                clean_text = line.replace("t m d", "tmd").replace("z z z", "zzz").replace("a g e n t", "agent")
                
                print(f"  {i}/{len(lines)}: {clean_text[:30]}...")
                
                if await self.synthesize(clean_text, output_path):
                    success += 1
                    print(f"    ✅ 成功：{filename}")
                else:
                    print(f"    ❌ 失败：{filename}")
                
                total += 1
                
                # 避免请求太快
                await asyncio.sleep(0.5)
            
            print()
        
        print(f" 批量生成完成！成功 {success}/{total}")
        return success, total


async def main():
    """主函数"""
    print("=" * 60)
    print(" 大肥猴 TTS 配音生成器")
    print("=" * 60)
    print()
    
    tts = DaFeiHouTTS()
    success, total = await tts.batch_synthesize()
    
    print()
    print("=" * 60)
    if success == total:
        print("✅ 所有配音生成成功！大王万岁！")
    else:
        print(f"⚠️  部分失败：{success}/{total}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
