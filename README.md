# steam_HoshinoBot
froked from [pcrbot/steam](https://github.com/SlightDust/steam.git)  
~~原项目四年不更新了，fork一份来缝一下~~

### 安装方法

- 1.在module目录下执行 `git clone https://github.com/SlightDust/steam_HoshinoBot.git`

- 2.在`__bot__.py`的`module`中添加`steam_HoshinoBot`

- 3.修改`steam.json`中的key为你的steam api key

### 使用方法
自备`simhei.ttf`和`tahoma.ttf`两个字体文件，放在插件目录即可。  
前者在`C:\Windows\Fonts\`，后者可以从L4D2的目录里拿`Left 4 Dead 2\platform\vgui\fonts\`。  
初次启动前，复制steam.json.example为steam.json，填入api key。或在初次启动后，在生成的steam.json中填入api key后重启bot。  

|指令|说明|指令示例|
|----|----|----|
| 添加steam订阅 steamid或自定义url | 订阅一个账号的游戏状态 | 添加steam订阅 114514 |
| 取消steam订阅 steamid或自定义url | 取消订阅 | 取消steam订阅 114514 |
| steam订阅列表 | 查询本群所有订阅账号的游戏状态 | steam订阅列表 |
| 谁在玩游戏 | 同上 | 谁在玩游戏 |
| 查询steam账号 | 查询指定steam账号的游戏状态 | 查询steam账号 114514 |

### steam api key创建方法
steam客户端 - 帮助 - Steam客服 - 我的账户 - 您Steam账户的相关数据 - 开发者设置

### 效果
![](https://s2.loli.net/2024/03/24/WwR3FZuABXoSMTj.png)

### todo
- [x] 重启之后第一次查询会报错。遗留问题，之后改
- [ ] 图片里名字这行没找到合适的字体