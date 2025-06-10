#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机房模型
"""

from app.utils.db_config import execute_query, execute_update

class Room:
    def __init__(self, rid=None, location=None, capacity=None, open_time=None):
        self.rid = rid
        self.location = location
        self.capacity = capacity
        self.open_time = open_time
    
    @staticmethod
    def get_by_id(rid):
        """
        根据ID获取机房
        :param rid: 机房ID
        :return: 机房对象
        """
        query = "SELECT * FROM rooms WHERE rid = %s"
        room_data = execute_query(query, (rid,), fetch_one=True)
        if room_data:
            return Room(
                rid=room_data['rid'],
                location=room_data['location'],
                capacity=room_data['capacity'],
                open_time=room_data['open_time']
            )
        return None
    
    @staticmethod
    def get_all_rooms():
        """
        获取所有机房
        :return: 机房列表
        """
        query = "SELECT * FROM rooms"
        rooms_data = execute_query(query)
        rooms = []
        
        if rooms_data:
            for room_data in rooms_data:
                rooms.append(Room(
                    rid=room_data['rid'],
                    location=room_data['location'],
                    capacity=room_data['capacity'],
                    open_time=room_data['open_time']
                ))
        return rooms
    
    def save(self):
        """
        保存机房（新增或更新）
        :return: 成功返回True，失败返回False
        """
        if self.rid:
            # 更新现有机房
            query = """
                UPDATE rooms 
                SET location = %s, capacity = %s, open_time = %s
                WHERE rid = %s
            """
            params = (self.location, self.capacity, self.open_time, self.rid)
            return execute_update(query, params) > 0
        else:
            # 新增机房
            query = """
                INSERT INTO rooms (location, capacity, open_time)
                VALUES (%s, %s, %s)
            """
            params = (self.location, self.capacity, self.open_time)
            return execute_update(query, params) > 0
    
    def delete(self):
        """
        删除机房
        :return: 成功返回True，失败返回False
        """
        if not self.rid:
            return False
        
        query = "DELETE FROM rooms WHERE rid = %s"
        return execute_update(query, (self.rid,)) > 0
