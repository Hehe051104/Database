#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主应用程序入口
"""

from flask import Flask, render_template, session, redirect, url_for
import os
from datetime import timedelta

# 导入控制器蓝图
from app.controllers.auth_controller import auth_bp
from app.controllers.device_controller import device_bp
from app.controllers.room_controller import room_bp
from app.controllers.reservation_controller import reservation_bp
from app.controllers.maintenance_controller import maintenance_bp
from app.controllers.stats_controller import stats_bp
from app.controllers.audit_controller import audit_bp

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # 配置应用
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(device_bp, url_prefix='/api/devices')
    app.register_blueprint(room_bp, url_prefix='/api/rooms')
    app.register_blueprint(reservation_bp, url_prefix='/api/reservations')
    app.register_blueprint(maintenance_bp, url_prefix='/api/maintenances')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(audit_bp, url_prefix='/api/audit')
    
    # 主页路由
    @app.route('/')
    def index():
        if 'user_id' in session:
            return render_template('index.html')
        return redirect(url_for('auth.login'))
    
    # 错误处理
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
