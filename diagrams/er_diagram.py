#!/usr/bin/env python3
from graphviz import Digraph

# 创建ER图
er = Digraph('ER', filename='er_diagram', format='png')
er.attr(rankdir='LR', size='8,5')

# 设置节点样式
er.attr('node', shape='box', style='filled', color='lightblue')

# 添加实体
er.node('users', '用户(users)\n用户ID(uid)\n姓名(uname)\n角色(role)\n学号/工号(code)\n密码(password)\n联系方式(phone)')
er.node('devices', '设备(devices)\n设备ID(did)\n名称(dname)\n类型(type)\n配置(spec)\n状态(status)\n机房ID(room_id)')
er.node('rooms', '机房(rooms)\n机房ID(rid)\n位置(location)\n容量(capacity)\n开放时间(open_time)')
er.node('reservations', '预约记录(reservations)\n预约ID(res_id)\n用户ID(uid)\n设备ID(did)\n开始时间(start_time)\n结束时间(end_time)\n状态(status)')
er.node('maintenances', '维护记录(maintenances)\n维护ID(mid)\n设备ID(did)\n故障描述(issue)\n报修时间(report_time)\n处理人(handler)\n状态(status)')
er.node('audit_log', '操作日志(audit_log)\n日志ID(log_id)\n用户ID(user_id)\n操作类型(action)\n目标表(target_table)\nSQL文本(sql_text)\nIP地址(ip_address)\n操作时间(action_time)')

# 添加关系
er.edge('users', 'reservations', label='创建')
er.edge('devices', 'reservations', label='被预约')
er.edge('rooms', 'devices', label='包含')
er.edge('devices', 'maintenances', label='报修')
er.edge('users', 'audit_log', label='产生')

# 保存图像
er.render(cleanup=True)
print("ER图已生成: er_diagram.png")
