#!/usr/bin/env python3
"""
大肥猴测试
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from client.state_machine import MonkeyStateMachine, MonkeyState
from bili.diary import DaFeiHouDiary


class TestStateMachine(unittest.TestCase):
    """状态机测试"""
    
    def setUp(self):
        self.sm = MonkeyStateMachine()
    
    def test_initial_state(self):
        self.assertEqual(self.sm.get_current_state(), MonkeyState.IDLE)
    
    def test_task_start(self):
        self.sm.trigger("task_start")
        self.assertEqual(self.sm.get_current_state(), MonkeyState.THINKING)
    
    def test_task_complete(self):
        self.sm.trigger("task_start")
        self.sm.trigger("task_complete")
        self.assertEqual(self.sm.get_current_state(), MonkeyState.HAPPY)
    
    def test_error(self):
        self.sm.trigger("task_start")
        self.sm.trigger("error")
        self.assertEqual(self.sm.get_current_state(), MonkeyState.SAD)
    
    def test_click(self):
        self.sm.trigger("click")
        self.assertEqual(self.sm.get_current_state(), MonkeyState.HAPPY)
    
    def test_poke_three_times(self):
        self.sm.poke()
        self.sm.poke()
        self.sm.poke()
        self.assertEqual(self.sm.get_current_state(), MonkeyState.ANGRY)


class TestDiary(unittest.TestCase):
    """日记测试"""
    
    def setUp(self):
        import tempfile
        self.diary = DaFeiHouDiary(Path(tempfile.mkdtemp()))
    
    def test_empty_diary(self):
        diary = self.diary.load_diary()
        self.assertEqual(len(diary["videos_watched"]), 0)
    
    def test_add_video(self):
        self.diary.add_video({
            "title": "测试视频",
            "aid": "123",
            "up_name": "测试UP",
            "play_count": 100,
        })
        diary = self.diary.load_diary()
        self.assertEqual(len(diary["videos_watched"]), 1)


if __name__ == "__main__":
    unittest.main()
