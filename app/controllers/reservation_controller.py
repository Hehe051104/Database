#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
预约管理控制器
"""

from flask import Blueprint, request, jsonify, session
from app.models.reservation import Reservation
from app.models.device import Device
from app.models.user import User
from app.models.audit_log import AuditLog
from app.controllers.auth_controller import login_required
from datetime import datetime

reservation_bp = Blueprint('reservation', __name__)

@reservation_bp.route('/', methods=['GET'])
@login_required()
def get_reservations():
    """
    获取预约记录
    - 学生/教师：只能查看自己的预约
    - 管理员：可以查看所有预约
    """
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    # 获取查询参数
    status = request.args.get('status')
    device_id = request.args.get('did', type=int)
    
    if user_role == '管理员':
        # 管理员可以查看所有预约
        if device_id:
            reservations = Reservation.get_by_device(device_id)
        else:
            # 获取详细预约信息（包含用户名和设备名）
            reservations_data = Reservation.get_detailed_reservations()
            
            # 如果有状态过滤
            if status:
                reservations_data = [r for r in reservations_data if r['status'] == status]
                
            return jsonify({'status': 'success', 'reservations': reservations_data})
    else:
        # 普通用户只能查看自己的预约
        reservations = Reservation.get_by_user(user_id)
    
    # 如果有状态过滤
    if status and isinstance(reservations, list):
        reservations = [r for r in reservations if r.status == status]
    
    # 转换为JSON格式
    reservations_data = []
    for res in reservations:
        reservations_data.append({
            'res_id': res.res_id,
            'uid': res.uid,
            'did': res.did,
            'start_time': res.start_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(res.start_time, datetime) else res.start_time,
            'end_time': res.end_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(res.end_time, datetime) else res.end_time,
            'status': res.status
        })
    
    return jsonify({'status': 'success', 'reservations': reservations_data})

@reservation_bp.route('/reservations/pending', methods=['GET'])
@login_required(role='教师')
def get_pending_reviews():
    """
    获取待审核的预约（仅教师）
    """
    pending_reviews = Reservation.get_pending_reviews()
    return jsonify({'status': 'success', 'pending_reviews': pending_reviews})

@reservation_bp.route('/reservations/<int:res_id>', methods=['GET'])
@login_required()
def get_reservation(res_id):
    """
    获取单个预约记录
    - 学生/教师：只能查看自己的预约
    - 管理员：可以查看所有预约
    """
    reservation = Reservation.get_by_id(res_id)
    if not reservation:
        return jsonify({'status': 'error', 'message': '预约记录不存在'}), 404
    
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    # 权限检查
    if user_role != '管理员' and reservation.uid != user_id:
        return jsonify({'status': 'error', 'message': '无权查看此预约记录'}), 403
    
    return jsonify({
        'status': 'success',
        'reservation': {
            'res_id': reservation.res_id,
            'uid': reservation.uid,
            'did': reservation.did,
            'start_time': reservation.start_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(reservation.start_time, datetime) else reservation.start_time,
            'end_time': reservation.end_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(reservation.end_time, datetime) else reservation.end_time,
            'status': reservation.status
        }
    })

@reservation_bp.route('/reservations', methods=['POST'])
@login_required()
def create_reservation():
    """
    创建预约
    """
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['did', 'start_time', 'end_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'缺少必填字段: {field}'}), 400
    
    # 验证设备是否存在
    device = Device.get_by_id(data['did'])
    if not device:
        return jsonify({'status': 'error', 'message': '设备不存在'}), 400
    
    # 验证设备是否可用
    if device.status != '空闲':
        return jsonify({'status': 'error', 'message': '设备当前不可用'}), 400
    
    # 解析时间
    try:
        start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'status': 'error', 'message': '时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式'}), 400
    
    # 验证时间合理性
    if start_time >= end_time:
        return jsonify({'status': 'error', 'message': '开始时间必须早于结束时间'}), 400
    
    if start_time < datetime.now():
        return jsonify({'status': 'error', 'message': '开始时间不能早于当前时间'}), 400
    
    # 创建预约
    user_id = session.get('user_id')
    reservation = Reservation(
        uid=user_id,
        did=data['did'],
        start_time=start_time,
        end_time=end_time,
        status='待审核'
    )
    
    # 检查时间冲突
    if Reservation.check_conflict(data['did'], start_time, end_time):
        return jsonify({'status': 'error', 'message': '预约时间与已有预约冲突'}), 400
    
    # 使用存储过程创建预约（包含冲突检查）
    try:
        if reservation.create_with_conflict_check():
            # 记录审计日志
            AuditLog.add_log(
                user_id=user_id,
                action='INSERT',
                target_table='reservations',
                sql_text=f'创建预约: 设备ID {data["did"]}',
                ip_address=request.remote_addr
            )
            return jsonify({'status': 'success', 'message': '预约创建成功，等待审核'})
        else:
            return jsonify({'status': 'error', 'message': '预约创建失败'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'预约创建失败: {str(e)}'}), 500

@reservation_bp.route('/reservations/<int:res_id>/status', methods=['PUT'])
@login_required()
def update_reservation_status(res_id):
    """
    更新预约状态
    - 学生：只能取消自己的预约
    - 教师：可以审核预约（确认/拒绝）
    - 管理员：可以更新任何预约状态
    """
    reservation = Reservation.get_by_id(res_id)
    if not reservation:
        return jsonify({'status': 'error', 'message': '预约记录不存在'}), 404
    
    data = request.get_json()
    if 'status' not in data:
        return jsonify({'status': 'error', 'message': '缺少状态字段'}), 400
    
    new_status = data['status']
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    # 权限检查
    if user_role == '学生':
        # 学生只能取消自己的预约
        if reservation.uid != user_id:
            return jsonify({'status': 'error', 'message': '无权更新此预约记录'}), 403
        
        if new_status != '已取消':
            return jsonify({'status': 'error', 'message': '学生只能取消预约'}), 403
    
    elif user_role == '教师':
        # 教师可以审核预约（确认/拒绝）
        if new_status not in ['已确认', '已取消']:
            return jsonify({'status': 'error', 'message': '教师只能确认或取消预约'}), 403
    
    # 更新预约状态
    if reservation.update_status(new_status):
        # 记录审计日志
        AuditLog.add_log(
            user_id=user_id,
            action='UPDATE',
            target_table='reservations',
            sql_text=f'更新预约状态: {res_id} -> {new_status}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '预约状态更新成功'})
    else:
        return jsonify({'status': 'error', 'message': '预约状态更新失败'}), 500

@reservation_bp.route('/reservations/<int:res_id>', methods=['DELETE'])
@login_required(role='管理员')
def delete_reservation(res_id):
    """
    删除预约记录（仅管理员）
    """
    reservation = Reservation.get_by_id(res_id)
    if not reservation:
        return jsonify({'status': 'error', 'message': '预约记录不存在'}), 404
    
    if reservation.delete():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session.get('user_id'),
            action='DELETE',
            target_table='reservations',
            sql_text=f'删除预约: {res_id}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '预约删除成功'})
    else:
        return jsonify({'status': 'error', 'message': '预约删除失败'}), 500
