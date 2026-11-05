/*
 * 大肥猴桌宠配置
 */

export const DaFeiHouConfig = {
  // 基本配置
  name: '大肥猴',
  size: 175,  // 像素
  opacity: 1.0,
  
  // 状态配置
  states: {
    idle: {
      image: '/api/da-fei-hou/asset/sprites/idle.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    blink: {
      image: '/api/da-fei-hou/asset/sprites/blink.png',
      frames: [
        { image: '/api/da-fei-hou/asset/sprites/blink_0.png', duration: 200 },
        { image: '/api/da-fei-hou/asset/sprites/blink_1.png', duration: 300 },
        { image: '/api/da-fei-hou/asset/sprites/blink_2.png', duration: 200 },
      ],
      loop: false,
      facing: 1,
    },
    thinking: {
      image: '/api/da-fei-hou/asset/sprites/thinking.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    happy: {
      image: '/api/da-fei-hou/asset/sprites/happy.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    sad: {
      image: '/api/da-fei-hou/asset/sprites/sad.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    angry: {
      image: '/api/da-fei-hou/asset/sprites/angry.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    surprise: {
      image: '/api/da-fei-hou/asset/sprites/surprise.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    sleeping: {
      image: '/api/da-fei-hou/asset/sprites/sleeping.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    wave: {
      image: '/api/da-fei-hou/asset/sprites/wave.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    singing: {
      image: '/api/da-fei-hou/asset/sprites/singing.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    basin: {
      image: '/api/da-fei-hou/asset/sprites/basin.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    eating: {
      image: '/api/da-fei-hou/asset/sprites/eating.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    fishing: {
      image: '/api/da-fei-hou/asset/sprites/fishing.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    heart: {
      image: '/api/da-fei-hou/asset/sprites/heart.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    walking: {
      image: '/api/da-fei-hou/asset/sprites/walk.png',
      frames: [
        { image: '/api/da-fei-hou/asset/sprites/walk_0.png', duration: 300 },
        { image: '/api/da-fei-hou/asset/sprites/walk_1.png', duration: 300 },
        { image: '/api/da-fei-hou/asset/sprites/walk_2.png', duration: 300 },
      ],
      loop: true,
      facing: 1,
    },
    speaking: {
      image: '/api/da-fei-hou/asset/sprites/speaking.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    patting: {
      image: '/api/da-fei-hou/asset/sprites/patting.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    cheer: {
      image: '/api/da-fei-hou/asset/sprites/cheer.png',
      frames: [],
      loop: true,
      facing: 1,
    },
    drag_suspended: {
      image: '/api/da-fei-hou/asset/sprites/drag.png',
      frames: [],
      loop: true,
      facing: 1,
    },
  },
  
  // 配音配置
  voiceLines: {
    greeting: [
      { text: '大王！小的大肥猴在呢！', audio: '/api/da-fei-hou/asset/voice/greeting/greeting_01.mp3', duration: 2000 },
      { text: '大王万岁！山寨喽喽随时待命！', audio: '/api/da-fei-hou/asset/voice/greeting/greeting_02.mp3', duration: 2500 },
      { text: '大王来啦！小的给您磕头了！', audio: '/api/da-fei-hou/asset/voice/greeting/greeting_03.mp3', duration: 2200 },
    ],
    thinking: [
      { text: 'tmd 这任务有点意思...', audio: '/api/da-fei-hou/asset/voice/thinking/thinking_01.mp3', duration: 1800 },
      { text: '让小的想想...大王英明神武！', audio: '/api/da-fei-hou/asset/voice/thinking/thinking_02.mp3', duration: 2200 },
    ],
    happy: [
      { text: '大王夸奖！小的太开心了！', audio: '/api/da-fei-hou/asset/voice/happy/happy_01.mp3', duration: 2000 },
      { text: '大王英明！小的拍马屁时间到！', audio: '/api/da-fei-hou/asset/voice/happy/happy_02.mp3', duration: 2500 },
    ],
    // ... 其他类别
  },
  
  // 音效配置
  soundEffects: {
    click: { file: '/api/da-fei-hou/asset/sfx/click.mp3', volume: 0.6 },
    drop: { file: '/api/da-fei-hou/asset/sfx/drop.mp3', volume: 0.7 },
    drag: { file: '/api/da-fei-hou/asset/sfx/drag.mp3', volume: 0.5 },
    sparkle: { file: '/api/da-fei-hou/asset/sfx/sparkle.mp3', volume: 0.4 },
  },
  
  // 背景音乐配置
  backgroundMusic: {
    file: '/api/da-fei-hou/asset/bgm/loop.mp3',
    volume: 0.35,
    autoPauseOnTabSwitch: true,
  },
  
  // 行为配置
  behavior: {
    autoWalk: true,
    fidget: true,
    bubble: true,
    proactive: true,
    quietHours: {
      start: '23:00',
      end: '08:00',
    },
  },
  
  // 事件回调
  onInteract: null,
  onStateChange: null,
  onBilibiliFound: null,
};
