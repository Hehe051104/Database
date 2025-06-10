#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库配置模块
"""

import pymysql
from pymysql.cursors import DictCursor

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'db': 'RoomManagement',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

def get_db_connection():
    """
    获取数据库连接
    :return: 数据库连接对象
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def execute_query(query, params=None, fetch_one=False):
    """
    执行查询语句
    :param query: SQL查询语句
    :param params: 查询参数
    :param fetch_one: 是否只获取一条记录
    :return: 查询结果
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"查询执行失败: {e}")
        return None
    finally:
        connection.close()

def execute_update(query, params=None):
    """
    执行更新语句（INSERT, UPDATE, DELETE）
    :param query: SQL更新语句
    :param params: 更新参数
    :return: 受影响的行数，失败返回-1
    """
    connection = get_db_connection()
    if not connection:
        return -1
    
    try:
        with connection.cursor() as cursor:
            affected_rows = cursor.execute(query, params)
            connection.commit()
            return affected_rows
    except Exception as e:
        connection.rollback()
        print(f"更新执行失败: {e}")
        return -1
    finally:
        connection.close()

def call_procedure(proc_name, params=None):
    """
    调用存储过程
    :param proc_name: 存储过程名称
    :param params: 存储过程参数
    :return: 存储过程执行结果
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            if params:
                cursor.callproc(proc_name, params)
            else:
                cursor.callproc(proc_name)
            result = cursor.fetchall()
            connection.commit()
            return result
    except Exception as e:
        connection.rollback()
        print(f"存储过程调用失败: {e}")
        return None
    finally:
        connection.close()
