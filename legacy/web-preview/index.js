// 大肥猴 — 前端桌宠渲染
// Browser half for OpenClaw Web UI

// 18种状态精灵图
const STATES = {
  idle:       { url: '/api/da-fei-hou/asset/sprites/idle.png', facing: 1 },
  blink:      { url: '/api/da-fei-hou/asset/sprites/blink.png', facing: 1 },
  walk_right: { url: '/api/da-fei-hou/asset/sprites/walk-right.png', facing: 1 },
  walk_left:  { url: '/api/da-fei-hou/asset/sprites/walk-left.png', facing: -1 },
  happy:      { url: '/api/da-fei-hou/asset/sprites/happy.png', facing: 1 },
  cheer:      { url: '/api/da-fei-hou/asset/sprites/cheer.png', facing: 1 },
  speaking:   { url: '/api/da-fei-hou/asset/sprites/speaking.png', facing: 1 },
  thinking:   { url: '/api/da-fei-hou/asset/sprites/thinking.png', facing: 1 },
  heart:      { url: '/api/da-fei-hou/asset/sprites/heart.png', facing: 1 },
  sad:        { url: '/api/da-fei-hou/asset/sprites/sad.png', facing: 1 },
  angry:      { url: '/api/da-fei-hou/asset/sprites/angry.png', facing: 1 },
  surprise:   { url: '/api/da-fei-hou/asset/sprites/surprise.png', facing: 1 },
  sleeping:   { url: '/api/da-fei-hou/asset/sprites/sleeping.png', facing: 1 },
  wave:       { url: '/api/da-fei-hou/asset/sprites/wave.png', facing: 1 },
  singing:    { url: '/api/da-fei-hou/asset/sprites/singing.png', facing: 1 },
  basin:      { url: '/api/da-fei-hou/asset/sprites/basin.png', facing: 1 },
  eating:     { url: '/api/da-fei-hou/asset/sprites/eating.png', facing: 1 },
  fishing:    { url: '/api/da-fei-hou/asset/sprites/fishing.png', facing: 1 },  // 摸鱼
};

// 配音台词
const LINES = {
  greeting: [
    "大王！小的大肥猴在呢！😝",
    "大王万岁！山寨喽喽随时待命！🫡",
    "大王来啦！小的给您磕头了！🙇",
  ],
  thinking: [
    "tmd 这任务有点意思...",
    "让小的想想...大王英明神武！🤔",
    "大王放心，小的马上搞定！💪",
  ],
  happy: [
    "大王夸奖！小的太开心了！🎉",
    "大王英明！小的拍马屁时间到！👏",
    "大王万岁！小的给您唱首歌！🎵",
  ],
  sad: [
    "大王骂我了...小的难过...😢",
    "小的错了...大王别生气...🙏",
  ],
  angry: [
    "别戳了！再戳小的大王万岁都不喊了！😤",
    "tmd 再戳我试试！...大王我开玩笑的！😰",
  ],
  surprise: [
    "卧槽！大王这也太厉害了！😲",
    "tmd 这任务小的是真没想到！🤯",
  ],
  sleeping: [
    "zzz...大王...zzz...万岁...zzz...",
    "zzz...摸鱼...zzz...",
  ],
  wave: [
    "大王好！小的给您挥手！👋",
    "大王回来啦！小的等您好久了！😊",
  ],
  singing: [
    "大王万岁~万岁~万万岁~🎵",
    "山寨喽喽~永远忠于大王~🎵",
  ],
  basin: [
    "哐——嗡——（敲盆）",
    "大王骂我了...顶个盆防弹...🪈",
  ],
  eating: [
    "大王，小的吃饭去了！🍚",
    "剩饭 = 缓存，外包摸鱼 = agent 调用！🍜",
  ],
  fishing: [
    "tmd 摸鱼时间到...打哈欠...😴",
    "大王不在，小的偷偷看个B站...📱",
  ],
  bilibili: [
    "大王！小的在B站看到个好东西！📺",
    "大王，这个视频太绝了！tmd 绝了！🎬",
  ],
};

// 音效
const SFX = {
  click: '/api/da-fei-hou/asset/sfx/click.mp3',
  drag: '/api/da-fei-hou/asset/sfx/drag.mp3',
  drop: '/api/da-fei-hou/asset/sfx/drop.mp3',
  sparkle: '/api/da-fei-hou/asset/sfx/sparkle.mp3',
  heart: '/api/da-fei-hou/asset/sfx/heart.mp3',
  pat: '/api/da-fei-hou/asset/sfx/pat.mp3',  // 拍马屁
};

// 背景音乐
const BGM = '/api/da-fei-hou/asset/bgm/loop.mp3';

// 大肥猴控制器
class DaFeiHouController {
  constructor(config) {
    this.config = config;
    this.state = 'idle';
    this.position = { x: 0, y: 0 };
    this.isDragging = false;
    this.isDropping = false;
    this.pokeCount = 0;
    this.pokeTimer = null;
    this.speechQueue = [];
    this.audioCtx = null;
    
    this.init();
  }
  
  init() {
    // 创建 DOM
    this.el = document.createElement('div');
    this.el.className = 'da-fei-hou';
    this.el.style.cssText = `
      position: fixed;
      width: ${this.config.size}px;
      height: ${this.config.size}px;
      cursor: grab;
      user-select: none;
      z-index: 999999;
      transition: transform 0.1s;
    `;
    
    // 精灵图
    this.sprite = document.createElement('img');
    this.sprite.src = STATES[this.state].url;
    this.sprite.style.cssText = `
      width: 100%;
      height: 100%;
      image-rendering: pixelated;
    `;
    this.el.appendChild(this.sprite);
    
    // 气泡
    this.bubble = document.createElement('div');
    this.bubble.className = 'da-fei-hou-bubble';
    this.bubble.style.cssText = `
      position: absolute;
      top: -40px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(255,255,255,0.9);
      border-radius: 12px;
      padding: 8px 12px;
      font-size: 12px;
      white-space: nowrap;
      display: none;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    `;
    this.el.appendChild(this.bubble);
    
    // 初始位置
    this.position.x = window.innerWidth - this.config.size - 20;
    this.position.y = window.innerHeight - this.config.size - 20;
    this.el.style.left = `${this.position.x}px`;
    this.el.style.top = `${this.position.y}px`;
    
    // 事件绑定
    this.el.addEventListener('mousedown', (e) => this.onDragStart(e));
    this.el.addEventListener('click', (e) => this.onClick(e));
    this.el.addEventListener('mouseenter', (e) => this.onHover(e));
    
    document.body.appendChild(this.el);
    
    // 启动状态机
    this.startStateMachine();
    
    console.log('🐒 大肥猴已上线！大王万岁！');
  }
  
  // 切换状态
  setState(newState, duration) {
    const prevState = this.state;
    this.state = newState;
    this.sprite.src = STATES[newState].url;
    
    // 镜像方向
    const facing = STATES[newState].facing;
    this.sprite.style.transform = facing < 0 ? 'scaleX(-1)' : '';
    
    if (duration) {
      setTimeout(() => {
        this.state = prevState;
        this.sprite.src = STATES[prevState].url;
      }, duration);
    }
  }
  
  // 说话
  speak(category) {
    const lines = LINES[category];
    if (!lines || lines.length === 0) return;
    
    const line = lines[Math.floor(Math.random() * lines.length)];
    this.bubble.textContent = line;
    this.bubble.style.display = 'block';
    
    this.setState('speaking', line.length * 200);
    
    // 播放配音
    this.playVoice(category, line);
    
    setTimeout(() => {
      this.bubble.style.display = 'none';
    }, line.length * 200);
  }
  
  // 播放配音
  playVoice(category, text) {
    // TODO: 接入 TTS 或预渲染语音
    console.log(`🐒 大肥猴说：${text}`);
  }
  
  // 播放音效
  playSfx(name) {
    const audio = new Audio(SFX[name]);
    audio.volume = this.config.sound_effects?.volume / 100 || 0.6;
    audio.play().catch(() => {});
  }
  
  // 拖拽
  onDragStart(e) {
    this.isDragging = true;
    this.el.style.cursor = 'grabbing';
    this.playSfx('drag');
    
    const startX = e.clientX - this.position.x;
    const startY = e.clientY - this.position.y;
    
    const onMove = (e) => {
      this.position.x = e.clientX - startX;
      this.position.y = e.clientY - startY;
      this.el.style.left = `${this.position.x}px`;
      this.el.style.top = `${this.position.y}px`;
    };
    
    const onUp = () => {
      this.isDragging = false;
      this.el.style.cursor = 'grab';
      this.playSfx('drop');
      
      // 落地动画
      this.setState('happy', 1000);
      
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    };
    
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }
  
  // 点击
  onClick(e) {
    this.pokeCount++;
    
    if (this.pokeCount >= 3) {
      // 戳三下 → 生气
      this.setState('angry', 3000);
      this.speak('angry');
      this.pokeCount = 0;
    } else {
      // 点击 → 唤醒
      this.setState('happy', 1000);
      this.speak('greeting');
      this.playSfx('click');
    }
    
    clearTimeout(this.pokeTimer);
    this.pokeTimer = setTimeout(() => { this.pokeCount = 0; }, 2000);
  }
  
  // 悬停
  onHover(e) {
    // 显示工具栏
  }
  
  // 状态机
  startStateMachine() {
    // 自动走路
    if (this.config.behavior?.auto_walk) {
      setInterval(() => {
        if (this.state === 'idle') {
          this.setState('walk_right', 3000);
        }
      }, 15000);
    }
    
    // 眨眼
    setInterval(() => {
      if (this.state === 'idle') {
        this.setState('blink', 500);
      }
    }, 3000 + Math.random() * 5000);
    
    // 小动作
    if (this.config.behavior?.fidget) {
      setInterval(() => {
        if (this.state === 'idle') {
          const actions = ['thinking', 'basin', 'eating', 'singing', 'cheer', 'heart', 'angry'];
          const action = actions[Math.floor(Math.random() * actions.length)];
          this.setState(action, 2000);
          this.speak(action);
        }
      }, 30000 + Math.random() * 60000);
    }
    
    // 主动搭话
    if (this.config.behavior?.proactive) {
      setInterval(() => {
        if (this.state === 'idle') {
          this.speak('greeting');
        }
      }, 120000 + Math.random() * 180000);
    }
    
    // 睡觉（长时间无人）
    let lastInteraction = Date.now();
    setInterval(() => {
      if (Date.now() - lastInteraction > 600000 && this.state !== 'sleeping') {  // 10分钟
        this.setState('sleeping');
        this.speak('sleeping');
      }
    }, 60000);
  }
  
  // OpenClaw 事件监听
  onTaskStart(task) {
    this.setState('thinking');
    this.speak('thinking');
  }
  
  onTaskComplete(task) {
    this.setState('happy');
    this.speak('happy');
  }
  
  onError(error) {
    this.setState('sad');
    this.speak('sad');
  }
  
  onBilibiliFound(video) {
    this.setState('surprise');
    this.speak('bilibili');
  }
}

// 导出
if (typeof module !== 'undefined') {
  module.exports = { DaFeiHouController, STATES, LINES, SFX };
}
