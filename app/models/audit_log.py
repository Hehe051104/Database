#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
审计日志模型
"""

from app.utils.db_config import execute_query, execute_update

class AuditLog:
    def __init__(self, log_id=None, user_id=None, action=None, target_table=None, sql_text=None, ip_address=None, action_time=None):
        self.log_id = log_id
        self.user_id = user_id
        self.action = action
        self.target_table = target_table
        self.sql_text = sql_text
        self.ip_address = ip_address
        self.action_time = action_time
    
    @staticmethod
    def get_all_logs():
        """
        获取所有审计日志
        :return: 审计日志列表
        """
        query = "SELECT * FROM audit_log ORDER BY action_time DESC"
        return execute_query(query)
    
    @staticmethod
    def get_logs_by_user(user_id):
        """
        获取指定用户的审计日志
        :param user_id: 用户ID
        :return: 审计日志列表
        """
        query = "SELECT * FROM audit_log WHERE user_id = %s ORDER BY action_time DESC"
        return execute_query(query, (user_id,))
    
    @staticmethod
    def get_logs_by_action(action):
        """
        获取指定操作类型的审计日志
        :param action: 操作类型
        :return: 审计日志列表
        """
        query = "SELECT * FROM audit_log WHERE action = %s ORDER BY action_time DESC"
        return execute_query(query, (action,))
    
    @staticmethod
    def get_logs_by_table(target_table):
        """
        获取指定表的审计日志
        :param target_table: 目标表
        :return: 审计日志列表
        """
        query = "SELECT * FROM audit_log WHERE target_table = %s ORDER BY action_time DESC"
        return execute_query(query, (target_table,))
    
    @staticmethod
    def add_log(user_id, action, target_table, sql_text, ip_address=None):
        """
        添加审计日志
        :param user_id: 用户ID
        :param action: 操作类型
        :param target_table: 目标表
        :param sql_text: SQL文本
        :param ip_address: IP地址
        :return: 成功返回True，失败返回False
        """
        query = """
            INSERT INTO audit_log (user_id, action, target_table, sql_text, ip_address)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (user_id, action, target_table, sql_text, ip_address)
        return execute_update(query, params) > 0
    
    @staticmethod
    def get_detailed_logs():
        """
        获取详细的审计日志（包含用户名）
        :return: 审计日志详情列表
        """
        query = """
            SELECT a.*, u.uname
            FROM audit_log a
            JOIN users u ON a.user_id = u.uid
            ORDER BY a.action_time DESC
        """
        return execute_query(query)
