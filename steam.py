import json
import os
from lxml import etree
from asyncio import sleep

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from nonebot import MessageSegment

from hoshino import service, aiorequests
from hoshino.util import pic2b64

help_ ="""
[添加steam订阅 steamid或自定义url] 订阅一个账号的游戏状态
[取消steam订阅 steamid或自定义url] 取消订阅
[steam订阅列表] 查询本群所有订阅账号的游戏状态
[谁在玩游戏] 看看谁在玩游戏
[查询steam账号] 查询指定steam账号的游戏状态
"""

sv = service.Service("steam", enable_on_default=True, help_=help_)

proxies = None
# proxies = {
#     'http': "",
#     'https': "",
# }

current_folder = os.path.dirname(__file__)
config_file = os.path.join(current_folder, 'steam.json')
with open(config_file, mode="r") as f:
    f = f.read()
    cfg = json.loads(f)

playing_state = {}

async def format_id(id: str) -> str:
    if id.startswith('76561') and len(id) == 17:
        return id
    else:
        resp = await aiorequests.get(f'https://steamcommunity.com/id/{id}?xml=1', proxies=proxies)
        xml = etree.XML(await resp.content)
        return xml.xpath('/profile/steamID64')[0].text


def make_img(data):
    top = data["personaname"]
    mid = "is now playing"
    bottom = data["gameextrainfo"]
    url = data["avatarmedium"]

    text_size = 16
    spacing = 20
    font_multilang_path = os.path.join(os.path.dirname(__file__), 'simhei.ttf')
    font_ascii_path = os.path.join(os.path.dirname(__file__), 'tahoma.ttf')
    font_ascii = ImageFont.truetype(font_ascii_path, size=text_size)
    font_multilang = ImageFont.truetype(font_multilang_path, size=text_size)

    image_bytes = urlopen(url).read()
    data_stream = BytesIO(image_bytes)
    avatar = Image.open(data_stream)
    w = int(280 * 1.6)
    h = 86
    img = Image.new("RGB", (w, h), (33, 33, 33))
    draw = ImageDraw.Draw(img)
    avatar = avatar.resize((60, 60))
    green_line = Image.new("RGB", (3, 60), (89, 191, 64))
    img.paste(avatar, (13, 10))
    img.paste(green_line, (74, 10))
    draw.text((90, 10), top, fill=(193, 217, 167), font=font_multilang)
    draw.text((90, 10 + spacing - 2), mid, fill=(115, 115, 115), font=font_ascii)
    # draw.text((90, 10+spacing*2), bottom, fill=(135, 181, 82), font=font_ascii)

    x_position = 90  # 起始x位置
    for char in bottom:
        current_font = font_ascii
        # 如果当前字体默认字体并且字符不在默认字体中，则切换到回退字体
        if current_font == font_ascii and draw.textlength(char, font=font_ascii) == text_size:
            current_font = font_multilang
        # 绘制字符
        draw.text((x_position, 10 + spacing * 2), text=char, font=current_font, fill=(135, 181, 82))
        # 更新x位置以便下一个字符能紧挨着前一个字符
        x_position += draw.textlength(char, font=current_font)

    # img.show()
    return img


@sv.on_prefix("添加steam订阅")
async def steam(bot, ev):
    account = str(ev.message).strip()
    try:
        await update_steam_ids(account, ev["group_id"])
        rsp = await get_account_status(account)
        if rsp["personaname"] == "":
            await bot.send(ev, "添加订阅失败！")
        elif rsp["gameextrainfo"] == "":
            await bot.send(ev, f"%s 没在玩游戏！" % rsp["personaname"])
        else:
            await bot.send(ev, f"%s 正在玩 %s ！" % (rsp["personaname"], rsp["gameextrainfo"]))
        await bot.send(ev, "订阅成功")
    except:
        await bot.send(ev, "订阅失败")


@sv.on_prefix("取消steam订阅")
async def steam(bot, ev):
    account = str(ev.message).strip()
    try:
        await del_steam_ids(account, ev["group_id"])
        await bot.send(ev, "取消订阅成功")
    except:
        await bot.send(ev, "取消订阅失败")


@sv.on_fullmatch(("steam订阅列表", "谁在玩游戏"))
async def steam(bot, ev):
    group_id = ev["group_id"]
    msg = '======steam======\n'
    await update_game_status()
    for key, val in playing_state.items():
        if group_id in cfg["subscribes"][str(key)]:
            if val["gameextrainfo"] == "":
                msg += "%s 没在玩游戏\n" % val["personaname"]
            else:
                msg += "%s 正在游玩 %s\n" % (val["personaname"], val["gameextrainfo"])
    await bot.send(ev, msg)


@sv.on_prefix("查询steam账号")
async def steam(bot, ev):
    account = str(ev.message).strip()
    rsp = await get_account_status(account)
    if rsp["personaname"] == "":
        await bot.send(ev, "查询失败！")
    elif rsp["gameextrainfo"] == "":
        await bot.send(ev, f"%s 没在玩游戏！" % rsp["personaname"])
    else:
        await bot.send(ev, f"%s 正在玩 %s ！" % (rsp["personaname"], rsp["gameextrainfo"]))


async def get_account_status(id) -> dict:
    id = await format_id(id)
    params = {
        "key": cfg["key"],
        "format": "json",
        "steamids": id
    }
    resp = await aiorequests.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/", params=params, proxies=proxies)
    rsp = await resp.json()
    friend = rsp["response"]["players"][0]
    return {
        "personaname": friend["personaname"] if "personaname" in friend else "",
        "gameextrainfo": friend["gameextrainfo"] if "gameextrainfo" in friend else ""
    }


async def update_game_status():
    params = {
        "key": cfg["key"],
        "format": "json",
        "steamids": ",".join(cfg["subscribes"].keys())
    }
    resp = await aiorequests.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/", params=params, proxies=proxies)
    rsp = await resp.json()
    for friend in rsp["response"]["players"]:
        playing_state[friend["steamid"]] = {
            "personaname": friend["personaname"],
            "gameextrainfo": friend["gameextrainfo"] if "gameextrainfo" in friend else "",
            "avatarmedium": friend["avatarmedium"],
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


@sv.scheduled_job('cron', minute='*/2')
async def check_steam_status():
    old_state = playing_state.copy()
    await update_game_status()
    for key, val in playing_state.items():
        try:
            if val["gameextrainfo"] != old_state[key]["gameextrainfo"]:
                glist = set(cfg["subscribes"][key]) & set((await sv.get_enable_groups()).keys())
                if val["gameextrainfo"] == "":
                    await broadcast(glist,
                                    "%s 不玩 %s 了！" % (val["personaname"], old_state[key]["gameextrainfo"]))
                else:
                    # await broadcast(glist,
                    #                 "%s 正在游玩 %s ！" % (val["personaname"], val["gameextrainfo"]))
                    await broadcast(glist, MessageSegment.image(pic2b64(make_img(playing_state[key]))))
        except Exception as e:
            sv.logger.warning(f"check_steam_status error: {e}, key: {key}, val: {val}, skipped.")



async def broadcast(group_list: set, msg):
    for group in group_list:
        await sv.bot.send_group_msg(group_id=group, message=msg)
        await sleep(0.5)