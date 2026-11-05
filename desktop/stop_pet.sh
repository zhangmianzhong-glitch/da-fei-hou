#!/bin/bash
# 停止大肥猴桌面宠物
launchctl unload ~/Library/LaunchAgents/com.openclaw.da-fei-hou.plist 2>/dev/null
pkill -f da_fei_hou.py 2>/dev/null
echo "大肥猴下班了...大王晚安！"
