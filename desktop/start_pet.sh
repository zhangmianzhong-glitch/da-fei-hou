#!/bin/bash
# 启动大肥猴桌面宠物
launchctl load ~/Library/LaunchAgents/com.openclaw.da-fei-hou.plist 2>/dev/null
sleep 1
if pgrep -f da_fei_hou.py > /dev/null; then echo "大肥猴已在桌面上！大王万岁！"; else echo "启动失败，请查看 logs/pet.err"; fi
