# 📚 FastAPI 图书管理系统 (Book Management System)

基于 **Python 3.12 + FastAPI + SQLAlchemy + Jinja2** 构建的轻量级、现代化服务端渲染（SSR）后台管理系统。

本项目以极简的后端架构搭配**纯本地零依赖**（无外部 CDN）的现代化前端 UI，实现了完整的图书、出版社与作者的关联管理。非常适合作为 FastAPI 全栈开发的学习脚手架或轻量级内部管理工具。

---

## ✨ 核心特性

- **🚀 极速后端**：基于 FastAPI 框架，提供高性能的异步路由与依赖注入。
- **🗄️ 完整关系映射**：使用 SQLAlchemy ORM 完美处理复杂的数据关联：
  - **一对多 (1:N)**：出版社与图书。
  - **多对多 (N:M)**：作者与图书（包含中间关联表）。
- **🎨 现代化 UI (纯手写/零依赖)**：
  - 前端不依赖任何外部 CDN（如 Bootstrap、Vue 等），纯 HTML/CSS/JS 实现。
  - 采用 **Glassmorphism (毛玻璃)**、平滑渐变背景、柔和阴影与圆角卡片设计。
  - 原生 JavaScript 实现顺滑的 Modal (模态框) 弹窗交互。
- **⚙️ 完备的后台功能**：
  - 图书、出版社、作者的完整 **增删改查 (CRUD)**。
  - 全局支持模糊 **搜索 (Search)**。
  - 全局支持服务端 **分页 (Pagination)**。

---

## 🛠️ 技术栈

### 后端 (Backend)
- **Python 3.12**
- **FastAPI**：现代、高性能的 Web 框架。
- **SQLAlchemy**：强大的 ORM 库。
- **SQLite**：轻量级本地数据库（开箱即用，免配置）。

### 前端 (Frontend)
- **Jinja2**：强大的 Python 模板引擎。
- **HTML5 / CSS3 / Vanilla JS**：纯原生前端技术栈。

---

## 📂 项目结构

```text
book_management_system/
├── main.py              # FastAPI 后端核心代码 (路由、模型、数据库配置)
├── library.db           # SQLite 数据库文件 (运行时自动生成)
├── README.md            # 项目说明文档
└── templates/           # HTML 模板目录
    ├── base.html        # 基础样式和布局 (包含所有的本地 CSS 和 JS 逻辑)
    ├── publishers.html  # 出版社管理页面
    ├── authors.html     # 作者管理页面
    └── books.html       # 图书管理页面 (含多选关联逻辑)
```
## 安装依赖
在项目根目录下，执行以下命令安装所需依赖：
```text
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart
```
## 运行服务
```text
uvicorn main:app --reload
```
