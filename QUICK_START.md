# 🚀 Prompt Center 快速启动指南

## ⚡ 一键启动

### 方式1: 使用脚本 (推荐)
```bash
# 启动前后端
./scripts/start.sh

# 查看状态
./scripts/status.sh

# 停止服务
./scripts/stop.sh
```

### 方式2: 使用Makefile
```bash
# 启动前后端
make start

# 查看状态
make status

# 停止服务
make stop
```

### 方式3: 使用别名 (最便捷)
```bash
# 加载别名
source ./scripts/aliases.sh

# 快速命令
pc-start      # 启动服务
pc-status     # 查看状态
pc-stop       # 停止服务
```

## 🎛️ 独立控制

### 前端服务
```bash
# 脚本方式
./scripts/start-frontend.sh
./scripts/stop.sh --frontend-only

# Makefile方式
make frontend
make stop-frontend

# 别名方式
pc-frontend
pc-stop-f
```

### 后端服务
```bash
# 脚本方式
./scripts/start-backend.sh
./scripts/stop.sh --backend-only

# Makefile方式
make backend
make stop-backend

# 别名方式
pc-backend
pc-stop-b
```

## 📊 服务状态

### 检查状态
```bash
./scripts/status.sh
# 或
make status
# 或
pc-status
```

### 查看日志
```bash
# 前端日志
tail -f logs/frontend.log
make logs-frontend
pc-logs-f

# 后端日志
tail -f logs/backend.log
make logs-backend
pc-logs-b
```

## 🌐 访问地址

启动成功后访问：

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 🔄 重启服务

```bash
# 重启所有服务
./scripts/restart.sh
make restart
pc-restart

# 重启前端
./scripts/restart.sh --frontend-only
make restart-frontend
pc-restart-f

# 重启后端
./scripts/restart.sh --backend-only
make restart-backend
pc-restart-b
```

## 🛠️ 开发工具

### 项目初始化
```bash
make setup
```

### 安装依赖
```bash
make install
```

### 代码检查
```bash
make lint
```

### 代码格式化
```bash
make format
```

### 运行测试
```bash
make test
```

### 清理临时文件
```bash
make clean
```

## 📝 常用命令速查

| 操作 | 脚本命令 | Makefile | 别名命令 |
|------|----------|----------|----------|
| 启动全部 | `./scripts/start.sh` | `make start` | `pc-start` |
| 停止全部 | `./scripts/stop.sh` | `make stop` | `pc-stop` |
| 查看状态 | `./scripts/status.sh` | `make status` | `pc-status` |
| 重启全部 | `./scripts/restart.sh` | `make restart` | `pc-restart` |
| 启动前端 | `./scripts/start-frontend.sh` | `make frontend` | `pc-frontend` |
| 启动后端 | `./scripts/start-backend.sh` | `make backend` | `pc-backend` |
| 停止前端 | `./scripts/stop.sh --frontend-only` | `make stop-frontend` | `pc-stop-f` |
| 停止后端 | `./scripts/stop.sh --backend-only` | `make stop-backend` | `pc-stop-b` |
| 前端日志 | `tail -f logs/frontend.log` | `make logs-frontend` | `pc-logs-f` |
| 后端日志 | `tail -f logs/backend.log` | `make logs-backend` | `pc-logs-b` |

## 🔧 故障排除

### 端口被占用
```bash
# 停止所有服务
./scripts/stop.sh

# 手动清理端口
lsof -ti:3000 | xargs kill -9  # 前端
lsof -ti:8000 | xargs kill -9  # 后端
```

### 依赖问题
```bash
# 重新安装依赖
make install

# 或手动安装
cd backend && uv pip install -e . --dev
cd frontend && yarn install
```

### 权限问题
```bash
# 确保脚本有执行权限
chmod +x scripts/*.sh
```

## 📋 环境要求

- **Python 3.8+** (后端)
- **Node.js 16+** (前端)
- **uv** (Python包管理器)
- **yarn** (Node.js包管理器)

### 安装依赖工具
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 yarn
npm install -g yarn
```

## 🎯 开发工作流

### 日常开发
```bash
# 1. 启动开发环境
make dev

# 2. 查看服务状态
make status

# 3. 查看日志
make logs

# 4. 代码检查
make lint

# 5. 停止服务
make stop
```

### 生产部署
```bash
# 1. 构建前端
make build

# 2. 启动生产服务
# (需要配置生产环境变量)
make start
```

---

🎉 **现在你可以轻松管理 Prompt Center 服务了！**

选择你喜欢的方式：
- 📜 **脚本方式** - 详细输出，适合调试
- 🔨 **Makefile方式** - 标准化，适合团队
- ⚡ **别名方式** - 最快捷，适合日常开发
