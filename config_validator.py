#!/usr/bin/env python3
"""
配置验证工具
用于验证邮件管家的配置是否正确
"""

import os
import sys
from typing import List, Tuple
import socket
import requests
import imaplib
from openai import OpenAI
from dotenv import load_dotenv

def load_env_config():
    """加载环境变量配置"""
    load_dotenv()
    
    return {
        'email_user': os.getenv('EMAIL_USER'),
        'email_password': os.getenv('EMAIL_PASSWORD'),
        'imap_server': os.getenv('IMAP_SERVER', 'imap.chinatelecom.cn'),
        'imap_port': int(os.getenv('IMAP_PORT', 993)),
        'base_url': os.getenv('BASE_URL', 'https://api.openai.com/v1'),
        'api_key': os.getenv('API_KEY'),
        'model': os.getenv('MODEL', 'gpt-4o-mini'),
        'weixin_corp_id': os.getenv('WEIXIN_CORP_ID'),
        'weixin_corp_secret': os.getenv('WEIXIN_CORP_SECRET'),
        'weixin_agent_id': os.getenv('WEIXIN_AGENT_ID'),
        'weixin_to_user': os.getenv('WEIXIN_TO_USER'),
    }

def test_imap_connection(config: dict) -> Tuple[bool, str]:
    """测试IMAP连接"""
    try:
        mail = imaplib.IMAP4_SSL(config['imap_server'], config['imap_port'])
        mail.login(config['email_user'], config['email_password'])
        mail.select('INBOX')
        mail.logout()
        return True, "IMAP连接成功"
    except Exception as e:
        return False, f"IMAP连接失败: {str(e)}"

def test_openai_connection(config: dict) -> Tuple[bool, str]:
    """测试OpenAI API连接"""
    try:
        client = OpenAI(
            api_key=config['api_key'],
            base_url=config['base_url']
        )
        
        # 测试简单对话
        response = client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True, "OpenAI API连接成功"
    except Exception as e:
        return False, f"OpenAI API连接失败: {str(e)}"

def test_weixin_connection(config: dict) -> Tuple[bool, str]:
    """测试企业微信连接"""
    try:
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            'corpid': config['weixin_corp_id'],
            'corpsecret': config['weixin_corp_secret']
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'access_token' in data:
            return True, "企业微信配置正确"
        else:
            return False, f"企业微信配置错误: {data.get('errmsg', 'Unknown error')}"
    except Exception as e:
        return False, f"企业微信连接失败: {str(e)}"

def check_missing_config(config: dict) -> List[str]:
    """检查缺失的配置项"""
    required_fields = [
        'email_user', 'email_password',
        'api_key', 'weixin_corp_id', 
        'weixin_corp_secret', 'weixin_agent_id'
    ]
    
    missing = []
    for field in required_fields:
        if not config.get(field):
            missing.append(field.upper().replace('_', '_'))
    
    return missing

def main():
    """主函数"""
    print("🔍 邮件管家配置验证工具")
    print("=" * 50)
    
    # 加载配置
    config = load_env_config()
    
    # 检查缺失配置
    missing = check_missing_config(config)
    if missing:
        print("❌ 缺失必要配置:")
        for item in missing:
            print(f"   - {item}")
        return
    
    print("✅ 基础配置检查通过")
    
    # 测试各项连接
    tests = [
        ("IMAP连接", test_imap_connection),
        ("OpenAI/API", test_openai_connection),
        ("企业微信", test_weixin_connection)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n🧪 测试{test_name}...")
        success, message = test_func(config)
        if success:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有配置验证通过！可以正常使用邮件管家了")
    else:
        print("⚠️  部分配置有问题，请根据提示修改")

if __name__ == '__main__':
    main()