#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
预约模型
"""

from app.utils.db_config import execute_query, execute_update, call_procedure
from datetime import datetime

class Reservation:
    def __init__(self, res_id=None, uid=None, did=None, start_time=None, end_time=None, status=None):
        self.res_id = res_id
        self.uid = uid
        self.did = did
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
    
    @staticmethod
    def get_by_id(res_id):
        """
        根据ID获取预约记录
        :param res_id: 预约ID
        :return: 预约对象
        """
        query = "SELECT * FROM reservations WHERE res_id = %s"
        res_data = execute_query(query, (res_id,), fetch_one=True)
        if res_data:
            return Reservation(
                res_id=res_data['res_id'],
                uid=res_data['uid'],
                did=res_data['did'],
                start_time=res_data['start_time'],
                end_time=res_data['end_time'],
                status=res_data['status']
            )
        return None
    
    @staticmethod
    def get_by_user(uid):
        """
        获取用户的所有预约
        :param uid: 用户ID
        :return: 预约列表
        """
        query = "SELECT * FROM reservations WHERE uid = %s ORDER BY start_time DESC"
        res_data_list = execute_query(query, (uid,))
        reservations = []
        
        if res_data_list:
            for res_data in res_data_list:
                reservations.append(Reservation(
                    res_id=res_data['res_id'],
                    uid=res_data['uid'],
                    did=res_data['did'],
                    start_time=res_data['start_time'],
                    end_time=res_data['end_time'],
                    status=res_data['status']
                ))
        return reservations
    
    @staticmethod
    def get_by_device(did):
        """
        获取设备的所有预约
        :param did: 设备ID
        :return: 预约列表
        """
        query = "SELECT * FROM reservations WHERE did = %s ORDER BY start_time DESC"
        res_data_list = execute_query(query, (did,))
        reservations = []
        
        if res_data_list:
            for res_data in res_data_list:
                reservations.append(Reservation(
                    res_id=res_data['res_id'],
                    uid=res_data['uid'],
                    did=res_data['did'],
                    start_time=res_data['start_time'],
                    end_time=res_data['end_time'],
                    status=res_data['status']
                ))
        return reservations
    
    @staticmethod
    def get_pending_reviews():
        """
        获取所有待审核的预约
        :return: 预约列表
        """
        query = "SELECT * FROM teacher_review"
        return execute_query(query)
    
    @staticmethod
    def check_conflict(did, start_time, end_time, exclude_res_id=None):
        """
        检查预约时间是否冲突
        :param did: 设备ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param exclude_res_id: 排除的预约ID（用于更新时）
        :return: 有冲突返回True，无冲突返回False
        """
        query = """
            SELECT COUNT(*) as conflict_count
            FROM reservations
            WHERE did = %s
              AND status = '已确认'
              AND %s < end_time
              AND %s > start_time
        """
        params = [did, start_time, end_time]
        
        if exclude_res_id:
            query += " AND res_id != %s"
            params.append(exclude_res_id)
        
        result = execute_query(query, tuple(params), fetch_one=True)
        return result['conflict_count'] > 0
    
    def create_with_conflict_check(self):
        """
        创建预约并检查冲突（使用存储过程）
        :return: 成功返回True，失败返回False
        """
        if self.res_id:
            return False  # 已有ID，不应使用此方法
        
        try:
            call_procedure('CheckReservationConflict', (self.uid, self.did, self.start_time, self.end_time))
            return True
        except Exception as e:
            print(f"预约创建失败: {e}")
            return False
    
    def save(self):
        """
        保存预约（新增或更新）
        :return: 成功返回True，失败返回False
        """
        if self.res_id:
            # 更新现有预约
            query = """
                UPDATE reservations 
                SET uid = %s, did = %s, start_time = %s, end_time = %s, status = %s
                WHERE res_id = %s
            """
            params = (self.uid, self.did, self.start_time, self.end_time, self.status, self.res_id)
            return execute_update(query, params) > 0
        else:
            # 新增预约
            query = """
                INSERT INTO reservations (uid, did, start_time, end_time, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (self.uid, self.did, self.start_time, self.end_time, self.status or '待审核')
            return execute_update(query, params) > 0
    
    def update_status(self, new_status):
        """
        更新预约状态
        :param new_status: 新状态
        :return: 成功返回True，失败返回False
        """
        if not self.res_id:
            return False
        
        query = "UPDATE reservations SET status = %s WHERE res_id = %s"
        params = (new_status, self.res_id)
        result = execute_update(query, params) > 0
        if result:
            self.status = new_status
        return result
    
    def delete(self):
        """
        删除预约
        :return: 成功返回True，失败返回False
        """
        if not self.res_id:
            return False
        
        query = "DELETE FROM reservations WHERE res_id = %s"
        return execute_update(query, (self.res_id,)) > 0
    
    @staticmethod
    def get_detailed_reservations():
        """
        获取详细的预约信息（包含用户名和设备名）
        :return: 预约详情列表
        """
        query = """
            SELECT r.res_id, r.uid, r.did, r.start_time, r.end_time, r.status,
                   u.uname, d.dname, d.type
            FROM reservations r
            JOIN users u ON r.uid = u.uid
            JOIN devices d ON r.did = d.did
            ORDER BY r.start_time DESC
        """
        return execute_query(query)
