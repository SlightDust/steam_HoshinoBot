# steam_HoshinoBot

Forked from [pcrbot/steam](https://github.com/SlightDust/steam.git)  
~~原项目四年不更新了，fork一份来缝一下~~

### 安装方法

#### 第一次部署

1. 在module目录下执行 `git clone https://github.com/SlightDust/steam_HoshinoBot.git`

2. 在`__bot__.py`的`module`中添加`steam_HoshinoBot`

3. 初次启动前，复制`steam.json.example`为`steam.json`，填入api key。或在初次启动后，在生成的steam.json中填入api
   key，然后在群聊内发送`@bot 重载steam订阅配置`。

#### 从旧版移植

1. 将旧版`steam.py`重命名为`steam.py.temp`, 将旧版`steam.json`复制一份为`steam.old.json`进行备份, 将本仓库的`steam.py`放到该目录下

> [!TIP]
> 如果你持有的json文件是和[旧版](https://github.com/SlightDust/steam)
> 以及[pcrbot/steam](https://github.com/SlightDust/steam)自动生成的json格式相同, 则新版代码可以自动兼容旧版json

2. 将`res`文件夹与`MiSans-Regular.ttf`字体文件放到与`steam.py`同目录下

### 使用方法

| 指令                       | 说明               | 指令示例             |
|--------------------------|------------------|------------------|
| 添加steam订阅 steamid或自定义url | 订阅一个账号的游戏状态      | 添加steam订阅 114514 |
| 取消steam订阅 steamid或自定义url | 取消订阅             | 取消steam订阅 114514 |
| steam订阅列表                | 查询本群所有订阅账号的游戏状态  | steam订阅列表        |
| 谁在玩游戏                    | 同上               | 谁在玩游戏            |
| 查询steam账号                | 查询指定steam账号的游戏状态 | 查询steam账号 114514 |
| @bot 重载steam订阅配置         | 重载配置             | -                |

### steam api key创建方法

Steam API Key 是由 Valve 提供的一个专门的 API 密钥，允许开发者访问特定的 Steamworks API 功能。这个密钥用来识别请求者的身份，并允许进行对 Steam 平台数据的程序化查询，例如玩家的游戏库、朋友列表、游戏成就等信息

> [!WARNING]  
> **安全警告**: 请不要将你的 Steam API Key 上传到公共代码仓库。泄露 API 密钥会导致你的账户遭到盗用以及**严重经济损失**。
> 见[Steam API 密钥劫持](https://zhuanlan.zhihu.com/p/624601556)

steam客户端 - 帮助 - Steam客服 - 我的账户 - 您Steam账户的相关数据 - 开发者设置

### 配置文件结构

```json5
{
  // 你的steam api key, 注意不要将此密钥上传到公共仓库, 以免造成经济损失!!!!
  "key": "填写你的Steam API Key",
  // 本地化语言, 默认为简体中文
  "language": "schinese",
  // 订阅列表, 此字段无需手动填写, 可以通过群内命令添加订阅
  "subscribes": {
    // steamid
    "765611989294*****": [
      // 群号
      100000000
    ]
  },
  // 是否将订阅的steam游戏状态合并发送, 避免刷屏
  "combined_mode": true,
  // 代理设置
  "proxies": null,
  // 向steamapi发起请求的间隔, 单位为分钟, 默认2分钟, 请勿过快请求
  "request_interval": 2
}
```

### 效果

![](https://s2.loli.net/2024/05/04/BjdAOsp92F3emal.jpg)

![](https://s2.loli.net/2024/05/05/keulIEoxNM1Ggj6.png)

![](https://s2.loli.net/2024/05/05/FIs65cthVj3fpMK.png)

### todo

- [x] 重启之后第一次查询会报错。遗留问题，之后改
- [x] 图片里名字这行没找到合适的字体。 开摆，[MiSans](https://hyperos.mi.com/font/zh/)看着也舒服。