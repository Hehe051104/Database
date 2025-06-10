#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户模型
"""

from app.utils.db_config import execute_query, execute_update
import hashlib

class User:
    def __init__(self, uid=None, uname=None, role=None, code=None, password=None, phone=None):
        self.uid = uid
        self.uname = uname
        self.role = role
        self.code = code
        self.password = password
        self.phone = phone
    
    @staticmethod
    def get_by_id(uid):
        """
        根据ID获取用户
        :param uid: 用户ID
        :return: 用户对象
        """
        query = "SELECT * FROM users WHERE uid = %s"
        user_data = execute_query(query, (uid,), fetch_one=True)
        if user_data:
            return User(
                uid=user_data['uid'],
                uname=user_data['uname'],
                role=user_data['role'],
                code=user_data['code'],
                password=user_data['password'],
                phone=user_data['phone']
            )
        return None
    
    @staticmethod
    def get_by_code(code):
        """
        根据学号/工号获取用户
        :param code: 学号/工号
        :return: 用户对象
        """
        query = "SELECT * FROM users WHERE code = %s"
        user_data = execute_query(query, (code,), fetch_one=True)
        if user_data:
            return User(
                uid=user_data['uid'],
                uname=user_data['uname'],
                role=user_data['role'],
                code=user_data['code'],
                password=user_data['password'],
                phone=user_data['phone']
            )
        return None
    
    @staticmethod
    def authenticate(code, password):
        """
        用户认证
        :param code: 学号/工号
        :param password: 密码
        :return: 认证成功返回用户对象，失败返回None
        """
        # 对密码进行SHA-256加密
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        query = "SELECT * FROM users WHERE code = %s AND password = %s"
        user_data = execute_query(query, (code, hashed_password), fetch_one=True)
        
        if user_data:
            return User(
                uid=user_data['uid'],
                uname=user_data['uname'],
                role=user_data['role'],
                code=user_data['code'],
                password=user_data['password'],
                phone=user_data['phone']
            )
        return None
    
    @staticmethod
    def get_all_users():
        """
        获取所有用户
        :return: 用户列表
        """
        query = "SELECT * FROM users"
        users_data = execute_query(query)
        users = []
        
        if users_data:
            for user_data in users_data:
                users.append(User(
                    uid=user_data['uid'],
                    uname=user_data['uname'],
                    role=user_data['role'],
                    code=user_data['code'],
                    password=user_data['password'],
                    phone=user_data['phone']
                ))
        return users
    
    def save(self):
        """
        保存用户（新增或更新）
        :return: 成功返回True，失败返回False
        """
        if self.uid:
            # 更新现有用户
            query = """
                UPDATE users 
                SET uname = %s, role = %s, code = %s, phone = %s
                WHERE uid = %s
            """
            params = (self.uname, self.role, self.code, self.phone, self.uid)
            return execute_update(query, params) > 0
        else:
            # 新增用户
            # 对密码进行SHA-256加密
            hashed_password = hashlib.sha256(self.password.encode()).hexdigest()
            
            query = """
                INSERT INTO users (uname, role, code, password, phone)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (self.uname, self.role, self.code, hashed_password, self.phone)
            return execute_update(query, params) > 0
    
    def update_password(self, new_password):
        """
        更新用户密码
        :param new_password: 新密码
        :return: 成功返回True，失败返回False
        """
        if not self.uid:
            return False
        
        # 对密码进行SHA-256加密
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        
        query = "UPDATE users SET password = %s WHERE uid = %s"
        params = (hashed_password, self.uid)
        return execute_update(query, params) > 0
    
    def delete(self):
        """
        删除用户
        :return: 成功返回True，失败返回False
        """
        if not self.uid:
            return False
        
        query = "DELETE FROM users WHERE uid = %s"
        return execute_update(query, (self.uid,)) > 0
