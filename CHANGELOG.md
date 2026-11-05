# 🐒 大肥猴开发日志

## 2026-11-04

### 项目启动
- 创建项目结构
- 完成 README.md 概念文档
- 完成 BILI.md B站冲浪计划
- 完成 package.json 插件配置
- 完成 config.yaml 配置文件
- 完成 host/index.js 后端插件入口
- 完成 client/index.js 前端桌宠渲染
- 完成 client/state_machine.py 状态机
- 完成 client/renderer.py 精灵渲染器
- 完成 bili/scraper.py B站冲浪器
- 完成 bili/bilibili_api.py B站API封装
- 完成 bili/diary.py 日记系统
- 完成 bili/dingtalk_notifier.py 钉钉通知
- 完成 assets/sprites/manifest.yaml 精灵配置
- 完成 assets/audio/manifest.yaml 音频配置
- 完成 main.py 主入口
- 完成 install.sh 安装脚本
- 完成 requirements.txt 依赖列表
- 完成 test/test_state_machine.py 测试

### 技术参考
- 桌宠：`dsh-pet-dafeiyu`（18种状态、3帧走路循环、物理拖拽）
- 桌面伴侣：`dsh-dafeiyu`（透明无边框窗口、实时状态）
- B站插件：`dsh-bili-whale`（自动刷站、评论、日记）
- B站API：`dsh-whale-dive`（WBI签名、内容读取）

### 下一步
- [ ] 生成大肥猴形象图片（AI 生成中）
- [ ] 录制配音（东北话+天津话）
- [ ] 实现 Playwright B站自动化
- [ ] 接入 OpenClaw 事件系统
- [ ] 测试和调试

---

*大王万岁！大肥猴永远忠于大王！* 🐒🫡

## 2026-11-05 桌面版完成

### 大肥猴 macOS 原生桌面宠物
- 新增 desktop/native/da_fei_hou.py（PyObjC 原生实现，替代 Electron）
- 透明无边框置顶窗口（NSWindowStyleMaskBorderless + NSStatusWindowLevel）
- 18 种状态精灵图，全部抠白底转透明（assets/sprites_transparent/）
- 中文语音：macOS 内置 AVSpeechSynthesizer（zh-CN，免费）
- 鼠标交互：NSView 子类接管 mouseDown/Dragged/Up + 右键菜单
- HTTP 控制接口：POST http://127.0.0.1:7788
- LaunchAgent 常驻：com.openclaw.da-fei-hou，开机自启 + 崩溃自动重启
- 启动/停止脚本：desktop/start_pet.sh 与 desktop/stop_pet.sh

### 踩坑记录（新版 PyObjC / macOS 26）
- NSSpeech 已移除，改用 AVSpeechSynthesizer + AVSpeechUtterance
- 事件掩码改为模块级 NSEventMaskLeftMouseDown 等，旧名不存在
- NSEvent.addGlobalMonitorForEventsMask_handler_ 不存在，改用 NSView 子类接管鼠标
- NSWindowCollectionBehaviorFullscreenAuxiliary 不存在
- NSImageView 没有 setIgnoresMouseEvents_，改用 hitTest_ 返回自身
- PyObjC 子类方法名会被当 selector 校验：speak(self, text) 报 BadPrototypeError
  业务逻辑放纯 Python 类，ObjC 子类只留 TickTarget / MenuHandler / PetView 桥接

## 2026-11-05 接入 OpenClaw 真实 Hook

- 新增托管 Hook：~/.openclaw/hooks/da-fei-hou/（HOOK.md + handler.js）
- 事件映射：message:received -> 挥手；message:sent -> 开心；
  command:new/reset -> 欢呼；session:auto-reset -> 待机
- 传输：Hook 通过 HTTP POST 127.0.0.1:7788 驱动本机桌宠进程
- 启用：openclaw.json 里 hooks.internal.enabled = true（开放发现，内置 hook 不丢）
- 桌宠未启动时 Hook 静默失败，不影响主流程
- 端到端实测：4 类事件均正确改变桌宠状态

## 2026-11-05 第二项：猴猴活起来了

### 修复致命 bug
- BASE 路径算错一级，精灵图目录指向 desktop/assets/sprites_transparent（不存在）
  导致 18 张图一张都没加载，桌宠其实是个空窗口。改为上两级后 sprite_loaded=true

### 接上 47 个预渲染 MP3 配音
- 新增 VoicePlayer：优先播 Edge TTS 的 MP3，缺省回退 macOS 系统中文 TTS
- VOICE_MAP 把 18 个状态映射到 14 个配音目录（heart/blink/cheer 无 MP3，回退 TTS）
- 坑：AVAudioPlayer 只有 initWithContentsOfURL_error_（返回 tuple），没有单参数版

### 三帧走路步态 + 自动溜达
- WALK_FRAMES 三帧：接地(右脚前) -> 过渡(身体上抬) -> 接地(左脚前)
- 帧间隔 0.14s，配合 1.7px/帧 的水平位移形成步态
- 自动溜达：空闲 15-40 秒起步，走 3-8 秒，到屏幕边缘反弹
- 右键菜单加了「出门溜达」，HTTP 也支持 state=walk

### 实测结果
- 14 个状态语音来源 = mp3，heart/blink/cheer = tts 回退
- sprite_loaded = true（bug 修复确认）
- 窗口位置 1230 -> 1250 -> 1204，自动行走 + 反弹正常
- walking 标志与状态切换（walk <-> idle）均正常

## 2026-11-05 第一项：B站冲浪真跑起来了

### bili/bilibili_api.py 全部换成真实实现
- WBI 签名（mixin key 混淆表 + nav 接口取密钥），实测搜索接口 code=0 返回 18 条真结果
- buvid3/buvid4 指纹自动获取（finger/spi 接口）
- 推荐流 30 条 / 热门榜 10 条 / 视频详情 / 评论 / 弹幕(实测 3543 条) / 字幕 / UP 投稿
- 点赞、投币、评论 POST 接口

### bili/login.py 真实扫码登录
- 二维码生成存 PNG（可直接发钉钉让大王扫）
- 轮询登录状态，cookies 存 data/cookies/bilibili.json（30 天有效）
- 用双重 fork 守护进程启动，避免被 exec 会话收尾杀掉

### bili/scraper.py 真实刷站
- 采集池：推荐流 30 + 热门 20 + 4 组兴趣搜索
- 六路理解：标题 + 简介 + 字幕 + 评论 + 弹幕 + 数据
- 评分：兴趣命中 0.45 + 权威UP 0.15 + 播放量 0.15 + 热词 0.15 + 评论数 0.10
- 写日报 data/report/YYYY-MM-DD.json（含钉钉文案 text 字段）
- 推桌宠表情（surprise + 拍马屁）
- 实测：12 条真视频全分析完，弹幕/评论数都是真的

### 钉钉定时汇报
- OpenClaw cron：大肥猴B站冲浪汇报
- 30 8,12,18,20 * * * (Asia/Shanghai) -> announce -> dingtalk-connector
- 投递目标已配 user:265707340624258391

### TODO 35 -> 17

## 2026-11-05 B站登录打通 + 真评论实测

- 大王扫码登录成功：zmzray / Lv4 / 923 硬币
- 踩坑：B站现版本登录态走 Set-Cookie 响应头下发，不再走 data.cookies 字段
  必须从 aiohttp cookie jar 抓 SESSDATA / bili_jct / DedeUserID
- 评论接口要带 csrf=bili_jct
- 坑：验证自己刚发的评论要用 sort=0（按时间），sort=2（按热度）会把 0 点赞的排到末尾找不到
- 实测发了两条真评论，state=0 正常显示：
  rpid 322994369840 「大王！这个视频太绝了！tmd 绝了！大肥猴给大王磕头了！🐒」
  rpid 322994382304 「大肥猴测试：大肥猴给大王请安了！🐒」
- 目标视频：从 LLM 到 Agent Skill，一期视频带你打通底层逻辑！
  https://www.bilibili.com/video/BV1E7wtzaEdq
- cookies 30 天有效，存 data/cookies/bilibili.json
