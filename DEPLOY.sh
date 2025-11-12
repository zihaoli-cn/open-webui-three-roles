#!/bin/bash

# OpenWebUI Three-Admin-Roles Deployment Script
# This script helps deploy the customized OpenWebUI with three-admin-roles feature

set -e

echo "=========================================="
echo "OpenWebUI 三权分立部署脚本"
echo "=========================================="
echo ""

# Check if running in the correct directory
if [ ! -f "package.json" ] || [ ! -d "backend" ]; then
    echo "错误: 请在 OpenWebUI 项目根目录运行此脚本"
    exit 1
fi

echo "步骤 1: 检查依赖..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"
echo "✓ Node.js 版本: $(node --version)"
echo ""

echo "步骤 2: 安装后端依赖..."
echo ""
cd backend
pip3 install -r requirements.txt
cd ..

echo ""
echo "步骤 3: 运行数据库迁移..."
echo ""
cd backend
python3 -m alembic upgrade head
cd ..

echo ""
echo "步骤 4: 安装前端依赖..."
echo ""
npm install

echo ""
echo "步骤 5: 构建前端..."
echo ""
npm run build

echo ""
echo "=========================================="
echo "部署完成!"
echo "=========================================="
echo ""
echo "后续步骤:"
echo "1. 配置环境变量 (参考 .env.example)"
echo "2. 启动后端服务: cd backend && ./start.sh"
echo "3. 访问 http://localhost:8080"
echo ""
echo "首次登录后，系统会自动创建第一个用户为 system_admin"
echo "然后需要手动创建 auth_admin 和 audit_admin 用户"
echo ""
echo "详细文档请参考 DEPLOYMENT_GUIDE.md"
echo ""
