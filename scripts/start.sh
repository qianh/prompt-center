#!/bin/bash

# Prompt Center 启动脚本
# 一键启动前后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# PID文件
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

# 日志文件
BACKEND_LOG="$PROJECT_ROOT/logs/backend.log"
FRONTEND_LOG="$PROJECT_ROOT/logs/frontend.log"

# 创建日志目录
mkdir -p "$PROJECT_ROOT/logs"

echo -e "${BLUE}🚀 Prompt Center 启动脚本${NC}"
echo "=================================="

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}📋 检查依赖...${NC}"
    
    # 检查 uv
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ uv 未安装，请先安装 uv${NC}"
        echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    # 检查 yarn
    if ! command -v yarn &> /dev/null; then
        echo -e "${RED}❌ yarn 未安装，请先安装 yarn${NC}"
        echo "安装命令: npm install -g yarn"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 依赖检查通过${NC}"
}

# 启动后端
start_backend() {
    echo -e "${YELLOW}🔧 启动后端服务...${NC}"
    
    cd "$BACKEND_DIR"
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}📦 创建虚拟环境...${NC}"
        uv venv
    fi
    
    # 安装依赖
    echo -e "${YELLOW}📦 安装后端依赖...${NC}"
    uv sync --dev
    
    # 启动后端服务
    echo -e "${YELLOW}🚀 启动后端服务器...${NC}"
    nohup uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"
    
    # 等待后端启动
    echo -e "${YELLOW}⏳ 等待后端服务启动...${NC}"
    sleep 5
    
    # 检查后端是否启动成功
    if curl -s http://localhost:8000/health > /dev/null 2>&1 || curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务启动成功 (PID: $BACKEND_PID)${NC}"
        echo -e "${GREEN}📍 后端地址: http://localhost:8000${NC}"
        echo -e "${GREEN}📖 API文档: http://localhost:8000/docs${NC}"
    else
        echo -e "${RED}❌ 后端服务启动失败${NC}"
        echo "查看日志: tail -f $BACKEND_LOG"
        exit 1
    fi
}

# 启动前端
start_frontend() {
    echo -e "${YELLOW}🎨 启动前端服务...${NC}"
    
    cd "$FRONTEND_DIR"
    
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
    
    start_backend
    echo ""
    
    start_frontend
    echo ""
    
    echo -e "${GREEN}🎉 Prompt Center 启动完成！${NC}"
    echo "=================================="
    echo -e "${GREEN}📍 前端地址: http://localhost:3000${NC}"
    echo -e "${GREEN}📍 后端地址: http://localhost:8000${NC}"
    echo -e "${GREEN}📖 API文档: http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}📋 管理命令:${NC}"
    echo "  查看状态: ./scripts/status.sh"
    echo "  停止服务: ./scripts/stop.sh"
    echo "  重启服务: ./scripts/restart.sh"
    echo "  查看日志: tail -f logs/backend.log 或 tail -f logs/frontend.log"
    echo ""
}

# 执行主函数
main "$@"
