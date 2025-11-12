# OpenWebUI Three-Admin-Roles Edition

基于 OpenWebUI v0.6.5 的三权分立定制版本，遵循分级保护要求实现系统管理、授权管理和安全审计的职责分离。

## 🎯 核心特性

本版本将原有的超级管理员（admin）权限拆分为三个相互独立的管理员角色：

- **系统管理员 (system_admin)**: 负责系统配置、模型管理、知识库管理等核心功能
- **授权管理员 (auth_admin)**: 负责用户管理、角色分配、权限设置
- **安全审计员 (audit_admin)**: 负责审计所有用户和管理员的操作，拥有独立的审计界面

## 📋 主要功能

### 1. 三权分立角色系统
- ✅ 三种管理员角色权限完全隔离
- ✅ 每个角色仅拥有最小必要权限
- ✅ 向后兼容原有的 admin 角色

### 2. 审计日志系统
- ✅ 自动记录所有 API 操作到数据库
- ✅ 支持多维度查询（用户、角色、操作类型、资源类型、时间范围、IP地址）
- ✅ 敏感信息自动脱敏（密码等）
- ✅ 提供审计摘要报告

### 3. 登录日志系统
- ✅ 记录所有登录尝试（成功和失败）
- ✅ 支持多种登录方式追踪
- ✅ 记录失败原因和IP地址
- ✅ 提供登录摘要报告

### 4. 审计管理员专属界面
- ✅ 审计仪表盘（展示7天统计数据）
- ✅ 审计日志查询页面
- ✅ 登录日志查询页面
- ✅ 角色权限保护

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18.0+
- 数据库（SQLite/PostgreSQL/MySQL）

### 部署步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/zihaoli-cn/open-webui-three-roles.git
   cd open-webui-three-roles
   ```

2. **运行部署脚本**
   ```bash
   chmod +x DEPLOY.sh
   ./DEPLOY.sh
   ```

3. **配置环境变量**
   ```bash
   cp backend/.env.example backend/.env
   # 编辑 backend/.env 文件进行配置
   ```

4. **启动服务**
   ```bash
   cd backend
   ./start.sh
   ```

5. **访问系统**
   
   打开浏览器访问 `http://localhost:8080`

### 初始管理员设置

1. **创建系统管理员**: 第一个注册的用户会自动成为 `system_admin`

2. **创建其他管理员**: 注册两个新用户，然后通过数据库设置角色：
   ```sql
   -- 设置授权管理员
   UPDATE users SET role = 'auth_admin' WHERE email = 'auth-admin@example.com';
   
   -- 设置安全审计员
   UPDATE users SET role = 'audit_admin' WHERE email = 'audit-admin@example.com';
   ```

## 📖 详细文档

- [部署与使用指南](DEPLOYMENT_GUIDE.md)
- [验证报告](VALIDATION_REPORT.md)
- [文件修改清单](CHANGES.md)

## 🔒 安全特性

- **权限隔离**: 三种管理员角色权限互不重叠
- **审计完整性**: 所有操作自动记录，无法篡改
- **敏感信息保护**: 密码等敏感信息自动脱敏
- **登录追踪**: 所有登录尝试都被记录
- **角色保护**: 前后端双重权限验证

## 📊 角色权限对照表

| 功能 | system_admin | auth_admin | audit_admin | user |
|:---|:---:|:---:|:---:|:---:|
| 系统配置 | ✅ | ❌ | ❌ | ❌ |
| 模型管理 | ✅ | ❌ | ❌ | ❌ |
| 知识库管理 | ✅ | ❌ | ❌ | ❌ |
| 用户管理 | ❌ | ✅ | ❌ | ❌ |
| 角色分配 | ❌ | ✅ | ❌ | ❌ |
| 审计日志查询 | ❌ | ❌ | ✅ | ❌ |
| 登录日志查询 | ❌ | ❌ | ✅ | ❌ |
| 聊天功能 | ✅ | ✅ | ✅ | ✅ |

## 🗄️ 数据库变更

本版本新增了两个数据库表：

1. **audit_log**: 审计日志表
   - 包含 5 个索引：user_id, timestamp, action, resource_type, user_role

2. **login_log**: 登录日志表
   - 包含 4 个索引：user_id, timestamp, status, user_email

## 🔧 技术实现

### 后端修改
- 新增审计日志和登录日志数据模型
- 新增审计 API 路由（仅限 audit_admin 访问）
- 增强审计中间件，支持数据库记录
- 修改用户管理路由权限（仅限 auth_admin 访问）
- 添加三种管理员角色的权限装饰器

### 前端修改
- 新增审计管理员专属界面
- 在侧边栏添加"安全审计"菜单（仅对 audit_admin 可见）
- 实现审计日志查询和筛选功能
- 实现登录日志查询和筛选功能

## 📝 版本信息

- **原始版本**: OpenWebUI v0.6.5
- **定制版本**: v0.6.5-three-admin-roles
- **发布日期**: 2025-11-12

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目基于 OpenWebUI 的原始许可证。

## 🙏 致谢

感谢 [OpenWebUI](https://github.com/open-webui/open-webui) 项目提供的优秀基础。

---

**注意**: 本版本专为满足分级保护要求而定制，适合需要严格权限分离和审计功能的企业和组织使用。
