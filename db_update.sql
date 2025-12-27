-- 数据库更新脚本 - 班级文件收集系统增强功能
-- 在 MySQL 中执行此脚本
-- 数据库名: class_collection

USE class_collection;

-- 1. 更新 submissions 表的 file_type 列长度（防止 MIME 类型过长）
ALTER TABLE submissions MODIFY COLUMN file_type VARCHAR(100);

-- 2. 为 tasks 表添加新字段（忽略已存在的错误）
-- 如果列已存在会报错，可以忽略

-- 收集类型配置 (JSON格式: {file:true, text:false, image:false, questionnaire:false})
ALTER TABLE tasks ADD COLUMN collect_types JSON COMMENT '收集类型配置';

-- 每人需要提交的项目数
ALTER TABLE tasks ADD COLUMN items_per_person INT DEFAULT 1 COMMENT '每人需要提交的项目数';

-- 问卷配置 (JSON数组: [{type, title, options, required}])
ALTER TABLE tasks ADD COLUMN questionnaire_config JSON COMMENT '问卷配置';

-- 是否允许用户自选可见性
ALTER TABLE tasks ADD COLUMN allow_user_set_visibility BOOLEAN DEFAULT TRUE COMMENT '是否允许用户自选可见性';

-- 3. 为 submissions 表添加新字段

-- 提交类型: file, text, image, questionnaire
ALTER TABLE submissions ADD COLUMN submission_type VARCHAR(20) DEFAULT 'file' COMMENT '提交类型';

-- 文本内容（text类型使用）
ALTER TABLE submissions ADD COLUMN text_content TEXT COMMENT '文本内容';

-- 问卷答案（questionnaire类型使用）
ALTER TABLE submissions ADD COLUMN questionnaire_answers JSON COMMENT '问卷答案';

-- 是否仅管理员可见
ALTER TABLE submissions ADD COLUMN is_private BOOLEAN DEFAULT FALSE COMMENT '是否仅管理员可见';

-- 第几项提交（用于多项提交）
ALTER TABLE submissions ADD COLUMN item_index INT DEFAULT 1 COMMENT '第几项提交';

-- 确保 updated_at 列存在
ALTER TABLE submissions ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间';

-- 完成提示
SELECT '数据库更新完成！如果某些 ALTER 语句报错说列已存在，可以忽略。' AS message;
