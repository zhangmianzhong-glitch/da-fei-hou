// 大肥猴 OpenClaw 插件 - 后端入口
// Host half for OpenClaw plugin

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const CONFIG_PATH = path.join(process.env.HOME || '', '.openclaw', 'da-fei-hou', 'config.yaml');
const DEFAULT_CONFIG = path.join(__dirname, '..', 'config.yaml');

// 加载配置
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const content = fs.readFileSync(CONFIG_PATH, 'utf8');
      return yaml.load(content);
    }
  } catch (e) {
    console.error('🐒 加载配置失败:', e.message);
  }
  
  // 使用默认配置
  const content = fs.readFileSync(DEFAULT_CONFIG, 'utf8');
  return yaml.load(content);
}

// 保存配置
function saveConfig(config) {
  const dir = path.dirname(CONFIG_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(CONFIG_PATH, yaml.dump(config));
}

// API 路由
const routes = {
  // 获取配置
  'GET /api/da-fei-hou/config': (req) => {
    return { status: 200, body: loadConfig() };
  },
  
  // 更新配置
  'PUT /api/da-fei-hou/config': (req) => {
    try {
      const config = JSON.parse(req.body);
      saveConfig(config);
      return { status: 200, body: { ok: true } };
    } catch (e) {
      return { status: 400, body: { error: e.message } };
    }
  },
  
  // 触发大肥猴说话
  'POST /api/da-fei-hou/speak': (req) => {
    const { category, line } = JSON.parse(req.body);
    // 加入语音队列
    return { status: 200, body: { queued: true } };
  },
  
  // 获取大肥猴状态
  'GET /api/da-fei-hou/status': () => {
    return {
      status: 200,
      body: {
        state: 'idle',  // idle, thinking, working, sleeping, fishing
        position: { x: 0, y: 0 },
        lastActivity: Date.now(),
        isDragging: false,
      }
    };
  },
  
  // 获取配音文件列表
  'GET /api/da-fei-hou/voice-list': () => {
    const voiceDir = path.join(__dirname, '..', 'assets', 'voice');
    const categories = [];
    
    if (fs.existsSync(voiceDir)) {
      const dirs = fs.readdirSync(voiceDir);
      for (const dir of dirs) {
        const dirPath = path.join(voiceDir, dir);
        if (fs.statSync(dirPath).isDirectory()) {
          const files = fs.readdirSync(dirPath).filter(f => f.endsWith('.mp3'));
          categories.push({
            name: dir,
            count: files.length,
            files: files,
          });
        }
      }
    }
    
    return { status: 200, body: { categories } };
  },
  
  // 获取精灵图
  'GET /api/da-fei-hou/asset/sprites/:name': (req, params) => {
    const spritePath = path.join(__dirname, '..', 'assets', 'sprites', params.name);
    if (fs.existsSync(spritePath)) {
      const content = fs.readFileSync(spritePath);
      return {
        status: 200,
        body: content,
        headers: { 'Content-Type': 'image/png' },
      };
    }
    return { status: 404, body: { error: 'Not found' } };
  },
  
  // 获取音频文件
  'GET /api/da-fei-hou/asset/voice/:category/:name': (req, params) => {
    const audioPath = path.join(__dirname, '..', 'assets', 'voice', params.category, params.name);
    if (fs.existsSync(audioPath)) {
      const content = fs.readFileSync(audioPath);
      return {
        status: 200,
        body: content,
        headers: { 'Content-Type': 'audio/mpeg' },
      };
    }
    return { status: 404, body: { error: 'Not found' } };
  },
};

// 启动插件
function start(openclaw) {
  console.log('🐒 大肥猴启动中...大王万岁！');
  console.log('🐒 山寨喽喽随时待命！');
  
  const config = loadConfig();
  
  // 注册 API 路由
  Object.entries(routes).forEach(([methodUrl, handler]) => {
    const [method, url] = methodUrl.split(' ');
    openclaw.registerRoute(method, url, handler);
    console.log(`  ${method} ${url}`);
  });
  
  // 监听 OpenClaw 事件
  if (openclaw.on) {
    // 任务开始 → 大肥猴思考状态
    openclaw.on('task:start', (task) => {
      console.log(' 任务开始:', task.name);
      broadcastToClients({ type: 'task_start', task });
    });
    
    // 任务完成 → 大肥猴开心状态
    openclaw.on('task:complete', (task) => {
      console.log('🐒 任务完成:', task.name);
      broadcastToClients({ type: 'task_complete', task });
    });
    
    // 错误 → 大肥猴难过状态
    openclaw.on('error', (error) => {
      console.log(' 错误:', error.message);
      broadcastToClients({ type: 'error', error });
    });
    
    // 会话开始 → 大肥猴挥手
    openclaw.on('session:start', () => {
      console.log(' 新会话开始');
      broadcastToClients({ type: 'session_start' });
    });
    
    // 会话结束 → 大肥猴睡觉
    openclaw.on('session:end', () => {
      console.log('🐒 会话结束');
      broadcastToClients({ type: 'session_end' });
    });
  }
  
  // 广播消息到客户端
  function broadcastToClients(message) {
    // TODO: 通过 WebSocket 或 Server-Sent Events 发送到客户端
    console.log('🐒 广播消息:', message);
  }
  
  console.log('🐒 大肥猴已上线！大王万岁！');
  
  return { stopped: false };
}

// 停止插件
function stop() {
  console.log('🐒 大肥猴下班了...大王晚安！');
  return { stopped: true };
}

module.exports = { start, stop, loadConfig, saveConfig };
