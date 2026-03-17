#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送团队规划文档到少帅邮箱
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# 邮箱配置
SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 587
SENDER_EMAIL = '417895006@qq.com'
SENDER_PASSWORD = 'lgnzpppvjvfmcadj'
RECEIVER_EMAIL = 'szideaf7@163.com'

# 文件路径
FILE1 = '/root/.openclaw/workspace/03_输出成果/九星智囊团运营监控机制.docx'
FILE2 = '/root/.openclaw/workspace/03_输出成果/九星智囊团能力审计与创新规划.docx'

def send_email():
    """发送邮件"""
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f'【南乔】九星智囊团团队规划文档_{datetime.now().strftime("%Y-%m-%d")}'
    
    # 邮件正文
    body = f"""
少帅您好！

南乔已完成团队规划和能力审计，生成以下2份文档：

1. 九星智囊团运营监控机制.docx
   - 监控维度
   - 运营机制
   - 产出物管理
   - 团队协作机制
   - 南乔职责
   - 应急预案
   - 成功标准

2. 九星智囊团能力审计与创新规划.docx
   - 现有技能清单（25个）
   - 团队能力矩阵
   - 创新方向规划
   - 推荐行动计划
   - 推荐安装技能及理由
   - 新Agent规划
   - 团队发展路线图

请查阅！

南乔 🌿
{datetime.now().strftime("%Y-%m-%d %H:%M")}
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 附件1
    with open(FILE1, 'rb') as f:
        part1 = MIMEBase('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document')
        part1.set_payload(f.read())
        encoders.encode_base64(part1)
        part1.add_header('Content-Disposition', 'attachment', filename='九星智囊团运营监控机制.docx')
        msg.attach(part1)
    
    # 附件2
    with open(FILE2, 'rb') as f:
        part2 = MIMEBase('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document')
        part2.set_payload(f.read())
        encoders.encode_base64(part2)
        part2.add_header('Content-Disposition', 'attachment', filename='九星智囊团能力审计与创新规划.docx')
        msg.attach(part2)
    
    # 发送邮件
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f'✅ 邮件发送成功！')
        print(f'收件人：{RECEIVER_EMAIL}')
        print(f'附件：')
        print(f'  1. 九星智囊团运营监控机制.docx')
        print(f'  2. 九星智囊团能力审计与创新规划.docx')
        return True
    except Exception as e:
        print(f'❌ 邮件发送失败：{e}')
        return False

if __name__ == '__main__':
    send_email()
