// 大肥猴 — 后端插件入口
// Host half for OpenClaw plugin

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const CONFIG_PATH = path.join(process.env.HOME, '.openclaw', 'da-fei-hou', 'config.yaml');
const DEFAULT_CONFIG = path.join(__dirname, '..', 'config.yaml');

// 加载配置
function loadConfig() {
  try {
    const content = fs.readFileSync(CONFIG_PATH, 'utf8');
    return yaml.load(content);
  } catch {
    const content = fs.readFileSync(DEFAULT_CONFIG, 'utf8');
    return yaml.load(content);
  }
}

// API 路由
const routes = {
  // 获取配置
  'GET /api/da-fei-hou/config': (req) => {
    return { status: 200, body: loadConfig() };
  },
  
  // 更新配置
  'PUT /api/da-fei-hou/config': (req) => {
    const config = JSON.parse(req.body);
    fs.writeFileSync(CONFIG_PATH, yaml.dump(config));
    return { status: 200, body: { ok: true } };
  },
  
  // 触发大肥猴说话
  'POST /api/da-fei-hou/speak': (req) => {
    const { message } = JSON.parse(req.body);
    // 加入语音队列
    return { status: 200, body: { queued: true } };
  },
  
  // 获取大肥猴状态
  'GET /api/da-fei-hou/status': () => {
    return {
      status: 200,
      body: {
        state: 'idle',  // idle, thinking, working, sleeping,摸鱼
        position: { x: 0, y: 0 },
        lastActivity: Date.now()
      }
    };
  }
};

// 启动插件
function start() {
  console.log('🐒 大肥猴启动中...');
  console.log('大王万岁！山寨喽喽随时待命！');
  
  // 注册路由
  Object.entries(routes).forEach(([methodUrl, handler]) => {
    const [method, url] = methodUrl.split(' ');
    // 注册到 OpenClaw 路由系统
    console.log(`  ${method} ${url}`);
  });
  
  // 监听 OpenClaw 事件
  // - 任务开始 → 大肥猴思考状态
  // - 任务完成 → 大肥猴开心状态
  // - 错误 → 大肥猴难过状态
  
  return { stopped: false };
}

// 停止插件
function stop() {
  console.log('🐒 大肥猴下班了...大王万岁！');
  return { stopped: true };
}

module.exports = { start, stop, loadConfig };
