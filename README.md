# 邮件管家 - 智能邮件管理助手

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于Python的智能邮件管理工具，自动获取每日邮件，使用AI进行智能摘要，并推送到企业微信。

## ✨ 功能特性

- 📧 **智能邮件获取**：支持IMAP协议，自动获取指定日期范围的邮件
- 🤖 **AI智能摘要**：使用OpenAI GPT模型生成邮件摘要
- 📱 **企业微信推送**：自动将邮件摘要推送到企业微信
- ⚡ **并行处理**：支持多线程并行处理邮件，提升效率
- 🔒 **安全配置**：敏感信息通过环境变量管理，避免明文存储
- 🎯 **灵活过滤**：支持关键词过滤、发件人过滤等高级功能
- 📊 **详细日志**：完整的操作日志，便于调试和监控

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/blacksamuraiiii/mail-manager.git
cd email-manager

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

#### 方法1：使用环境变量（推荐）

```bash
# 复制环境变量模板
cp .env.template .env

# 编辑 .env 文件，填入你的配置
nano .env
```

#### 方法2：使用配置文件

```bash
# 复制配置模板
cp config_template.py config.py

# 编辑 config.py，填入你的配置
nano config.py
```

### 3. 配置说明

#### 邮件服务器配置

```bash
# IMAP服务器信息
EMAIL_USER=your_email@chinatelecom.cn
EMAIL_PASSWORD=your_email_password

# 支持的IMAP服务器：
# - 中国电信: imap.chinatelecom.cn:993
# - QQ邮箱: imap.qq.com:993
# - 163邮箱: imap.163.com:993
# - Gmail: imap.gmail.com:993
```

#### AI服务配置

```bash
# OpenAI API配置
BASE_URL=https://api.openai.com/v1
API_KEY=sk-your-openai-api-key
MODEL=gpt-4o-mini

# 支持的AI服务：
# - OpenAI: gpt-4o-mini, gpt-3.5-turbo
# - DeepSeek: https://api.deepseek.com
# - 其他OpenAI兼容API
```

#### 企业微信配置

```bash
# 企业微信机器人配置
WEIXIN_CORP_ID=ww-your-corp-id
WEIXIN_CORP_SECRET=your-corp-secret
WEIXIN_AGENT_ID=your-agent-id
WEIXIN_TO_USER=User1 # 推送目标用户, "@all" 表示所有人, 或者指定成员 "User1|User2"
```

### 4. 运行程序

#### 运行一次

```bash
# 处理今天的邮件
python run.py

# 处理指定日期的邮件
python run.py --date 2024-07-31
```

#### 设置定时任务

```bash
# 每天9点自动运行
python run.py --schedule 09:00

# 每天18点自动运行
python run.py --schedule 18:00
```

#### 测试配置

```bash
# 测试配置是否正确
python run.py --test
```

## 📋 命令行参数

| 参数               | 说明         | 示例                  |
| ------------------ | ------------ | --------------------- |
| `--date, -d`     | 指定处理日期 | `--date 2024-07-31` |
| `--schedule, -s` | 设置定时运行 | `--schedule 09:00`  |
| `--test, -t`     | 测试配置     | `--test`            |
| `--version, -v`  | 显示版本     | `--version`         |

## ⚙️ 高级配置

### 环境变量

在 `.env` 文件中可以配置以下可选参数：

```bash
# 处理设置
MAX_EMAILS_TO_SCAN=200     # 最大扫描邮件数
AI_TIMEOUT=120            # AI调用超时时间（秒）
IMAP_TIMEOUT=60           # IMAP连接超时时间（秒）
MAX_WORKERS=4             # 并行处理线程数

# 日志设置
LOG_LEVEL=INFO            # 日志级别：DEBUG, INFO, WARNING, ERROR
LOG_FILE=email_manager.log # 日志文件路径
```

### 邮件过滤规则

在 `config.py` 中可以配置邮件过滤规则：

```python
EMAIL_FILTERS = {
    "exclude_senders": ["noreply@xxx.com", "newsletter@xxx.com"],
    "include_keywords": ["重要", "紧急", "会议"],
    "exclude_keywords": ["退订", "取消订阅", "广告"],
    "min_content_length": 10,
}
```

## 🔧 开发指南

### 项目结构

```
email-manager/
├── main_optimized.py    # 主程序（优化版）
├── run.py              # 命令行启动脚本
├── config_template.py  # 配置模板
├── requirements.txt    # 依赖列表
├── .env.template       # 环境变量模板
├── README.md           # 项目说明
└── CLAUDE.md          # Claude Code配置
```

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements.txt

# 代码格式化
black *.py

# 代码检查
flake8 *.py

# 运行测试
pytest tests/
```

### 添加新功能

1. **新的邮件提供商**：继承 `IMAPClient` 类实现特定提供商
2. **新的通知方式**：继承 `Notifier` 类实现新的通知渠道
3. **新的AI服务**：继承 `AIService` 类接入其他AI服务

## 🐛 常见问题

### Q1: 连接IMAP服务器失败

**原因**：可能是网络问题或配置错误
**解决**：

- 检查网络连接
- 确认IMAP服务器地址和端口
- 检查邮箱是否开启IMAP服务

### Q2: AI调用失败

**原因**：API密钥错误或余额不足
**解决**：

- 检查API密钥是否正确
- 确认账户余额充足
- 检查API调用频率限制

### Q3: 企业微信推送失败

**原因**：配置错误或权限问题
**解决**：

- 检查企业微信配置
- 确认应用有发送消息权限
- 检查用户是否在接收范围内

### Q4: 中文乱码问题

**原因**：编码问题
**解决**：

- 确认邮件编码为UTF-8
- 检查系统编码设置

## 📊 监控与日志

### 日志文件

程序运行日志保存在 `email_manager.log` 文件中，包含：

- 邮件获取状态
- AI调用记录
- 推送结果
- 错误信息

### 性能监控

可以通过日志监控：

- 邮件处理时间
- AI调用延迟
- 网络请求状态

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 提交Issue

请包含以下信息：

- 问题描述
- 复现步骤
- 环境信息（Python版本、操作系统）
- 相关日志

### 提交代码

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 联系方式

- 项目地址：[GitHub](https://github.com/blacksamuraiiii/mail-manager)
- 邮箱：black_samurai@yeah.net

---

**⭐ 如果这个项目对你有帮助，请给个Star！**
