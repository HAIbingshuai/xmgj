# 项目管家

> 个人事项常态/长时间跟进追踪系统

基于 Django 4.2.30 + Bootstrap 5 的个人任务管理工具，支持时间轴分阶段跟踪、步骤管理、附件/图片上传、操作记录日志。

---

## 功能特性

### 📋 事项管理
- 创建/编辑/删除事项
- 按状态分组展示（进行中/未开始/已完成/暂停）
- 按标签快速筛选
- 仪表盘统计总览

### ⏳ 时间轴节点
- 垂直时间轴可视化
- 每个节点代表一个阶段
- 节点状态：待处理/进行中/已完成/已跳过
- 节点编辑弹窗（预填数据）

### ✅ 步骤管理
- 每个节点包含多个步骤
- 步骤状态：未开始/进行中/已完成/受阻
- 行内编辑（AJAX 无刷新保存）
- 步骤展开/收拢查看详情

### 📎 附件与图片
- 附件上传/下载/删除
- 图片上传/预览/删除
- 支持多选上传，实时进度条
- 根据 MIME 类型自动归类

### 📝 操作记录
- 自动记录所有操作变更
- 按日期分组的时间线展示
- 4色圆点分类（创建/更新/完成/问题）

---

## 技术栈

| 前端 | 后端 | 数据库 | 插件 |
|------|------|--------|------|
| Bootstrap 5 | Django 4.2.30 | SQLite | flatpickr（日期选择） |
| Bootstrap Icons | Python 3 | | Tom Select（选择框增强） |
| 自定义 CSS（CSS 变量） | | | |

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/HAIbingshuai/xmgj.git
cd xmgj
```

### 2. 安装依赖

```bash
pip install django
```

### 3. 初始化数据库

```bash
python manage.py migrate
```

### 4. 创建管理员（可选）

```bash
python manage.py createsuperuser
```

### 5. 启动服务

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000

---

## 使用流程

```
注册 → 登录 → 创建事项 → 添加时间轴节点 → 添加步骤
                                            → 上传附件/图片
                                            → 勾选完成
                                            → 记录结果
```

---

## 项目结构

```
xmgj/
├── manage.py
├── XMGJ_app/              # 主应用
│   ├── models.py          # 5个数据模型
│   ├── views.py           # 18个视图
│   ├── forms.py           # 表单类
│   ├── urls.py            # 路由
│   ├── templatetags/      # 模板过滤器
│   └── static/xmgj/       # CSS + JS
├── templates/xmgj/        # 模板文件
│   ├── includes/          # 组件模板
│   │   ├── node_card.html
│   │   ├── node_detail_panel.html
│   │   ├── step_card.html
│   │   ├── node_form_modal.html
│   │   ├── step_form_modal.html
│   │   └── ...
│   └── auth/              # 登录/注册
├── docs/                  # 设计文档
├── design_mockup/         # 视觉设计稿
└── xmgj/                  # Django项目配置
```

---

## 数据模型

| 模型 | 说明 |
|------|------|
| `Item` | 事项（标题/状态/优先级） |
| `TimelineNode` | 时间轴节点（日期/概要/状态） |
| `NodeStep` | 步骤（标题/内容/状态/结果） |
| `NodeStepFile` | 文件（附件/图片） |
| `NodeAction` | 操作日志 |
