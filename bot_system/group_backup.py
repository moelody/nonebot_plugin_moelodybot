from nonebot import get_driver, on_shell_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot.rule import ArgumentParser

import aiohttp
import os
import time
from pathlib import Path

from ..bot_utils import get_root_path


from nonebot.plugin import PluginMetadata
__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="备份群文件",
    description="",
    usage='''关键词: 备份群文件
关键词: 恢复群文件''',
    extra={
        "version": __version__,
        "license": "MIT",
        "author": "yueli",
        "command": ["备份群文件", "恢复群文件"],
        "type": 1,
        "group": "群管理"
    },
)


backup_group = get_driver().config.dict().get('backup_group', [])
backup_command = get_driver().config.dict().get('backup_command', "备份群文件")
backup_maxsize = get_driver().config.dict().get('backup_maxsize', 300)
backup_minsize = get_driver().config.dict().get('backup_minsize', 0.01)
backup_temp_files = get_driver().config.dict().get('backup_temp_files', True)
backup_temp_file_ignore = get_driver().config.dict().get(
    'backup_temp_file_ignore', [".gif", ".png", ".jpg", ".mp4"])


linker_parser = ArgumentParser(add_help=False)
linker = on_shell_command(backup_command, parser=linker_parser, priority=1)

recovery_command = get_driver().config.dict().get('recovery_command', "恢复群文件")
recovery_parser = ArgumentParser(add_help=False)
recovery = on_shell_command(
    recovery_command, parser=recovery_parser, priority=1)


essence_command = get_driver().config.dict().get('essence_command', "备份群精华")
essence_parser = ArgumentParser(add_help=False)
essence = on_shell_command(
    essence_command, parser=essence_parser, priority=1)


success_count = 0
jump_count = 0
back_size = 0
large_files = []
broken_files = []


async def SaveToDisk(bot, file_data, local_folder, gid):
    fname = file_data["file_name"]
    fid = file_data["file_id"]
    fbusid = file_data["busid"]
    fsize = file_data["file_size"]
    fpath = Path(local_folder, fname)

    if fsize / 1024 / 1024 < backup_minsize:
        return

    if fsize / 1024 / 1024 > backup_maxsize:
        global large_files
        large_files.append(fname)
        return
    global jump_count, back_size, success_count
    if not Path(fpath).exists():
        try:
            finfo = await bot.get_group_file_url(group_id=gid, file_id=str(fid), bus_id=int(fbusid))
            url = finfo['url']
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        if not Path(local_folder).exists():
                            os.makedirs(local_folder)
                        with open(fpath, 'wb') as f:
                            while True:
                                chunk = await response.content.read(1024)
                                if not chunk:
                                    break
                                f.write(chunk)

            back_size += fsize
            success_count += 1
        except Exception as e:
            broken_files.append(fname)
            print(e)
    else:
        back_size += Path(fpath).stat().st_size
        jump_count += 1


async def createFolder(bot, root_dir, gid):
    # 获取QQ群的文件夹名
    group_root = await bot.get_group_root_files(group_id=gid)
    group_folders = group_root.get("folders")
    group_folder_names = []
    if group_folders:
        group_folder_names = [i["folder_name"] for i in group_folders]

    # 如果本地有该文件夹 而群没有, 则创建

    for local_folder in os.scandir(root_dir):
        if local_folder.is_dir() and local_folder.name not in group_folder_names:

            await bot.create_group_file_folder(
                group_id=gid, name=local_folder.name, parent_id="/")


async def upload_files(bot, gid, folder_id, root_dir):
    group_root = await bot.get_group_files_by_folder(group_id=gid, folder_id=folder_id)
    files = group_root.get("files")
    filenames = []
    if files:
        filenames = [ff["file_name"] for ff in files]
    if os.path.exists(root_dir):
        for entry in os.scandir(root_dir):
            if entry.is_file() and entry.name not in filenames:
                absolute_path = Path(root_dir).resolve().joinpath(entry.name)

                await bot.upload_group_file(
                    group_id=gid, file=str(absolute_path), name=entry.name, folder=folder_id)


@essence.handle()
async def essen(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id

    messages = []
    essen_list = await bot.get_essence_msg_list(group_id=gid)
    for es in essen_list:

        message_id = es["message_id"]
        # try:
        msg = await bot.get_msg(message_id=message_id)
        print(msg["message"])
        node = {
            "type": "node",
            "data": {
                "name": "精华收集者",
                "uin": "10086",
                "content": msg["message"]
            }}
        messages.append(node)
        # except Exception as e:
        #     print(e)
    await bot.send_group_forward_msg(group_id=491207941, messages=messages)

    await essence.finish("备份完成")


@recovery.handle()
async def recover(bot: Bot, event: GroupMessageEvent):

    if await GROUP_ADMIN(bot, event) and await GROUP_OWNER(bot, event):
        await linker.finish("只允许群主或者管理员备份!")

    gid = event.group_id
    if str(gid) in backup_group or backup_group == []:

        await bot.send(event, "恢复中,请稍后(可能需要机器人管理员权限)")
        root_dir = f"{get_root_path()}/data/qqgroup/{str(gid)}"

        # 创建群文件夹
        await createFolder(bot, root_dir, gid)

        # 上传文件
        root = await bot.get_group_root_files(group_id=gid)
        folders = root.get("folders")
        await upload_files(bot, gid, "/", root_dir)

        if folders:
            for folder_data in folders:
                folder_id = folder_data["folder_id"]
                root = await bot.get_group_files_by_folder(group_id=gid, folder_id=folder_id)

                await upload_files(bot, gid, folder_id, root_dir + "/" + folder_data["folder_name"])

        await recovery.finish("恢复完成")


@linker.handle()
async def link(bot: Bot, event: GroupMessageEvent):

    if await GROUP_ADMIN(bot, event) and await GROUP_OWNER(bot, event):
        await linker.finish("只允许群主或者管理员备份!")

    global success_count, jump_count, back_size, large_files, broken_files
    success_count = 0
    jump_count = 0
    back_size = 0
    large_files = []
    broken_files = []
    gid = event.group_id
    if str(gid) in backup_group or backup_group == []:

        await bot.send(event, "备份中,请稍后…(不会备份根目录文件,请把重要文件放文件夹里)")
        tstart = time.time()
        group_root = await bot.get_group_root_files(group_id=gid)
        group_folders = group_root.get("folders")

        # 是否备份根目录文件
        if backup_temp_files:
            root_files = group_root.get("files")
            local_folder = f"{get_root_path()}/data/qqgroup/{str(gid)}"
            if root_files:
                for root_file in root_files:
                    ignore_suf = Path(root_file["file_name"]).suffix

                    # 忽略特定文件
                    if ignore_suf in backup_temp_file_ignore:
                        continue
                    await SaveToDisk(bot, root_file, local_folder, gid)

        if group_folders:
            for group_folder in group_folders:

                group_folder_data = await bot.get_group_files_by_folder(group_id=gid, folder_id=group_folder["folder_id"])

                local_folder_path = f"{get_root_path()}/data/qqgroup/{str(gid)}/{group_folder['folder_name']}"

                group_folder_files = group_folder_data.get("files")

                if group_folder_files:
                    for group_folder_file in group_folder_files:
                        await SaveToDisk(bot, group_folder_file, local_folder_path, gid)

        if len(large_files) == 0:
            large_info = "无"
        else:
            large_info = "\n".join(large_files)

        if len(broken_files) == 0:
            broken_info = ""
        else:
            broken_info = "检测到损坏文件:" + '\n'.join(broken_files)

        back_size_info = round(back_size / 1024 / 1024, 2)
        tsum = round(time.time() - tstart, 2)

        await linker.finish("此次备份耗时%2d秒; 共备份%d个文件,跳过已备份%d个文件, 累计备份大小%.2f M,\n未备份大文件列表(>%dm):\n%s\n%s" % (tsum, success_count, jump_count, back_size_info, backup_maxsize, large_info, broken_info))
