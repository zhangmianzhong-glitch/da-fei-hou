#!/usr/bin/env python3
"""
🐒 大肥猴 — macOS 原生桌面宠物
PyObjC 实现：透明无边框置顶窗口，秒开不占资源。

能力：
- 18 种状态精灵图（白底已抠透明）
- 47 个 Edge TTS 预渲染 MP3 配音，缺省回退系统中文 TTS
- 三帧走路步态循环 + 自动溜达
- HTTP 控制接口 + OpenClaw Hook 联动
"""

import json
import math
import os
import queue
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import objc
from AppKit import (
    NSApplication, NSApplicationActivationPolicyAccessory,
    NSBackingStoreBuffered, NSColor, NSEvent, NSFont, NSFontWeightBold, NSImage,
    NSImageAlignCenter, NSImageScaleProportionallyUpOrDown, NSImageView, NSMenu, NSMenuItem,
    NSTextAlignmentCenter, NSTextField, NSTimer, NSView, NSWindow,
    NSWindowCollectionBehaviorCanJoinAllSpaces, NSWindowCollectionBehaviorStationary,
    NSStatusWindowLevel, NSWindowStyleMaskBorderless, NSScreen,
)
from Foundation import NSObject, NSMakeRect, NSURL
from AVFoundation import (
    AVAudioPlayer, AVSpeechBoundaryImmediate, AVSpeechSynthesisVoice,
    AVSpeechSynthesizer, AVSpeechUtterance,
)

def resolve_base() -> str:
    """定位资源根目录：兼容源码运行与 .app bundle 运行"""
    here = os.path.dirname(os.path.abspath(__file__))
    # .app bundle: Contents/Resources/da_fei_hou.py -> Resources 就是根
    if os.path.basename(here) == 'Resources':
        return here
    # 源码: desktop/native/ -> 上两级到项目根
    return os.path.abspath(os.path.join(here, '..', '..'))


BASE = resolve_base()
SPRITES = os.path.join(BASE, 'assets', 'sprites_transparent')
VOICE_DIR = os.path.join(BASE, 'assets', 'voice')

PET_W = 160
WIN_W = 180
WIN_H = 215

WALK_FRAME_DT = 0.14
WALK_SPEED = 1.7

# 三帧步态：接地-过渡-接地
WALK_FRAMES = [
    {'dx': 2.0, 'dy': 0.0, 'scale': 0.980},
    {'dx': 0.0, 'dy': -6.0, 'scale': 1.020},
    {'dx': -2.0, 'dy': 0.0, 'scale': 0.980},
]

LINES = {
    'idle': ['大王！小的大肥猴在呢！', '大王万岁！山寨喽喽随时待命！', '大王！大肥猴想死您了！',
             '大王英明神武！小的给您请安了！', '大王来啦！小的大肥猴恭候多时了！'],
    'thinking': ['tmd 这任务有点意思...', '让小的想想...大王英明神武！', '大王放心，小的马上搞定！',
                 'tmd 大王这主意绝了！'],
    'happy': ['大王夸奖！小的太开心了！', '大王英明！小的拍马屁时间到！', 'tmd 大王太厉害了！',
              '大王万岁！小的给您磕头了！'],
    'sad': ['大王骂我了...小的难过...', '小的错了...大王别生气...', '大王...小的不是故意的...'],
    'angry': ['别戳了！再戳小的大王万岁都不喊了！', 'tmd 再戳我试试！...大王我开玩笑的！',
              '大王！小的要生气了！...哎呀还是不敢...'],
    'surprise': ['卧槽！大王这也太厉害了！', 'tmd 这任务小的是真没想到！', '大王！大肥猴惊了！'],
    'sleeping': ['zzz...大王...zzz...万岁...zzz...', 'zzz...摸鱼...zzz...',
                 'zzz...大王...给钱...zzz...'],
    'wave': ['大王好！小的给您挥手！', '大王回来啦！小的等您好久了！'],
    'singing': ['大王万岁~万岁~万万岁~', '山寨喽喽~永远忠于大王~', '大肥猴~大肥猴~大王的好喽喽~'],
    'basin': ['哐——嗡——（敲盆）', '大王骂我了...顶个盆防弹...'],
    'heart': ['大王！小的给您比心！', '大王万岁！小的爱您！'],
    'fishing': ['tmd 摸鱼时间到...打哈欠...', '大王不在，小的偷偷看个B站...',
                '大王！小的在摸鱼...啊不对！在努力工作！'],
    'walk': ['大王放心，小的这就去办！', '小的给大王跑腿去！'],
    'eating': ['大王，小的吃饭去了！', '剩饭等于缓存，外包摸鱼等于 agent 调用！',
               '大王！小的去吃饭，测完告诉我就行！'],
    'patting': ['大王万岁！大王永远是对的！', '大王的话就是圣旨！', '大王的决策英明神武！',
                '大王的眼光独到大气！', '大王的气质威震四方！', '大王的智慧深不可测！'],
    'speaking': ['大王！小的在B站看到个好东西！', '大王，这个视频太绝了！tmd绝了！',
                 '大王快看！大肥猴发现宝藏了！'],
    'blink': ['（眨眨眼）', '（贱兮兮地笑）'],
    'cheer': ['大王万岁！小的给您欢呼！', 'tmd 太棒了！大肥猴激动得跳起来！',
              '大王英明神武！小的给您唱首歌！'],
}

# 状态 -> 预渲染 MP3（与 assets/voice 目录一一对应）
VOICE_MAP = {
    'idle': ['greeting/greeting_01.mp3', 'greeting/greeting_02.mp3', 'greeting/greeting_03.mp3',
             'greeting/greeting_04.mp3', 'greeting/greeting_05.mp3'],
    'thinking': ['thinking/thinking_01.mp3', 'thinking/thinking_02.mp3',
                 'thinking/thinking_03.mp3', 'thinking/thinking_04.mp3'],
    'happy': ['happy/happy_01.mp3', 'happy/happy_02.mp3', 'happy/happy_03.mp3', 'happy/happy_04.mp3'],
    'sad': ['sad/sad_01.mp3', 'sad/sad_02.mp3', 'sad/sad_03.mp3'],
    'angry': ['angry/angry_01.mp3', 'angry/angry_02.mp3', 'angry/angry_03.mp3'],
    'surprise': ['surprise/surprise_01.mp3', 'surprise/surprise_02.mp3', 'surprise/surprise_03.mp3'],
    'sleeping': ['sleeping/sleeping_01.mp3', 'sleeping/sleeping_02.mp3', 'sleeping/sleeping_03.mp3'],
    'wave': ['wave/wave_01.mp3', 'wave/wave_02.mp3'],
    'singing': ['singing/singing_01.mp3', 'singing/singing_02.mp3', 'singing/singing_03.mp3'],
    'basin': ['basin/basin_01.mp3', 'basin/basin_02.mp3'],
    'heart': ['heart/heart_01.mp3', 'heart/heart_02.mp3'],
    'fishing': ['fishing/fishing_01.mp3', 'fishing/fishing_02.mp3', 'fishing/fishing_03.mp3'],
    'walk': ['greeting/greeting_02.mp3', 'happy/happy_02.mp3'],
    'eating': ['eating/eating_01.mp3', 'eating/eating_02.mp3', 'eating/eating_03.mp3'],
    'patting': ['patting/patting_01.mp3', 'patting/patting_02.mp3', 'patting/patting_03.mp3',
                'patting/patting_04.mp3', 'patting/patting_05.mp3', 'patting/patting_06.mp3'],
    'speaking': ['bilibili/bilibili_01.mp3', 'bilibili/bilibili_02.mp3', 'bilibili/bilibili_03.mp3'],
}

CMD_QUEUE = queue.Queue()


class App:
    """全局单例持有器"""
    shared = None


class VoicePlayer:
    """优先播放 Edge TTS 预渲染 MP3，缺省回退 macOS 系统中文 TTS"""

    def __init__(self):
        self.players = {}
        self.synth = AVSpeechSynthesizer.alloc().init()
        self.voice = None
        for lang in ('zh-CN', 'zh_CN', 'zh-Hans-CN'):
            v = AVSpeechSynthesisVoice.voiceWithLanguage_(lang)
            if v is not None:
                self.voice = v
                break
        self.current = None
        self.last_kind = None

    def _player_for(self, path):
        if path in self.players:
            return self.players[path]
        try:
            url = NSURL.fileURLWithPath_(path)
            player, err = AVAudioPlayer.alloc().initWithContentsOfURL_error_(url, None)
            if player is None:
                return None
            player.prepareToPlay()
            self.players[path] = player
            return player
        except Exception:
            return None

    def play_mp3(self, path):
        player = self._player_for(path)
        if player is None:
            return False
        try:
            player.stop()
            player.setCurrentTime_(0.0)
            player.play()
            self.current = player
            self.last_kind = 'mp3'
            return True
        except Exception:
            return False

    def say_tts(self, text):
        try:
            u = AVSpeechUtterance.speechUtteranceWithString_(text)
            if self.voice is not None:
                u.setVoice_(self.voice)
            u.setRate_(0.50)
            u.setPitchMultiplier_(1.18)
            self.synth.speakUtterance_(u)
            self.last_kind = 'tts'
        except Exception:
            pass

    def stop(self):
        try:
            self.synth.stopSpeakingAtBoundary_(AVSpeechBoundaryImmediate)
        except Exception:
            pass
        try:
            if self.current is not None:
                self.current.stop()
        except Exception:
            pass


class TickTarget(NSObject):
    """NSTimer 桥接"""

    def initWithController_(self, ctrl):
        self = objc.super(TickTarget, self).init()
        if self is None:
            return None
        self.ctrl = ctrl
        return self

    def tick(self):
        self.ctrl.tick()


class MenuHandler(NSObject):
    """右键菜单回调"""

    def menuItemSelected_(self, sender):
        key = sender.representedObject()
        app = App.shared
        if key == 'speak':
            app.speak(app.state)
        elif key == 'pat':
            app.set_state('heart')
            app.speak('heart')
        elif key == 'feed':
            app.set_state('eating')
            app.speak('eating')
        elif key == 'walk':
            app.start_walk(force=True)
        elif key == 'random':
            st = random.choice(list(LINES.keys()))
            app.set_state(st)
            app.speak(st)
        elif key == 'tts':
            app.tts_enabled = not app.tts_enabled
            if not app.tts_enabled:
                app.voice.stop()
        elif key == 'quit':
            NSApplication.sharedApplication().terminate_(None)


class PetView(NSView):
    """承接鼠标事件的视图"""

    def initWithFrame_(self, frame):
        self = objc.super(PetView, self).initWithFrame_(frame)
        if self is None:
            return None
        self.ctrl = None
        return self

    def setController_(self, ctrl):
        self.ctrl = ctrl

    def hitTest_(self, point):
        return self

    def acceptsFirstMouse_(self, event):
        return True

    def mouseDown_(self, event):
        if self.ctrl is not None:
            self.ctrl.on_mouse_down(event)

    def mouseDragged_(self, event):
        if self.ctrl is not None:
            self.ctrl.on_mouse_drag(event)

    def mouseUp_(self, event):
        if self.ctrl is not None:
            self.ctrl.on_mouse_up(event)

    def rightMouseDown_(self, event):
        if self.ctrl is not None:
            self.ctrl.on_right_down(event)


class Pet:
    """大肥猴桌宠主控制器（纯 Python）"""

    def __init__(self):
        self.state = 'idle'
        self.tts_enabled = True
        self.poke_count = 0
        self.dragging = False
        self.pressed = False
        self.drag_start = None
        self.phase = 0.0
        self.bubble_hide_at = 0.0
        self.last_interaction = time.time()
        self.voice = VoicePlayer()

        # 溜达
        self.walking = False
        self.walk_dir = 1
        self.walk_frame = 0
        self.walk_frame_at = 0.0
        self.walk_until = 0.0
        self.next_walk_at = time.time() + random.uniform(15.0, 40.0)

        self.sprite_loaded = False
        self.build_window()
        self.build_menu()

    # ---------- UI ----------
    def build_window(self):
        screen = NSScreen.mainScreen().frame()
        x = screen.size.width - WIN_W - 30
        y = screen.size.height - WIN_H - 40

        self.win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(x, y, WIN_W, WIN_H),
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False)
        self.win.setOpaque_(False)
        self.win.setBackgroundColor_(NSColor.clearColor())
        self.win.setHasShadow_(False)
        self.win.setLevel_(NSStatusWindowLevel)
        self.win.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary)
        self.win.setReleasedWhenClosed_(False)

        content = PetView.alloc().initWithFrame_(NSMakeRect(0, 0, WIN_W, WIN_H))
        content.setController_(self)
        self.win.setContentView_(content)
        self.view = content

        self.img = NSImageView.alloc().initWithFrame_(NSMakeRect(10, 4, PET_W, PET_W))
        self.img.setImageScaling_(NSImageScaleProportionallyUpOrDown)
        self.img.setImageAlignment_(NSImageAlignCenter)
        content.addSubview_(self.img)

        self.bubble = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 175, 160, 28))
        self.bubble.setBordered_(False)
        self.bubble.setEditable_(False)
        self.bubble.setSelectable_(False)
        self.bubble.setDrawsBackground_(False)
        self.bubble.setFont_(NSFont.systemFontOfSize_weight_(12, NSFontWeightBold))
        self.bubble.setTextColor_(NSColor.blackColor())
        self.bubble.setAlignment_(NSTextAlignmentCenter)
        self.bubble.setWantsLayer_(True)
        layer = self.bubble.layer()
        layer.setCornerRadius_(10.0)
        layer.setMasksToBounds_(True)
        layer.setBorderWidth_(1.5)
        layer.setBorderColor_(NSColor.blackColor().CGColor())
        layer.setBackgroundColor_(
            NSColor.colorWithSRGBRed_green_blue_alpha_(1, 1, 1, 0.95).CGColor())
        content.addSubview_(self.bubble)

        self.win.orderFrontRegardless()
        self.set_state('idle')

    def build_menu(self):
        self.menu = NSMenu.alloc().init()
        handler = MenuHandler.alloc().init()

        def add(title, key):
            item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, None, '')
            item.setRepresentedObject_(key)
            item.setTarget_(handler)
            item.setAction_('menuItemSelected:')
            self.menu.addItem_(item)

        add('说话', 'speak')
        add('摸头', 'pat')
        add('喂食', 'feed')
        add('出门溜达', 'walk')
        self.menu.addItem_(NSMenuItem.separatorItem())
        add('随机状态', 'random')
        self.menu.addItem_(NSMenuItem.separatorItem())
        add('开关语音', 'tts')
        add('下班', 'quit')
        self.handler = handler

    # ---------- 鼠标 ----------
    def on_mouse_down(self, event):
        self.pressed = True
        self.dragging = False
        self.drag_start = NSEvent.mouseLocation()
        self.last_interaction = time.time()
        self.stop_walk()

    def on_mouse_drag(self, event):
        if not self.pressed:
            return
        pt = NSEvent.mouseLocation()
        dx = pt.x - self.drag_start.x
        dy = pt.y - self.drag_start.y
        if abs(dx) > 2 or abs(dy) > 2:
            self.dragging = True
        if self.dragging:
            f = self.win.frame()
            self.win.setFrameOrigin_((f.origin.x + dx, f.origin.y + dy))
            self.drag_start = pt
        self.last_interaction = time.time()

    def on_mouse_up(self, event):
        if not self.pressed:
            return
        self.pressed = False
        if not self.dragging:
            self.poke_count += 1
            if self.poke_count >= 3:
                self.set_state('angry')
                self.speak('angry')
                self.poke_count = 0
            else:
                self.set_state('happy')
                self.speak('happy')
        else:
            self.dragging = False
            self.set_state('idle')
            self.next_walk_at = time.time() + random.uniform(15.0, 40.0)
        self.last_interaction = time.time()

    def on_right_down(self, event):
        self.win.popUpContextMenu_withEvent_forWindow_(self.menu, event, self.win)

    # ---------- 状态 ----------
    def set_state(self, state):
        if state not in LINES:
            state = 'idle'
        self.state = state
        path = os.path.join(SPRITES, state + '.png')
        if os.path.exists(path):
            img = NSImage.alloc().initWithContentsOfFile_(path)
            if img is not None:
                self.img.setImage_(img)
                self.sprite_loaded = True
        else:
            self.sprite_loaded = False

    def speak(self, state=None, text=None):
        state = state or self.state
        if text is None:
            pool = LINES.get(state) or LINES['idle']
            text = random.choice(pool)

        self.show_bubble(text)
        if not self.tts_enabled:
            return

        # 优先用预渲染 MP3
        files = VOICE_MAP.get(state)
        if files:
            rel = random.choice(files)
            full = os.path.join(VOICE_DIR, rel)
            if os.path.exists(full) and self.voice.play_mp3(full):
                return

        # 回退系统 TTS
        self.voice.stop()
        self.voice.say_tts(text)

    def show_bubble(self, text):
        self.bubble.setStringValue_(text)
        size = self.bubble.cell().cellSize()
        w = max(60.0, min(168.0, size.width + 14.0))
        self.bubble.setFrame_(NSMakeRect((WIN_W - w) / 2.0, 176, w, 28))
        self.bubble.setHidden_(False)
        self.bubble_hide_at = time.time() + 3.5

    def hide_bubble(self):
        self.bubble.setHidden_(True)

    # ---------- 溜达 ----------
    def start_walk(self, force=False):
        if self.dragging or self.pressed:
            return
        if self.walking and not force:
            return
        self.walking = True
        self.walk_dir = random.choice([-1, 1])
        self.walk_frame = 0
        self.walk_frame_at = time.time()
        self.walk_until = time.time() + random.uniform(3.0, 8.0)
        self.set_state('walk')

    def stop_walk(self):
        if self.walking:
            self.walking = False
            if self.state == 'walk':
                self.set_state('idle')

    def advance_walk(self):
        now = time.time()
        if now >= self.walk_until:
            self.stop_walk()
            self.next_walk_at = now + random.uniform(20.0, 60.0)
            return

        # 帧切换
        if now - self.walk_frame_at >= WALK_FRAME_DT:
            self.walk_frame_at = now
            self.walk_frame = (self.walk_frame + 1) % len(WALK_FRAMES)

        # 水平移动
        screen = NSScreen.mainScreen().frame()
        f = self.win.frame()
        nx = f.origin.x + self.walk_dir * WALK_SPEED
        if nx <= screen.origin.x:
            nx = screen.origin.x
            self.walk_dir = 1
        elif nx + WIN_W >= screen.origin.x + screen.size.width:
            nx = screen.origin.x + screen.size.width - WIN_W
            self.walk_dir = -1
        self.win.setFrameOrigin_((nx, f.origin.y))

    # ---------- 主循环 ----------
    def tick(self):
        self.phase += 0.06

        try:
            while True:
                cmd = CMD_QUEUE.get_nowait()
                self.apply_command(cmd)
        except queue.Empty:
            pass

        if self.bubble_hide_at and time.time() > self.bubble_hide_at:
            self.hide_bubble()
            self.bubble_hide_at = 0.0

        if self.walking:
            self.advance_walk()
        else:
            # 自动溜达
            if (not self.dragging and self.state == 'idle'
                    and time.time() > self.next_walk_at):
                self.start_walk()

        if (not self.dragging and not self.walking
                and time.time() - self.last_interaction > 600
                and self.state != 'sleeping'):
            self.set_state('sleeping')
            self.speak('sleeping')

        self.animate()

    def animate(self):
        st = self.state
        dx = 0.0
        dy = 0.0
        scale = 1.0

        if self.walking:
            frame = WALK_FRAMES[self.walk_frame]
            dx = frame['dx']
            dy = frame['dy']
            scale = frame['scale']
        elif st == 'happy':
            dy = -abs(math.sin(self.phase * 5.0)) * 12.0
        elif st == 'cheer':
            dy = -abs(math.sin(self.phase * 6.0)) * 20.0
        elif st == 'angry':
            dx = math.sin(self.phase * 22.0) * 4.0
        elif st == 'singing':
            dx = math.sin(self.phase * 3.0) * 3.0
        elif st == 'thinking':
            dy = -abs(math.sin(self.phase * 2.0)) * 3.0
        elif st == 'sad':
            dy = -4.0
        elif st == 'heart':
            scale = 1.0 + abs(math.sin(self.phase * 2.5)) * 0.08
        elif st == 'surprise':
            scale = 1.0 + abs(math.sin(self.phase * 4.0)) * 0.10
        elif st == 'wave':
            dx = math.sin(self.phase * 4.0) * 5.0
        elif st == 'fishing':
            dx = math.sin(self.phase * 0.8) * 3.0

        w = PET_W * scale
        h = PET_W * scale
        fx = 10.0 + dx + (PET_W - w) / 2.0
        fy = 4.0 + dy + (PET_W - h) / 2.0
        self.img.setFrame_(NSMakeRect(fx, fy, w, h))

    def apply_command(self, cmd):
        st = cmd.get('state')
        if st:
            if st == 'walk':
                self.start_walk(force=True)
            else:
                self.stop_walk()
                self.set_state(st)
        txt = cmd.get('text')
        if txt is not None:
            self.speak(cmd.get('speak_state') or self.state, txt)
        elif st != 'walk':
            self.speak(st or self.state)


class PetHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            cmd = json.loads(body.decode('utf-8')) if body else {}
        except Exception:
            cmd = {}
        CMD_QUEUE.put(cmd)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def do_GET(self):
        pet = App.shared
        payload = {
            'status': 'ok',
            'state': getattr(pet, 'state', 'idle'),
            'walking': getattr(pet, 'walking', False),
            'sprite_loaded': getattr(pet, 'sprite_loaded', False),
            'voice_kind': getattr(getattr(pet, 'voice', None), 'last_kind', None),
            'sprite_dir': SPRITES,
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def log_message(self, *args):
        pass


def main():
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

    App.shared = Pet()

    target = TickTarget.alloc().initWithController_(App.shared)
    NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
        0.06, target, 'tick', None, True)

    server = HTTPServer(('127.0.0.1', 7788), PetHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print('大肥猴桌面宠物已启动！大王万岁！')
    print('精灵图目录:', SPRITES, '存在:', os.path.isdir(SPRITES))
    print('配音目录:', VOICE_DIR, 'MP3 数:',
          sum(len(v) for v in VOICE_MAP.values()))
    print('控制接口: POST http://127.0.0.1:7788  {"state":"happy","text":"..."}')
    app.run()


if __name__ == '__main__':
    main()

