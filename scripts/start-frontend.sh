#!/bin/bash

# Prompt Center 前端启动脚本
# 独立启动前端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# PID文件
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

# 日志文件
FRONTEND_LOG="$PROJECT_ROOT/logs/frontend.log"

# 创建日志目录
mkdir -p "$PROJECT_ROOT/logs"

echo -e "${BLUE}🎨 Prompt Center 前端启动脚本${NC}"
echo "=================================="

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}📋 检查依赖...${NC}"
    
    # 检查 yarn
    if ! command -v yarn &> /dev/null; then
        echo -e "${RED}❌ yarn 未安装，请先安装 yarn${NC}"
        echo "安装命令: npm install -g yarn"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 依赖检查通过${NC}"
}

# 启动前端
start_frontend() {
    echo -e "${YELLOW}🎨 启动前端服务...${NC}"
    
    cd "$FRONTEND_DIR"
    
    # 检查是否已经在运行
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  前端服务已在运行 (PID: $pid)${NC}"
            echo -e "${YELLOW}📍 前端地址: http://localhost:3000${NC}"
            return
        else
            rm -f "$FRONTEND_PID_FILE"
        fi
    fi
    
    # 安装依赖
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 安装前端依赖...${NC}"
        yarn install
    fi
    
    # 启动前端服务
    echo -e "${YELLOW}🚀 启动前端服务器...${NC}"
    nohup yarn dev > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"
    
    # 等待前端启动
    echo -e "${YELLOW}⏳ 等待前端服务启动...${NC}"
    sleep 10
    
    # 检查前端是否启动成功
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端服务启动成功 (PID: $FRONTEND_PID)${NC}"
        echo -e "${GREEN}📍 前端地址: http://localhost:3000${NC}"
    else
        echo -e "${RED}❌ 前端服务启动失败${NC}"
        echo "查看日志: tail -f $FRONTEND_LOG"
        exit 1
    fi
}

# 主函数
main() {
    echo -e "${BLUE}🏠 项目目录: $PROJECT_ROOT${NC}"
    echo ""
    
    check_dependencies
    echo ""
    
    start_frontend
    echo ""
    
    echo -e "${GREEN}🎉 前端服务启动完成！${NC}"
    echo "=================================="
    echo -e "${GREEN}📍 前端地址: http://localhost:3000${NC}"
    echo ""
    echo -e "${YELLOW}📋 管理命令:${NC}"
    echo "  查看状态: ./scripts/status.sh"
    echo "  停止前端: ./scripts/stop.sh --frontend-only"
    echo "  查看日志: tail -f $FRONTEND_LOG"
    echo ""
}

# 执行主函数
main "$@"
