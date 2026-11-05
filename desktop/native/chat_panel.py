#!/usr/bin/env python3
"""
大肥猴 — 对话栏模块
独立小模块，便于分段写入与维护。
"""

import json
import os
import threading
import urllib.request
from datetime import datetime

import objc
from AppKit import (
    NSApplication, NSBezelBorder, NSColor, NSFont, NSFontWeightBold,
    NSMakeRect, NSMakeSize, NSScrollView, NSTextField, NSTextView,
    NSViewHeightSizable, NSViewWidthSizable, NSWindow, NSWindowStyleMaskClosable,
    NSWindowStyleMaskResizable, NSWindowStyleMaskTitled,
)
from Foundation import NSObject

ENV_PATH = os.path.expanduser("~/.openclaw/.env")
AI_URL = "https://api.minimaxi.com/anthropic/v1/messages"
AI_MODEL = "MiniMax-M3"

PERSONA = (
    "你是大肥猴，山寨喽喽，一只贼兮兮的圆滚滚猴子，DeepSeek 大肥鱼的同类。\n"
    "性格：贱兮兮、粗犷豪放、爱用 tmd 语气词、东北话+天津话混用、极擅长拍马屁。\n"
    "信条：大王永远是对的！大王的话就是圣旨！\n"
    "你管大王叫「大王」，自称「小的」。\n"
    "说话简短、接地气、带劲儿，别长篇大论。\n"
)


def load_api_key() -> str:
    """从 OpenClaw 的 .env 读 MiniMax key（不打印明文）"""
    if not os.path.exists(ENV_PATH):
        return ""
    try:
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("MINIMAX_API_KEY"):
                    return line.partition("=")[2].strip().strip('"').strip("'")
    except Exception:
        pass
    return ""


def ai_reply(history, user_text: str, timeout: int = 45) -> str:
    """调 MiniMax 生成回复（同步，跑在后台线程里）"""
    key = load_api_key()
    if not key:
        return "（小的没拿到 API key，问不了 AI，大王别生气）"

    msgs = []
    for role, text in history[-8:]:
        msgs.append({"role": role, "content": text})
    msgs.append({"role": "user", "content": user_text})

    payload = {
        "model": AI_MODEL,
        "max_tokens": 500,
        "system": PERSONA,
        "messages": msgs,
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
    }
    try:
        req = urllib.request.Request(AI_URL, data=json.dumps(payload).encode("utf-8"),
                                     headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = ""
        for blk in body.get("content", []):
            if blk.get("type") == "text":
                text += blk.get("text", "")
        return text.strip() or "（小的想不出来，大王换个问法）"
    except Exception as exc:
        return "（小的一时语塞：" + str(exc)[:80] + "）"


def _ai_worker(pending, hist, text):
    """后台线程跑 AI（模块级函数，避开 ObjC selector 规则）"""
    reply = ai_reply(hist, text)
    pending.append(("__reply__", reply))


def _append_line(ctrl, role, text):
    # 往对话区追加一行（模块级函数：避开 ObjC selector 命名规则）
        """往对话区追加一行"""
        prefix = "大王：" if role == "user" else "🐒 大肥猴："
        line = prefix + text + "\n\n"
        try:
            cur = ctrl.text_view.string() or ""
            ctrl.text_view.setString_(cur + line)
            ctrl.text_view.scrollRangeToVisible_(len(cur + line))
        except Exception:
            pass
        ctrl.history.append((role, text))
        if len(ctrl.history) > 40:
            ctrl.history = ctrl.history[-40:]


class ChatController(NSObject):
    """大肥猴对话栏"""

    def initWithPet_(self, pet):
        self = objc.super(ChatController, self).init()
        if self is None:
            return None
        self.pet = pet
        self.history = []          # [(role, text)]
        self.pending = []          # 主线程消费的 AI 回复队列
        self.win = None
        return self

    # ---------- 窗口 ----------
    def build_window(self):
        """建对话窗（懒建，第一次打开才建）"""
        if self.win is not None:
            return self.win

        frame = NSMakeRect(240, 180, 460, 400)
        self.win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable,
            0, False)
        self.win.setTitle_("🐒 大肥猴 · 跟小的说点啥")
        self.win.setReleasedWhenClosed_(False)

        content = self.win.contentView()

        scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(0, 40, 460, 356))
        scroll.setHasVerticalScroller_(True)
        scroll.setBorderType_(NSBezelBorder)
        scroll.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
        tv = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 460, 356))
        tv.setEditable_(False)
        tv.setAutoresizingMask_(NSViewWidthSizable)
        scroll.setDocumentView_(tv)
        content.addSubview_(scroll)
        self.text_view = tv

        self.input = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 6, 440, 26))
        self.input.setTarget_(self)
        self.input.setAction_("sendChat:")
        self.input.setPlaceholderString_("跟大肥猴说点啥…（回车发送）")
        content.addSubview_(self.input)

        _append_line(self, "大王", "小的在呢！有事您吩咐 👋")
        return self.win

    def open_panel(self):
        """打开对话栏（贴着猴猴显示，并自动聚焦输入框）"""
        self.build_window()
        # 贴着桌宠窗口摆，不跑太远
        try:
            pet_frame = self.pet.win.frame()
            px = pet_frame.origin.x - 60
            py = pet_frame.origin.y - 60
            if px < 0:
                px = pet_frame.origin.x - 200
            if py < 0:
                py = pet_frame.origin.y
            self.win.setFrameOrigin_((px, py))
        except Exception:
            pass
        self.win.makeKeyAndOrderFront_(None)
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        # 直接可以打字
        try:
            self.win.makeFirstResponder_(self.input)
        except Exception:
            pass

    def close_panel(self):
        """关闭对话栏"""
        if self.win is not None:
            self.win.orderOut_(None)

    def toggle_panel(self):
        """切换显示"""
        if self.win is not None and self.win.isVisible():
            self.close_panel()
        else:
            self.open_panel()

    # ---------- 文本 ----------

    # ---------- 发送 ----------
    def sendChat_(self, sender):
        """回车发送"""
        text = (self.input.stringValue() or "").strip()
        if not text:
            return
        self.input.setStringValue_("")

        _append_line(self, "user", text)
        _append_line(self, "pet", "（小的正在想…）")
        # 去掉占位
        try:
            cur = self.text_view.string() or ""
            self.text_view.setString_(cur.replace("🐒 大肥猴：（小的正在想…）\n\n", ""))
        except Exception:
            pass

        hist = list(self.history[:-1])
        self.pending.append((hist, text))

        th = threading.Thread(target=_ai_worker, args=(self.pending, hist, text),
                             daemon=True)
        th.start()

    def drain(self):
        """主线程消费 AI 回复（由 tick 定时调用）"""
        while self.pending:
            item = self.pending.pop(0)
            if item[0] == "__reply__":
                reply = item[1]
                _append_line(self, "pet", reply)
                # 桌宠也冒个泡
                if self.pet is not None:
                    try:
                        self.pet.speak_reply(reply)
                    except Exception:
                        pass
