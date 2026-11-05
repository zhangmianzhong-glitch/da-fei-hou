/*
 * 大肥猴桌宠动画系统
 * 支持 18 种状态 + 动画 + 物理效果 + 配音
 */

// 导入配置
import { DaFeiHouConfig } from './config.js';

// 大肥猴桌宠类
export class DaFeiHouPet {
  constructor(options = {}) {
    this.config = { ...DaFeiHouConfig, ...options };
    this.state = 'idle';
    this.position = { x: 0, y: 0 };
    this.isDragging = false;
    this.isAnimating = false;
    this.currentFrame = 0;
    this.animationFrames = [];
    this.animationTimer = null;
    this.audioPlayer = null;
    this.speechBubble = null;
    
    this.init();
  }
  
  // 初始化
  init() {
    // 创建 DOM 结构
    this.createPetElement();
    this.createBubbleElement();
    
    // 初始化位置
    this.position.x = window.innerWidth - this.config.size - 20;
    this.position.y = window.innerHeight - this.config.size - 20;
    this.updatePosition();
    
    // 绑定事件
    this.bindEvents();
    
    // 启动动画循环
    this.startAnimationLoop();
    
    console.log('🐒 大肥猴桌宠已上线！大王万岁！');
  }
  
  // 创建桌宠元素
  createPetElement() {
    this.el = document.createElement('div');
    this.el.className = 'da-fei-hou-pet';
    this.el.style.cssText = `
      position: fixed;
      width: ${this.config.size}px;
      height: ${this.config.size}px;
      cursor: grab;
      user-select: none;
      z-index: 999999;
      transition: transform 0.1s ease-out;
      pointer-events: auto;
    `;
    
    // 精灵图容器
    this.spriteContainer = document.createElement('div');
    this.spriteContainer.className = 'da-fei-hou-sprite';
    this.spriteContainer.style.cssText = `
      width: 100%;
      height: 100%;
      background-size: contain;
      background-repeat: no-repeat;
      background-position: center;
      image-rendering: -webkit-optimize-contrast;
      image-rendering: crisp-edges;
    `;
    
    this.el.appendChild(this.spriteContainer);
    document.body.appendChild(this.el);
    
    // 加载初始状态
    this.loadState('idle');
  }
  
  // 创建对话气泡
  createBubbleElement() {
    this.speechBubble = document.createElement('div');
    this.speechBubble.className = 'da-fei-hou-bubble';
    this.speechBubble.style.cssText = `
      position: absolute;
      top: -50px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(255, 255, 255, 0.95);
      border: 2px solid #333;
      border-radius: 12px;
      padding: 8px 16px;
      font-size: 14px;
      font-weight: bold;
      color: #333;
      white-space: nowrap;
      display: none;
      box-shadow: 0 2px 12px rgba(0,0,0,0.15);
      pointer-events: none;
      z-index: 1000000;
    `;
    
    // 气泡小三角
    const arrow = document.createElement('div');
    arrow.style.cssText = `
      position: absolute;
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%);
      width: 0;
      height: 0;
      border-left: 8px solid transparent;
      border-right: 8px solid transparent;
      border-top: 8px solid #333;
    `;
    
    this.speechBubble.appendChild(arrow);
    this.el.appendChild(this.speechBubble);
  }
  
  // 加载状态
  async loadState(stateName) {
    const stateConfig = this.config.states[stateName];
    if (!stateConfig) {
      console.warn(`️ 状态不存在：${stateName}`);
      return;
    }
    
    this.state = stateName;
    this.currentFrame = 0;
    
    // 加载精灵图
    if (stateConfig.frames && stateConfig.frames.length > 0) {
      this.animationFrames = stateConfig.frames;
      this.isAnimating = stateConfig.loop || false;
      this.playAnimation();
    } else {
      // 单帧状态
      this.spriteContainer.style.backgroundImage = `url(${stateConfig.image})`;
      this.isAnimating = false;
    }
    
    // 更新朝向
    const facing = stateConfig.facing || 1;
    this.spriteContainer.style.transform = facing < 0 ? 'scaleX(-1)' : '';
  }
  
  // 播放动画
  playAnimation() {
    if (!this.isAnimating || this.animationFrames.length === 0) {
      return;
    }
    
    if (this.animationTimer) {
      clearInterval(this.animationTimer);
    }
    
    const frameDuration = this.animationFrames[0]?.duration || 100;
    
    this.animationTimer = setInterval(() => {
      this.currentFrame = (this.currentFrame + 1) % this.animationFrames.length;
      const frame = this.animationFrames[this.currentFrame];
      
      if (frame) {
        this.spriteContainer.style.backgroundImage = `url(${frame.image})`;
      }
    }, frameDuration);
  }
  
  // 停止动画
  stopAnimation() {
    if (this.animationTimer) {
      clearInterval(this.animationTimer);
      this.animationTimer = null;
    }
    this.isAnimating = false;
  }
  
  // 更新位置
  updatePosition() {
    this.el.style.left = `${this.position.x}px`;
    this.el.style.top = `${this.position.y}px`;
  }
  
  // 绑定事件
  bindEvents() {
    // 鼠标按下 - 开始拖拽
    this.el.addEventListener('mousedown', (e) => this.onDragStart(e));
    
    // 点击 - 互动
    this.el.addEventListener('click', (e) => this.onClick(e));
    
    // 鼠标悬停
    this.el.addEventListener('mouseenter', (e) => this.onHover(e));
    this.el.addEventListener('mouseleave', (e) => this.onLeave(e));
    
    // 触摸事件（移动端）
    this.el.addEventListener('touchstart', (e) => this.onTouchStart(e));
  }
  
  // 开始拖拽
  onDragStart(e) {
    this.isDragging = true;
    this.el.style.cursor = 'grabbing';
    
    const startX = e.clientX - this.position.x;
    const startY = e.clientY - this.position.y;
    
    const onMove = (e) => {
      if (!this.isDragging) return;
      
      this.position.x = e.clientX - startX;
      this.position.y = e.clientY - startY;
      this.updatePosition();
      
      // 拖拽时播放悬空姿势
      this.loadState('drag_suspended');
    };
    
    const onUp = () => {
      this.isDragging = false;
      this.el.style.cursor = 'grab';
      
      // 落地动画
      this.playDropAnimation();
      
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    };
    
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }
  
  // 点击互动
  onClick(e) {
    // 播放点击音效
    this.playSFX('click');
    
    // 切换到开心状态
    this.loadState('happy');
    
    // 说话
    this.speak('greeting');
    
    // 触发事件
    if (this.config.onInteract) {
      this.config.onInteract('click');
    }
  }
  
  // 悬停
  onHover(e) {
    this.el.style.opacity = '0.9';
  }
  
  // 离开
  onLeave(e) {
    this.el.style.opacity = '1';
  }
  
  // 触摸开始（移动端）
  onTouchStart(e) {
    e.preventDefault();
    const touch = e.touches[0];
    this.onDragStart({
      clientX: touch.clientX,
      clientY: touch.clientY,
    });
  }
  
  // 播放落地动画
  playDropAnimation() {
    // squash-and-stretch 效果
    this.el.style.transform = 'scaleY(0.8) scaleX(1.2)';
    
    setTimeout(() => {
      this.el.style.transform = 'scaleY(1.2) scaleX(0.8)';
    }, 100);
    
    setTimeout(() => {
      this.el.style.transform = 'scaleY(1) scaleX(1)';
      this.loadState('idle');
    }, 200);
    
    // 播放落地音效
    this.playSFX('drop');
  }
  
  // 说话
  speak(category) {
    const lines = this.config.voiceLines[category];
    if (!lines || lines.length === 0) {
      return;
    }
    
    // 随机选择台词
    const line = lines[Math.floor(Math.random() * lines.length)];
    
    // 显示气泡
    this.showBubble(line.text);
    
    // 播放配音
    this.playVoice(category, line.audio);
    
    // 切换到说话状态
    this.loadState('speaking');
    
    // 自动隐藏气泡
    setTimeout(() => {
      this.hideBubble();
    }, line.duration || 2000);
  }
  
  // 显示气泡
  showBubble(text) {
    this.speechBubble.childNodes[0].nodeValue = text;
    this.speechBubble.style.display = 'block';
  }
  
  // 隐藏气泡
  hideBubble() {
    this.speechBubble.style.display = 'none';
  }
  
  // 播放配音
  playVoice(category, audioPath) {
    if (!audioPath) return;
    
    const audio = new Audio(audioPath);
    audio.volume = this.config.voice?.volume || 0.8;
    audio.play().catch(() => {});
  }
  
  // 播放音效
  playSFX(name) {
    const sfx = this.config.soundEffects[name];
    if (!sfx) return;
    
    const audio = new Audio(sfx.file);
    audio.volume = sfx.volume || 0.6;
    audio.play().catch(() => {});
  }
  
  // 播放背景音乐
  playBGM() {
    const bgm = this.config.backgroundMusic;
    if (!bgm) return;
    
    const audio = new Audio(bgm.file);
    audio.volume = bgm.volume || 0.35;
    audio.loop = true;
    audio.play().catch(() => {});
  }
  
  // 停止背景音乐
  stopBGM() {
    // 停止所有背景音乐
    const bgmElements = document.querySelectorAll('.da-fei-hou-bgm');
    bgmElements.forEach(el => el.pause());
  }
  
  // 动画循环
  startAnimationLoop() {
    // 待机动画：眨眼、呼吸等
    setInterval(() => {
      if (this.state === 'idle' && !this.isDragging) {
        // 随机眨眼
        if (Math.random() < 0.05) {
          this.loadState('blink');
          setTimeout(() => this.loadState('idle'), 500);
        }
        
        // 随机小动作
        if (Math.random() < 0.02) {
          const actions = ['thinking', 'basin', 'eating', 'singing', 'cheer', 'heart'];
          const action = actions[Math.floor(Math.random() * actions.length)];
          this.loadState(action);
          setTimeout(() => this.loadState('idle'), 2000);
        }
      }
    }, 3000);
  }
  
  // 销毁
  destroy() {
    this.stopAnimation();
    this.el.remove();
    console.log(' 大肥猴下班了...大王晚安！');
  }
}

// 导出
if (typeof window !== 'undefined') {
  window.DaFeiHouPet = DaFeiHouPet;
}
