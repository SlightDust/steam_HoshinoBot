import json
import os
from enum import Enum

from lxml import etree
from asyncio import sleep
from datetime import datetime

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from nonebot import MessageSegment
from collections import defaultdict
from hoshino import service, aiorequests, get_self_ids, get_bot
from hoshino.util import pic2b64

help_ = """
[添加steam订阅 steamid或自定义url] 订阅一个账号的游戏状态
[取消steam订阅 steamid或自定义url] 取消订阅
[steam订阅列表] 查询本群所有订阅账号的游戏状态
[谁在玩游戏] 看看谁在玩游戏
[查询steam账号] 查询指定steam账号的游戏状态
"""

sv = service.Service("steam", enable_on_default=True, help_=help_)

current_folder = os.path.dirname(__file__)
config_file = os.path.join(current_folder, 'steam.json')

# 初次启动时创建缺省配置文件
if not os.path.exists(config_file):
    with open(config_file, mode="w") as f:
        f.write(json.dumps({
            "key": "your-steam-key-here",
            "language": "schinese",
            "subscribes": {},
            "combined_mode": True,
            "proxies": None
        }, indent=4))
    sv.logger.error("Steam推送初始化成功, 请编辑steam.json配置文件！")

# 加载配置文件
with open(config_file, mode="r") as f:
    f = f.read()
    cfg = json.loads(f)
    # 兼容旧版本配置文件
    if "language" not in cfg:
        cfg["language"] = "schinese"
    if "combined_mode" not in cfg:
        cfg["combined_mode"] = True
    if "proxies" not in cfg:
        cfg["proxies"] = None
    combined_mode = cfg["combined_mode"]
    proxies = cfg["proxies"]
    # 保存更新后的配置文件
    with open(config_file, mode="w") as f:
        f.write(json.dumps(cfg, indent=4))

playing_state = {}

# load image from res
busy_img = Image.open(os.path.join(current_folder, 'res', "busy.png"))
zzz_gaming_img = Image.open(os.path.join(current_folder, 'res', "zzz_gaming.png"))
zzz_online_img = Image.open(os.path.join(current_folder, 'res', "zzz_online.png"))


class SteamStatus(Enum):
    """
    Steam在线状态
    """
    OFFLINE = 0
    ONLINE = 1
    BUSY = 2
    AWAY = 3
    SNOOZE = 4
    LOOKING_TO_TRADE = 5
    LOOKING_TO_PLAY = 6


async def format_id(steam_id: str) -> str:
    """
    获取steam64位id
    """
    if steam_id.startswith('76561') and len(steam_id) == 17:
        return steam_id
    else:
        resp = await aiorequests.get(f'https://steamcommunity.com/id/{steam_id}?xml=1', proxies=proxies)
        xml = etree.XML(await resp.content)
        return xml.xpath('/profile/steamID64')[0].text


async def fetch_avatar(url):
    """use aiorequests to fetch avatar"""
    resp = await aiorequests.get(url, proxies=proxies)
    data_stream = BytesIO(await resp.content)
    return Image.open(data_stream)


async def make_img(data):
    """
    生成steam用户游戏状态图片
    """
    player_name = data["personaname"]  # 昵称
    mid = "is now playing"
    game_name = data["localized_game_name"] if data["localized_game_name"] != "" else data["gameextrainfo"]
    avatar_url = data["avatarmedium"]

    text_size = 16
    spacing = 20
    font_path = os.path.join(os.path.dirname(__file__), 'MiSans-Regular.ttf')
    font = ImageFont.truetype(font_path, size=text_size)
    avatar = await fetch_avatar(avatar_url)
    w = int(280 * 1.6)
    h = 86
    img = Image.new("RGB", (w, h), (33, 33, 33))
    draw = ImageDraw.Draw(img)
    avatar = avatar.resize((60, 60))
    green_line = Image.new("RGB", (3, 60), (89, 191, 64))
    img.paste(avatar, (13, 10))
    img.paste(green_line, (74, 10))
    draw.text((90, 10), player_name, fill=(193, 217, 167), font=font)
    draw.text((90, 10 + spacing - 2), mid, fill=(115, 115, 115), font=font)
    draw.text((90, 10 + spacing * 2), game_name, fill=(135, 181, 82), font=font)
    return img


def calculate_last_login_time(last_logoff: int) -> str:
    """
    计算steam距离最后一次登录距离现在时间过去了多次时间,
    如果超过一年则显示年份，
    如果达到月则显示月份，
    如果达到天则显示天数和小时，
    如果是小时则显示小时,
    否则显示分钟
    :param last_logoff: 最后一次登录时间
    :return: 距离最后一次登录时间过去了多久
    """
    current_time = datetime.now().timestamp()
    time_diff = current_time - last_logoff
    if time_diff > 365 * 24 * 60 * 60:
        return f"{int(time_diff / (365 * 24 * 60 * 60))}年"
    elif time_diff > 30 * 24 * 60 * 60:
        return f"{int(time_diff / (30 * 24 * 60 * 60))}月"
    elif time_diff > 24 * 60 * 60:
        return f"{int(time_diff / (24 * 60 * 60))}天{int((time_diff % (24 * 60 * 60)) / 3600)}小时"
    elif time_diff > 60 * 60:
        return f"{int(time_diff / (60 * 60))}小时"
    else:
        return f"{int(time_diff / 60)}分钟"


def draw_user_info(draw, x, y,
                   player_name,
                   info,
                   font,
                   font_small,
                   text_color,
                   line_color,
                   padding_top, padding_left,
                   background):
    """
    绘制用户信息
    """
    # 用户名
    draw.text((x + padding_left + 48 + 5, y + padding_top), player_name, fill=text_color,
              font=font)
    # 线
    background.paste(line_color, (x + 48 + 1, y))
    draw.text((x + padding_left + 48 + 5, y + padding_top + 23), info,
              fill=text_color,
              font=font_small)


def draw_additional_state_info(state_img, x, y, player_name_size, padding_top, background):
    """
    绘制额外信息的图标如忙碌状态、离开状态等
    """
    background.paste(state_img, (x + 48 + 5 + player_name_size + 10, y + padding_top + 5))
    return y + 20


async def generate_subscribe_list_image(group_playing_state: dict) -> Image:
    """
    生成订阅列表的图片
    """
    text_size_normal = 17
    text_size_small = 11
    spacing = 10
    border_size = 10
    green = (144, 186, 60)
    dark_green = (98, 129, 59)
    blue = (87, 203, 222)
    dark_blue = (69, 117, 139)
    gray = (137, 137, 137)
    font_path = os.path.join(os.path.dirname(__file__), 'MiSans-Regular.ttf')
    font = ImageFont.truetype(font_path, size=text_size_normal)
    font_small = ImageFont.truetype(font_path, size=text_size_small)
    green_line = Image.new("RGB", (3, 48), green)
    dark_green_line = Image.new("RGB", (3, 48), dark_green)
    blue_line = Image.new("RGB", (3, 48), blue)
    gray_line = Image.new("RGB", (3, 48), gray)
    dark_blue_line = Image.new("RGB", (3, 48), dark_blue)
    status_num = len(group_playing_state)
    x = 0
    y = 0
    w = 290
    h = 48 * status_num + spacing * (status_num - 1)
    background = Image.new("RGB", (w, h), (33, 33, 33))
    draw = ImageDraw.Draw(background)

    def _sorting_key(player_status):
        _game_name = player_status["gameextrainfo"]
        _is_playing = bool(_game_name)
        _is_online = player_status.get("personastate").value
        _last_logoff = player_status.get("lastlogoff")
        if _is_playing:
            return 0, _game_name, _is_online  # 在游戏中优先级最高，其次按照游戏名称排序, 之后按照在线状态排序
        elif _is_online:
            return 1, "", _is_online  # 在线但不在游戏中, 按照在线状态排序
        elif _last_logoff is not None:
            # 不在线，按照 last_logoff 倒序排序
            return 2, -_last_logoff
        else:
            return 3, 0  # 不在线，且没有 last_logoff 信息

    # 按照在线状态排序
    for steam_id, status in sorted(group_playing_state.items(), key=lambda state: _sorting_key(state[1])):
        player_name: str = status["personaname"]
        game_info: str = status["localized_game_name"] \
            if status["localized_game_name"] != "" \
            else status["gameextrainfo"]
        avatar_url = status["avatarmedium"]

        player_state: SteamStatus = status["personastate"]
        is_playing: bool = game_info != ""

        player_name_size = int(font.getlength(player_name))

        avatar = await fetch_avatar(avatar_url)
        avatar = avatar.resize((48, 48))
        background.paste(avatar, (x, y))
        padding_top = 8  # 用于调整右侧文字区域的padding top
        padding_left = 5  # 用于调整右侧文字区域的padding left
        if player_state == SteamStatus.BUSY:
            # todo 忙碌状态, 但是目前还没找到设置这个状态的方法, 好像steam客户端的请勿打扰只是在客户端关闭消息提醒
            draw_additional_state_info(busy_img, x, y, player_name_size, padding_top, background)
        if is_playing and player_state in [SteamStatus.SNOOZE, SteamStatus.AWAY]:
            draw_user_info(draw, x, y, player_name, game_info, font, font_small,
                           dark_green, dark_green_line, padding_top,
                           padding_left, background)
            draw_additional_state_info(zzz_gaming_img, x, y, player_name_size, padding_top, background)
        elif is_playing:
            draw_user_info(draw, x, y, player_name, game_info, font, font_small,
                           green, green_line, padding_top,
                           padding_left, background)
        elif player_state in [SteamStatus.SNOOZE, SteamStatus.AWAY]:
            draw_user_info(draw, x, y, player_name, "离开", font, font_small,
                           dark_blue, dark_blue_line, padding_top,
                           padding_left, background)
            draw_additional_state_info(zzz_online_img, x, y, player_name_size, padding_top, background)
        elif player_state in [SteamStatus.ONLINE, SteamStatus.LOOKING_TO_PLAY, SteamStatus.LOOKING_TO_TRADE]:
            draw_user_info(draw, x, y, player_name, "在线", font, font_small,
                           blue, blue_line, padding_top,
                           padding_left, background)
        else:  # offline
            # 显示离线时间
            if status["lastlogoff"]:  # 是apikey所属账号的好友，可以获取上次在线时间
                last_logoff = f'上次在线{calculate_last_login_time(status["lastlogoff"])}前'
            else:  # 非好友
                last_logoff = "离线"
            draw_user_info(draw, x, y, player_name, last_logoff, font, font_small,
                           gray, gray_line, padding_top,
                           padding_left, background)
        y += 48 + spacing
    # 给最终结果创建一个环绕四周的边框, 颜色和背景色一致
    result_with_border = Image.new("RGB", (w + border_size * 2, h + border_size * 2), (33, 33, 33))
    result_with_border.paste(background, (border_size, border_size))
    return result_with_border


async def get_localized_game_name(steam_appid: str, game_name: str) -> str:
    """
    根据steam游戏id获取指定语言的游戏名，通过steamapi
    :param steam_appid: steam游戏id
    :param game_name: 英文游戏名
    :return: 指定语言的游戏名
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    # 首次调用，检查本地缓存文件
    if not os.path.exists(os.path.join(current_folder, 'localized_game_name.json')):
        with open(os.path.join(current_folder, 'localized_game_name.json'), mode="w") as f:
            f.write(json.dumps({"000000": {"language_name": "localized_game_name"}}, indent=4, ensure_ascii=False))
    # 先尝试从本地缓存中找指定语言的游戏名：
    with open(os.path.join(current_folder, 'localized_game_name.json'), mode="r") as f:
        localized_game_name_dict = json.loads(f.read())
        if str(steam_appid) in localized_game_name_dict and \
                cfg["language"] in localized_game_name_dict[str(steam_appid)]:
            return localized_game_name_dict[str(steam_appid)][cfg["language"]]
    # 本地缓存里没有
    # 通过steamapi查询
    url = f'https://store.steampowered.com/api/appdetails?appids={steam_appid}&l={cfg["language"]}'
    try:
        resp = await aiorequests.get(url, headers=headers, timeout=5, proxies=proxies)
        data = await resp.json()
        # print(data)
        if data[str(steam_appid)]["success"]:
            localized_game_name = data[str(steam_appid)]["data"]["name"]
            # 只有成功才写入本地缓存
            with open(os.path.join(current_folder, 'localized_game_name.json'), mode="r") as f:
                localized_game_name_dict = json.loads(f.read())
            if steam_appid in localized_game_name_dict:  # appid已存在，更新对应语言的翻译
                localized_game_name_dict[str(steam_appid)][cfg["language"]] = localized_game_name
            else:  # appid不存在，新增
                localized_game_name_dict[str(steam_appid)] = {cfg["language"]: localized_game_name}
            with open(os.path.join(current_folder, 'localized_game_name.json'), mode="w") as f:
                f.write(json.dumps(localized_game_name_dict, indent=4, ensure_ascii=False))
            return localized_game_name
        else:
            return ""
    except Exception as e:
        sv.logger.error(f"获取游戏名失败: {e}")
        return ""


async def get_account_status(steam_id) -> dict:
    steam_id = await format_id(steam_id)
    params = {
        "key": cfg["key"],
        "format": "json",
        "steamids": steam_id
    }
    resp = await aiorequests.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/", params=params,
                                 proxies=proxies)
    rsp = await resp.json()
    friend = rsp["response"]["players"][0]
    return {
        "personaname": friend["personaname"] if "personaname" in friend else "",
        "gameextrainfo": friend["gameextrainfo"] if "gameextrainfo" in friend else "",
        "localized_game_name": (
            await get_localized_game_name(friend["gameid"], friend["gameextrainfo"])) if "gameid" in friend else ""
    }


async def update_game_status():
    params = {
        "key": cfg["key"],
        "format": "json",
        "steamids": ",".join(cfg["subscribes"].keys())
    }
    resp = await aiorequests.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/", params=params,
                                 proxies=proxies)
    rsp = await resp.json()
    for player in rsp["response"]["players"]:
        playing_state[player["steamid"]] = {
            "personaname": player["personaname"],
            "personastate": SteamStatus(player["personastate"]),
            "gameextrainfo": player["gameextrainfo"] if "gameextrainfo" in player else "",
            "avatarmedium": player["avatarmedium"],
            "gameid": player["gameid"] if "gameid" in player else "",
            "lastlogoff": player["lastlogoff"] if "lastlogoff" in player else None,
            # 非steam好友，没有lastlogoff字段，置为None供generate_subscribe_list_image判断
            "localized_game_name": (
                await get_localized_game_name(player["gameid"], player["gameextrainfo"])) if "gameid" in player else ""
            # 本体游戏名
        }


async def update_steam_ids(steam_id, group):
    steam_id = await format_id(steam_id)
    if steam_id not in cfg["subscribes"]:
        cfg["subscribes"][str(steam_id)] = []
    if group not in cfg["subscribes"][str(steam_id)]:
        cfg["subscribes"][str(steam_id)].append(group)
    with open(config_file, mode="w") as fil:
        json.dump(cfg, fil, indent=4, ensure_ascii=False)
    await update_game_status()


async def del_steam_ids(steam_id, group):
    steam_id = await format_id(steam_id)
    if group in cfg["subscribes"][str(steam_id)]:
        cfg["subscribes"][str(steam_id)].remove(group)
    with open(config_file, mode="w") as fil:
        json.dump(cfg, fil, indent=4, ensure_ascii=False)
    await update_game_status()


@sv.on_prefix("添加steam订阅")
async def add_steam_sub(bot, ev):
    account = str(ev.message).strip()
    try:
        await update_steam_ids(account, ev["group_id"])
        rsp = await get_account_status(account)
        if rsp["personaname"] == "":
            await bot.send(ev, "添加订阅失败！")
        elif rsp["gameextrainfo"] == "":
            await bot.send(ev, f"%s 没在玩游戏！" % rsp["personaname"])
        else:
            await bot.send(ev, f"%s 正在玩 %s ！" % (rsp["personaname"],
                                                    rsp["localized_game_name"] if rsp["localized_game_name"] != "" else
                                                    rsp["gameextrainfo"]))
        await bot.send(ev, "订阅成功")
    except Exception as e:
        sv.logger.error(f"添加Steam订阅失败: {e}")
        await bot.send(ev, "订阅失败")


@sv.on_prefix("取消steam订阅")
async def remove_steam_sub(bot, ev):
    account = str(ev.message).strip()
    try:
        await del_steam_ids(account, ev["group_id"])
        await bot.send(ev, "取消订阅成功")
    except Exception as e:
        sv.logger.error(f"取消Steam订阅失败: {e}")
        await bot.send(ev, "取消订阅失败")


@sv.on_fullmatch(("steam订阅列表", "谁在玩游戏"))
async def steam_sub_list(bot, ev):
    group_id = ev["group_id"]
    group_state_dict = {}
    await update_game_status()
    for key, val in playing_state.items():
        if group_id in cfg["subscribes"][str(key)]:
            group_state_dict[key] = val
    if len(group_state_dict) == 0:
        await bot.send(ev, "没有订阅的steam账号！")
        return
    img = await generate_subscribe_list_image(group_state_dict)
    msg = MessageSegment.image(pic2b64(img))
    await bot.send(ev, msg)


@sv.on_prefix("查询steam账号")
async def search_steam_account(bot, ev):
    account = str(ev.message).strip()
    rsp = await get_account_status(account)
    if rsp["personaname"] == "":
        await bot.send(ev, "查询失败！")
    elif rsp["gameextrainfo"] == "":
        await bot.send(ev, f"%s 没在玩游戏！" % rsp["personaname"])
    else:
        await bot.send(ev, f"%s 正在玩 %s ！" % (
            rsp["personaname"],
            rsp["localized_game_name"] if rsp["localized_game_name"] != "" else rsp["gameextrainfo"]))


@sv.on_fullmatch("重载steam订阅配置", only_to_me=True)
async def reload_config(bot, ev):
    global cfg
    with open(config_file, mode="r") as f:
        f = f.read()
        cfg = json.loads(f)
    await bot.send(ev, "重载成功！")


@sv.scheduled_job('cron', minute='*/2')  # 时间为偶数分钟时运行, 每两分钟运行一次
async def check_steam_status():
    old_state = playing_state.copy()
    await update_game_status()
    if combined_mode:
        await combined_broadcast(old_state)
    else:
        await single_broadcast(old_state)


async def combined_broadcast(old_state: dict):
    # { group_id: { game_name: {start: [player1, player2], stop: [player3, player4]}}}
    # 查询每个群组的游戏状态变化, 将信息整合为群组级别的变化
    group_game_info_broadcast_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for key, val in playing_state.items():  # 遍历每个人的游戏状态
        if key not in old_state:
            sv.logger.info(f"缓存为空，初始化 {key} 的游戏状态。")
            continue
        if val["gameextrainfo"] != old_state[key]["gameextrainfo"]:
            # 获取订阅了该账号的群
            glist = set(cfg["subscribes"][key]) & set((await sv.get_enable_groups()).keys())
            for group in glist:
                if val["gameextrainfo"] == "":  # 如果新状态为空，说明停止了游戏
                    # 由于新状态为空，所以从旧状态中获取游戏名
                    game_name = old_state[key]["localized_game_name"] \
                        if old_state[key]["localized_game_name"] != "" \
                        else old_state[key]["gameextrainfo"]
                    group_game_info_broadcast_dict[group][game_name]["stop"].append(old_state[key])
                else:  # 否则说明开始了游戏
                    # 从新状态中获取游戏名
                    game_name = val["localized_game_name"] if val["localized_game_name"] != "" else val["gameextrainfo"]
                    group_game_info_broadcast_dict[group][game_name]["start"].append(val)
    # 遍历每个群组的游戏状态变化，发送消息
    for group, game_change in group_game_info_broadcast_dict.items():
        start_game_image_list = []
        stop_game_message_list = []
        for game_name, info in game_change.items():
            start = info["start"]
            stop = info["stop"]
            if len(start) != 0:
                # 迭代创建所有人的图片并添加到img_list
                start_game_image_list.extend([await make_img(player) for player in start])
            if len(stop) != 0:
                stop_game_message_list.append("{} 不玩 {} 了！".format(
                    ", ".join([player["personaname"] for player in stop]),
                    game_name))
        # 将所有图片合并为从上到下的一张图片
        if len(start_game_image_list) != 0:
            img = Image.new("RGB", (int(280 * 1.6), 86 * len(start_game_image_list)), (33, 33, 33))
            for i, image in enumerate(start_game_image_list):
                img.paste(image, (0, 86 * i))
            await broadcast({group}, MessageSegment.image(pic2b64(img)))
        # 发送停止游戏的消息
        if len(stop_game_message_list) != 0:
            await broadcast({group}, "\n".join(stop_game_message_list))


async def single_broadcast(old_state: dict):
    for key, val in playing_state.items():
        if key not in old_state:
            sv.logger.info(f"缓存为空，初始化 {key} 的游戏状态。")
            continue
        if val["gameextrainfo"] != old_state[key]["gameextrainfo"]:
            glist = set(cfg["subscribes"][key]) & set((await sv.get_enable_groups()).keys())
            if val["gameextrainfo"] == "":
                await broadcast(glist,
                                "%s 不玩 %s 了！" % (val["personaname"],
                                                    old_state[key]["localized_game_name"] if old_state[key][
                                                                                                 "localized_game_name"] != "" else
                                                    old_state[key]["gameextrainfo"]))
            else:
                await broadcast(glist, MessageSegment.image(pic2b64(await make_img(playing_state[key]))))


async def broadcast(group_list: set, msg):
    bot = get_bot()
    bot_ids = get_self_ids()
    if len(bot_ids) > 1:
        group_bot_map = {}
        for bot_id in bot_ids:
            glist = await bot.get_group_list(self_id=bot_id, no_cache=True)
            for g in glist:
                group_bot_map[g["group_id"]] = bot_id
        for group in group_list:
            await sv.bot.send_group_msg(self_id=group_bot_map[group], group_id=group, message=msg)
            await sleep(0.5)
    else:
        for group in group_list:
            await sv.bot.send_group_msg(self_id=bot_ids[0], group_id=group, message=msg)
            await sleep(0.5)
