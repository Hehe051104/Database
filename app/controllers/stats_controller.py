#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统计分析控制器
"""

from flask import Blueprint, request, jsonify, session
from app.models.statistics import Statistics
from app.controllers.auth_controller import login_required

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/device_usage', methods=['GET'])
@login_required()
def get_device_usage_stats():
    """
    获取设备使用率统计
    """
    stats = Statistics.get_device_usage_stats()
    return jsonify({'status': 'success', 'device_usage_stats': stats})

@stats_bp.route('/room_usage', methods=['GET'])
@login_required()
def get_room_usage_stats():
    """
    获取机房使用率统计
    """
    stats = Statistics.get_room_usage_stats()
    return jsonify({'status': 'success', 'room_usage_stats': stats})

@stats_bp.route('/user_role', methods=['GET'])
@login_required(role='管理员')
def get_user_role_stats():
    """
    按角色统计设备使用率（仅管理员）
    """
    stats = Statistics.get_user_role_stats()
    return jsonify({'status': 'success', 'user_role_stats': stats})

@stats_bp.route('/maintenance', methods=['GET'])
@login_required(role='管理员')
def get_maintenance_stats():
    """
    获取维护统计数据（仅管理员）
    """
    stats = Statistics.get_maintenance_stats()
    return jsonify({'status': 'success', 'maintenance_stats': stats})

@stats_bp.route('/monthly_usage', methods=['GET'])
@login_required(role='管理员')
def get_monthly_usage_trend():
    """
    获取月度使用趋势（仅管理员）
    """
    stats = Statistics.get_monthly_usage_trend()
    return jsonify({'status': 'success', 'monthly_usage_trend': stats})

@stats_bp.route('/device_status', methods=['GET'])
@login_required()
def get_device_status_summary():
    """
    获取设备状态汇总
    """
    stats = Statistics.get_device_status_summary()
    return jsonify({'status': 'success', 'device_status_summary': stats})

@stats_bp.route('/reservation_status', methods=['GET'])
@login_required()
def get_reservation_status_summary():
    """
    获取预约状态汇总
    """
    stats = Statistics.get_reservation_status_summary()
    return jsonify({'status': 'success', 'reservation_status_summary': stats})

@stats_bp.route('/dashboard', methods=['GET'])
@login_required()
def get_dashboard_stats():
    """
    获取仪表盘统计数据
    """
    user_role = session.get('user_role')
    
    # 基础统计数据（所有角色可见）
    device_status = Statistics.get_device_status_summary()
    reservation_status = Statistics.get_reservation_status_summary()
    
    dashboard_data = {
        'device_status': device_status,
        'reservation_status': reservation_status
    }
    
    # 管理员可见的高级统计数据
    if user_role == '管理员':
        dashboard_data.update({
            'user_role_stats': Statistics.get_user_role_stats(),
            'maintenance_stats': Statistics.get_maintenance_stats(),
            'monthly_usage_trend': Statistics.get_monthly_usage_trend()
        })
    
    return jsonify({'status': 'success', 'dashboard': dashboard_data})
