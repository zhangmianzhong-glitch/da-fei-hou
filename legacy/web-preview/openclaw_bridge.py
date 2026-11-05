# 大肥猴 OpenClaw 事件对接
# 监听 OpenClaw 事件，驱动大肥猴状态变化

import asyncio
import json
from typing import Dict, Optional, Callable
from datetime import datetime


class DaFeiHouOpenClawBridge:
    """大肥猴 OpenClaw 桥接器"""
    
    def __init__(self, state_machine, notifier):
        self.state_machine = state_machine
        self.notifier = notifier
        self.listeners = {}
        self.is_connected = False
    
    async def connect(self):
        """连接 OpenClaw 事件系统"""
        print("🐒 大肥猴连接 OpenClaw...")
        self.is_connected = True
        
        # 注册事件监听
        # TODO: 实际接入 OpenClaw WebSocket 或 API
        
        # 发送连接成功消息
        await self.notifier.send_message("🐒 大肥猴已连接 OpenClaw！大王万岁！")
    
    async def disconnect(self):
        """断开连接"""
        self.is_connected = False
        await self.notifier.send_message("🐒 大肥猴断开连接...大王晚安！")
    
    def on(self, event: str, callback: Callable):
        """注册事件监听"""
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
    
    async def handle_event(self, event: Dict):
        """处理 OpenClaw 事件"""
        event_type = event.get("type")
        
        if event_type == "task_start":
            await self._on_task_start(event)
        elif event_type == "task_complete":
            await self._on_task_complete(event)
        elif event_type == "error":
            await self._on_error(event)
        elif event_type == "session_start":
            await self._on_session_start(event)
        elif event_type == "session_end":
            await self._on_session_end(event)
        
        # 触发自定义监听器
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                await callback(event)
    
    async def _on_task_start(self, event: Dict):
        """任务开始"""
        task_name = event.get("task_name", "未知任务")
        print(f"🐒 任务开始：{task_name}")
        
        # 大肥猴进入思考状态
        self.state_machine.trigger("task_start")
        
        # 发送通知
        await self.notifier.send_task_notification(task_name, "start")
    
    async def _on_task_complete(self, event: Dict):
        """任务完成"""
        task_name = event.get("task_name", "未知任务")
        print(f"🐒 任务完成：{task_name}")
        
        # 大肥猴进入开心状态
        self.state_machine.trigger("task_complete")
        
        # 发送通知
        await self.notifier.send_task_notification(task_name, "complete")
    
    async def _on_error(self, event: Dict):
        """错误"""
        error_msg = event.get("error", "未知错误")
        print(f"🐒 错误：{error_msg}")
        
        # 大肥猴进入难过状态
        self.state_machine.trigger("error")
        
        # 发送通知
        await self.notifier.send_error_notification(error_msg)
    
    async def _on_session_start(self, event: Dict):
        """会话开始"""
        print("🐒 新会话开始")
        
        # 大肥猴挥手
        self.state_machine.set_state("wave")
        
        # 发送通知
        await self.notifier.send_message("🐒 大王好！大肥猴等您好久了！")
    
    async def _on_session_end(self, event: Dict):
        """会话结束"""
        print("🐒 会话结束")
        
        # 大肥猴睡觉
        self.state_machine.set_state("sleeping")
        
        # 发送通知
        await self.notifier.send_message("🐒 大王晚安！大肥猴睡觉了...zzz")
    
    async def send_to_openclaw(self, message: str):
        """发送消息到 OpenClaw"""
        # TODO: 实际接入 OpenClaw API
        print(f"🐒 大肥猴发消息到 OpenClaw：{message}")
    
    async def get_openclaw_status(self) -> Dict:
        """获取 OpenClaw 状态"""
        # TODO: 实际接入 OpenClaw API
        return {
            "status": "running",
            "active_tasks": 0,
            "last_event": None,
        }


# 主入口
if __name__ == "__main__":
    import asyncio
    
    from client.state_machine import MonkeyStateMachine
    from bili.dingtalk_notifier import DaFeiHouDingTalkNotifier
    
    config = {"client_id": "dinginhyci8m2jm0ilgw"}
    sm = MonkeyStateMachine()
    notifier = DaFeiHouDingTalkNotifier(config)
    bridge = DaFeiHouOpenClawBridge(sm, notifier)
    
    async def test():
        await bridge.connect()
        
        # 模拟事件
        await bridge.handle_event({
            "type": "task_start",
            "task_name": "分析基金数据",
        })
        
        await asyncio.sleep(2)
        
        await bridge.handle_event({
            "type": "task_complete",
            "task_name": "分析基金数据",
        })
        
        await bridge.disconnect()
    
    asyncio.run(test())
