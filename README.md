# 班级文件收集系统

一个基于 FastAPI + MySQL 的班级文件收集管理系统，支持学院/年级/班级管理、文件收集、批量导出、QQ邮箱提醒等功能。

## 功能特性

- 📁 **组织结构管理**: 学院 → 年级 → 班级 层级管理
- 👥 **成员管理**: Excel批量导入、导出，支持学号/姓名/性别/寝室/QQ邮箱
- 📋 **收集任务**: 创建任务、设置截止时间、上传限制、文件类型限制
- 📤 **文件上传**: 点击姓名即可上传，支持多种文件类型
- 📦 **批量导出**: ZIP打包下载，自定义命名格式（如：学号_姓名）
- 📧 **邮件提醒**: QQ邮箱自动/手动提醒未提交成员
- 📊 **统计功能**: 实时查看提交进度、未提交名单

## 快速开始

### 方式一：Docker部署（推荐）

1. 克隆项目并进入目录

2. 创建环境变量文件
```bash
cp .env.example .env
```

3. 编辑 `.env` 文件，配置必要参数：
```env
SECRET_KEY=your-random-secret-key
MYSQL_ROOT_PASSWORD=your-mysql-password
SMTP_USER=your-qq-email@qq.com
SMTP_PASSWORD=your-smtp-authorization-code
SITE_URL=http://your-domain.com
```

4. 启动服务
```bash
docker-compose up -d
```

5. 访问 http://localhost:8000

### 方式二：本地开发

1. 安装 Python 3.9+

2. 安装 MySQL 8.0 并创建数据库
```sql
CREATE DATABASE class_collection CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件配置数据库连接
```

5. 启动服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. 访问 http://localhost:8000

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| SECRET_KEY | JWT密钥 | - |
| DB_HOST | MySQL主机 | localhost |
| DB_PORT | MySQL端口 | 3306 |
| DB_USER | MySQL用户 | root |
| DB_PASSWORD | MySQL密码 | - |
| DB_NAME | 数据库名 | class_collection |
| UPLOAD_DIR | 上传目录 | ./uploads |
| SMTP_HOST | SMTP服务器 | smtp.qq.com |
| SMTP_PORT | SMTP端口 | 465 |
| SMTP_USER | 邮箱账号 | - |
| SMTP_PASSWORD | SMTP授权码 | - |
| SITE_URL | 网站URL | http://localhost:8000 |


## QQ邮箱SMTP配置

1. 登录 QQ邮箱 → 设置 → 账户
2. 开启 "POP3/SMTP服务"
3. 生成授权码（不是QQ密码）
4. 将授权码填入 `SMTP_PASSWORD`

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
├── app/
│   ├── main.py          # 应用入口
│   ├── config.py        # 配置管理
│   ├── database.py      # 数据库连接
│   ├── models/          # 数据模型
│   ├── schemas/         # Pydantic模式
│   ├── services/        # 业务逻辑
│   ├── routers/         # API路由
│   └── utils/           # 工具函数
├── static/              # 前端静态文件
├── uploads/             # 上传文件存储
├── tests/               # 测试文件
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 使用说明

1. **首次使用**: 访问系统后设置管理员账号密码
2. **创建组织**: 依次创建学院 → 年级 → 班级
3. **导入成员**: 下载模板 → 填写信息 → 上传导入
4. **创建任务**: 选择班级 → 设置任务参数 → 创建
5. **收集文件**: 成员点击自己名字上传文件
6. **导出文件**: 点击导出按钮下载ZIP包

## 技术栈

- **后端**: FastAPI, SQLAlchemy, PyMySQL
- **数据库**: MySQL 8.0
- **前端**: HTML5, CSS3, JavaScript
- **部署**: Docker, Uvicorn

## License

MIT
