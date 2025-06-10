#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
维护管理控制器
"""

from flask import Blueprint, request, jsonify, session
from app.models.maintenance import Maintenance
from app.models.device import Device
from app.models.audit_log import AuditLog
from app.controllers.auth_controller import login_required
from datetime import datetime

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/', methods=['GET'])
@login_required()
def get_maintenances():
    """
    获取维护记录
    """
    # 获取查询参数
    status = request.args.get('status')
    device_id = request.args.get('did', type=int)
    
    if device_id:
        maintenances = Maintenance.get_by_device(device_id)
    else:
        # 获取详细维护信息（包含设备名称）
        maintenances_data = Maintenance.get_detailed_maintenances()
        
        # 如果有状态过滤
        if status:
            maintenances_data = [m for m in maintenances_data if m['status'] == status]
            
        return jsonify({'status': 'success', 'maintenances': maintenances_data})
    
    # 如果有状态过滤
    if status and isinstance(maintenances, list):
        maintenances = [m for m in maintenances if m.status == status]
    
    # 转换为JSON格式
    maintenances_data = []
    for maint in maintenances:
        maintenances_data.append({
            'mid': maint.mid,
            'did': maint.did,
            'issue': maint.issue,
            'report_time': maint.report_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(maint.report_time, datetime) else maint.report_time,
            'handler': maint.handler,
            'status': maint.status,
            'complete_time': maint.complete_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(maint.complete_time, datetime) and maint.complete_time else None
        })
    
    return jsonify({'status': 'success', 'maintenances': maintenances_data})

@maintenance_bp.route('/maintenances/pending', methods=['GET'])
@login_required()
def get_pending_maintenances():
    """
    获取待处理的维护记录
    """
    pending_maintenances = Maintenance.get_pending_maintenances()
    return jsonify({'status': 'success', 'pending_maintenances': pending_maintenances})

@maintenance_bp.route('/maintenances/overdue', methods=['GET'])
@login_required(role='管理员')
def get_overdue_maintenances():
    """
    获取超时未处理的维护请求（>24小时）
    """
    overdue_maintenances = Maintenance.get_overdue_maintenances()
    return jsonify({'status': 'success', 'overdue_maintenances': overdue_maintenances})

@maintenance_bp.route('/maintenances/<int:mid>', methods=['GET'])
@login_required()
def get_maintenance(mid):
    """
    获取单个维护记录
    """
    maintenance = Maintenance.get_by_id(mid)
    if not maintenance:
        return jsonify({'status': 'error', 'message': '维护记录不存在'}), 404
    
    return jsonify({
        'status': 'success',
        'maintenance': {
            'mid': maintenance.mid,
            'did': maintenance.did,
            'issue': maintenance.issue,
            'report_time': maintenance.report_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(maintenance.report_time, datetime) else maintenance.report_time,
            'handler': maintenance.handler,
            'status': maintenance.status,
            'complete_time': maintenance.complete_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(maintenance.complete_time, datetime) and maintenance.complete_time else None
        }
    })

@maintenance_bp.route('/maintenances', methods=['POST'])
@login_required()
def create_maintenance():
    """
    创建维护记录
    """
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['did', 'issue']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'缺少必填字段: {field}'}), 400
    
    # 验证设备是否存在
    device = Device.get_by_id(data['did'])
    if not device:
        return jsonify({'status': 'error', 'message': '设备不存在'}), 400
    
    # 创建维护记录
    user_id = session.get('user_id')
    maintenance = Maintenance(
        did=data['did'],
        issue=data['issue'],
        report_time=datetime.now(),
        status='待处理'
    )
    
    # 使用存储过程创建维护记录（包含设备状态更新和预约取消）
    try:
        if maintenance.create_with_device_update(user_id):
            return jsonify({'status': 'success', 'message': '维护记录创建成功'})
        else:
            return jsonify({'status': 'error', 'message': '维护记录创建失败'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'维护记录创建失败: {str(e)}'}), 500

@maintenance_bp.route('/maintenances/<int:mid>/status', methods=['PUT'])
@login_required(role='管理员')
def update_maintenance_status(mid):
    """
    更新维护状态（仅管理员）
    """
    maintenance = Maintenance.get_by_id(mid)
    if not maintenance:
        return jsonify({'status': 'error', 'message': '维护记录不存在'}), 404
    
    data = request.get_json()
    if 'status' not in data:
        return jsonify({'status': 'error', 'message': '缺少状态字段'}), 400
    
    new_status = data['status']
    handler = data.get('handler')
    
    if maintenance.update_status(new_status, handler):
        # 记录审计日志
        AuditLog.add_log(
            user_id=session.get('user_id'),
            action='UPDATE',
            target_table='maintenances',
            sql_text=f'更新维护状态: {mid} -> {new_status}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '维护状态更新成功'})
    else:
        return jsonify({'status': 'error', 'message': '维护状态更新失败'}), 500

@maintenance_bp.route('/maintenances/<int:mid>', methods=['DELETE'])
@login_required(role='管理员')
def delete_maintenance(mid):
    """
    删除维护记录（仅管理员）
    """
    maintenance = Maintenance.get_by_id(mid)
    if not maintenance:
        return jsonify({'status': 'error', 'message': '维护记录不存在'}), 404
    
    if maintenance.delete():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session.get('user_id'),
            action='DELETE',
            target_table='maintenances',
            sql_text=f'删除维护记录: {mid}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '维护记录删除成功'})
    else:
        return jsonify({'status': 'error', 'message': '维护记录删除失败'}), 500
