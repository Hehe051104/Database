# 实验室设备与机房管理系统 - 目录结构说明

本项目是一个基于 Python Flask 和 MySQL 的 Web 应用程序。以下是项目的主要目录和文件结构说明：

## 根目录文件

- `run.py`:
  项目的总入口文件。执行 `python run.py` 即可启动 Web 服务器。

- `requirements.txt`:
  定义了项目所需的所有 Python 第三方库及其版本。可通过 `pip install -r requirements.txt` 命令一键安装所有依赖。

- `user_manual.md`:
  系统的用户使用手册，详细介绍了各项功能的操作方法。

- `README.md`:
  项目的基础自述文件。
  
- `readme.txt` (本文件):
  对项目代码目录结构的详细说明。

## 主要目录

### `/app`
本项目的核心应用程序目录，遵循标准的 Flask 项目结构。

- `/app/controllers`: 控制器目录。
  存放所有业务逻辑的蓝图（Blueprint）。每个文件对应一个功能模块（如 `device_controller.py` 负责设备管理），负责处理 HTTP 请求、调用模型层并返回响应。

- `/app/models`: 模型目录。
  存放所有与数据库表对应的模型类。这些类封装了对数据库的直接操作（CRUD），以及相关的业务逻辑（如密码加密、冲突检测算法等）。

- `/app/static`: 静态文件目录。
  存放前端页面所需的静态资源，如 CSS 样式表、JavaScript 脚本、图片等。

- `/app/templates`: 模板目录。
  存放所有 HTML 页面模板。后端通过渲染这些模板来生成用户看到的页面。

- `/app/utils`: 工具类目录。
  存放项目通用的辅助模块。例如 `db_config.py`，它封装了数据库连接池和执行 SQL 的方法，供所有模型类调用。

- `app.py`: 应用工厂。
  定义了 `create_app()` 函数，用于创建和配置 Flask 应用实例，注册所有蓝图，并设置全局路由。

### `/database`
存放与数据库设计和构建相关的 SQL 脚本。

- `tables.sql`: 包含了所有数据表的创建语句（DDL）。
- `views.sql`: 包含了所有数据库视图的创建语句。
- `procedures.sql`: 包含了所有存储过程的创建语句。
- `data.sql`: (可选) 包含了一些用于测试的初始数据。

### `/diagrams`
存放项目设计过程中的图表文件。

- `er_diagram.png`: 数据库的实体-关系（E-R）图。
- `flowcharts/`: 可能包含各个业务流程的流程图。 