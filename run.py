#!/usr/bin/env python3
"""
邮件管家启动脚本
提供命令行接口和后台运行支持
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
import schedule
import time

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_optimized import EmailManager
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)

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
        from main_optimized import EmailConfig
        config = EmailConfig()
        
        if config.validate():
            print("✅ 配置验证通过")
            return True
        else:
            print("❌ 配置验证失败")
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
                       version='邮件管家 v2.0')
    
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