#!/bin/bash

# Prompt Center 停止脚本
# 停止前后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# PID文件
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

echo -e "${BLUE}🛑 Prompt Center 停止脚本${NC}"
echo "=================================="

# 停止服务函数
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}🛑 停止 $service_name (PID: $pid)...${NC}"
            kill $pid
            
            # 等待进程结束
            local count=0
            while ps -p $pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # 如果进程还在运行，强制杀死
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠️  强制停止 $service_name...${NC}"
                kill -9 $pid
            fi
            
            echo -e "${GREEN}✅ $service_name 已停止${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name 进程不存在${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️  $service_name PID文件不存在${NC}"
    fi
}

# 停止后端
stop_backend() {
    stop_service "后端服务" "$BACKEND_PID_FILE"
}

# 停止前端
stop_frontend() {
    stop_service "前端服务" "$FRONTEND_PID_FILE"
}

# 清理端口（备用方案）
cleanup_port() {
    local port=$1
    local service_name=$2
    
    echo -e "${YELLOW}🔍 清理端口 $port 上的 $service_name...${NC}"
    
    # 查找占用端口的进程
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}🛑 强制停止端口 $port 上的进程: $pids${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✅ 端口 $port 已清理${NC}"
    else
        echo -e "${GREEN}✅ 端口 $port 未被占用${NC}"
    fi
}

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
                echo "  --backend-only   只停止后端服务"
                echo "  --frontend-only  只停止前端服务"
                exit 1
                ;;
        esac
    done
    
    if [ "$backend_only" = true ]; then
        stop_backend
    elif [ "$frontend_only" = true ]; then
        stop_frontend
    else
        stop_backend
        echo ""
        stop_frontend
    fi
    
    echo ""
    
    # 清理端口（确保完全停止）
    if [ "$backend_only" != true ]; then
        cleanup_port 3000 "前端服务"
    fi
    
    if [ "$frontend_only" != true ]; then
        cleanup_port 8000 "后端服务"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Prompt Center 服务已停止！${NC}"
    echo "=================================="
}

# 执行主函数
main "$@"
