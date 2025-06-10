#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设备管理控制器
"""

from flask import Blueprint, request, jsonify, session
from app.models.device import Device
from app.models.room import Room
from app.models.audit_log import AuditLog
from app.controllers.auth_controller import login_required

device_bp = Blueprint('device', __name__)

@device_bp.route('/', methods=['GET'])
@login_required()
def get_devices():

    """
    获取所有设备
    """
    # 获取查询参数
    room_id = request.args.get('room_id', type=int)
    status = request.args.get('status')
    
    if room_id:
        devices = Device.get_devices_by_room(room_id)
    elif status:
        if status == '空闲':
            devices = Device.get_available_devices()
        else:
            # 根据状态过滤设备
            all_devices = Device.get_all_devices()
            devices = [d for d in all_devices if d.status == status]
    else:
        devices = Device.get_all_devices()
    
    devices_data = []
    for device in devices:
        devices_data.append({
            'did': device.did,
            'dname': device.dname,
            'type': device.type,
            'spec': device.spec,
            'status': device.status,
            'room_id': device.room_id
        })
    
    return jsonify({'status': 'success', 'devices': devices_data})

@device_bp.route('/details', methods=['GET'])
@login_required()
def get_device_details():
    """
    获取设备详情（包含机房位置）
    """
    device_details = Device.get_device_details()
    return jsonify({'status': 'success', 'device_details': device_details})

@device_bp.route('/<int:did>', methods=['GET'])
@login_required()
def get_device(did):
    """
    获取单个设备信息
    """
    device = Device.get_by_id(did)
    if not device:
        return jsonify({'status': 'error', 'message': '设备不存在'}), 404
    
    return jsonify({
        'status': 'success',
        'device': {
            'did': device.did,
            'dname': device.dname,
            'type': device.type,
            'spec': device.spec,
            'status': device.status,
            'room_id': device.room_id
        }
    })

@device_bp.route('/', methods=['POST'])
@login_required(role='管理员')
def create_device():
    """
    创建新设备（仅管理员）
    """
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['dname', 'type', 'room_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'缺少必填字段: {field}'}), 400
    
    # 验证机房是否存在
    room = Room.get_by_id(data['room_id'])
    if not room:
        return jsonify({'status': 'error', 'message': '机房不存在'}), 400
    
    # 创建新设备
    device = Device(
        dname=data['dname'],
        type=data['type'],
        spec=data.get('spec'),
        status=data.get('status', '空闲'),
        room_id=data['room_id']
    )
    
    if device.save():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='INSERT',
            target_table='devices',
            sql_text=f'创建设备: {device.dname}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '设备创建成功'})
    else:
        return jsonify({'status': 'error', 'message': '设备创建失败'}), 500

@device_bp.route('/<int:did>', methods=['PUT'])
@login_required(role='管理员')
def update_device(did):
    """
    更新设备信息（仅管理员）
    """
    device = Device.get_by_id(did)
    if not device:
        return jsonify({'status': 'error', 'message': '设备不存在'}), 404
    
    data = request.get_json()
    
    # 更新设备信息
    if 'dname' in data:
        device.dname = data['dname']
    if 'type' in data:
        device.type = data['type']
    if 'spec' in data:
        device.spec = data['spec']
    if 'status' in data:
        device.status = data['status']
    if 'room_id' in data:
        # 验证机房是否存在
        room = Room.get_by_id(data['room_id'])
        if not room:
            return jsonify({'status': 'error', 'message': '机房不存在'}), 400
        device.room_id = data['room_id']
    
    if device.save():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='UPDATE',
            target_table='devices',
            sql_text=f'更新设备: {device.dname}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '设备更新成功'})
    else:
        return jsonify({'status': 'error', 'message': '设备更新失败'}), 500

@device_bp.route('/devices/<int:did>/status', methods=['PUT'])
@login_required(role='管理员')
def update_device_status(did):
    """
    更新设备状态（仅管理员）
    """
    device = Device.get_by_id(did)
    if not device:
        return jsonify({'status': 'error', 'message': '设备不存在'}), 404
    
    data = request.get_json()
    if 'status' not in data:
        return jsonify({'status': 'error', 'message': '缺少状态字段'}), 400
    
    if device.update_status(data['status']):
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='UPDATE',
            target_table='devices',
            sql_text=f'更新设备状态: {device.dname} -> {data["status"]}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '设备状态更新成功'})
    else:
        return jsonify({'status': 'error', 'message': '设备状态更新失败'}), 500

@device_bp.route('/<int:did>', methods=['DELETE'])
@login_required(role='管理员')
def delete_device(did):
    """
    删除设备（仅管理员）
    """
    device = Device.get_by_id(did)
    if not device:
        return jsonify({'status': 'error', 'message': '设备不存在'}), 404
    
    if device.delete():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='DELETE',
            target_table='devices',
            sql_text=f'删除设备: {device.dname}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '设备删除成功'})
    else:
        return jsonify({'status': 'error', 'message': '设备删除失败'}), 500
