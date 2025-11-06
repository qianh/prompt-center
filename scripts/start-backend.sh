#!/bin/bash

# Prompt Center 后端启动脚本
# 独立启动后端服务

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

# PID文件
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"

# 日志文件
BACKEND_LOG="$PROJECT_ROOT/logs/backend.log"

# 创建日志目录
mkdir -p "$PROJECT_ROOT/logs"

echo -e "${BLUE}🔧 Prompt Center 后端启动脚本${NC}"
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
    
    echo -e "${GREEN}✅ 依赖检查通过${NC}"
}

# 启动后端
start_backend() {
    echo -e "${YELLOW}🔧 启动后端服务...${NC}"
    
    cd "$BACKEND_DIR"
    
    # 检查是否已经在运行
    if [ -f "$BACKEND_PID_FILE" ]; then
        local pid=$(cat "$BACKEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  后端服务已在运行 (PID: $pid)${NC}"
            echo -e "${YELLOW}📍 后端地址: http://localhost:8000${NC}"
            echo -e "${YELLOW}📖 API文档: http://localhost:8000/docs${NC}"
            return
        else
            rm -f "$BACKEND_PID_FILE"
        fi
    fi
    
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

# 主函数
main() {
    echo -e "${BLUE}🏠 项目目录: $PROJECT_ROOT${NC}"
    echo ""
    
    check_dependencies
    echo ""
    
    start_backend
    echo ""
    
    echo -e "${GREEN}🎉 后端服务启动完成！${NC}"
    echo "=================================="
    echo -e "${GREEN}📍 后端地址: http://localhost:8000${NC}"
    echo -e "${GREEN}📖 API文档: http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}📋 管理命令:${NC}"
    echo "  查看状态: ./scripts/status.sh"
    echo "  停止后端: ./scripts/stop.sh --backend-only"
    echo "  查看日志: tail -f $BACKEND_LOG"
    echo ""
}

# 执行主函数
main "$@"
