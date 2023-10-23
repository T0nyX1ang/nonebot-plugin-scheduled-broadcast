# <center> Nonebot Plugin Scheduled Broadcast </center>

<center> ✨ 一款可配置的, 不依赖具体适配器的, 基于事件的定时广播插件. ✨ </center>

## 特性

* 基于一般事件 `nonebot.adapters.Event` 构造, 从而支持全部协议的信息发送
* 定时广播由文件配置, 基于 `apscheduler` 提供类 `crontab` 的配置参数

## 安装

### 使用 `nb-cli` 安装

* 在 `nonebot2` 项目的根目录下打开命令行, 输入以下指令即可安装:

```bash
    nb-cli plugin install nonebot-plugin-scheduled-broadcast
```

### 使用包管理器安装

* 使用 `pdm` 安装:

```bash
    pdm add nonebot-plugin-scheduled-broadcast
```

* 使用 `poetry` 安装:

```bash
    poetry add nonebot-plugin-scheduled-broadcast
```

* 使用 `pip` 安装: ~~(虽然不太推荐但大概率没事)~~

```bash
    pip install nonebot-plugin-scheduled-broadcast
```

## 使用

### 启动广播

* 保证发送消息的 `id` 位于 `SUPERUSER` 用户组中
* 在需要启动广播的地方发送:

```txt
    启动广播/enablebc
```

* 如果没有问题的话, 机器人会发送一条包含 `广播ID` 的消息, 该消息为 `pickle.dumps(event)` 的 `sha256` 哈希结果
* 如果没有问题的话, 机器人在发送 `广播ID` 时, 同时会在 `nonebot2` 项目的根目录下生成一个名为 `broadcast_policy.json` 的配置文件

### 配置文件的填写

* 一般而言, 配置文件的结构如下

```json
{
    "self_id": {
        "broadcast_id": {
            "config": {
                "example": {"second": "*/30"}
            },
            "edata": "base64 data"
        },
        "another broadcast_id": {
            // ...
        }
    },
    "another self_id": {
        // ...
    }
}
```

* 只要改 `config` 键下的配置即可, 改其它地方可能会导致哈希校验不通过. `config` 的可用配置与 `apscheduler` 一致, 以下给出一个示例, 该示例表示, `example` 命令会在每天 `20:48`, 每隔 `10` 秒被触发:

```json
{
    "config": {
        "example": {
            "hour": 20,
            "minute": 48,
            "second": "*/10"
        }
    }
}
```

* 在准备好了配置文件后, 就可以准备编写待触发的指令了.

### 待触发指令的编写

* 由于本插件提供了一个装饰器, 可以按照如下方式编写待触发指令:

```python
from nonebot import require
from nonebot.adapters import Event
from nonebot.log import logger

require("nonebot_plugin_scheduled_broadcast")

from nonebot_plugin_scheduled_broadcast.core import broadcast

@broadcast('example')
async def _(self_id: str, event: Event):
    """Scheduled example broadcast."""
    message = generate_your_message()
    try:
        bot = nonebot.get_bots()[bot_id]  # select the target bot
        await bot.send(event=event, message=message)  # send message
    except Exception:
        logger.error(traceback.format_exc())  # print logs
```

* 触发指令编写完成以后, 重新启动机器人即可.

### 停止广播

* 保证发送消息的 `id` 位于 `SUPERUSER` 用户组中
* 在需要停止广播的地方发送:

```txt
    停止广播/disablebc 广播ID
```

* 停止广播之后, 对应 `广播ID` 的键将被**删除**, 这意味着需要重新配置所有信息

## 配置

* `broadcast_policy_location`: 代表配置文件的存放位置, 默认值为 `./broadcast_policy.json`

## 注意事项

* 由于每一个 `Event` 几乎不会相同, 请不要在一个地方同时启动多次广播, 会刷屏的
* 由于用到了 `pickle` 的序列化和反序列化功能, 而该功能具有潜在的安全风险, **请谨慎对待来源不明的配置文件**. 如果不确定配置文件的安全性, 建议重新生成 `广播ID`, 只使用配置文件中的 `config` 键里面的内容.

## 协议

* 本项目使用 [MIT](./LICENSE) 协议
