#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主程序入口文件
"""


import os
from app.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
