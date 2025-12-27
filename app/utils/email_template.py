"""邮件模板工具"""
from datetime import datetime
from typing import Optional


def generate_reminder_email(
    task_title: str,
    deadline: Optional[datetime],
    submit_url: str,
    member_name: str
) -> tuple[str, str]:
    """
    生成提醒邮件内容
    
    Args:
        task_title: 任务标题
        deadline: 截止时间
        submit_url: 提交链接
        member_name: 成员姓名
    
    Returns:
        (邮件主题, 邮件HTML内容)
    """
    subject = f"【文件收集提醒】{task_title}"
    
    deadline_str = deadline.strftime("%Y年%m月%d日 %H:%M") if deadline else "未设置"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #f9f9f9;
            padding: 20px;
            border: 1px solid #ddd;
            border-top: none;
        }}
        .info-box {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }}
        .info-item {{
            margin: 10px 0;
        }}
        .info-label {{
            color: #666;
            font-size: 14px;
        }}
        .info-value {{
            font-weight: bold;
            color: #333;
        }}
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 25px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
            padding: 10px;
            border-top: 1px solid #eee;
        }}
        .warning {{
            color: #e74c3c;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h2>📋 文件收集提醒</h2>
    </div>
    <div class="content">
        <p>亲爱的 <strong>{member_name}</strong> 同学：</p>
        <p>您有一个文件收集任务尚未完成，请尽快提交！</p>
        
        <div class="info-box">
            <div class="info-item">
                <span class="info-label">任务名称：</span>
                <span class="info-value">{task_title}</span>
            </div>
            <div class="info-item">
                <span class="info-label">截止时间：</span>
                <span class="info-value warning">{deadline_str}</span>
            </div>
        </div>
        
        <p style="text-align: center;">
            <a href="{submit_url}" class="btn">立即提交 →</a>
        </p>
        
        <p style="color: #666; font-size: 14px;">
            如果按钮无法点击，请复制以下链接到浏览器打开：<br>
            <a href="{submit_url}" style="color: #667eea;">{submit_url}</a>
        </p>
    </div>
    <div class="footer">
        <p>此邮件由班级文件收集系统自动发送，请勿直接回复</p>
    </div>
</body>
</html>
"""
    
    return subject, html_content


def generate_plain_text_reminder(
    task_title: str,
    deadline: Optional[datetime],
    submit_url: str,
    member_name: str
) -> str:
    """
    生成纯文本提醒内容
    
    Args:
        task_title: 任务标题
        deadline: 截止时间
        submit_url: 提交链接
        member_name: 成员姓名
    
    Returns:
        纯文本内容
    """
    deadline_str = deadline.strftime("%Y年%m月%d日 %H:%M") if deadline else "未设置"
    
    return f"""
【文件收集提醒】

亲爱的 {member_name} 同学：

您有一个文件收集任务尚未完成，请尽快提交！

任务名称：{task_title}
截止时间：{deadline_str}

提交链接：{submit_url}

---
此邮件由班级文件收集系统自动发送，请勿直接回复
"""
