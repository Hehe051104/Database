#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主程序入口文件
"""

import os
import sys

# 将项目根目录添加到sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from app.app import create_app
from database.init_db import initialize_database

if __name__ == '__main__':
    # 运行数据库初始化脚本
    print("--- 正在检查数据库状态 ---")
    initialize_database()
    print("--- 数据库检查完成 ---\n")
    
    # 启动Flask应用
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
