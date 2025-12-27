# 实现计划

- [x] 1. 项目初始化和基础架构

  - [x] 1.1 创建项目目录结构和配置文件
    - 创建app/目录及子目录（models, schemas, services, routers, utils）
    - 创建requirements.txt，包含FastAPI, SQLAlchemy, PyMySQL, uvicorn, python-multipart, openpyxl, hypothesis, APScheduler等依赖
    - 创建.env.example环境变量模板（包含MySQL连接配置、SMTP邮箱配置）
    - _Requirements: 11.1, 11.2_

  - [x] 1.2 实现数据库连接和配置管理
    - 创建app/config.py，支持环境变量配置（MySQL主机、端口、用户名、密码、数据库名、SMTP配置）
    - 创建app/database.py，实现SQLAlchemy MySQL 8.0数据库连接
    - _Requirements: 11.2, 11.3_

  - [x] 1.3 创建FastAPI应用入口
    - 创建app/main.py，配置CORS、静态文件、路由挂载
    - _Requirements: 11.1_

- [x] 2. 数据模型实现

  - [x] 2.1 实现组织结构模型（College, Grade, Class）
    - 创建app/models/college.py, grade.py, class_.py
    - 定义外键关系和级联删除
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 1.6, 1.7_

  - [x] 2.2 编写属性测试：组织结构创建一致性
    - **Property 1: 组织结构创建一致性**
    - **Validates: Requirements 1.1, 1.2, 1.3**

  - [x] 2.3 编写属性测试：级联删除一致性
    - **Property 3: 级联删除一致性**
    - **Validates: Requirements 1.5, 1.6, 1.7**

  - [x] 2.4 实现成员模型（Member）
    - 创建app/models/member.py
    - 包含学号、姓名、性别、寝室号、QQ邮箱字段
    - _Requirements: 2.4_






  - [x] 2.5 编写属性测试：成员CRUD操作一致性

    - **Property 5: 成员CRUD操作一致性**
    - **Validates: Requirements 2.4, 2.5, 2.6**
  - [x] 2.6 实现任务和提交模型（Task, Submission）

    - 创建app/models/task.py, submission.py


    - 包含截止时间、上传限制、文件类型、自动提醒时间等配置
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.1_


  - [x] 2.7 实现管理员和设置模型（Admin, Setting）
    - 创建app/models/admin.py, setting.py
    - 包含密码哈希、登录失败计数、锁定时间
    - _Requirements: 10.1, 10.4_

  - [x] 2.8 实现提醒记录模型（ReminderLog）
    - 创建app/models/reminder_log.py
    - 包含任务ID、成员ID、邮箱、发送状态、发送时间
    - _Requirements: 9.6_

- [x] 3. Pydantic模式定义

  - [x] 3.1 创建所有实体的请求/响应模式
    - 创建app/schemas/目录下所有模式文件
    - 定义Create, Update, Response模式
    - 包含邮件提醒相关模式
    - _Requirements: 1.1-1.7, 2.4-2.6, 3.1-3.7, 9.1-9.7_

- [x] 4. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 5. 组织结构管理服务和API

  - [x] 5.1 实现OrganizationService
    - 创建app/services/organization.py
    - 实现学院、年级、班级的CRUD和级联删除
    - _Requirements: 1.1-1.7_

  - [x] 5.2 实现组织结构API路由
    - 创建app/routers/colleges.py, grades.py, classes.py
    - 实现GET, POST, PUT, DELETE端点
    - _Requirements: 1.1-1.7_

  - [x] 5.3 编写属性测试：组织结构更新保持关联完整性
    - **Property 2: 组织结构更新保持关联完整性**
    - **Validates: Requirements 1.4**

- [x] 6. 成员管理服务和API

  - [x] 6.1 实现MemberService
    - 创建app/services/member.py
    - 实现成员CRUD、导入导出逻辑
    - _Requirements: 2.1-2.7_

  - [x] 6.2 实现成员导入导出功能
    - 实现模板下载（Excel/CSV格式）
    - 实现批量导入解析和冲突处理
    - 实现成员列表导出
    - _Requirements: 2.1, 2.2, 2.3, 2.7_

  - [x] 6.3 编写属性测试：成员导入导出往返一致性
    - **Property 4: 成员导入导出往返一致性**
    - **Validates: Requirements 2.2, 2.7**

  - [x] 6.4 实现成员API路由
    - 创建app/routers/members.py
    - 实现CRUD、模板下载、导入导出端点
    - _Requirements: 2.1-2.7_

- [x] 7. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 8. 收集任务管理服务和API

  - [x] 8.1 实现TaskService
    - 创建app/services/task.py
    - 实现任务CRUD、配置管理、统计计算
    - _Requirements: 3.1-3.7, 6.1, 6.3_

  - [x] 8.2 编写属性测试：收集任务配置持久化
    - **Property 6: 收集任务配置持久化**
    - **Validates: Requirements 3.1, 3.6_

  - [x] 8.3 编写属性测试：统计数据准确性
    - **Property 16: 统计数据准确性**
    - **Validates: Requirements 6.1, 6.3**

  - [x] 8.4 实现任务API路由
    - 创建app/routers/tasks.py
    - 实现CRUD、统计端点
    - _Requirements: 3.1-3.7, 6.1-6.4_

- [x] 9. 文件上传服务和API

  - [x] 9.1 实现SubmissionService
    - 创建app/services/submission.py
    - 实现文件上传、验证、存储逻辑
    - 实现截止时间、上传次数、文件类型验证
    - _Requirements: 4.1-4.7_

  - [x] 9.2 编写属性测试：截止时间强制执行
    - **Property 7: 截止时间强制执行**
    - **Validates: Requirements 3.2, 4.4**

  - [x] 9.3 编写属性测试：上传次数限制强制执行
    - **Property 8: 上传次数限制强制执行**
    - **Validates: Requirements 3.3, 4.5**

  - [x] 9.4 编写属性测试：文件修改权限控制
    - **Property 9: 文件修改权限控制**
    - **Validates: Requirements 3.4, 4.6**

  - [x] 9.5 编写属性测试：文件类型验证
    - **Property 11: 文件类型验证**
    - **Validates: Requirements 4.3**

  - [x] 9.6 编写属性测试：上传状态标记一致性
    - **Property 12: 上传状态标记一致性**
    - **Validates: Requirements 4.7**

  - [x] 9.7 实现文件上传API路由
    - 创建app/routers/submissions.py
    - 实现上传、替换、删除端点
    - _Requirements: 4.1-4.7_

- [x] 10. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 11. 批量导出服务

  - [x] 11.1 实现命名格式处理工具
    - 创建app/utils/naming.py
    - 实现变量解析和替换逻辑
    - _Requirements: 5.2, 5.3, 5.4_

  - [x] 11.2 编写属性测试：命名格式正确应用
    - **Property 14: 命名格式正确应用**
    - **Validates: Requirements 5.2, 5.3, 5.4**

  - [x] 11.3 实现ExportService
    - 创建app/services/export.py
    - 实现批量导出、ZIP打包、文件重命名
    - _Requirements: 5.1, 5.5, 5.6_

  - [x] 11.4 编写属性测试：批量导出完整性
    - **Property 13: 批量导出完整性**
    - **Validates: Requirements 5.1**

  - [x] 11.5 编写属性测试：选择性导出过滤
    - **Property 15: 选择性导出过滤**
    - **Validates: Requirements 5.5**

  - [x] 11.6 实现导出API端点
    - 在submissions路由中添加导出端点
    - 在settings路由中添加命名格式设置端点
    - _Requirements: 5.1-5.6_

- [x] 12. 认证服务和API

  - [x] 12.1 实现AuthService
    - 创建app/services/auth.py
    - 实现密码哈希、登录验证、账号锁定
    - _Requirements: 7.1-7.4_

  - [x] 12.2 编写属性测试：管理功能认证保护
    - **Property 17: 管理功能认证保护**
    - **Validates: Requirements 7.2**

  - [x] 12.3 编写属性测试：账号锁定机制
    - **Property 18: 账号锁定机制**
    - **Validates: Requirements 7.4**

  - [x] 12.4 实现认证API路由
    - 创建app/routers/auth.py
    - 实现登录、初始设置端点
    - _Requirements: 7.1-7.4_

  - [x] 12.5 添加认证中间件
    - 为管理功能路由添加认证依赖
    - _Requirements: 7.2_

  - [x] 12.6 编写属性测试：管理员可见性控制
    - **Property 10: 管理员可见性控制**
    - **Validates: Requirements 3.5**

- [x] 13. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 14. 邮件提醒服务

  - [x] 14.1 实现邮件模板工具
    - 创建app/utils/email_template.py
    - 实现提醒邮件HTML模板，包含任务名称、截止时间、提交链接
    - _Requirements: 9.5_

  - [x] 14.2 实现EmailService
    - 创建app/services/email.py
    - 实现QQ邮箱SMTP发送功能
    - 实现批量发送和单独发送
    - _Requirements: 9.3, 9.4, 9.7_

  - [x] 14.3 编写属性测试：提醒邮件内容完整性
    - **Property 21: 提醒邮件内容完整性**
    - **Validates: Requirements 9.5**

  - [x] 14.4 实现SchedulerService
    - 创建app/services/scheduler.py
    - 使用APScheduler实现自动提醒定时任务
    - _Requirements: 9.1, 9.2_

  - [x] 14.5 编写属性测试：自动提醒触发准确性
    - **Property 20: 自动提醒触发准确性**
    - **Validates: Requirements 9.1, 9.2**

  - [x] 14.6 编写属性测试：提醒记录完整性
    - **Property 22: 提醒记录完整性**
    - **Validates: Requirements 9.6**

  - [x] 14.7 实现提醒API端点
    - 在tasks路由中添加手动提醒端点
    - 在settings路由中添加SMTP配置端点
    - _Requirements: 9.3, 9.4, 9.7_

- [x] 15. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 16. 前端界面实现

  - [x] 16.1 创建基础HTML结构和样式
    - 创建static/index.html主页面
    - 创建static/css/style.css样式文件
    - _Requirements: 4.1_

  - [x] 16.2 实现组织结构管理界面
    - 学院、年级、班级的列表和表单
    - _Requirements: 1.1-1.7_

  - [x] 16.3 实现成员管理界面
    - 成员列表、导入导出、模板下载（包含QQ邮箱字段）
    - _Requirements: 2.1-2.7_

  - [x] 16.4 实现收集任务管理界面
    - 任务创建、配置、统计显示
    - 包含自动提醒时间设置
    - _Requirements: 3.1-3.7, 6.1-6.4, 9.1_

  - [x] 16.5 实现文件上传界面
    - 成员列表点击上传、进度显示、状态标记
    - _Requirements: 4.1-4.7_

  - [x] 16.6 实现批量导出界面
    - 命名格式设置、选择导出、下载
    - _Requirements: 5.1-5.6_

  - [x] 16.7 实现登录界面
    - 管理员登录、初始设置
    - _Requirements: 10.1-10.3_

  - [x] 16.8 实现提醒管理界面
    - 手动提醒按钮、选择成员提醒、SMTP配置界面
    - 提醒发送记录查看
    - _Requirements: 9.3, 9.4, 9.6, 9.7_

- [x] 17. 文件存储配置

  - [x] 17.1 实现文件处理工具
    - 创建app/utils/file_handler.py
    - 实现文件保存、路径管理
    - _Requirements: 11.3_

  - [x] 17.2 编写属性测试：文件存储路径可配置
    - **Property 19: 文件存储路径可配置**
    - **Validates: Requirements 11.3**

- [x] 18. Docker部署配置

  - [x] 18.1 创建Dockerfile
    - 基于Python镜像，安装依赖，配置启动命令
    - _Requirements: 11.4_

  - [x] 18.2 创建docker-compose.yml
    - 配置应用服务、MySQL 8.0服务、卷挂载、环境变量
    - 配置MySQL数据持久化
    - _Requirements: 11.4_

- [x] 19. 文档编写

  - [x] 19.1 创建README.md部署和运行说明
    - 包含本地开发、Docker部署、环境变量配置说明
    - 包含QQ邮箱SMTP配置说明
    - _Requirements: 11.5_

- [x] 20. Final Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。
