#!/usr/bin/env python3
"""
邮件管家 - 重构简化版
Email Manager - Simplified Refactored Version
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
import schedule
import time
import json
import imaplib
import email
import socket
import re
import logging
from email.header import decode_header
from email.utils import parsedate_to_datetime
from typing import List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# 从 dotenv 加载环境变量
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# 加载 .env 文件
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    """邮件数据结构"""
    sender: str
    recipient: str
    subject: str
    date: str
    content: str
    message_id: Optional[str] = None


class EmailProcessor:
    """邮件处理器"""

    @staticmethod
    def decode_str(s: str) -> str:
        """解码邮件头中的编码字符串"""
        if not s:
            return ""
        try:
            value, charset = decode_header(s)[0]
            if isinstance(value, bytes):
                return value.decode(charset or 'utf-8', errors='ignore')
            return str(value)
        except Exception as e:
            logger.warning(f"解码字符串失败: {e}")
            return str(s)

    @staticmethod
    def extract_main_body(text: str) -> str:
        """智能提取邮件正文"""
        if not text:
            return ""

        # 清理HTML实体
        text = text.replace('&nbsp;', ' ').strip()

        # 移除引用和转发标记
        patterns = [
            r'\n-+\s*Original Message\s*-+',
            r'\n-+\s*Forwarded message\s*-+',
            r'On.*?wrote:',
            r'在.*?写道：',
            r'发件人:.*?主题:',
            r'From:.*?Subject:'
        ]

        for pattern in patterns:
            text = re.split(pattern, text, maxsplit=1)[0]

        # 清理引用行
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if not line.strip().startswith('>')]
        text = '\n'.join(cleaned_lines)

        # 移除签名
        text = text.split('\n-- \n')[0].strip()

        # 清理多余空行
        return re.sub(r'\n\s*\n', '\n\n', text)

    @staticmethod
    def get_body_from_msg(msg: email.message.Message) -> str:
        """从邮件消息中提取正文"""
        body_plain = ""
        body_html = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_filename() or part.get('Content-Disposition', '').startswith('attachment'):
                    continue

                content_type = part.get_content_type()
                charset = part.get_content_charset() or 'utf-8'

                try:
                    if content_type == 'text/plain' and not body_plain:
                        body_plain = part.get_payload(decode=True).decode(charset, errors='ignore')
                    elif content_type == 'text/html' and not body_html:
                        body_html = part.get_payload(decode=True).decode(charset, errors='ignore')
                except Exception as e:
                    logger.warning(f"解析邮件内容失败: {e}")
                    continue
        else:
            charset = msg.get_content_charset() or 'utf-8'
            try:
                body_plain = msg.get_payload(decode=True).decode(charset, errors='ignore')
            except Exception as e:
                logger.warning(f"解析非multipart邮件失败: {e}")

        if body_plain:
            return body_plain
        elif body_html:
            soup = BeautifulSoup(body_html, 'html.parser')
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()
            return soup.get_text(separator='\n', strip=True)

        return ""


class IMAPClient:
    """IMAP客户端封装"""

    def __init__(self):
        # 从环境变量读取配置
        self.imap_server = os.getenv("IMAP_SERVER")
        self.imap_port = int(os.getenv("IMAP_PORT", 993))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.imap_timeout = int(os.getenv("IMAP_TIMEOUT", 60))
        self.max_emails_to_scan = int(os.getenv("MAX_EMAILS_TO_SCAN", 200))
        
        self.mail = None

    def connect(self) -> bool:
        """连接到IMAP服务器"""
        try:
            socket.setdefaulttimeout(self.imap_timeout)
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.email_user, self.email_password)
            self.mail.select('INBOX')
            logger.info("IMAP连接成功")
            return True
        except Exception as e:
            logger.error(f"IMAP连接失败: {e}")
            return False

    def disconnect(self):
        """断开IMAP连接"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
                logger.info("IMAP连接已关闭")
            except Exception as e:
                logger.warning(f"关闭IMAP连接时出错: {e}")
            finally:
                self.mail = None

    def search_emails_by_date(self, start_date: datetime.date, end_date: datetime.date) -> List[str]:
        """按日期搜索邮件ID"""
        if not self.mail:
            return []

        try:
            status, messages = self.mail.search(None, 'ALL')
            if status != 'OK':
                logger.error("搜索邮件失败")
                return []

            email_ids = messages[0].split()
            if not email_ids:
                logger.info("收件箱为空")
                return []

            # 限制扫描范围
            target_ids = email_ids[-self.max_emails_to_scan:]
            logger.info(f"准备扫描 {len(target_ids)} 封邮件")

            filtered_ids = []
            for num in reversed(target_ids):
                try:
                    status, data = self.mail.fetch(num, '(BODY[HEADER.FIELDS (DATE)])')
                    if status != 'OK' or not data or not data[0]:
                        continue

                    header_bytes = data[0][1]
                    msg_header = email.message_from_bytes(header_bytes)
                    date_str = msg_header['Date']

                    if not date_str:
                        continue

                    email_date = parsedate_to_datetime(date_str).date()

                    if start_date <= email_date <= end_date:
                        filtered_ids.append(num.decode() if isinstance(num, bytes) else str(num))
                    elif email_date < start_date:
                        break

                except Exception as e:
                    logger.warning(f"处理邮件ID {num} 时出错: {e}")
                    continue

            logger.info(f"找到 {len(filtered_ids)} 封符合条件的邮件")
            return filtered_ids

        except Exception as e:
            logger.error(f"搜索邮件时出错: {e}")
            return []

    def fetch_email_content(self, email_id: str) -> Optional[EmailData]:
        """获取单封邮件内容"""
        try:
            status, data = self.mail.fetch(email_id, '(RFC822)')
            if status != 'OK' or not data[0]:
                return None

            msg = email.message_from_bytes(data[0][1])

            return EmailData(
                sender=EmailProcessor.decode_str(msg['from']),
                recipient=EmailProcessor.decode_str(msg['to']),
                subject=EmailProcessor.decode_str(msg['subject']),
                date=msg['date'],
                content=EmailProcessor.get_body_from_msg(msg),
                message_id=msg.get('Message-ID')
            )

        except Exception as e:
            logger.error(f"获取邮件 {email_id} 内容失败: {e}")
            return None


class AIService:
    """AI服务封装"""

    def __init__(self):
        # 从环境变量读取配置
        self.llm_base_url = os.getenv("LLM_BASE_URL")
        self.llm_api_key = os.getenv("LLM_API_KEY")
        self.llm_model = os.getenv("LLM_MODEL")
        self.ai_timeout = int(os.getenv("AI_TIMEOUT", 120))

        self.client = OpenAI(
            api_key=self.llm_api_key,
            base_url=self.llm_base_url,
            timeout=self.ai_timeout
        )

    def summarize_emails(self, emails: List[EmailData]) -> str:
        """使用AI总结邮件"""
        if not emails:
            return f"{datetime.now().date().strftime('%Y-%m-%d')} 未收到新邮件。"

        logger.info("准备AI总结...")

        formatted_emails = []
        for i, email_data in enumerate(emails):
            content_preview = email_data.content[:300]
            if len(email_data.content) > 300:
                content_preview += '...'

            formatted_emails.append(
                f"邮件 {i+1}:\n"
                f"发件人: {email_data.sender}\n"
                f"主题: {email_data.subject}\n"
                f"日期: {email_data.date}\n"
                f"内容预览: {content_preview}\n"
            )

        ai_input = "\n\n".join(formatted_emails)

        system_prompt = (
            f"你是一个专业的邮件摘要助手。请根据以下邮件内容，为我生成一份今日（{datetime.now().date().strftime('%Y-%m-%d')}）的邮件摘要报告。"
            "报告格式如下：\n\n"
            f"今日共收到 {len(emails)} 封重要邮件，其中x封需回复，摘要如下：\n\n"
            "1. 【邮件主题】\n   - 发件人: [发件人姓名]\n   - 核心内容: [对邮件内容的1-2句话精炼总结，突出要点和待办事项]\n\n"
            "2. 【另一封邮件主题】\n   - 发件人: [发件人姓名]\n   - 核心内容: [总结...]\n\n"
            "如果邮件内容需要回复或处理，请在核心内容最后加上提醒，例如 '(需回复)'。"
            "请确保总结简明扼要，严格遵循以上格式。"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": ai_input},
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI调用失败: {e}")
            return f"AI总结失败：{str(e)}"


class WeChatNotifier:
    """企业微信通知器"""

    def __init__(self):
        # 从环境变量读取配置
        self.weixin_corp_id = os.getenv("WEIXIN_CORP_ID")
        self.weixin_corp_secret = os.getenv("WEIXIN_CORP_SECRET")
        self.weixin_agent_id = int(os.getenv("WEIXIN_AGENT_ID"))
        self.weixin_to_user = os.getenv("WEIXIN_TO_USER")

    def send_message(self, content: str) -> bool:
        """发送消息到企业微信"""
        if not content:
            logger.warning("消息内容为空，跳过发送")
            return False

        try:
            # 获取access_token
            token_url = (
                f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?"
                f"corpid={self.weixin_corp_id}&corpsecret={self.weixin_corp_secret}"
            )

            response = requests.get(token_url, timeout=10)
            response.raise_for_status()
            token_data = response.json()

            if "access_token" not in token_data:
                logger.error(f"获取access_token失败: {token_data}")
                return False

            access_token = token_data['access_token']
            push_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"

            data = {
                "touser": self.weixin_to_user,
                "msgtype": "text",
                "agentid": self.weixin_agent_id,
                "text": {"content": content},
                "safe": 0
            }

            response = requests.post(push_url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("errcode") == 0:
                logger.info("企业微信消息发送成功")
                return True
            else:
                logger.error(f"企业微信消息发送失败: {result}")
                return False

        except requests.RequestException as e:
            logger.error(f"企业微信网络请求失败: {e}")
            return False
        except Exception as e:
            logger.error(f"企业微信发送异常: {e}")
            return False


class EmailManager:
    """邮件管理器主类"""

    def __init__(self):
        self.imap_client = IMAPClient()
        self.ai_service = AIService()
        self.notifier = WeChatNotifier()
        self.max_workers = int(os.getenv("MAX_WORKERS", 4))

    def run_daily_summary(self, target_date: datetime.date = None):
        """运行每日邮件总结"""
        if target_date is None:
            target_date = datetime.now().date()

        logger.info(f"--- 每日邮件总结任务开始 ({target_date}) ---")

        try:
            # 连接IMAP
            if not self.imap_client.connect():
                return

            # 获取邮件
            email_ids = self.imap_client.search_emails_by_date(target_date, target_date)
            if not email_ids:
                summary = f"{target_date.strftime('%Y-%m-%d')} 未收到新邮件。"
            else:
                # 并行获取邮件内容
                emails = []
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    future_to_email = {
                        executor.submit(self.imap_client.fetch_email_content, email_id): email_id
                        for email_id in email_ids
                    }

                    for future in as_completed(future_to_email):
                        email_data = future.result()
                        if email_data:
                            # 清理邮件内容
                            email_data.content = EmailProcessor.extract_main_body(email_data.content)
                            emails.append(email_data)

                # AI总结
                summary = self.ai_service.summarize_emails(emails)

            # 发送通知
            logger.info(f"\n--- 生成的总结 ---\n{summary}\n")
            self.notifier.send_message(summary)

        except Exception as e:
            logger.error(f"每日总结任务失败: {e}")
            self.notifier.send_message(f"邮件总结任务执行失败: {str(e)}")
        finally:
            self.imap_client.disconnect()
            logger.info("--- 任务执行完毕 ---")


def run_once(date_str: str = None):
    """运行一次邮件总结"""
    manager = EmailManager()

    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print("日期格式错误，请使用 YYYY-MM-DD 格式")
            return
    else:
        target_date = datetime.now().date()

    print(f"正在处理 {target_date} 的邮件...")
    manager.run_daily_summary(target_date)


def run_scheduled(time_str: str = "09:00"):
    """定时运行邮件总结"""
    print(f"设置定时任务，每天 {time_str} 运行")

    schedule.every().day.at(time_str).do(lambda: EmailManager().run_daily_summary())

    print("定时任务已启动，按 Ctrl+C 退出")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n定时任务已停止")


def test_config():
    """测试配置是否正确"""
    try:
        # 检查必要环境变量
        required_vars = [
            'EMAIL_USER', 'EMAIL_PASSWORD', 'IMAP_SERVER',
            'LLM_API_KEY', 'WEIXIN_CORP_ID',
            'WEIXIN_CORP_SECRET', 'WEIXIN_AGENT_ID'
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            print(f"❌ 缺少必要配置: {', '.join(missing_vars)}")
            return False

        print("✅ 必要配置检查通过")
        
        # 尝试连接IMAP
        client = IMAPClient()
        if client.connect():
            client.disconnect()
            print("✅ IMAP连接测试成功")
            return True
        else:
            print("❌ IMAP连接测试失败")
            return False

    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='邮件管家 - 每日邮件总结工具')
    parser.add_argument('--date', '-d',
                        help='指定日期 (YYYY-MM-DD)，默认为今天')
    parser.add_argument('--schedule', '-s',
                        help='设置定时运行时间 (HH:MM)，例如 09:00')
    parser.add_argument('--test', '-t',
                        action='store_true',
                        help='测试配置是否正确')
    parser.add_argument('--version', '-v',
                        action='version',
                        version='邮件管家 v2.1 (重构简化版)')

    args = parser.parse_args()

    if args.test:
        test_config()
        return

    if args.schedule:
        run_scheduled(args.schedule)
    elif args.date:
        run_once(args.date)
    else:
        run_once()


if __name__ == '__main__':
    main()