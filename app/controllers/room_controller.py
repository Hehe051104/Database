#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机房管理控制器
"""

from flask import Blueprint, request, jsonify, session
from app.models.room import Room
from app.models.audit_log import AuditLog
from app.controllers.auth_controller import login_required

room_bp = Blueprint('room', __name__)

@room_bp.route('/', methods=['GET'])
@login_required()
def get_rooms():
    """
    获取所有机房
    """
    rooms = Room.get_all_rooms()
    rooms_data = []
    
    for room in rooms:
        rooms_data.append({
            'rid': room.rid,
            'location': room.location,
            'capacity': room.capacity,
            'open_time': room.open_time
        })
    
    return jsonify({'status': 'success', 'rooms': rooms_data})

@room_bp.route('/rooms/<int:rid>', methods=['GET'])
@login_required()
def get_room(rid):
    """
    获取单个机房信息
    """
    room = Room.get_by_id(rid)
    if not room:
        return jsonify({'status': 'error', 'message': '机房不存在'}), 404
    
    return jsonify({
        'status': 'success',
        'room': {
            'rid': room.rid,
            'location': room.location,
            'capacity': room.capacity,
            'open_time': room.open_time
        }
    })

@room_bp.route('/rooms', methods=['POST'])
@login_required(role='管理员')
def create_room():
    """
    创建新机房（仅管理员）
    """
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['location', 'capacity', 'open_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'缺少必填字段: {field}'}), 400
    
    # 创建新机房
    room = Room(
        location=data['location'],
        capacity=data['capacity'],
        open_time=data['open_time']
    )
    
    if room.save():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='INSERT',
            target_table='rooms',
            sql_text=f'创建机房: {room.location}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '机房创建成功'})
    else:
        return jsonify({'status': 'error', 'message': '机房创建失败'}), 500

@room_bp.route('/rooms/<int:rid>', methods=['PUT'])
@login_required(role='管理员')
def update_room(rid):
    """
    更新机房信息（仅管理员）
    """
    room = Room.get_by_id(rid)
    if not room:
        return jsonify({'status': 'error', 'message': '机房不存在'}), 404
    
    data = request.get_json()
    
    # 更新机房信息
    if 'location' in data:
        room.location = data['location']
    if 'capacity' in data:
        room.capacity = data['capacity']
    if 'open_time' in data:
        room.open_time = data['open_time']
    
    if room.save():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='UPDATE',
            target_table='rooms',
            sql_text=f'更新机房: {room.location}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '机房更新成功'})
    else:
        return jsonify({'status': 'error', 'message': '机房更新失败'}), 500

@room_bp.route('/rooms/<int:rid>', methods=['DELETE'])
@login_required(role='管理员')
def delete_room(rid):
    """
    删除机房（仅管理员）
    """
    room = Room.get_by_id(rid)
    if not room:
        return jsonify({'status': 'error', 'message': '机房不存在'}), 404
    
    if room.delete():
        # 记录审计日志
        AuditLog.add_log(
            user_id=session['user_id'],
            action='DELETE',
            target_table='rooms',
            sql_text=f'删除机房: {room.location}',
            ip_address=request.remote_addr
        )
        return jsonify({'status': 'success', 'message': '机房删除成功'})
    else:
        return jsonify({'status': 'error', 'message': '机房删除失败'}), 500
