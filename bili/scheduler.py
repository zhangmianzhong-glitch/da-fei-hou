# 大肥猴定时任务调度
# 管理所有定时任务

import asyncio
import schedule
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional


class DaFeiHouScheduler:
    """大肥猴任务调度器"""
    
    def __init__(self):
        self.tasks = []
        self.is_running = False
    
    def add_task(self, name: str, schedule_time: str, 
                 callback: Callable, description: str = ""):
        """添加定时任务"""
        task = {
            "name": name,
            "schedule": schedule_time,
            "callback": callback,
            "description": description,
            "last_run": None,
            "next_run": None,
        }
        self.tasks.append(task)
        print(f"🐒 添加任务：{name} - {schedule_time}")
    
    def start(self):
        """启动调度器"""
        self.is_running = True
        print("🐒 大肥猴调度器启动！大王万岁！")
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        print("🐒 大肥猴调度器停止...大王晚安！")


class DaFeiHouAsyncScheduler:
    """大肥猴异步任务调度器"""
    
    def __init__(self):
        self.tasks = []
        self.is_running = False
    
    def add_cron_task(self, name: str, hour: int, minute: int = 0,
                      callback: Callable = None, description: str = ""):
        """添加 cron 风格任务"""
        task = {
            "name": name,
            "hour": hour,
            "minute": minute,
            "callback": callback,
            "description": description,
            "last_run": None,
        }
        self.tasks.append(task)
        print(f"🐒 添加任务：{name} - {hour:02d}:{minute:02d}")
    
    async def run(self):
        """运行调度器"""
        self.is_running = True
        print("🐒 大肥猴异步调度器启动！大王万岁！")
        
        last_hour = -1
        
        while self.is_running:
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            
            # 检查是否有任务需要执行
            if current_hour != last_hour:
                for task in self.tasks:
                    if (task["hour"] == current_hour and 
                        task["minute"] == current_minute):
                        print(f"🐒 执行任务：{task['name']}")
                        if task["callback"]:
                            await task["callback"]()
                        task["last_run"] = now.isoformat()
                
                last_hour = current_hour
            
            await asyncio.sleep(30)  # 每 30 秒检查一次
    
    async def stop(self):
        """停止调度器"""
        self.is_running = False
        print("🐒 大肥猴异步调度器停止...大王晚安！")


# 主入口
if __name__ == "__main__":
    import asyncio
    
    async def test_task():
        print("🐒 测试任务执行！大王万岁！")
    
    scheduler = DaFeiHouAsyncScheduler()
    scheduler.add_cron_task("早间刷站", 8, 0, test_task)
    scheduler.add_cron_task("午间刷站", 12, 0, test_task)
    scheduler.add_cron_task("晚间刷站", 18, 0, test_task)
    
    async def main():
        await scheduler.run()
    
    asyncio.run(main())
