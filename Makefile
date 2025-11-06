# Prompt Center Makefile
# 便捷的项目管理命令

.PHONY: help start stop status restart frontend backend stop-frontend stop-backend restart-frontend restart-backend logs logs-frontend logs-backend clean install setup

# 默认目标
help:
	@echo "🚀 Prompt Center 管理命令"
	@echo "=========================="
	@echo ""
	@echo "🎯 启动命令:"
	@echo "  make start          - 启动前后端服务"
	@echo "  make frontend       - 启动前端服务"
	@echo "  make backend        - 启动后端服务"
	@echo ""
	@echo "🛑 停止命令:"
	@echo "  make stop           - 停止所有服务"
	@echo "  make stop-frontend  - 停止前端服务"
	@echo "  make stop-backend   - 停止后端服务"
	@echo ""
	@echo "🔄 重启命令:"
	@echo "  make restart        - 重启所有服务"
	@echo "  make restart-frontend - 重启前端服务"
	@echo "  make restart-backend  - 重启后端服务"
	@echo ""
	@echo "📊 状态命令:"
	@echo "  make status         - 查看服务状态"
	@echo "  make logs           - 查看所有日志"
	@echo "  make logs-frontend  - 查看前端日志"
	@echo "  make logs-backend   - 查看后端日志"
	@echo ""
	@echo "🔧 维护命令:"
	@echo "  make install        - 安装所有依赖"
	@echo "  make setup          - 初始化项目"
	@echo "  make clean          - 清理临时文件"
	@echo ""
	@echo "🌐 访问地址:"
	@echo "  前端: http://localhost:3000"
	@echo "  后端: http://localhost:8000"
	@echo "  API文档: http://localhost:8000/docs"

# 启动命令
start:
	@./scripts/start.sh

frontend:
	@./scripts/start-frontend.sh

backend:
	@./scripts/start-backend.sh

# 停止命令
stop:
	@./scripts/stop.sh

stop-frontend:
	@./scripts/stop.sh --frontend-only

stop-backend:
	@./scripts/stop.sh --backend-only

# 重启命令
restart:
	@./scripts/restart.sh

restart-frontend:
	@./scripts/restart.sh --frontend-only

restart-backend:
	@./scripts/restart.sh --backend-only

# 状态命令
status:
	@./scripts/status.sh

logs:
	@echo "📋 查看前端日志 (Ctrl+C 退出):"
	@sleep 2
	@tail -f logs/frontend.log &
	@echo "📋 查看后端日志 (Ctrl+C 退出):"
	@sleep 2
	@tail -f logs/backend.log

logs-frontend:
	@tail -f logs/frontend.log

logs-backend:
	@tail -f logs/backend.log

# 维护命令
install:
	@echo "📦 安装依赖..."
	@cd backend && uv sync --dev
	@cd frontend && yarn install
	@echo "✅ 依赖安装完成"

setup:
	@echo "🔧 初始化项目..."
	@mkdir -p logs
	@chmod +x scripts/*.sh
	@make install
	@echo "✅ 项目初始化完成"

clean:
	@echo "🧹 清理临时文件..."
	@rm -f .frontend.pid .backend.pid
	@rm -rf logs/*
	@cd frontend && rm -rf dist
	@echo "✅ 清理完成"

# 快速开发命令
dev: setup start
	@echo "🚀 开发环境已启动"

# 生产构建
build:
	@echo "🏗️ 构建生产版本..."
	@cd frontend && yarn build
	@echo "✅ 构建完成"

# 测试命令
test:
	@echo "🧪 运行测试..."
	@cd backend && uv run pytest
	@cd frontend && yarn test
	@echo "✅ 测试完成"

# 代码检查
lint:
	@echo "🔍 代码检查..."
	@cd backend && uv run ruff check
	@cd frontend && yarn lint
	@echo "✅ 检查完成"

# 代码格式化
format:
	@echo "💅 代码格式化..."
	@cd backend && uv run ruff format
	@cd frontend && yarn format
	@echo "✅ 格式化完成"
