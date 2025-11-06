#!/bin/bash

# Prompt Center 快速命令别名
# 使用方法: source ./scripts/aliases.sh

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Prompt Center 快速命令已加载${NC}"
echo -e "${GREEN}可用命令:${NC}"
echo "  pc-start     - 启动前后端服务"
echo "  pc-stop      - 停止所有服务"
echo "  pc-status    - 查看服务状态"
echo "  pc-restart   - 重启所有服务"
echo "  pc-frontend  - 启动前端服务"
echo "  pc-backend   - 启动后端服务"
echo "  pc-stop-f    - 停止前端服务"
echo "  pc-stop-b    - 停止后端服务"
echo "  pc-restart-f - 重启前端服务"
echo "  pc-restart-b - 重启后端服务"
echo "  pc-logs-f    - 查看前端日志"
echo "  pc-logs-b    - 查看后端日志"
echo ""

# 获取项目根目录
PC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 定义别名
alias pc-start="$PC_ROOT/scripts/start.sh"
alias pc-stop="$PC_ROOT/scripts/stop.sh"
alias pc-status="$PC_ROOT/scripts/status.sh"
alias pc-restart="$PC_ROOT/scripts/restart.sh"
alias pc-frontend="$PC_ROOT/scripts/start-frontend.sh"
alias pc-backend="$PC_ROOT/scripts/start-backend.sh"
alias pc-stop-f="$PC_ROOT/scripts/stop.sh --frontend-only"
alias pc-stop-b="$PC_ROOT/scripts/stop.sh --backend-only"
alias pc-restart-f="$PC_ROOT/scripts/restart.sh --frontend-only"
alias pc-restart-b="$PC_ROOT/scripts/restart.sh --backend-only"
alias pc-logs-f="tail -f $PC_ROOT/logs/frontend.log"
alias pc-logs-b="tail -f $PC_ROOT/logs/backend.log"

echo -e "${GREEN}✅ 别名设置完成！现在可以使用快速命令了。${NC}"
