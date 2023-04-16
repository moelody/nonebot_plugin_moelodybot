import asyncio

import aiohttp
from nonebot import logger


class Config:
    bing_key: str
    bing_region: str
    deepl_key: str


# config = Config(deepl_key="d54b8da3-58ac-0cfd-a1a6-a3630b75ff06:fx")
config = Config()
"""
fork: https://github.com/sena-nana/nonebot-plugin-novelai/blob/main/nonebot_plugin_novelai/
"""


async def translate_bing(text: str, to: str):
    """
    en,jp,zh_Hans
    """
    if to == "zh":
        to = "zh-Hans"
    key = config.bing_key
    if not key:
        return None
    region = config.bing_region
    if not region:
        return None
    header = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-Type": "application/json",
    }
    async with aiohttp.ClientSession() as session:
        body = [{"text": text}]
        params = {
            "api-version": "3.0",
            "to": to,
            "profanityAction": "Deleted",
        }
        async with session.post(
            "https://api.cognitive.microsofttranslator.com/translate",
            json=body,
            params=params,
            headers=header,
        ) as resp:
            if resp.status != 200:
                logger.error(f"Bing翻译接口调用失败,错误代码{resp.status},{await resp.text()}")
                return None
            jsonresult = await resp.json()
            result = jsonresult[0]["translations"][0]["text"]
            logger.debug(f"Bing翻译启动，获取到{text},翻译后{result}")
            return result


async def translate_deepl(text: str, to: str):
    """
    EN,JA,ZH
    """
    to = to.upper()
    key = config.deepl_key
    if not key:
        return None
    async with aiohttp.ClientSession() as session:
        params = {
            "auth_key": key,
            "text": text,
            "target_lang": to,
        }
        async with session.get(
            "https://api-free.deepl.com/v2/translate", params=params
        ) as resp:
            if resp.status != 200:
                logger.error(f"DeepL翻译接口调用失败,错误代码{resp.status},{await resp.text()}")
                return None
            jsonresult = await resp.json()
            result = jsonresult["translations"][0]["text"]
            logger.debug(f"DeepL翻译启动，获取到{text},翻译后{result}")
            return result


async def translate_youdao(input: str, mode: str):
    """
    默认auto
    ZH_CH2EN 中译英
    EN2ZH_CN 英译汉
    """
    if mode == "zh":
        mode = "EN2ZH_CN"
    elif mode == "en":
        mode = "ZH_CH2EN"

    mode = "JA2ZH_CN"
    async with aiohttp.ClientSession() as session:
        data = {"doctype": "json", "type": mode, "i": input}
        async with session.post("http://fanyi.youdao.com/translate", data=data) as resp:
            if resp.status != 200:
                logger.error(f"有道翻译接口调用失败,错误代码{resp.status},{await resp.text()}")
                return None
            result = await resp.json()
            result = result["translateResult"][0][0]["tgt"]
            logger.debug(f"有道翻译启动，获取到{input},翻译后{result}")
            return result


async def translate_google_proxy(input: str, to: str):
    """
    en,jp,zh 需要来源语言
    """
    if to == "zh":
        from_ = "en"
    else:
        from_ = "zh"
    async with aiohttp.ClientSession() as session:
        data = {"data": [input, from_, to]}
        async with session.post(
            "https://hf.space/embed/mikeee/gradio-gtr/+/api/predict", json=data
        ) as resp:
            if resp.status != 200:
                logger.error(f"谷歌代理翻译接口调用失败,错误代码{resp.status},{await resp.text()}")
                return None
            result = await resp.json()
            result = result["data"][0]
            logger.debug(f"谷歌代理翻译启动，获取到{input},翻译后{result}")
            return
