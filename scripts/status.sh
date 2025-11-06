#!/bin/bash

# Prompt Center 状态检查脚本
# 检查前后端服务状态

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

# 日志文件
BACKEND_LOG="$PROJECT_ROOT/logs/backend.log"
FRONTEND_LOG="$PROJECT_ROOT/logs/frontend.log"

echo -e "${BLUE}📊 Prompt Center 状态检查${NC}"
echo "=================================="

# 检查服务状态
check_service() {
    local service_name=$1
    local port=$2
    local pid_file=$3
    local log_file=$4
    
    echo -e "${YELLOW}🔍 检查 $service_name...${NC}"
    
    # 检查PID文件
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo -e "  📄 PID文件: 存在 (PID: $pid)"
        
        # 检查进程是否存在
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "  🔄 进程状态: ${GREEN}运行中${NC}"
            
            # 检查端口是否被占用
            if lsof -i:$port > /dev/null 2>&1; then
                echo -e "  🌐 端口状态: ${GREEN}已占用 (端口 $port)${NC}"
                
                # 检查服务是否响应
                if curl -s --max-time 3 http://localhost:$port > /dev/null 2>&1; then
                    echo -e "  ✅ 服务响应: ${GREEN}正常${NC}"
                else
                    echo -e "  ⚠️  服务响应: ${YELLOW}无响应${NC}"
                fi
            else
                echo -e "  🌐 端口状态: ${RED}未占用${NC}"
            fi
        else
            echo -e "  🔄 进程状态: ${RED}已停止${NC}"
        fi
    else
        echo -e "  📄 PID文件: ${RED}不存在${NC}"
        echo -e "  🔄 进程状态: ${RED}未知${NC}"
    fi
    
    # 检查日志文件
    if [ -f "$log_file" ]; then
        local log_size=$(du -h "$log_file" | cut -f1)
        echo -e "  📝 日志文件: 存在 (大小: $log_size)"
        echo -e "  📋 查看日志: tail -f $log_file"
    else
        echo -e "  📝 日志文件: ${YELLOW}不存在${NC}"
    fi
    
    echo ""
}

# 检查端口占用详情
check_port_details() {
    local port=$1
    local service_name=$2
    
    echo -e "${YELLOW}🔍 端口 $port 详细信息:${NC}"
    
    local process_info=$(lsof -i:$port 2>/dev/null || echo "无进程占用")
    if [ "$process_info" != "无进程占用" ]; then
        echo "$process_info" | while read line; do
            echo "  $line"
        done
    else
        echo "  无进程占用端口 $port"
    fi
    echo ""
}

# 显示系统信息
show_system_info() {
    echo -e "${YELLOW}💻 系统信息:${NC}"
    echo "  操作系统: $(uname -s)"
    echo "  架构: $(uname -m)"
    echo "  当前时间: $(date)"
    echo "  项目目录: $PROJECT_ROOT"
    echo ""
}

# 显示快速操作提示
show_quick_actions() {
    echo -e "${BLUE}🚀 快速操作:${NC}"
    echo "  启动服务: ./scripts/start.sh"
    echo "  停止服务: ./scripts/stop.sh"
    echo "  重启服务: ./scripts/restart.sh"
    echo "  停止后端: ./scripts/stop.sh --backend-only"
    echo "  停止前端: ./scripts/stop.sh --frontend-only"
    echo ""
}

# 主函数
main() {
    show_system_info
    
    # 检查后端服务
    check_service "后端服务" 8000 "$BACKEND_PID_FILE" "$BACKEND_LOG"
    check_port_details 8000 "后端服务"
    
    # 检查前端服务
    check_service "前端服务" 3000 "$FRONTEND_PID_FILE" "$FRONTEND_LOG"
    check_port_details 3000 "前端服务"
    
    # 显示访问地址
    echo -e "${BLUE}📍 访问地址:${NC}"
    
    # 检查服务状态并显示相应地址
    if curl -s --max-time 3 http://localhost:8000 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ 后端API: http://localhost:8000${NC}"
        echo -e "  ${GREEN}📖 API文档: http://localhost:8000/docs${NC}"
    else
        echo -e "  ${RED}❌ 后端服务未运行${NC}"
    fi
    
    if curl -s --max-time 3 http://localhost:3000 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ 前端界面: http://localhost:3000${NC}"
    else
        echo -e "  ${RED}❌ 前端服务未运行${NC}"
    fi
    
    echo ""
    show_quick_actions
}

# 执行主函数
main "$@"
