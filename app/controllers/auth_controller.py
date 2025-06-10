#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户认证控制器
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from app.models.user import User
from app.models.audit_log import AuditLog
import hashlib
import functools

auth_bp = Blueprint('auth', __name__)

def login_required(role=None):
    """
    登录验证装饰器
    :param role: 需要的角色，None表示任何已登录用户
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'status': 'error', 'message': '请先登录'}), 401
            
            if role and session.get('user_role') != role:
                return jsonify({'status': 'error', 'message': '权限不足'}), 403
                
            return func(*args, **kwargs)
        return wrapper
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录
    """
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    code = data.get('code')
    password = data.get('password')
    
    if not code or not password:
        return jsonify({'status': 'error', 'message': '学号/工号和密码不能为空'}), 400
    
    user = User.authenticate(code, password)
    if not user:
        return jsonify({'status': 'error', 'message': '学号/工号或密码错误'}), 401
    
    # 记录登录信息到会话
    session['user_id'] = user.uid
    session['user_name'] = user.uname
    session['user_role'] = user.role
    
    # 记录审计日志
    AuditLog.add_log(
        user_id=user.uid,
        action='LOGIN',
        target_table='users',
        sql_text=f'用户登录: {user.uname}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'status': 'success',
        'message': '登录成功',
        'user': {
            'uid': user.uid,
            'uname': user.uname,
            'role': user.role
        }
    })

@auth_bp.route('/logout')
def logout():
    """
    用户登出
    """
    if 'user_id' in session:
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='LOGOUT',
            target_table='users',
            sql_text=f'用户登出: {session["user_name"]}',
            ip_address=request.remote_addr
        )
        
        # 清除会话
        session.clear()
    
    return jsonify({'status': 'success', 'message': '已登出'})

@auth_bp.route('/profile')
@login_required()
def profile():
    """
    获取当前用户信息
    """
    user = User.get_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    return jsonify({
        'status': 'success',
        'user': {
            'uid': user.uid,
            'uname': user.uname,
            'role': user.role,
            'code': user.code,
            'phone': user.phone
        }
    })

@auth_bp.route('/change_password', methods=['POST'])
@login_required()
def change_password():
    """
    修改密码
    """
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'status': 'error', 'message': '原密码和新密码不能为空'}), 400
    
    user = User.get_by_id(session['user_id'])
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    # 验证原密码
    hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
    if user.password != hashed_old_password:
        return jsonify({'status': 'error', 'message': '原密码错误'}), 401
    
    # 更新密码
    if user.update_password(new_password):
        # 记录审计日志
        AuditLog.add_log(
            user_id=user.uid,
            action='UPDATE',
            target_table='users',
            sql_text=f'修改密码: {user.uname}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '密码修改成功'})
    else:
        return jsonify({'status': 'error', 'message': '密码修改失败'}), 500

@auth_bp.route('/users', methods=['GET'])
@login_required(role='管理员')
def get_users():
    """
    获取所有用户（仅管理员）
    """
    users = User.get_all_users()
    users_data = []
    
    for user in users:
        users_data.append({
            'uid': user.uid,
            'uname': user.uname,
            'role': user.role,
            'code': user.code,
            'phone': user.phone
        })
    
    return jsonify({'status': 'success', 'users': users_data})

@auth_bp.route('/users', methods=['POST'])
@login_required(role='管理员')
def create_user():
    """
    创建新用户（仅管理员）
    """
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['uname', 'role', 'code', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'缺少必填字段: {field}'}), 400
    
    # 检查学号/工号是否已存在
    if User.get_by_code(data['code']):
        return jsonify({'status': 'error', 'message': '学号/工号已存在'}), 400
    
    # 创建新用户
    user = User(
        uname=data['uname'],
        role=data['role'],
        code=data['code'],
        password=data['password'],
        phone=data.get('phone')
    )
    
    if user.save():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='INSERT',
            target_table='users',
            sql_text=f'创建用户: {user.uname}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '用户创建成功'})
    else:
        return jsonify({'status': 'error', 'message': '用户创建失败'}), 500

@auth_bp.route('/users/<int:uid>', methods=['PUT'])
@login_required(role='管理员')
def update_user(uid):
    """
    更新用户信息（仅管理员）
    """
    user = User.get_by_id(uid)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 更新用户信息
    if 'uname' in data:
        user.uname = data['uname']
    if 'role' in data:
        user.role = data['role']
    if 'code' in data:
        # 检查学号/工号是否已存在
        existing_user = User.get_by_code(data['code'])
        if existing_user and existing_user.uid != uid:
            return jsonify({'status': 'error', 'message': '学号/工号已存在'}), 400
        user.code = data['code']
    if 'phone' in data:
        user.phone = data['phone']
    
    if user.save():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='UPDATE',
            target_table='users',
            sql_text=f'更新用户: {user.uname}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '用户更新成功'})
    else:
        return jsonify({'status': 'error', 'message': '用户更新失败'}), 500

@auth_bp.route('/users/<int:uid>', methods=['DELETE'])
@login_required(role='管理员')
def delete_user(uid):
    """
    删除用户（仅管理员）
    """
    # 不能删除自己
    if uid == session['user_id']:
        return jsonify({'status': 'error', 'message': '不能删除当前登录用户'}), 400
    
    user = User.get_by_id(uid)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    if user.delete():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='DELETE',
            target_table='users',
            sql_text=f'删除用户: {user.uname}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '用户删除成功'})
    else:
        return jsonify({'status': 'error', 'message': '用户删除失败'}), 500
