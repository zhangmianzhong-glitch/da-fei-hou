# 大肥猴精灵渲染器
# 基于 CSS + Sprite 的 2D 渲染引擎

import time
import random
import math
from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class SpriteFrame:
    """精灵帧"""
    image_path: str
    duration: int  # 毫秒
    width: int
    height: int


@dataclass
class Animation:
    """动画序列"""
    name: str
    frames: list
    loop: bool
    facing: int  # 1=right, -1=left


class DaFeiHouRenderer:
    """大肥猴精灵渲染器"""
    
    def __init__(self, sprite_dir: str = "assets/sprites"):
        self.sprite_dir = sprite_dir
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[Animation] = None
        self.current_frame_index: int = 0
        self.frame_start_time: float = 0
        self.is_playing: bool = False
        
        # 位置
        self.position = {"x": 0, "y": 0}
        self.shadow_offset = 0
        self.shadow_opacity = 1.0
        
        # 物理
        self.is_airborne = False
        self.velocity_y = 0
        self.gravity = 980  # px/s²
        self.squash_factor = 1.0  # 压扁系数
        
        # 粒子效果
        self.particles = []
        
        self._load_all_animations()
    
    def _load_all_animations(self):
        """加载所有动画"""
        import yaml
        import os
        
        manifest_path = os.path.join(self.sprite_dir, "manifest.yaml")
        if not os.path.exists(manifest_path):
            return
        
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        for name, config in manifest.get("sprites", {}).items():
            frames = []
            for i in range(config.get("frames", 1)):
                frame_path = os.path.join(
                    self.sprite_dir, f"{name}_{i}.png"
                )
                frames.append(SpriteFrame(
                    image_path=frame_path,
                    duration=config.get("duration", 100),
                    width=config.get("width", 412),
                    height=config.get("height", 344),
                ))
            
            self.animations[name] = Animation(
                name=name,
                frames=frames,
                loop=config.get("loop", False),
                facing=config.get("facing", 1),
            )
    
    def play_animation(self, name: str, loop: bool = False):
        """播放动画"""
        if name not in self.animations:
            return
        
        anim = self.animations[name]
        if loop:
            anim.loop = True
        
        self.current_animation = anim
        self.current_frame_index = 0
        self.frame_start_time = time.time()
        self.is_playing = True
    
    def stop_animation(self):
        """停止动画"""
        self.is_playing = False
        self.current_animation = None
    
    def get_current_frame(self) -> Optional[SpriteFrame]:
        """获取当前帧"""
        if not self.current_animation or not self.is_playing:
            return None
        
        anim = self.current_animation
        elapsed = time.time() - self.frame_start_time
        current_frame = anim.frames[self.current_frame_index]
        
        # 检查是否需要切换到下一帧
        if elapsed * 1000 >= current_frame.duration:
            self._next_frame()
        
        return anim.frames[self.current_frame_index]
    
    def _next_frame(self):
        """切换到下一帧"""
        if not self.current_animation:
            return
        
        anim = self.current_animation
        self.current_frame_index += 1
        
        if self.current_frame_index >= len(anim.frames):
            if anim.loop:
                self.current_frame_index = 0
            else:
                self.is_playing = False
                self.current_frame_index = 0
        
        self.frame_start_time = time.time()
    
    # 物理系统
    def start_drag(self):
        """开始拖拽"""
        self.is_airborne = True
        self.velocity_y = 0
        self.shadow_offset = 0
        self.shadow_opacity = 0.5
    
    def update_drag(self, dx: float, dy: float):
        """更新拖拽位置"""
        self.position["x"] += dx
        self.position["y"] += dy
        # 拖拽时尾巴悬空
        self.squash_factor = 0.8
    
    def drop(self, height: float):
        """松开掉落"""
        self.is_airborne = False
        self.velocity_y = 0
        
        # 落地动画
        if height > 100:
            self.squash_factor = 0.5  # 压扁
            self._spawn_sparkles()
        else:
            self.squash_factor = 0.7
        
        # 弹起
        self._bounce()
    
    def _bounce(self):
        """弹起动画"""
        # 模拟 squash-and-stretch
        import threading
        
        def bounce_sequence():
            time.sleep(0.05)
            self.squash_factor = 1.2  # 拉伸
            time.sleep(0.05)
            self.squash_factor = 1.0  # 恢复
        
        threading.Thread(target=bounce_sequence, daemon=True).start()
    
    def _spawn_sparkles(self):
        """生成火花粒子"""
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            self.particles.append({
                "x": self.position["x"],
                "y": self.position["y"],
                "vx": math.cos(angle) * 50,
                "vy": math.sin(angle) * 50,
                "life": 1.0,
            })
    
    def update_particles(self, dt: float):
        """更新粒子"""
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        
        self.particles = [p for p in self.particles if p["life"] > 0]
    
    # 待机动画
    def update_idle(self):
        """更新待机状态"""
        if not self.is_playing and random.random() < 0.02:
            # 随机眨眼
            self.play_animation("blink")
        
        if not self.is_playing and random.random() < 0.01:
            # 随机呼吸
            self.squash_factor = 1.0 + random.uniform(-0.02, 0.02)
    
    # 渲染输出
    def render_state(self) -> Dict:
        """渲染当前状态（供前端使用）"""
        frame = self.get_current_frame()
        
        return {
            "image": frame.image_path if frame else None,
            "position": self.position,
            "facing": self.current_animation.facing if self.current_animation else 1,
            "squash": self.squash_factor,
            "shadow_offset": self.shadow_offset,
            "shadow_opacity": self.shadow_opacity,
            "particles": self.particles,
        }


# 主入口
if __name__ == "__main__":
    renderer = DaFeiHouRenderer()
    renderer.play_animation("idle", loop=True)
    
    while True:
        state = renderer.render_state()
        # 前端会消费这个 state
        time.sleep(0.016)  # 60fps
