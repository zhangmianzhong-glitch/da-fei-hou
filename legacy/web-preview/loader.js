// 大肥猴 OpenClaw 插件 - 客户端加载器
// Browser half for OpenClaw Web UI

import { DaFeiHouPet } from './pet.js';
import { DaFeiHouConfig } from './config.js';

// 全局状态
let petInstance = null;
let isConnected = false;
let eventSource = null;

// 初始化大肥猴
function initDaFeiHou() {
  console.log('🐒 大肥猴客户端初始化中...');
  
  // 检查是否已存在
  if (petInstance) {
    console.log('🐒 大肥猴已存在，跳过初始化');
    return;
  }
  
  // 创建桌宠实例
  petInstance = new DaFeiHouPet({
    ...DaFeiHouConfig,
    onInteract: handleInteraction,
    onStateChange: handleStateChange,
    onBilibiliFound: handleBilibiliFound,
  });
  
  // 连接事件源
  connectEventSource();
  
  console.log('🐒 大肥猴已上线！大王万岁！');
}

// 连接事件源（Server-Sent Events）
function connectEventSource() {
  if (eventSource) {
    eventSource.close();
  }
  
  // 连接到 OpenClaw 事件流
  eventSource = new EventSource('/api/da-fei-hou/events');
  
  eventSource.onopen = () => {
    isConnected = true;
    console.log('🐒 大肥猴已连接事件源');
  };
  
  eventSource.onerror = (e) => {
    isConnected = false;
    console.error('🐒 事件源连接失败:', e);
    
    // 3 秒后重连
    setTimeout(() => {
      if (!isConnected) {
        connectEventSource();
      }
    }, 3000);
  };
  
  // 监听任务开始事件
  eventSource.addEventListener('task_start', (e) => {
    const task = JSON.parse(e.data);
    handleTaskStart(task);
  });
  
  // 监听任务完成事件
  eventSource.addEventListener('task_complete', (e) => {
    const task = JSON.parse(e.data);
    handleTaskComplete(task);
  });
  
  // 监听错误事件
  eventSource.addEventListener('error', (e) => {
    const error = JSON.parse(e.data);
    handleError(error);
  });
  
  // 监听会话开始事件
  eventSource.addEventListener('session_start', () => {
    handleSessionStart();
  });
  
  // 监听会话结束事件
  eventSource.addEventListener('session_end', () => {
    handleSessionEnd();
  });
  
  // 监听 B 站发现事件
  eventSource.addEventListener('bilibili_found', (e) => {
    const video = JSON.parse(e.data);
    handleBilibiliFound(video);
  });
}

// 处理互动
function handleInteraction(type) {
  console.log(' 互动:', type);
  
  // 发送互动事件到后端
  fetch('/api/da-fei-hou/interact', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type }),
  }).catch(() => {});
}

// 处理状态变更
function handleStateChange(oldState, newState) {
  console.log(`🐒 状态变更：${oldState} → ${newState}`);
}

// 处理任务开始
function handleTaskStart(task) {
  console.log(' 任务开始:', task.name);
  
  if (petInstance) {
    petInstance.loadState('thinking');
    petInstance.speak('thinking');
  }
}

// 处理任务完成
function handleTaskComplete(task) {
  console.log('🐒 任务完成:', task.name);
  
  if (petInstance) {
    petInstance.loadState('happy');
    petInstance.speak('happy');
  }
}

// 处理错误
function handleError(error) {
  console.error('🐒 错误:', error.message);
  
  if (petInstance) {
    petInstance.loadState('sad');
    petInstance.speak('sad');
  }
}

// 处理会话开始
function handleSessionStart() {
  console.log('🐒 新会话开始');
  
  if (petInstance) {
    petInstance.loadState('wave');
    petInstance.speak('greeting');
  }
}

// 处理会话结束
function handleSessionEnd() {
  console.log(' 会话结束');
  
  if (petInstance) {
    petInstance.loadState('sleeping');
    petInstance.speak('sleeping');
  }
}

// 处理 B 站发现
function handleBilibiliFound(video) {
  console.log('🐒 B 站发现:', video.title);
  
  if (petInstance) {
    petInstance.loadState('surprise');
    petInstance.speak('bilibili');
  }
  
  // 发送钉钉通知
  fetch('/api/da-fei-hou/notify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      type: 'bilibili_found',
      video: video,
    }),
  }).catch(() => {});
}

// 清理
function cleanup() {
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  
  if (petInstance) {
    petInstance.destroy();
    petInstance = null;
  }
  
  isConnected = false;
  console.log('🐒 大肥猴已清理');
}

// 页面卸载时清理
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', cleanup);
  
  // 页面可见性变化时暂停/恢复
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      // 页面隐藏，暂停动画
      if (petInstance) {
        petInstance.stopAnimation();
      }
    } else {
      // 页面显示，恢复动画
      if (petInstance) {
        petInstance.startAnimationLoop();
      }
    }
  });
  
  // 自动初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDaFeiHou);
  } else {
    initDaFeiHou();
  }
}

// 导出
export { initDaFeiHou, cleanup, petInstance };
