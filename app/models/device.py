#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设备模型
"""

from app.utils.db_config import execute_query, execute_update

class Device:
    def __init__(self, did=None, dname=None, type=None, spec=None, status=None, room_id=None):
        self.did = did
        self.dname = dname
        self.type = type
        self.spec = spec
        self.status = status
        self.room_id = room_id
    
    @staticmethod
    def get_by_id(did):
        """
        根据ID获取设备
        :param did: 设备ID
        :return: 设备对象
        """
        query = "SELECT * FROM devices WHERE did = %s"
        device_data = execute_query(query, (did,), fetch_one=True)
        if device_data:
            return Device(
                did=device_data['did'],
                dname=device_data['dname'],
                type=device_data['type'],
                spec=device_data['spec'],
                status=device_data['status'],
                room_id=device_data['room_id']
            )
        return None
    
    @staticmethod
    def get_all_devices():
        """
        获取所有设备
        :return: 设备列表
        """
        query = "SELECT * FROM devices"
        devices_data = execute_query(query)
        devices = []
        
        if devices_data:
            for device_data in devices_data:
                devices.append(Device(
                    did=device_data['did'],
                    dname=device_data['dname'],
                    type=device_data['type'],
                    spec=device_data['spec'],
                    status=device_data['status'],
                    room_id=device_data['room_id']
                ))
        return devices
    
    @staticmethod
    def get_devices_by_room(room_id):
        """
        根据机房ID获取设备
        :param room_id: 机房ID
        :return: 设备列表
        """
        query = "SELECT * FROM devices WHERE room_id = %s"
        devices_data = execute_query(query, (room_id,))
        devices = []
        
        if devices_data:
            for device_data in devices_data:
                devices.append(Device(
                    did=device_data['did'],
                    dname=device_data['dname'],
                    type=device_data['type'],
                    spec=device_data['spec'],
                    status=device_data['status'],
                    room_id=device_data['room_id']
                ))
        return devices
    
    @staticmethod
    def get_available_devices():
        """
        获取所有空闲设备
        :return: 设备列表
        """
        query = "SELECT * FROM devices WHERE status = '空闲'"
        devices_data = execute_query(query)
        devices = []
        
        if devices_data:
            for device_data in devices_data:
                devices.append(Device(
                    did=device_data['did'],
                    dname=device_data['dname'],
                    type=device_data['type'],
                    spec=device_data['spec'],
                    status=device_data['status'],
                    room_id=device_data['room_id']
                ))
        return devices
    
    @staticmethod
    def get_device_details():
        """
        获取设备详情（包含机房位置）
        :return: 设备详情列表
        """
        query = "SELECT * FROM device_details"
        return execute_query(query)
    
    def save(self):
        """
        保存设备（新增或更新）
        :return: 成功返回True，失败返回False
        """
        if self.did:
            # 更新现有设备
            query = """
                UPDATE devices 
                SET dname = %s, type = %s, spec = %s, status = %s, room_id = %s
                WHERE did = %s
            """
            params = (self.dname, self.type, self.spec, self.status, self.room_id, self.did)
            return execute_update(query, params) > 0
        else:
            # 新增设备
            query = """
                INSERT INTO devices (dname, type, spec, status, room_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (self.dname, self.type, self.spec, self.status, self.room_id)
            return execute_update(query, params) > 0
    
    def update_status(self, new_status):
        """
        更新设备状态
        :param new_status: 新状态
        :return: 成功返回True，失败返回False
        """
        if not self.did:
            return False
        
        query = "UPDATE devices SET status = %s WHERE did = %s"
        params = (new_status, self.did)
        result = execute_update(query, params) > 0
        if result:
            self.status = new_status
        return result
    
    def delete(self):
        """
        删除设备
        :return: 成功返回True，失败返回False
        """
        if not self.did:
            return False
        
        query = "DELETE FROM devices WHERE did = %s"
        return execute_update(query, (self.did,)) > 0
