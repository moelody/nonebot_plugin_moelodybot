from nonebot import get_loaded_plugins
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment as MS
from ..bot_utils.text_to_image import text_to_image
from ..config import commands


def get_commands():
    help_info = []
    current_group = ""
    help_list = []
    plugins = get_loaded_plugins()

    for plugin in plugins:
        if plugin.metadata:
            if plugin.metadata.extra and plugin.metadata.extra.get("command", None):
                commands.extend(plugin.metadata.extra["command"])
            if plugin.metadata.extra and plugin.metadata.extra.get("group", None):
                help_info.append({"name": plugin.metadata.name, "usage": plugin.metadata.usage,
                                  "group": plugin.metadata.extra.get("group")})

    sorted_list = sorted(help_info, key=lambda x: x['group'])

    for ele in sorted_list:
        if current_group != ele["group"]:
            current_group = ele["group"]
            help_list.extend(["-----", current_group])
        else:
            name = ele["name"]
            usage = ele["usage"]
            help_list.extend([f"名称: {name} 用法:{usage}"])
    return help_list


test = on_command("help", aliases={"帮助"}, priority=99, block=True)


@test.handle()
async def handle_test():
    file = text_to_image(get_commands())
    msg = MS.image(file)
    await test.finish(msg)
