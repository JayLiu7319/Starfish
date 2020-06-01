# StarFish项目框架代码说明

StarFish项目框架代码，包括了API、控制层、代理层的主要代码框架，并给出了基本的服务调用示例和数据库操作示例。

## 前置条件

### 0，Python运行环境

Python版本为3.6+

### 1，安装消息队列RabbitMq

[CentOS安装RabbitMQ](https://www.cnblogs.com/toutou/p/install_rabbitmq.html#_label1)

### 2，安装依赖项

在StarFish项目主目录下，使用

~~~bash
pip3 install -r requirements
~~~

### 3，安装StarFish包

两种方式：

- 手动打包，更新项目版本并安装。

  在StarFish 项目下，存在`setup.py`与`setup.cfg`两个文件。在根目录下：

  ~~~bash
  python3 setup.py sdist
  ~~~

  会生成dist目录，和.tar.gz压缩包。手动安装.tar.gz安装包

  ~~~bash
  pip3 install starfish*****.tar.gz
  ~~~

- 使用已经打好的压缩包。

  ~~~bash
  pip3 install starfish*****.tar.gz
  ~~~

### 4，配置相关参数

- 数据库版本管理与配置。详见[《StarFish数据库版本管理与数据模型配置》](./StarFish数据库版本管理与数据模型配置.md)中数据库版本管理部分。

- 配置RestFul地址。项目中有三个位置需要对ip及端口进行配置：

  - api对外暴露服务端点：`starfish/cmd/api.py: 36`
  - driver向后端agent发送请求：`starfish/controller/worker/v1/tasks/amphora_driver_tasks.py:30`
  - agent向worker层暴露服务端点：`starfish/cmd/agent.py: 64`

  *测试代码的话，只需要将ip替换为本机ip即可。*

## 代码启动

代码需要同时启动三个进程：api进程、controller进程、agent进程。基本的控制流是从api到controller再到agent。

- api进程启动路径：`starfish\cmd\api.py`

- controller启动路径：`starfish\cmd\controller_worker.py`

- agent启动路径：`starfish\cmd\agent.py`

三个进程同时启动即可。

## 代码测试

目前代码是框架代码，主要实现了两个任务：

- 基本的数据库中表项的创建删除
- 从agent端获取信息

目前项目还没有单元测试。

使用Postman通过向api层发送restful请求，来测试这两个功能。在Postman中导入[Starfish API request](./Starfish API.postman_collection.json)，并修改request的ip为项目运行的主机，发送请求。



