# OpenStack扩展设计之stevedore插件
[toc]

OpenStack的Nova API提供了供开发者扩展接口，Neutron能够支持不同的网络虚拟化设备，Ceilometer能够支持不同的计费统计方法，都是通过插件机制实现的。不仅如此，很多厂商的定制OpenStack，通过插件，在不改变社区核心代码的前提下，扩展OpenStack的功能。

OpenStack的插件机制，是通过stevedore这个库实现的。

## 为什么要引入插件？

插件机制最重要的作用，是能够保持核心代码和扩展代码之间的分离，提高设计的抽象层次。虽然引入插件机制会带来更多的工作量，但从长远角度，也让你的系统具有更好的弹性和可维护性。

可以通过插线来实现设备驱动或者其他**策略模式**。应用系统维护通用核心逻辑，而与外部设备和系统的交互工作，就留给插件来完成。

通过将扩展程序与核心程序分开打包，可以有效降低软件包随着时间推移越发臃肿的问题。部署和管理也相应的变得容易，用户可以根据自己的需要使用不同的驱动，或者通过关闭某些插件来禁用特定功能。

插件还给开发者提供了扩展应用系统的方式，通过插件实现的钩子(Hook)，开发者可以在预先定义的系统扩展点，引入新逻辑。而利用这一机制对系统进行扩展，是完全间接地，不需要改变系统代码。而且，插件可以与应用系统分开开发和发布。

## 插件的三种模式

### 驱动 - 名字唯一，入口点唯一

动态加载函数库最常见的一种用法，就是加载驱动来和外部资源进行交互，屏蔽外部资源异构性，这里的外部资源，可以是数据库，文件系统，甚至是其他应用程序。最典型的例子，就是[SQLAlchemy](http://sqlalchemy.org/)。做为一个数据库封装层，SQLAlchemy提供了统一的数据库操作抽象，而底层利用插件，对不同数据库提供支持。

作为驱动的插件，特点是，尽管应用系统可能支持多种驱动，但在运行时，只有一个驱动会被加载运行。

### 钩子(Hook) - 名字唯一，多个入口点

钩子，信号，或者回调函数，说的其实是同一个事，即当应用系统触发某个事件，则调用对应的处理代码。OpenStack Nova在v3版本的[api](http://docs.openstack.org/developer/nova/devref/api_plugins.html)中，提供了4个与虚拟机资源操作有关的钩子：create, rebuild, update, resize. 当虚拟机创建是，会触发某个事件，比如create事件，这时，注册在create事件命名空间（在OpenStack中是`nova.api.v3.extensions.server.create`）的钩子代码就会被执行。

作为钩子的插件，特点是，同一个命名空间下，可以对应多个入口点，在运行时，当触发这个命名空间对应的事件时，会执行多个钩子代码。

### 扩展 - 多个名字，多个入口点

通过动态加载扩展，可以在运行时给应用增添新功能。因为扩展程序相较前两种插件提供的功能更复杂，因此，需要在加载时，由应用系统触发，执行一些初始化的安装配置。

作为扩展的插件，特点是，可以出现在多个命名空间下，同一个命名空间也可以对应多个入口点。

## stevedore插件

Doug Hellmann在设计Ceilometer时，认为需要提供一种完善的插件机制，所以他调研了很多实现了插件的软件和库，抽象出了一些典型插件场景，经过筛选和优化，构成了Ceilometer的插件框架。然后，他又将这一框架在此抽象提取，形成独立的库，就是stevedore。后来，Nova和Neutron等其他组件也引入了stevedore作为其插件框架。

stevedore在设计之初就力求简单，所以它并没有通过`__import__`或者`importlib`等方式提供一套全新的代码加载逻辑，而是选择了重用[pkg_resources](https://pythonhosted.org/setuptools/pkg_resources.html)的功能，因此，stevedore用非常少的代码，实现了OpenStack对于插件的大部分需求。

stevedore看起来好像是个人名，这个库，为什么叫这个名字呢？

> stevedore: |ˈstiːvədɔː| 中文翻译：码头工人 英文翻译：a person employed at a dock to load and unload ships.

## stevedore如何使用

使用stevedore给应用程序添加插件支持，非常简单。可以分为定义插件，声明插件，加载插件，执行接口四个步骤。我们通过一个例子来说明，这个例子的目的是实现一个格式化器，根据用户的命令行输入，指定要用的格式化方式，并输出结果。

### 定义插件

定义插件之前，要定义插件的接口，stevedore通过抽象基类（即abc，Abstract Base Class）来定义插件接口。

```python
# base.py
import abc

import six


@six.add_metaclass(abc.ABCMeta)
class FormatterBase(object):
    """Base class for example plugin used in the tutoral.
    """

    def __init__(self, max_width=60):
        self.max_width = max_width

    @abc.abstractmethod
    def format(self, data):
        """Format the data and return unicode text.

        :param data: A dictionary with string keys and simple types as
                     values.
        :type data: dict(str:?)
        :returns: Iterable producing the formatted text.
        """
```

这里我们定义了formatter插件的接口规范，即所有formatter接口，必须实现`format`方法。具体的插件实现，可以继承自FormatterBase。

```python
# simple.py
from example import base


class Simple(base.FormatterBase):
    """A very basic formatter.
    """

    def format(self, data):
        """Format the data and return unicode text.

        :param data: A dictionary with string keys and simple types as
                     values.
        :type data: dict(str:?)
        """
        for name, value in sorted(data.items()):
            line = '{name} = {value}'.format(
                name=name,
                value=value
            )
            yield line
```

不过，实现插件也可以不继承自基类，而只要实现了`format`接口即可，因为在stevedore调用插件时，并不检测插件是否继承自对应的基类，这就是duck-typing。从这一点来看，定义基类，其象征意义大于实际意义。

### 声明插件

stevedore利用了pkg_resources的entry_points功能，声明插件，就是在setup.py中添加一条entry_points记录。

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name='plugin_demo',
    version='1.0',

    description='Example for stevedore',

    packages=find_packages(),

    entry_points={
        'example.formatter': [
            'simple = example.simple:Simple',
            'field = example.fields:FieldList',
            'my_simple = my_plugin.my_simple:Simple',
        ],
    },

    requires=['stevedore']
)
```

其中`entry_points`部分就是在声明应用程序支持的插件，在这个例子中，插件的命名空间是`example.formmatter`，而对应的入口点有三个：

- 名字为`simple`的插件入口点是`example.simple:Simple`；
- 名字为`field`的插件入口点是`example.fields:FieldList`；
- 名字为`my_simple`的插件入口点是`my_plugin.my_simple:Simple`。

我们示例代码的目录结构是这样的：

```shell
$ tree plugin_demo
plugin_demo
├── example
│   ├── __init__.py
│   ├── __init__.pyc
│   ├── base.py
│   ├── base.pyc
│   ├── fields.py
│   ├── fields.pyc
│   ├── simple.py
│   └── simple.pyc
├── load_as_driver.py
├── load_as_driver.pyc
├── load_as_extension.py
└── setup.py

1 directory, 12 files
```

上面`entry_points`中的`simple`和`field`插件是我们的`plugin_demo`项目中`example`包提供的，而第三个`my_simple`插件，并不在当前的代码包中。这是因为，stevedore的插件，并不要求插件的实现与加载插件的应用程序一起打包发布，插件的代码可以独立发布，独立安装部署，这样就实现了代码的解耦。在运行时，stevedore会通过pkg_resources库在当前环境内查找需要的插件代码。

### 加载插件

加载插件的代码非常简单，以加载Driver为例。

```python
# load_as_driver.py
from __future__ import print_function

import argparse

from stevedore import driver


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'format',
        nargs='?',
        default='simple',
        help='the output format',
    )
    parser.add_argument(
        '--width',
        default=60,
        type=int,
        help='maximum output width for text',
    )
    parsed_args = parser.parse_args()

    data = {
        'a': 'A',
        'b': 'B',
        'long': 'word ' * 80,
    }

    mgr = driver.DriverManager(
        namespace='example.formatter',
        name=parsed_args.format,
        invoke_on_load=True,
        invoke_args=(parsed_args.width,),
    )
    for chunk in mgr.driver.format(data):
        print(chunk, end='')
```

上述代码的31到36行，就是加载插件的代码。实例化`stevedore.driver.DriverManager`的参数分别为：

- `namespace`: 插件的命名空间，在`setup.py`中，由`entry_points`字段声明；
- `name`: 插件的名字
- `invoke_on_load`: 是否在加载是调用
- `invoke_args`: 调用参数，在`invoke_on_load`为`True`时，这个参数会作为调用参数传给插件

假如我们通过命令`python load_as_driver.py simple --width 20`执行代码，当执行到加载插件这段代码时，stevedore会做这么几件事：

- `namespace`是`example.formatter`，于是从`entry_points`中找到`example.formatter`命名空间；
- `name`就是`simple`，在命名空间中找到名字为`simple`的插件，即`example.simple:Simple`；
- 因为`invoke_on_load`为`True`，所以在加载时要调用插件；
- 调用参数是命令行传入的参数`20`，所以stevedore会执行`Simple(20)`；
- 将结果存储在`mgr`中。

### 执行接口

在上面的代码段最后位置，第37行，是执行插件接口的代码，非常简单，`mgr.driver.format(data)`。

## OpenStack中的stevedore

再来看看OpenStack中是如何使用stevedore的。以Nova API v3中，实现虚拟机创建（create）的钩子为例。首先，在`setup.cfg`中定义`entry_points`（之所以是`setup.cfg`，不是`setup.py`，是因为OpenStack使用了[pbr](http://docs.openstack.org/developer/pbr/)）。

```config
#setup.cfg
...
nova.api.v3.extensions.server.create =
    access_ips = nova.api.openstack.compute.plugins.v3.access_ips:AccessIPs
    availability_zone = nova.api.openstack.compute.plugins.v3.availability_zone:AvailabilityZone
    block_device_mapping = nova.api.openstack.compute.plugins.v3.block_device_mapping:BlockDeviceMapping
    block_device_mapping_v1 = nova.api.openstack.compute.plugins.v3.block_device_mapping_v1:BlockDeviceMappingV1
    config_drive = nova.api.openstack.compute.plugins.v3.config_drive:ConfigDrive
    disk_config = nova.api.openstack.compute.plugins.v3.disk_config:DiskConfig
    keypairs_create = nova.api.openstack.compute.plugins.v3.keypairs:Keypairs
    multiple_create = nova.api.openstack.compute.plugins.v3.multiple_create:MultipleCreate
    personality = nova.api.openstack.compute.plugins.v3.personality:Personality
    scheduler_hints = nova.api.openstack.compute.plugins.v3.scheduler_hints:SchedulerHints
    security_groups = nova.api.openstack.compute.plugins.v3.security_groups:SecurityGroups
    user_data = nova.api.openstack.compute.plugins.v3.user_data:UserData
...
```

这些所有插件，都实现了同一个基类。

```python
# nova/nova/api/openstack/extensions.py
@six.add_metaclass(abc.ABCMeta)
class V3APIExtensionBase(object):
    """Abstract base class for all V3 API extensions.

    All V3 API extensions must derive from this class and implement
    the abstract methods get_resources and get_controller_extensions
    even if they just return an empty list. The extensions must also
    define the abstract properties.
    """

    def __init__(self, extension_info):
        self.extension_info = extension_info

    @abc.abstractmethod
    def get_resources(self):
        """Return a list of resources extensions.

        The extensions should return a list of ResourceExtension
        objects. This list may be empty.
        """
        pass

    @abc.abstractmethod
    def get_controller_extensions(self):
        """Return a list of controller extensions.

        The extensions should return a list of ControllerExtension
        objects. This list may be empty.
        """
        pass

    @abc.abstractproperty
    def name(self):
        """Name of the extension."""
        pass

    @abc.abstractproperty
    def alias(self):
        """Alias for the extension."""
        pass

    @abc.abstractproperty
    def version(self):
        """Version of the extension."""
        pass

    def __repr__(self):
        return "<Extension: name=%s, alias=%s, version=%s>" % (
            self.name, self.alias, self.version)

    def is_valid(self):
        """Validate required fields for extensions.

        Raises an attribute error if the attr is not defined
        """
        for attr in ('name', 'alias', 'version'):
            if getattr(self, attr) is None:
                raise AttributeError("%s is None, needs to be defined" % attr)
        return True
```

因为是作为API调用的钩子，所以在API Controller初始化时加载插件。

```python
# nova/nova/api/openstack/compute/plugins/v3/servers.py
class ServersController(wsgi.Controller):

    # ...
    # skip some code
    # ...

    EXTENSION_CREATE_NAMESPACE = 'nova.api.v3.extensions.server.create'

    # ...
    # skip some code
    # ...

    def __init__(self, **kwargs):
        def _check_load_extension(required_function):

            def check_whiteblack_lists(ext):
                # Check whitelist is either empty or if not then the extension
                # is in the whitelist
                if (not CONF.osapi_v3.extensions_whitelist or
                        ext.obj.alias in CONF.osapi_v3.extensions_whitelist):

                    # Check the extension is not in the blacklist
                    if ext.obj.alias not in CONF.osapi_v3.extensions_blacklist:
                        return True
                    else:
                        LOG.warning(_LW("Not loading %s because it is "
                                        "in the blacklist"), ext.obj.alias)
                        return False
                else:
                    LOG.warning(
                        _LW("Not loading %s because it is not in the "
                            "whitelist"), ext.obj.alias)
                    return False

            def check_load_extension(ext):
                if isinstance(ext.obj, extensions.V3APIExtensionBase):
                    # Filter out for the existence of the required
                    # function here rather than on every request. We
                    # don't have a new abstract base class to reduce
                    # duplication in the extensions as they may want
                    # to implement multiple server (and other) entry
                    # points if hasattr(ext.obj, 'server_create'):
                    if hasattr(ext.obj, required_function):
                        LOG.debug('extension %(ext_alias)s detected by '
                                  'servers extension for function %(func)s',
                                  {'ext_alias': ext.obj.alias,
                                   'func': required_function})
                        return check_whiteblack_lists(ext)
                    else:
                        LOG.debug(
                            'extension %(ext_alias)s is missing %(func)s',
                            {'ext_alias': ext.obj.alias,
                            'func': required_function})
                        return False
                else:
                    return False
            return check_load_extension

        # ...
        # skip some code
        # ...

        # Look for implementation of extension point of server creation
        self.create_extension_manager = \
          stevedore.enabled.EnabledExtensionManager(
              namespace=self.EXTENSION_CREATE_NAMESPACE,
              check_func=_check_load_extension('server_create'),
              invoke_on_load=True,
              invoke_kwds={"extension_info": self.extension_info},
              propagate_map_exceptions=True)
        if not list(self.create_extension_manager):
            LOG.debug("Did not find any server create extensions")

        # ...
        # skip some code
        # ...
```

在执行虚拟机创建时，执行钩子指向的处理代码。需要注意的是，这里使用的是stevedore提供的EnabledExtension，和前面示例代码有几个不同点：

- 初始化参数里没有`name`参数，这是因为这里是采用钩子模式，也就是同时加载多个入口点，在事件触发时，执行多个处理代码；
- 既然这个插件叫做EnabledExtension，顾名思义，它应该提供了如何**enable**一个插件，而这个逻辑是通过参数`check_func`来提供，也就是`_check_load_extension('server_create')`，`_check_load_extension`通过`nova.conf`中配置的插件白名单，以及用户打开的插件列表，来过滤插件。

```python
# nova/nova/api/openstack/compute/plugins/v3/servers.py
class ServersController(wsgi.Controller):

    # ...
    # skip some code
    # ...

    def _create_extension_point(self, ext, server_dict,
                                create_kwargs, req_body):
        handler = ext.obj
        LOG.debug("Running _create_extension_point for %s", ext.obj)

        handler.server_create(server_dict, create_kwargs, req_body)

    # ...
    # skip some code
    # ...

    def create(self, req, body):

        # ...
        # skip some code
        # ...

        if list(self.create_extension_manager):
            self.create_extension_manager.map(self._create_extension_point,
                                              server_dict, create_kwargs, body)

        # ...
        # skip some code
        # ...
`
```

stevedore的Extension执行时，不像Driver那样直接调用接口，而是通过一个`map`方法来调用，其作用是遍历所有插件，对每一个插件，以相同的执行参数，执行`map`方法第一个参数引用的函数，这里就是`self._create_extension_point`。

## 引用

1. Doug Hellmann的论文 - http://docs.openstack.org/developer/stevedore/essays/pycon2013.html
2. stevedore的官方文档 - http://docs.openstack.org/developer/stevedore/index.html