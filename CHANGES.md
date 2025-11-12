# OpenWebUI 三权分立定制版 - 文件修改清单

## 新增文件

### 后端文件
1. `backend/open_webui/models/audit_logs.py` - 审计日志数据模型
2. `backend/open_webui/models/login_logs.py` - 登录日志数据模型
3. `backend/open_webui/routers/audit.py` - 审计日志 API 路由
4. `backend/open_webui/migrations/versions/add_three_admin_roles_and_audit.py` - 数据库迁移脚本

### 前端文件
5. `src/routes/(app)/audit-admin/+page.svelte` - 审计管理员主页
6. `src/routes/(app)/audit-admin/+layout.svelte` - 审计管理员布局文件
7. `src/routes/(app)/audit-admin/audit-logs/+page.svelte` - 审计日志查询页面
8. `src/routes/(app)/audit-admin/login-logs/+page.svelte` - 登录日志查询页面

### 文档和脚本
9. `DEPLOY.sh` - 自动化部署脚本
10. `DEPLOYMENT_GUIDE.md` - 部署和使用指南
11. `VALIDATION_REPORT.md` - 验证报告
12. `CHANGES.md` - 本文件

## 修改的文件

### 后端文件
1. `backend/open_webui/utils/auth.py`
   - 新增 `get_system_admin()` 装饰器
   - 新增 `get_auth_admin()` 装饰器
   - 新增 `get_audit_admin()` 装饰器
   - 新增 `get_any_admin()` 装饰器
   - 新增 `get_system_or_auth_admin()` 装饰器
   - 修改 `get_verified_user()` 支持新角色
   - 修改 `get_admin_user()` 支持新角色

2. `backend/open_webui/utils/audit.py`
   - 新增 `_determine_action()` 方法
   - 新增 `_extract_resource_type()` 方法
   - 新增 `_extract_resource_id()` 方法
   - 增强 `_log_audit_entry()` 方法，支持写入数据库

3. `backend/open_webui/routers/users.py`
   - 修改 `get_users()` 权限为 `auth_admin`
   - 修改 `update_user_role()` 权限为 `auth_admin`

4. `backend/open_webui/routers/auths.py`
   - 在 `signin()` 中添加登录日志记录

5. `backend/open_webui/main.py`
   - 导入 `audit` 路由模块
   - 注册 `/api/v1/audit` 路由

### 前端文件
6. `src/lib/components/layout/Sidebar.svelte`
   - 添加"安全审计"菜单项（仅对 `audit_admin` 可见）
   - 修改工作区菜单的角色检查，支持 `system_admin`

## 核心功能实现

### 1. 三权分立角色系统
- **system_admin**: 系统管理员，负责系统配置和模型管理
- **auth_admin**: 授权管理员，负责用户和权限管理
- **audit_admin**: 安全审计员，负责审计所有操作

### 2. 审计日志系统
- 自动记录所有 API 操作
- 支持多维度查询和筛选
- 敏感信息自动脱敏
- 提供审计摘要报告

### 3. 登录日志系统
- 记录所有登录尝试（成功和失败）
- 支持多种登录方式
- 提供登录摘要报告

### 4. 前端审计界面
- 审计仪表盘
- 审计日志查询
- 登录日志查询
- 角色权限保护

## 数据库变更

### 新增表
1. `audit_log` - 审计日志表
   - 包含 5 个索引：user_id, timestamp, action, resource_type, user_role

2. `login_log` - 登录日志表
   - 包含 4 个索引：user_id, timestamp, status, user_email

## 兼容性说明

- 基于 OpenWebUI v0.6.5
- 向后兼容原有的 `admin` 角色
- 不影响现有功能
- 可以通过迁移脚本安全升级

## 部署要求

- Python 3.10+
- Node.js 18.0+
- 数据库支持（SQLite/PostgreSQL/MySQL）
- 运行迁移脚本创建新表

## 测试状态

✅ 所有 Python 文件语法检查通过
✅ 数据库模型验证通过
✅ API 路由验证通过
✅ 前端组件验证通过
✅ 权限控制验证通过

## 版本信息

- 原始版本: OpenWebUI v0.6.5
- 定制版本: v0.6.5-custom-three-admin-roles
- 发布日期: 2025-11-12
