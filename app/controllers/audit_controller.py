#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
审计日志控制器
"""

from flask import Blueprint, request, jsonify, session
from app.models.audit_log import AuditLog
from app.controllers.auth_controller import login_required

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit_logs', methods=['GET'])
@login_required(role='管理员')
def get_audit_logs():
    """
    获取审计日志（仅管理员）
    """
    # 获取查询参数
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    target_table = request.args.get('target_table')
    
    if user_id:
        logs = AuditLog.get_logs_by_user(user_id)
    elif action:
        logs = AuditLog.get_logs_by_action(action)
    elif target_table:
        logs = AuditLog.get_logs_by_table(target_table)
    else:
        # 获取详细审计日志（包含用户名）
        logs = AuditLog.get_detailed_logs()
    
    return jsonify({'status': 'success', 'audit_logs': logs})

@audit_bp.route('/audit_logs/add', methods=['POST'])
@login_required(role='管理员')
def add_audit_log():
    """
    手动添加审计日志（仅管理员）
    """
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['action', 'target_table', 'sql_text']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'缺少必填字段: {field}'}), 400
    
    # 添加审计日志
    user_id = session.get('user_id')
    if AuditLog.add_log(
        user_id=user_id,
        action=data['action'],
        target_table=data['target_table'],
        sql_text=data['sql_text'],
        ip_address=request.remote_addr
    ):
        return jsonify({'status': 'success', 'message': '审计日志添加成功'})
    else:
        return jsonify({'status': 'error', 'message': '审计日志添加失败'}), 500
