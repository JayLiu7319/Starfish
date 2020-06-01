# StarFish数据库版本管理与数据模型配置

[toc]

## 数据模型问题

这里要讨论的问题主要是两个方面：一方面是持久化存储和ORM，也就是数据模型和数据库的关系配置；另一方面是请求响应实例与数据模型，也就是wsme式的数据实例和数据模型的关系。我们这里先行定义一个数据模型TestEntity：

> **TestEntity**
>
> 		- id
> 		- name
> 		- manage_ip
> 		- created_at
> 		- updated_at

接下来我们要对应这个数据模型，定义几个模型：

- TestEntity 基本模型

- TestEntity WSME请求响应模型
- TestEntity ORM映射模型
- TestEntity 数据库模型

与之对应的，在StarFish中数据模型的基类分别有：

- 基本数据模型基类
- WSME请求响应模型基类
- ORM映射模型基类
- 数据库模型基类

Starfish中的数据模型之间的映射，大致流程是：

- *WSME+Pecan根据WSME请求模型，获取请求参数或实体，并从中抽出数据库所需参数* 
- *调用对应的数据库模型进行增删改查*
- *数据库模型建立数据库连接，根据ORM映射对具体的表进行操作，并返回数据*
- *WSME+Pecan将数据库返回的数据，转换为WSME的响应模型，向用户做出响应*

### 基本模型

在`starfish/common/data_models.py`路径下，定义了Starfish项目数据模型的基类`BaseDataModel`，以及我们的TestEntity数据模型：

~~~python
class BaseDataModel(object):
    """从略，主要实现了一些基本方法"""
    
class TestEntity(BaseDataModel):
    def __init__(self, id=None, name=None, manage_ip=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.manage_ip = manage_ip
        self.created_at = created_at
        self.updated_at = updated_at
~~~

这个数据模型主要是一个象征意义，它实际上并没有在数据库的查询和返回，或者web框架的请求与响应中起作用。仅仅在数据库查询出错时，在Log信息中出现并返回一些数据模型的实体信息。

### WSME请求响应模型

在`starfish/frame_api/common/types.py`路径下，定义了Starfish项目中的一些WSME基本数据类型，比如IP地址类型、URL路径类型，Page页面类型等，以及实现这些类型的基类及其基本方法。这些数据类型用在Pecan框架的请求响应当中。

在`starfish/frame_api/v1/types/test_entity.py`路径下，定义了TestEntity的基本请求响应类型，这些类型事实上是封装了一些基本类型（名称、uuid、日期时间……）。

```python
class BaseTestEntityType(types.BaseType):
    _type_to_model_map = {}
    _child_map = {}

class TestEntityResponse(BaseTestEntityType):

class TestEntityRootResponse(types.BaseType):

class TestEntitiesRootResponse(types.BaseType):

class TestEntityPOST(BaseTestEntityType):

class TestEntityRootPOST(types.BaseType):

class TestEntityPUT(BaseTestEntityType):

class TestEntityRootPUT(types.BaseType):

```

封装后的TestEntity的请求响应模型，会被WSME这个框架使用，用来检查并封装具体业务中的请求响应实体。

### ORM映射模型

在`starfish/db/base_models.py`路径下，定义了Starfish项目的基本ORM映射模型。

在`starfish/db/models.py`路径下，定义了TestEntity的ORM映射模型：

```python
class TestEntity(base_models.BASE, base_models.IdMixin,
                 models.TimestampMixin, base_models.NameMixin):
    __data_model__ = data_models.TestEntity

    __tablename__ = "test_entity"

    __v1_wsme__ = test_entity.TestEntityResponse

    manage_ip = sa.Column('manage_ip', sa.String(64), nullable=False)

```

这个ORM映射，本质上是封装了SqlAlchemy的ORM。构建了从数据库表到具体的类的映射。

### 数据库模型

在`starfish/db/repositories.py`路径下定义了数据库模型基类，和具体的TestEntity数据库。

```python
class BaseRepository(object):

class Repositories(object):
    def __init__(self):
        self.test_entity = TestEntityRepository()

class TestEntityRepository(BaseRepository):
    model_class = models.TestEntity
```



## 数据库版本管理

数据库版本管理的概念，也称为**Database Migration**。基本原理是：**在我们要使用的数据库中建立一张表，里面保存了数据库的当前版本，然后我们在代码中为每个数据库版本写好所需的SQL语句。当对一个数据库执行migration操作时，会执行从当前版本到目标版本之间的所有SQL语句**。举个例子：

1. 在*Version 1*时，我们在数据库中建立一个user表。
2. 在*Version 2*时，我们在数据库中建立一个project表。
3. 在*Version 3*时，我们修改user表，增加一个age列。

那么在我们对一个数据库执行migration操作，数据库的当前版本*Version 1*，我们设定的目标版本是*Version 3*，那么操作就是：建立一个project表，修改user表，增加一个age列，并且把数据库当前版本设置为*Version 3*。

数据库的版本管理是所有大型数据库项目的需求，每种语言都有自己的解决方案。OpenStack中主要使用SQLAlchemy的两种解决方案：[sqlalchemy-migrate](https://github.com/openstack/sqlalchemy-migrate)和[Alembic](https://alembic.readthedocs.org/en/latest/)。早期的OpenStack项目使用了sqlalchemy-migrate，后来换成了Alembic。做出这个切换的主要原因是Alembic对数据库版本的设计和管理更灵活，可以支持分支，而sqlalchemy-migrate只能支持直线的版本管理，具体可以看OpenStack的WiKi文档[Alembic](https://wiki.openstack.org/wiki/Obsolete:Alembic)。

StarFish项目中引入**Alembic**来进行版本管理。

要使用Alembic，大概需要以下步骤：

1. 安装Alembic
2. 在项目中创建Alembic的migration环境
3. **修改Alembic配置文件**
4. **创建migration脚本**
5. **执行迁移动作**

看起来步骤很复杂，其实搭建好环境后，**新增数据库版本只需要执行最后三个步骤。**

### 修改Alembic配置文件

`starfish/db/migration/alembic.ini`文件，是Alembic 的配置文件，我们现在需要修改文件中的**sqlalchemy.url**这个配置项，用来指向我们的数据库。这里，我们使用SQLite数据库，数据库文件存放在系统的`tmp`文件夹下。

```bash
# sqlalchemy.url = driver://user:pass@localhost/dbname
sqlalchemy.url = sqlite:////tmp/starfish.db
```

>在实际项目中，数据库的URL信息是从项目配置文件中读取，然后通过动态方式传给Alembic的。具体做法可以参考Octavia项目中的实现。

### 创建migration脚本

现在我们可以创建一个新的数据库版本了。我们需要通过创建一个迁移脚本，来进行我们想要的一些操作（比如新建一个test_entity表）：

```bash
$ alembic revision -m "Create user table"
```

现在脚本已经帮我们生成好了，不过这个只是一个空的脚本，我们需要自己实现里面的具体操作，补充完整后的脚本如下：

```python
"""Create test entity table

Revision ID: 308463f02e7a
Revises: 
Create Date: 2020-03-04 22:11:09.331965

"""
import sqlalchemy as sa
from alembic import op
from oslo_utils import uuidutils, timeutils

# revision identifiers, used by Alembic.
revision = '308463f02e7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'test_entity',
        sa.Column('id', sa.String(36), primary_key=True, default=uuidutils.generate_uuid),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('manage_ip', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime, default=lambda: timeutils.utcnow()),
        sa.Column('updated_at', sa.DateTime, onupdate=lambda: timeutils.utcnow())
    )


def downgrade():
    op.drop_table('test_entity')
```

其实就是把ORM映射类的定义再写了一遍，使用了Alembic提供的接口来方便的创建和删除表。

### 执行迁移操作

我们需要在`starfish/db/migration`目录下进行迁移操作。

```bash
# 可能需要手动指定PYTHONPATH
$ PYTHONPATH=../../../ alembic upgrade head
```

`alembic upgrade head`会把数据库升级到最新的版本。如果指定路径没有db文件，则会新建一个db文件。

### 测试数据库

我们需要修改一下`starfish/common/config.py`中`_SQL_CONNECTION_DEFAULT`配置项，将其设置为我们当前环境的数据库路径。然后就可以在代码中测试数据库相关的API了。

