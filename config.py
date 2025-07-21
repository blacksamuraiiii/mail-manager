# config.py

# --- 邮箱配置 ---
IMAP_SERVER = "imap.chinatelecom.cn"
IMAP_PORT = 993
USER_EMAIL = "your_email@chinatelecom.cn"  # 替换为你的邮箱
PASSWORD = "your_email_password"          # 替换为你的邮箱密码

# --- AI 服务配置 ---
# 使用 DeepSeek API
AI_API_KEY = "sk-xxxxxxxx"  # 替换为你的 DeepSeek API Key
AI_BASE_URL = "https://api.deepseek.com"
AI_MODEL = "deepseek-chat"

# --- 企业微信推送配置 ---
WEIXIN_CORP_ID = "ww2f70eb08ff30cc13"      # 你的企业ID
WEIXIN_CORP_SECRET = "9jxgpMxrB-m-....."   # 你的应用Secret
WEIXIN_AGENT_ID = 1000003                 # 你的应用AgentId
# 推送目标用户, "@all" 表示所有人, 或者指定成员 "User1|User2"
WEIXIN_TO_USER = "HuangWeiShen"
