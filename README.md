# steam_HoshinoBot
Forked from [pcrbot/steam](https://github.com/SlightDust/steam.git)  
~~原项目四年不更新了，fork一份来缝一下~~

### 安装方法

1. 在module目录下执行 `git clone https://github.com/SlightDust/steam_HoshinoBot.git`

2. 在`__bot__.py`的`module`中添加`steam_HoshinoBot`

3. 初次启动前，复制`steam.json.example`为`steam.json`，填入api key。或在初次启动后，在生成的steam.json中填入api key，然后在群聊内发送`@bot 重载steam订阅配置`。  

### 使用方法

|指令|说明|指令示例|
|----|----|----|
| 添加steam订阅 steamid或自定义url | 订阅一个账号的游戏状态 | 添加steam订阅 114514 |
| 取消steam订阅 steamid或自定义url | 取消订阅 | 取消steam订阅 114514 |
| steam订阅列表 | 查询本群所有订阅账号的游戏状态 | steam订阅列表 |
| 谁在玩游戏 | 同上 | 谁在玩游戏 |
| 查询steam账号 | 查询指定steam账号的游戏状态 | 查询steam账号 114514 |
| @bot 重载steam订阅配置 | 重载配置 | - |

### steam api key创建方法
steam客户端 - 帮助 - Steam客服 - 我的账户 - 您Steam账户的相关数据 - 开发者设置

### 效果
![](https://s2.loli.net/2024/05/04/BjdAOsp92F3emal.jpg)  

![](https://private-user-images.githubusercontent.com/66729711/327839450-1c70f4ac-0d36-4a2c-ad67-0eb9014a40b7.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTQ4MjAwMDMsIm5iZiI6MTcxNDgxOTcwMywicGF0aCI6Ii82NjcyOTcxMS8zMjc4Mzk0NTAtMWM3MGY0YWMtMGQzNi00YTJjLWFkNjctMGViOTAxNGE0MGI3LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA1MDQlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNTA0VDEwNDgyM1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTVlMjE4ZTEyN2YwOGZjMmFjMzU1MGE4YjQ1ZjkwMzdlYWZiMTg3NzhlMTk0YTE1OWRmMzBiYjUwODJlNjVkZjkmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.tZjtb28B1Q1tK-q-nJ6fLm0oUsQKzvhmJDTxYCnp2lM)  

![](https://private-user-images.githubusercontent.com/66729711/327839482-8308e157-431a-45d4-8a82-45fa642b83b9.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTQ4MjAwMDMsIm5iZiI6MTcxNDgxOTcwMywicGF0aCI6Ii82NjcyOTcxMS8zMjc4Mzk0ODItODMwOGUxNTctNDMxYS00NWQ0LThhODItNDVmYTY0MmI4M2I5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA1MDQlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNTA0VDEwNDgyM1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWNmNmU1OTI5NmU5Y2VjZWQ0MDkzMDg5NzVmMjk4NmZiZGYyZWRiZDM4NjhlZDc1NGZiYTJiNTNkNGY4MjVhZWEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.Im8ehAhul9CWE28U0ADop3nAI0nSo8aOhpnU0Yqx8Ow)

### todo
- [x] 重启之后第一次查询会报错。遗留问题，之后改
- [x] 图片里名字这行没找到合适的字体。 开摆，[MiSans](https://hyperos.mi.com/font/zh/)看着也舒服。