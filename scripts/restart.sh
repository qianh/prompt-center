#!/bin/bash

# Prompt Center 重启脚本
# 重启前后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}🔄 Prompt Center 重启脚本${NC}"
echo "=================================="

# 主函数
main() {
    local backend_only=false
    local frontend_only=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                backend_only=true
                shift
                ;;
            --frontend-only)
                frontend_only=true
                shift
                ;;
            *)
                echo "用法: $0 [--backend-only] [--frontend-only]"
                echo "  --backend-only   只重启后端服务"
                echo "  --frontend-only  只重启前端服务"
                exit 1
                ;;
        esac
    done
    
    if [ "$backend_only" = true ]; then
        echo -e "${YELLOW}🔄 重启后端服务...${NC}"
        "$PROJECT_ROOT/scripts/stop.sh" --backend-only
        sleep 2
        cd "$PROJECT_ROOT/backend"
        nohup uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/logs/backend.log" 2>&1 &
        echo $! > "$PROJECT_ROOT/.backend.pid"
        echo -e "${GREEN}✅ 后端服务重启完成${NC}"
        
    elif [ "$frontend_only" = true ]; then
        echo -e "${YELLOW}🔄 重启前端服务...${NC}"
        "$PROJECT_ROOT/scripts/stop.sh" --frontend-only
        sleep 2
        cd "$PROJECT_ROOT/frontend"
        nohup yarn dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
        echo $! > "$PROJECT_ROOT/.frontend.pid"
        echo -e "${GREEN}✅ 前端服务重启完成${NC}"
        
    else
        echo -e "${YELLOW}🔄 重启所有服务...${NC}"
        "$PROJECT_ROOT/scripts/stop.sh"
        sleep 3
        "$PROJECT_ROOT/scripts/start.sh"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Prompt Center 重启完成！${NC}"
    echo "=================================="
    
    # 显示状态
    sleep 5
    "$PROJECT_ROOT/scripts/status.sh"
}

# 执行主函数
main "$@"
