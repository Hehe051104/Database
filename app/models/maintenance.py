#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
维护记录模型
"""

from app.utils.db_config import execute_query, execute_update, call_procedure
from datetime import datetime

class Maintenance:
    def __init__(self, mid=None, did=None, issue=None, report_time=None, handler=None, status=None, complete_time=None):
        self.mid = mid
        self.did = did
        self.issue = issue
        self.report_time = report_time
        self.handler = handler
        self.status = status
        self.complete_time = complete_time
    
    @staticmethod
    def get_by_id(mid):
        """
        根据ID获取维护记录
        :param mid: 维护ID
        :return: 维护对象
        """
        query = "SELECT * FROM maintenances WHERE mid = %s"
        maint_data = execute_query(query, (mid,), fetch_one=True)
        if maint_data:
            return Maintenance(
                mid=maint_data['mid'],
                did=maint_data['did'],
                issue=maint_data['issue'],
                report_time=maint_data['report_time'],
                handler=maint_data['handler'],
                status=maint_data['status'],
                complete_time=maint_data['complete_time']
            )
        return None
    
    @staticmethod
    def get_by_device(did):
        """
        获取设备的所有维护记录
        :param did: 设备ID
        :return: 维护记录列表
        """
        query = "SELECT * FROM maintenances WHERE did = %s ORDER BY report_time DESC"
        maint_data_list = execute_query(query, (did,))
        maintenances = []
        
        if maint_data_list:
            for maint_data in maint_data_list:
                maintenances.append(Maintenance(
                    mid=maint_data['mid'],
                    did=maint_data['did'],
                    issue=maint_data['issue'],
                    report_time=maint_data['report_time'],
                    handler=maint_data['handler'],
                    status=maint_data['status'],
                    complete_time=maint_data['complete_time']
                ))
        return maintenances
    
    @staticmethod
    def get_all_maintenances():
        """
        获取所有维护记录
        :return: 维护记录列表
        """
        query = "SELECT * FROM maintenances ORDER BY report_time DESC"
        maint_data_list = execute_query(query)
        maintenances = []
        
        if maint_data_list:
            for maint_data in maint_data_list:
                maintenances.append(Maintenance(
                    mid=maint_data['mid'],
                    did=maint_data['did'],
                    issue=maint_data['issue'],
                    report_time=maint_data['report_time'],
                    handler=maint_data['handler'],
                    status=maint_data['status'],
                    complete_time=maint_data['complete_time']
                ))
        return maintenances
    
    @staticmethod
    def get_pending_maintenances():
        """
        获取所有待处理的维护记录
        :return: 维护记录列表
        """
        query = "SELECT * FROM maintenances WHERE status = '待处理' ORDER BY report_time ASC"
        return execute_query(query)
    
    @staticmethod
    def get_overdue_maintenances():
        """
        获取超时未处理的维护请求（>24小时）
        :return: 维护记录列表
        """
        query = """
            SELECT m.mid, d.dname, m.issue, m.report_time
            FROM maintenances m
            JOIN devices d ON m.did = d.did
            WHERE m.status = '待处理'
              AND m.report_time < NOW() - INTERVAL 24 HOUR
        """
        return execute_query(query)
    
    def create_with_device_update(self, reporter_id):
        """
        创建维护记录并更新设备状态（使用存储过程）
        :param reporter_id: 报修人ID
        :return: 成功返回True，失败返回False
        """
        if self.mid:
            return False  # 已有ID，不应使用此方法
        
        try:
            call_procedure('ProcessMaintenance', (self.did, self.issue, reporter_id))
            return True
        except Exception as e:
            print(f"维护记录创建失败: {e}")
            return False
    
    def save(self):
        """
        保存维护记录（新增或更新）
        :return: 成功返回True，失败返回False
        """
        if self.mid:
            # 更新现有维护记录
            query = """
                UPDATE maintenances 
                SET did = %s, issue = %s, handler = %s, status = %s, complete_time = %s
                WHERE mid = %s
            """
            params = (self.did, self.issue, self.handler, self.status, self.complete_time, self.mid)
            return execute_update(query, params) > 0
        else:
            # 新增维护记录
            query = """
                INSERT INTO maintenances (did, issue, report_time, handler, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (self.did, self.issue, self.report_time or datetime.now(), self.handler, self.status or '待处理')
            return execute_update(query, params) > 0
    
    def update_status(self, new_status, handler=None):
        """
        更新维护状态
        :param new_status: 新状态
        :param handler: 处理人
        :return: 成功返回True，失败返回False
        """
        if not self.mid:
            return False
        
        query = "UPDATE maintenances SET status = %s"
        params = [new_status]
        
        if handler:
            query += ", handler = %s"
            params.append(handler)
        
        if new_status == '已完成':
            query += ", complete_time = NOW()"
        
        query += " WHERE mid = %s"
        params.append(self.mid)
        
        result = execute_update(query, tuple(params)) > 0
        if result:
            self.status = new_status
            if handler:
                self.handler = handler
            if new_status == '已完成':
                self.complete_time = datetime.now()
        return result
    
    def delete(self):
        """
        删除维护记录
        :return: 成功返回True，失败返回False
        """
        if not self.mid:
            return False
        
        query = "DELETE FROM maintenances WHERE mid = %s"
        return execute_update(query, (self.mid,)) > 0
    
    @staticmethod
    def get_detailed_maintenances():
        """
        获取详细的维护信息（包含设备名称）
        :return: 维护详情列表
        """
        query = """
            SELECT m.*, d.dname, d.type
            FROM maintenances m
            JOIN devices d ON m.did = d.did
            ORDER BY m.report_time DESC
        """
        return execute_query(query)
