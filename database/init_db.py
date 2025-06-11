import pymysql
import re
import os

# 从 app.utils.db_config 导入数据库配置
# 为了能够独立运行，需要将项目根目录添加到 sys.path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.utils.db_config import DB_CONFIG

def initialize_database():
    """
    初始化数据库。如果数据库不存在，则根据 create_database.sql 文件创建数据库和表。
    """
    db_name = DB_CONFIG['db']
    
    # 1. 连接到 MySQL 服务器 (不指定数据库)
    try:
        server_config = DB_CONFIG.copy()
        del server_config['db']
        
        connection = pymysql.connect(**server_config)
        print("成功连接到MySQL服务器。")
    except pymysql.Error as e:
        print(f"无法连接到MySQL服务器: {e}")
        print("请确保MySQL服务器正在运行，并且 'app/utils/db_config.py' 中的连接信息正确。")
        return

    try:
        with connection.cursor() as cursor:
            # 2. 检查数据库是否存在
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
            result = cursor.fetchone()

            if result:
                print(f"数据库 '{db_name}' 已存在，无需创建。")
                return

            # 3. 如果数据库不存在，则创建它
            print(f"数据库 '{db_name}' 不存在，正在创建...")
            
            # 读取SQL文件
            sql_file_path = os.path.join(os.path.dirname(__file__), 'create_database.sql')
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # 分割SQL命令
            # 使用正则表达式处理 DELIMITER 关键字
            # 默认分隔符为 ;
            delimiter = ';'
            statements = []
            current_statement = []

            for line in sql_script.splitlines():
                line = line.strip()
                if not line or line.startswith('--'):
                    continue
                
                if line.upper().startswith('DELIMITER'):
                    delimiter = line.split()[1]
                    continue
                
                current_statement.append(line)
                if line.endswith(delimiter):
                    statement = " ".join(current_statement)
                    # 去掉末尾的分隔符
                    statements.append(statement[:-len(delimiter)].strip())
                    current_statement = []
            
            # 执行SQL命令
            total_statements = len(statements)
            for i, statement in enumerate(statements):
                if not statement:
                    continue
                try:
                    # 对于 `CREATE DATABASE` 后的语句，需要重新连接到指定数据库
                    if statement.strip().upper().startswith('USE'):
                        connection.select_db(db_name)
                        print(f"切换到数据库 '{db_name}'")
                        continue

                    cursor.execute(statement)
                    # 打印进度
                    print(f"正在执行初始化... ({(i+1)}/{total_statements})", end='\r')
                except pymysql.Error as e:
                    # 某些用户创建语句如果用户已存在会报错，可以忽略
                    if "Cannot create a user that already exists" in str(e):
                        print(f"\n警告: {e}")
                    else:
                        print(f"\n执行SQL语句时出错: {statement}\n错误: {e}")
                        raise
            
            print("\n数据库初始化成功！")
            
            connection.commit()

    except Exception as e:
        print(f"\n数据库初始化失败: {e}")
    finally:
        connection.close()

if __name__ == '__main__':
    initialize_database() 