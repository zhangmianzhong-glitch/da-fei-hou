const { app, BrowserWindow, screen, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;
  
  mainWindow = new BrowserWindow({
    width: 200,
    height: 200,
    x: screenWidth - 250,
    y: screenHeight - 250,
    transparent: true,
    frame: false,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    hasShadow: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('index.html');
  
  // 让透明窗口真正透明
  mainWindow.setBackgroundColor('#00000000');
  
  // 鼠标穿透透明区域
  mainWindow.setIgnoreMouseEvents(false);
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// 处理窗口拖动
ipcMain.on('window-move', (event, { x, y }) => {
  const [winX, winY] = mainWindow.getPosition();
  mainWindow.setPosition(winX + x, winY + y);
});

// 处理窗口关闭
ipcMain.on('window-close', () => {
  mainWindow.close();
});
