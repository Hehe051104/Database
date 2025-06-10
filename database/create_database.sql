-- 机房管理系统数据库脚本
-- 创建数据库
DROP DATABASE IF EXISTS RoomManagement;
CREATE DATABASE RoomManagement DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE RoomManagement;

-- 创建用户表
CREATE TABLE users (
                       uid INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
                       uname VARCHAR(50) NOT NULL COMMENT '姓名',
                       role ENUM('学生', '教师', '管理员') NOT NULL COMMENT '角色',
                       code VARCHAR(20) NOT NULL UNIQUE COMMENT '学号/工号',
                       password VARCHAR(64) NOT NULL COMMENT '密码',
                       phone VARCHAR(20) COMMENT '联系方式',
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                       INDEX idx_role (role) COMMENT '角色索引'
) COMMENT='用户表';

-- 创建机房表
CREATE TABLE rooms (
                       rid INT PRIMARY KEY AUTO_INCREMENT COMMENT '机房ID',
                       location VARCHAR(100) NOT NULL COMMENT '位置',
                       capacity INT NOT NULL COMMENT '容量',
                       open_time VARCHAR(100) NOT NULL COMMENT '开放时间',
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='机房表';

-- 创建设备表
CREATE TABLE devices (
                         did INT PRIMARY KEY AUTO_INCREMENT COMMENT '设备ID',
                         dname VARCHAR(100) NOT NULL COMMENT '名称',
                         type VARCHAR(50) NOT NULL COMMENT '类型',
                         spec TEXT COMMENT '配置',
                         status ENUM('空闲', '使用中', '维护中') NOT NULL DEFAULT '空闲' COMMENT '状态',
                         room_id INT NOT NULL COMMENT '机房ID',
                         created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                         updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                         FOREIGN KEY (room_id) REFERENCES rooms(rid) ON DELETE CASCADE ON UPDATE CASCADE,
                         INDEX idx_device_status (status) COMMENT '设备状态索引'
) COMMENT='设备表';

-- 创建预约记录表
CREATE TABLE reservations (
                              res_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '预约ID',
                              uid INT NOT NULL COMMENT '用户ID',
                              did INT NOT NULL COMMENT '设备ID',
                              start_time DATETIME NOT NULL COMMENT '开始时间',
                              end_time DATETIME NOT NULL COMMENT '结束时间',
                              status ENUM('待审核', '已确认', '已取消', '已完成') NOT NULL DEFAULT '待审核' COMMENT '状态',
                              created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                              updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                              FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE ON UPDATE CASCADE,
                              FOREIGN KEY (did) REFERENCES devices(did) ON DELETE CASCADE ON UPDATE CASCADE,
                              INDEX idx_res_time (start_time, end_time) COMMENT '预约时间索引',
                              INDEX idx_res_status (status) COMMENT '预约状态索引'
) COMMENT='预约记录表';

-- 创建维护记录表
CREATE TABLE maintenances (
                              mid INT PRIMARY KEY AUTO_INCREMENT COMMENT '维护ID',
                              did INT NOT NULL COMMENT '设备ID',
                              issue TEXT NOT NULL COMMENT '故障描述',
                              report_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '报修时间',
                              handler VARCHAR(50) COMMENT '处理人',
                              status ENUM('待处理', '维修中', '已完成') NOT NULL DEFAULT '待处理' COMMENT '状态',
                              complete_time DATETIME COMMENT '完成时间',
                              created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                              updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                              FOREIGN KEY (did) REFERENCES devices(did) ON DELETE CASCADE ON UPDATE CASCADE,
                              INDEX idx_maintenance_status (status) COMMENT '维护状态索引'
) COMMENT='维护记录表';

-- 创建操作日志表（选做）
CREATE TABLE audit_log (
                           log_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
                           user_id INT NOT NULL COMMENT '用户ID',
                           action VARCHAR(50) NOT NULL COMMENT '操作类型',
                           target_table VARCHAR(30) NOT NULL COMMENT '目标表',
                           sql_text TEXT NOT NULL COMMENT 'SQL文本',
                           ip_address VARCHAR(45) COMMENT 'IP地址',
                           action_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
                           FOREIGN KEY (user_id) REFERENCES users(uid) ON DELETE CASCADE ON UPDATE CASCADE
) COMMENT='操作日志表';

-- 创建视图：设备详情视图（含机房位置）
CREATE VIEW device_details AS
SELECT d.did, d.dname, d.type, d.status, r.location, r.rid as room_id
FROM devices d
         JOIN rooms r ON d.room_id = r.rid;

-- 创建视图：教师审核视图（仅显示待审核记录）
CREATE VIEW teacher_review AS
SELECT res_id, uid, did, start_time, end_time
FROM reservations
WHERE status = '待审核';

-- 创建视图：设备使用率统计视图
CREATE VIEW device_usage_stats AS
SELECT
    d.did,
    d.dname,
    d.type,
    COUNT(r.res_id) AS reservation_count,
    SUM(TIMESTAMPDIFF(HOUR, r.start_time, r.end_time)) AS total_hours_used
FROM devices d
         LEFT JOIN reservations r ON d.did = r.did AND r.status = '已完成'
GROUP BY d.did, d.dname, d.type;

-- 创建存储过程：自动处理预约冲突
DELIMITER $$
CREATE PROCEDURE CheckReservationConflict(IN new_uid INT, IN new_did INT, IN new_start DATETIME, IN new_end DATETIME)
BEGIN
    DECLARE conflict_count INT;
SELECT COUNT(*) INTO conflict_count
FROM reservations
WHERE did = new_did
  AND status = '已确认'
  AND new_start < end_time
  AND new_end > start_time;

IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '时间冲突，预约失败';
ELSE
        INSERT INTO reservations (uid, did, start_time, end_time, status)
        VALUES (new_uid, new_did, new_start, new_end, '待审核');
END IF;
END$$
DELIMITER ;

-- 创建存储过程：设备维护处理
DELIMITER $$
CREATE PROCEDURE ProcessMaintenance(IN device_id INT, IN issue_desc TEXT, IN reporter_id INT)
BEGIN
    -- 开始事务
START TRANSACTION;

-- 步骤1：标记设备为维护中
UPDATE devices SET status = '维护中' WHERE did = device_id;

-- 步骤2：创建维护记录
INSERT INTO maintenances (did, issue, report_time)
VALUES (device_id, issue_desc, NOW());

-- 步骤3：取消关联预约
UPDATE reservations
SET status = '已取消'
WHERE did = device_id AND status = '已确认' AND end_time > NOW();

-- 步骤4：记录审计日志
INSERT INTO audit_log (user_id, action, target_table, sql_text)
VALUES (reporter_id, 'MAINTENANCE', 'devices', CONCAT('设备报修：', device_id));

-- 提交事务
COMMIT;
END$$
DELIMITER ;

-- 创建触发器：设备状态自动更新（当预约确认时）
DELIMITER $$
CREATE TRIGGER trg_device_status_update
    AFTER UPDATE ON reservations
    FOR EACH ROW
BEGIN
    IF NEW.status = '已确认' AND OLD.status != '已确认' THEN
    UPDATE devices SET status = '使用中' WHERE did = NEW.did;
END IF;

IF NEW.status = '已取消' AND OLD.status = '已确认' THEN
UPDATE devices SET status = '空闲' WHERE did = NEW.did;
END IF;
END$$
DELIMITER ;

-- 创建触发器：维护完成时更新设备状态
DELIMITER $$
CREATE TRIGGER trg_maintenance_complete
    AFTER UPDATE ON maintenances
    FOR EACH ROW
BEGIN
    IF NEW.status = '已完成' AND OLD.status != '已完成' THEN
    UPDATE devices SET status = '空闲' WHERE did = NEW.did;
END IF;
END$$
DELIMITER ;

-- 创建触发器：审计日志记录（预约操作）
DELIMITER $$
CREATE TRIGGER trg_audit_reservations
    AFTER INSERT ON reservations
    FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, action, target_table, sql_text)
    VALUES (NEW.uid, 'INSERT', 'reservations', CONCAT('添加预约：', NEW.res_id));
    END$$
    DELIMITER ;

-- 创建用户和权限
-- 创建学生用户
CREATE USER IF NOT EXISTS 'student_user'@'%' IDENTIFIED BY 'Std@123';
GRANT SELECT, INSERT ON RoomManagement.reservations TO 'student_user'@'%';
    GRANT SELECT ON RoomManagement.devices TO 'student_user'@'%';
    GRANT SELECT ON RoomManagement.rooms TO 'student_user'@'%';
    GRANT SELECT ON RoomManagement.device_details TO 'student_user'@'%';

-- 创建教师用户
    CREATE USER IF NOT EXISTS 'teacher_user'@'localhost' IDENTIFIED BY 'Tea@456';
GRANT SELECT, INSERT, UPDATE ON RoomManagement.reservations TO 'teacher_user'@'localhost';
    GRANT INSERT ON RoomManagement.maintenances TO 'teacher_user'@'localhost';
GRANT SELECT ON RoomManagement.devices TO 'teacher_user'@'localhost';
    GRANT SELECT ON RoomManagement.rooms TO 'teacher_user'@'localhost';
    GRANT SELECT ON RoomManagement.teacher_review TO 'teacher_user'@'localhost';

-- 创建管理员用户
    CREATE USER IF NOT EXISTS 'admin_user'@'localhost' IDENTIFIED BY 'Adm@789';
GRANT ALL PRIVILEGES ON RoomManagement.* TO 'admin_user'@'localhost';

-- 插入测试数据
-- 插入用户数据
    INSERT INTO users (uname, role, code, password, phone) VALUES
                                                               ('张三', '学生', '2023001', SHA2('password123', 256), '13800138001'),
                                                               ('李四', '学生', '2023002', SHA2('password123', 256), '13800138002'),
                                                               ('王五', '教师', 'T2023001', SHA2('password456', 256), '13900139001'),
                                                               ('赵六', '教师', 'T2023002', SHA2('password456', 256), '13900139002'),
                                                               ('管理员', '管理员', 'A2023001', SHA2('admin123', 256), '13700137001');

-- 插入机房数据
    INSERT INTO rooms (location, capacity, open_time) VALUES
                                                          ('教学楼A栋101', 50, '周一至周五 8:00-22:00，周末 9:00-18:00'),
                                                          ('教学楼B栋202', 40, '周一至周五 8:00-22:00，周末 9:00-18:00'),
                                                          ('图书馆3楼', 30, '每天 8:00-22:00');

-- 插入设备数据
    INSERT INTO devices (dname, type, spec, status, room_id) VALUES
                                                                 ('计算机A01', '台式电脑', 'Intel i5-12400, 16GB RAM, 512GB SSD', '空闲', 1),
                                                                 ('计算机A02', '台式电脑', 'Intel i5-12400, 16GB RAM, 512GB SSD', '空闲', 1),
                                                                 ('计算机A03', '台式电脑', 'Intel i5-12400, 16GB RAM, 512GB SSD', '空闲', 1),
                                                                 ('计算机B01', '台式电脑', 'Intel i7-12700, 32GB RAM, 1TB SSD', '空闲', 2),
                                                                 ('计算机B02', '台式电脑', 'Intel i7-12700, 32GB RAM, 1TB SSD', '使用中', 2),
                                                                 ('计算机C01', '工作站', 'AMD Ryzen 9 5950X, 64GB RAM, 2TB SSD', '空闲', 3),
                                                                 ('投影仪01', '投影设备', 'Epson 1080p', '空闲', 1),
                                                                 ('打印机01', '打印设备', 'HP LaserJet Pro', '维护中', 2);

-- 插入预约记录
    INSERT INTO reservations (uid, did, start_time, end_time, status) VALUES
                                                                          (1, 1, '2025-06-03 13:00:00', '2025-06-03 15:00:00', '已确认'),
                                                                          (2, 4, '2025-06-03 14:00:00', '2025-06-03 16:00:00', '已确认'),
                                                                          (1, 6, '2025-06-04 09:00:00', '2025-06-04 11:00:00', '待审核'),
                                                                          (2, 7, '2025-06-04 13:00:00', '2025-06-04 15:00:00', '待审核'),
                                                                          (1, 3, '2025-06-02 10:00:00', '2025-06-02 12:00:00', '已完成');

-- 插入维护记录
    INSERT INTO maintenances (did, issue, report_time, handler, status) VALUES
                                                                            (8, '打印机卡纸', '2025-06-01 09:30:00', '技术员小王', '维修中'),
                                                                            (5, '系统蓝屏', '2025-06-02 14:20:00', NULL, '待处理'),
                                                                            (3, '显示器故障', '2025-05-30 11:15:00', '技术员小李', '已完成');

-- 插入审计日志
    INSERT INTO audit_log (user_id, action, target_table, sql_text, ip_address) VALUES
                                                                                    (5, 'INSERT', 'devices', '添加设备：计算机A01', '192.168.1.100'),
                                                                                    (5, 'UPDATE', 'devices', '更新设备状态：计算机B02', '192.168.1.100'),
                                                                                    (3, 'INSERT', 'maintenances', '报修设备：打印机01', '192.168.1.101');
