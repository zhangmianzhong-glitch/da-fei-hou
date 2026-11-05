#!/usr/bin/env python3
"""
大肥猴 — 状态栏菜单 / 点击穿透 / 键鼠感知
独立小模块，分段写入用。
"""

import time

import objc
from AppKit import (
    NSMenu, NSMenuItem, NSStatusBar, NSEvent, NSEventMaskKeyDown,
    NSEventMaskLeftMouseDown, NSEventMaskMouseMoved, NSVariableStatusItemLength,
)
from Foundation import NSObject


class BarMenuHandler(NSObject):
    """状态栏菜单回调（按 representedObject 分发到 pet 的方法）"""

    def menuItemSelected_(self, sender):
        key = sender.representedObject()
        pet = getattr(self, "pet", None)
        if pet is None:
            return
        fn = getattr(pet, "bar_action_" + str(key), None)
        if fn is not None:
            try:
                fn()
            except Exception as exc:
                print("🐒 状态栏动作出错:", exc)


class StatusBarManager:
    """菜单栏常驻图标 + 控制菜单"""

    def __init__(self, pet):
        self.pet = pet
        self.item = None
        self.menu = None
        self.handler = None

    def build(self):
        """建状态栏项"""
        try:
            self.item = NSStatusBar.systemStatusBar().statusItemWithLength_(
                NSVariableStatusItemLength)
            self.item.setTitle_("🐒")
            self.item.setToolTip_("大肥猴 — 点我打开菜单")
            self.menu = NSMenu.alloc().init()
            self.handler = BarMenuHandler.alloc().init()
            self.handler.pet = self.pet
            self.item.setMenu_(self.menu)
            self.rebuild_menu()
            return True
        except Exception as exc:
            print("🐒 状态栏不可用（无 GUI 会话?）:", exc)
            return False

    def rebuild_menu(self):
        """重建菜单项"""
        if self.menu is None:
            return
        self.menu.removeAllItems()

        def add(title, key):
            it = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, None, "")
            it.setRepresentedObject_(key)
            it.setTarget_(self.handler)
            it.setAction_("menuItemSelected:")
            self.menu.addItem_(it)

        add("🗣️ 说话", "speak")
        add("💬 打开对话栏", "chat")
        self.menu.addItem_(NSMenuItem.separatorItem())
        add("👋 摸头", "pat")
        add("🍚 喂食", "feed")
        add("🚶 出门溜达", "walk")
        self.menu.addItem_(NSMenuItem.separatorItem())
        add("🖱️ 切换点击穿透", "clickthrough")
        add("🔊 开关语音", "tts")
        self.menu.addItem_(NSMenuItem.separatorItem())
        add("❌ 下班", "quit")

    def set_icon(self, text):
        """换状态栏图标（表达当前状态）"""
        if self.item is not None:
            try:
                self.item.setTitle_(text)
            except Exception:
                pass


class ActivityWatcher:
    """
    键鼠活动感知
    - 大王敲键盘 -> 猴猴在旁边伺候
    - 大王点鼠标 -> 猴猴跳过来看
    - 鼠标移动   -> 猴猴偶尔溜达过去
    """

    def __init__(self, pet):
        self.pet = pet
        self.monitors = []
        self.last_key_at = 0.0
        self.last_click_at = 0.0
        self.last_cursor = (0.0, 0.0)
        self.cursor_moved_at = 0.0
        self.key_count = 0

    def start(self):
        """装全局监听"""
        try:
            self.monitors.append(NSEvent.addGlobalMonitorForEventsMask_handler_(
                NSEventMaskKeyDown, self._on_key))
            self.monitors.append(NSEvent.addGlobalMonitorForEventsMask_handler_(
                NSEventMaskLeftMouseDown, self._on_click))
            self.monitors.append(NSEvent.addGlobalMonitorForEventsMask_handler_(
                NSEventMaskMouseMoved, self._on_move))
            return True
        except Exception as exc:
            print("🐒 键鼠监听不可用:", exc)
            return False

    def stop(self):
        for m in self.monitors:
            try:
                NSEvent.removeMonitor_(m)
            except Exception:
                pass
        self.monitors = []

    # ---- 回调 ----
    def _on_key(self, event):
        now = time.time()
        self.last_key_at = now
        self.key_count += 1
        pet = self.pet
        if pet is not None:
            try:
                pet.on_user_typing()
            except Exception:
                pass

    def _on_click(self, event):
        now = time.time()
        self.last_click_at = now
        pet = self.pet
        if pet is not None:
            try:
                pt = NSEvent.mouseLocation()
                self.last_cursor = (pt.x, pt.y)
                pet.on_user_click()
            except Exception:
                pass

    def _on_move(self, event):
        try:
            pt = NSEvent.mouseLocation()
            self.last_cursor = (pt.x, pt.y)
            self.cursor_moved_at = time.time()
        except Exception:
            pass

    def typing_recently(self, window: float = 8.0) -> bool:
        """大王最近在敲键盘吗"""
        return (time.time() - self.last_key_at) < window

    def click_recently(self, window: float = 3.0) -> bool:
        """大王最近点过鼠标吗"""
        return (time.time() - self.last_click_at) < window

    def cursor(self):
        return self.last_cursor
