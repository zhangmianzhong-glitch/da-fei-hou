# 大肥猴状态机
# 管理大肥猴的所有状态转换和动画

from enum import Enum
from typing import Optional, Callable, Dict
import random
import time


class MonkeyState(Enum):
    """大肥猴的 18 种状态"""
    IDLE = "idle"           # 待机（挠痒痒、东张西望）
    BLINK = "blink"         # 眨眼
    WALK_RIGHT = "walk_right"  # 迈步（向右）
    WALK_LEFT = "walk_left"    # 迈步（向左）
    HAPPY = "happy"         # 开心（拍手跳跃）
    CHEER = "cheer"         # 欢呼（举金箍棒）
    SPEAKING = "speaking"   # 说话
    THINKING = "thinking"   # 思考（挠头，头顶冒灯泡）
    HEART = "heart"         # 比心（尾巴比心）
    SAD = "sad"             # 难过（垂头丧气）
    ANGRY = "angry"         # 生气（龇牙咧嘴）
    SURPRISE = "surprise"   # 惊讶（嘴巴张大，金箍棒掉了）
    SLEEPING = "sleeping"   # 睡觉（打呼噜，流口水）
    WAVE = "wave"           # 挥手
    SINGING = "singing"     # 唱歌（摇头晃脑）
    BASIN = "basin"         # 顶钢盆（头顶钢盆，敲起来哐哐响）
    EATING = "eating"       # 吃白饭（抱着碗吃）
    FISHING = "fishing"     # 摸鱼（打哈欠，玩手机）


class StateTransition:
    """状态转换规则"""
    
    def __init__(self, from_state: MonkeyState, to_state: MonkeyState, 
                 duration: Optional[int] = None, trigger: str = "auto"):
        self.from_state = from_state
        self.to_state = to_state
        self.duration = duration  # 毫秒，None 表示保持
        self.trigger = trigger    # auto, click, poke, task_start, task_complete, error, bilibili


# 状态转换表
TRANSITIONS = [
    # 基础状态转换
    StateTransition(MonkeyState.IDLE, MonkeyState.BLINK, 500, "auto"),
    StateTransition(MonkeyState.IDLE, MonkeyState.WALK_RIGHT, 3000, "auto"),
    StateTransition(MonkeyState.IDLE, MonkeyState.WALK_LEFT, 3000, "auto"),
    StateTransition(MonkeyState.IDLE, MonkeyState.THINKING, 2000, "auto"),
    StateTransition(MonkeyState.IDLE, MonkeyState.BASIN, 2000, "auto"),
    StateTransition(MonkeyState.IDLE, MonkeyState.EATING, 2000, "auto"),
    StateTransition(MonkeyState.IDLE, MonkeyState.SINGING, 2000, "auto"),
    StateTransition(MonkeyState.IDLE, MonkeyState.CHEER, 2000, "auto"),
    StateTransition(MonkeyState.IDLE, MonkeyState.HEART, 2000, "auto"),
    StateTransition(MonkeyState.IDLE, MonkeyState.ANGRY, 2000, "auto"),
    
    # 任务相关
    StateTransition(MonkeyState.IDLE, MonkeyState.THINKING, None, "task_start"),
    StateTransition(MonkeyState.THINKING, MonkeyState.HAPPY, None, "task_complete"),
    StateTransition(MonkeyState.THINKING, MonkeyState.SAD, None, "error"),
    
    # 互动相关
    StateTransition(MonkeyState.IDLE, MonkeyState.HAPPY, 1000, "click"),
    StateTransition(MonkeyState.IDLE, MonkeyState.ANGRY, 3000, "poke_x3"),
    StateTransition(MonkeyState.IDLE, MonkeyState.SURPRISE, 2000, "bilibili"),
    
    # 时间相关
    StateTransition(MonkeyState.IDLE, MonkeyState.SLEEPING, None, "timeout_10min"),
    StateTransition(MonkeyState.SLEEPING, MonkeyState.WAVE, None, "wake"),
    
    # 摸鱼
    StateTransition(MonkeyState.IDLE, MonkeyState.FISHING, None, "idle_time"),
]


class MonkeyStateMachine:
    """大肥猴状态机"""
    
    def __init__(self):
        self.current_state = MonkeyState.IDLE
        self.state_start_time = time.time()
        self.listeners: Dict[str, list] = {}
        self.poke_count = 0
        self.poke_timer = None
        self.last_interaction_time = time.time()
        self.is_sleeping = False
        
    def get_current_state(self) -> MonkeyState:
        """获取当前状态"""
        return self.current_state
    
    def set_state(self, state: MonkeyState, duration: Optional[int] = None):
        """设置状态"""
        old_state = self.current_state
        self.current_state = state
        self.state_start_time = time.time()
        
        # 触发状态变更事件
        self._emit("state_change", old_state, state)
        
        # 更新最后互动时间
        self.last_interaction_time = time.time()
        self.is_sleeping = (state == MonkeyState.SLEEPING)
        
        # 定时恢复
        if duration:
            import threading
            timer = threading.Timer(duration / 1000.0, self._restore_state, args=[old_state])
            timer.start()
    
    def _restore_state(self, state: MonkeyState):
        """恢复状态"""
        self.current_state = state
        self._emit("state_change", self.current_state, state)
    
    def trigger(self, trigger_name: str, data: dict = None):
        """触发状态转换"""
        # 检查所有转换规则
        for transition in TRANSITIONS:
            if (transition.from_state == self.current_state and 
                transition.trigger == trigger_name):
                self.set_state(transition.to_state, transition.duration)
                return
        
        # 如果没有匹配的规则，保持当前状态
        pass
    
    def on(self, event: str, callback: Callable):
        """注册事件监听"""
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
    
    def _emit(self, event: str, *args):
        """触发事件"""
        if event in self.listeners:
            for callback in self.listeners[event]:
                callback(*args)
    
    def update(self):
        """更新状态机（定时调用）"""
        now = time.time()
        
        # 检查是否该睡觉了（10分钟无互动）
        if not self.is_sleeping and (now - self.last_interaction_time) > 600:
            self.trigger("timeout_10min")
        
        # 检查是否该摸鱼了（空闲时间）
        if self.current_state == MonkeyState.IDLE and random.random() < 0.01:
            self.trigger("idle_time")
        
        # 检查是否该眨眼了
        if self.current_state == MonkeyState.IDLE and random.random() < 0.05:
            self.trigger("blink")
        
        # 检查是否该走路了
        if self.current_state == MonkeyState.IDLE and random.random() < 0.02:
            direction = random.choice(["walk_right", "walk_left"])
            self.trigger(direction)
        
        # 检查是否该有小动作了
        if self.current_state == MonkeyState.IDLE and random.random() < 0.005:
            actions = ["thinking", "basin", "eating", "singing", "cheer", "heart", "angry"]
            action = random.choice(actions)
            self.trigger(action)
    
    def poke(self):
        """戳大肥猴"""
        self.poke_count += 1
        if self.poke_count >= 3:
            self.trigger("poke_x3")
            self.poke_count = 0
        else:
            self.trigger("click")
        
        # 重置戳计数
        import threading
        self.poke_timer = threading.Timer(2.0, self._reset_poke)
        self.poke_timer.start()
    
    def _reset_poke(self):
        """重置戳计数"""
        self.poke_count = 0
    
    def click(self):
        """点击大肥猴"""
        self.trigger("click")
        self.poke()
    
    def drag(self):
        """拖拽大肥猴"""
        # 拖拽时播放悬空姿势
        pass
    
    def drop(self):
        """松开大肥猴（掉落）"""
        # 落地动画：squash-and-stretch
        self.set_state(MonkeyState.HAPPY, 1000)
        self._emit("drop")


# 主入口
if __name__ == "__main__":
    import asyncio
    
    sm = MonkeyStateMachine()
    
    def on_state_change(old, new):
        print(f"🐒 状态变更：{old.value} → {new.value}")
    
    sm.on("state_change", on_state_change)
    
    # 测试
    sm.trigger("task_start")
    print(f"当前状态：{sm.get_current_state().value}")
    
    sm.trigger("task_complete")
    print(f"当前状态：{sm.get_current_state().value}")
