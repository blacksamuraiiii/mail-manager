# 邮件管家 - 智能邮件管理助手 (重构简化版)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于Python的智能邮件管理工具，自动获取每日邮件，使用AI进行智能摘要，并推送到企业微信。

> **重要提示**：此为重构简化版，项目结构和配置方式已发生重大变更，请仔细阅读以下文档。

## ✨ 功能特性

- 📧 **智能邮件获取**：支持IMAP协议，自动获取指定日期范围的邮件
- 🤖 **AI智能摘要**：使用OpenAI GPT模型生成邮件摘要
- 📱 **企业微信推送**：自动将邮件摘要推送到企业微信
- ⚡ **并行处理**：支持多线程并行处理邮件，提升效率
- 🔒 **安全配置**：敏感信息通过 `.env` 文件管理，避免明文存储
- 📊 **详细日志**：完整的操作日志，便于调试和监控

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目 (如果尚未克隆)
git clone https://github.com/blacksamuraiiii/mail-manager.git
cd email-manager

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

#### 使用 `.env` 文件（唯一配置方式）

```bash
# 复制环境变量模板
cp .env.template .env

# 编辑 .env 文件，填入你的配置
nano .env
```

### 3. 配置说明

#### 邮件服务器配置

```bash
# IMAP服务器信息
EMAIL_USER=your_email@chinatelecom.cn
EMAIL_PASSWORD=your_email_password
IMAP_SERVER=imap.chinatelecom.cn
IMAP_PORT=993

# 支持的IMAP服务器：
# - 中国电信: imap.chinatelecom.cn:993
# - QQ邮箱: imap.qq.com:993
# - 163邮箱: imap.163.com:993
# - Gmail: imap.gmail.com:993
```

#### AI服务配置

```bash
# LLM (AI) 配置
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-openai-api-key
LLM_MODEL=gpt-4o-mini

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

## 🧪 最终测试

确保您已正确配置 `.env` 文件，然后运行以下命令进行最终测试：

```bash
# 1. 测试配置
python run.py --test

# 2. 运行一次处理（处理今天邮件）
python run.py
```

观察日志输出和企业微信是否收到推送，以确认整个流程工作正常。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 联系方式

- 项目地址：[GitHub](https://github.com/blacksamuraiiii/mail-manager)
- 邮箱：black_samurai@yeah.net

---

**⭐ 如果这个项目对你有帮助，请给个Star！**