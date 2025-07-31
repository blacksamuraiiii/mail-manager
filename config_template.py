"""
配置文件模板 - 安全的配置管理
将此文件复制为 config.py 并填入实际配置
"""

import os
from typing import Optional

# 从环境变量读取敏感信息，提高安全性
class SecureConfig:
    """安全配置管理"""
    
    @staticmethod
    def get_env_var(key: str, default: Optional[str] = None) -> str:
        """获取环境变量，支持默认值"""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"环境变量 {key} 未设置")
        return value

# --- 邮件服务器配置 ---
IMAP_SERVER = "imap.chinatelecom.cn"
IMAP_PORT = 993

# 使用环境变量存储敏感信息
USER_EMAIL = SecureConfig.get_env_var("EMAIL_USER", "your_email@chinatelecom.cn")
PASSWORD = SecureConfig.get_env_var("EMAIL_PASSWORD", "your_email_password")

# --- AI 服务配置 ---
# openai API
AI_API_KEY = SecureConfig.get_env_var("API_KEY", "sk-xxxxxxxx")
AI_BASE_URL = SecureConfig.get_env_var("BASE_URL", "https://api.openai.com/v1")
AI_MODEL = SecureConfig.get_env_var("MODEL", "gpt-4o-mini")

# --- 企业微信配置 ---
WEIXIN_CORP_ID = SecureConfig.get_env_var("WEIXIN_CORP_ID", "ww2f70eb08ff30cc13")
WEIXIN_CORP_SECRET = SecureConfig.get_env_var("WEIXIN_CORP_SECRET", "your_corp_secret")
WEIXIN_AGENT_ID = int(SecureConfig.get_env_var("WEIXIN_AGENT_ID", "1000003"))
WEIXIN_TO_USER = SecureConfig.get_env_var("WEIXIN_TO_USER", "HuangWeiShen")

# --- 可选配置 ---
# 这些配置可以通过环境变量覆盖
MAX_EMAILS_TO_SCAN = int(os.getenv("MAX_EMAILS_TO_SCAN", "200"))
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "120"))
IMAP_TIMEOUT = int(os.getenv("IMAP_TIMEOUT", "60"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))

# --- 高级配置 ---
# 邮件过滤规则（可选）
EMAIL_FILTERS = {
    "exclude_senders": [],  # 排除的发件人列表
    "include_keywords": [],  # 包含关键词的邮件
    "exclude_keywords": ["退订", "取消订阅", "unsubscribe"],  # 排除关键词
    "min_content_length": 10,  # 最小内容长度
}

# 摘要配置
SUMMARY_CONFIG = {
    "max_content_length": 500,  # 每封邮件最大内容长度
    "include_attachments_info": True,  # 是否包含附件信息
    "timezone_offset": 8,  # 时区偏移（小时）
}

# 日志配置
LOG_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "file": os.getenv("LOG_FILE", "email_manager.log"),
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
}