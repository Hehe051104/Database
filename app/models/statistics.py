#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统计分析模块
"""

from app.utils.db_config import execute_query

class Statistics:
    @staticmethod
    def get_device_usage_stats():
        """
        获取设备使用率统计
        :return: 设备使用率统计数据
        """
        query = """
            SELECT 
                d.did,
                d.dname,
                d.type,
                COUNT(r.res_id) AS total_reservations,
                COALESCE(SUM(TIMESTAMPDIFF(HOUR, r.start_time, r.end_time)), 0) AS total_hours_used
            FROM devices d
            LEFT JOIN reservations r ON d.did = r.did AND r.status = '已完成'
            GROUP BY d.did, d.dname, d.type
        """
        results = execute_query(query)
        if results:
            for row in results:
                row['total_hours_used'] = int(row['total_hours_used'])
        return results
    
    @staticmethod
    def get_room_usage_stats():
        """
        获取机房使用率统计
        :return: 机房使用率统计数据
        """
        query = """
            SELECT 
                r.rid,
                r.location,
                COUNT(res.res_id) AS total_reservations,
                COUNT(DISTINCT d.did) AS total_devices,
                COUNT(DISTINCT res.uid) AS unique_users
            FROM rooms r
            LEFT JOIN devices d ON r.rid = d.room_id
            LEFT JOIN reservations res ON d.did = res.did AND res.status = '已完成'
            GROUP BY r.rid, r.location
        """
        return execute_query(query)
    
    @staticmethod
    def get_user_role_stats():
        """
        按角色统计设备使用率
        :return: 用户角色统计数据
        """
        query = """
            SELECT 
                u.role, 
                COUNT(r.res_id) AS total_reservations,
                COALESCE(AVG(TIMESTAMPDIFF(HOUR, r.start_time, r.end_time)), 0.0) AS avg_hours
            FROM reservations r
            JOIN users u ON r.uid = u.uid
            WHERE r.status = '已完成'
            GROUP BY u.role
        """
        results = execute_query(query)
        if results:
            for row in results:
                row['avg_hours'] = float(row['avg_hours'])
        return results
    
    @staticmethod
    def get_maintenance_stats():
        """
        获取维护统计数据
        :return: 包含汇总和按类型详情的维护统计数据字典
        """
        query_total_completed = "SELECT COUNT(*) AS count FROM maintenances WHERE status = '已完成'"
        total_completed_data = execute_query(query_total_completed, fetch_one=True)
        total_completed_count = total_completed_data['count'] if total_completed_data else 0

        query_total_pending = "SELECT COUNT(*) AS count FROM maintenances WHERE status = '待处理'"
        total_pending_data = execute_query(query_total_pending, fetch_one=True)
        total_pending_count = total_pending_data['count'] if total_pending_data else 0

        query_avg_duration = """
            SELECT COALESCE(AVG(TIMESTAMPDIFF(HOUR, report_time, complete_time)), 0.0) AS avg_hours
            FROM maintenances
            WHERE status = '已完成' AND complete_time IS NOT NULL
        """
        avg_duration_data = execute_query(query_avg_duration, fetch_one=True)
        avg_duration_hours = float(avg_duration_data['avg_hours']) if avg_duration_data else 0.0

        query_details_by_type = """
            SELECT 
                d.type,
                COUNT(m.mid) AS maintenance_count,
                COALESCE(AVG(TIMESTAMPDIFF(HOUR, m.report_time, m.complete_time)), 0.0) AS avg_repair_time_hours
            FROM maintenances m
            JOIN devices d ON m.did = d.did
            WHERE m.status = '已完成' AND m.complete_time IS NOT NULL
            GROUP BY d.type
        """
        details_by_type = execute_query(query_details_by_type)
        
        if details_by_type:
            for item in details_by_type:
                item['avg_repair_time_hours'] = float(item['avg_repair_time_hours'])
        
        return {
            'total_completed_maintenances': total_completed_count,
            'total_pending_maintenances': total_pending_count,
            'average_completion_time_hours': avg_duration_hours,
            'details_by_type': details_by_type if details_by_type else []
        }
    
    @staticmethod
    def get_monthly_usage_trend():
        """
        获取月度使用趋势
        :return: 月度使用趋势数据
        """
        query = """
            SELECT 
                DATE_FORMAT(start_time, '%Y-%m') AS month,
                COUNT(res_id) AS reservation_count,
                COALESCE(SUM(TIMESTAMPDIFF(HOUR, start_time, end_time)), 0) AS total_hours
            FROM reservations
            WHERE status = '已完成'
            GROUP BY DATE_FORMAT(start_time, '%Y-%m')
            ORDER BY month
        """
        results = execute_query(query)
        if results:
            for row in results:
                row['total_hours'] = int(row['total_hours'])
        return results
    
    @staticmethod
    def get_device_status_summary():
        """
        获取设备状态汇总
        :return: 设备状态汇总数据
        """
        query = """
            SELECT 
                status,
                COUNT(*) AS count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM devices), 2) AS percentage
            FROM devices
            GROUP BY status
        """
        return execute_query(query)
    
    @staticmethod
    def get_reservation_status_summary():
        """
        获取预约状态汇总
        :return: 预约状态汇总数据
        """
        query = """
            SELECT 
                status,
                COUNT(*) AS count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reservations), 2) AS percentage
            FROM reservations
            GROUP BY status
        """
        return execute_query(query)
