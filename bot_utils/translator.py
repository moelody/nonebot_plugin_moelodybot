import asyncio

import aiohttp

"""
fork: https://github.com/sena-nana/nonebot-plugin-novelai/blob/main/nonebot_plugin_novelai/extension/translation.py
"""


async def translate_bing(text: str, to: str, bing_key: str):
    """
    en,jp,zh_Hans
    """
    if to == "zh":
        to = "zh-Hans"
    key = bing_key
    if not key:
        return None
    header = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json",
    }
    async with aiohttp.ClientSession() as session:
        body = [{'text': text}]
        params = {
            "api-version": "3.0",
            "to": to,
            "profanityAction": "Deleted",
        }
        async with session.post('https://api.cognitive.microsofttranslator.com/translate', json=body, params=params, headers=header) as resp:
            if resp.status != 200:
                print(f"Bing翻译接口调用失败,错误代码{resp.status},{await resp.text()}")
                return None
            jsonresult = await resp.json()
            result = jsonresult[0]["translations"][0]["text"]

            return result


async def translate_deepl(text: str, key: str):
    """
    EN,JA,
    """

    async with aiohttp.ClientSession() as session:
        params = {
            "auth_key": key,
            "text": text,
            "target_lang": "ZH",
        }
        async with session.get('https://api-free.deepl.com/v2/translate', params=params) as resp:
            if resp.status != 200:
                print(f"DeepL翻译接口调用失败,错误代码{resp.status},{await resp.text()}")
                return None
            jsonresult = await resp.json()
            result = jsonresult["translations"][0]["text"]

            return result


async def translate_volcengine(src_content: str):
    async with aiohttp.ClientSession() as session:
        data = {
            'doctype': 'json',
            'type': 'EN2ZH_CN',
            'i': src_content
        }
        async with session.post("http://fanyi.youdao.com/translate", data=data) as resp:
            if resp.status != 200:
                print(f"有道翻译接口调用失败,错误代码{resp.status},{await resp.text()}")
                return None
            result = await resp.json()
            result = result["translateResult"][0][0]["tgt"]

            return result


async def translate_youdao(src_content: str):
    """
    EN2ZH_CN 英译汉
    """

    async with aiohttp.ClientSession() as session:
        data = {
            'doctype': 'json',
            'type': 'EN2ZH_CN',
            'i': src_content
        }
        async with session.post("http://fanyi.youdao.com/translate", data=data) as resp:
            if resp.status != 200:
                print(f"有道翻译接口调用失败,错误代码{resp.status},{await resp.text()}")
                return None
            result = await resp.json()
            result = result["translateResult"][0][0]["tgt"]

            return result


async def translate_google_proxy(src_content: str):
    """
    en,jp,zh 需要来源语言
    """
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    async with aiohttp.ClientSession()as session:
        data = {"data": [src_content, "en", "zh"]}
        async with session.post("https://hf.space/embed/mikeee/gradio-gtr/+/api/predict", json=data, proxy='http://127.0.0.1:10809')as resp:
            if resp.status != 200:
                print(f"谷歌代理翻译接口调用失败,错误代码{resp.status},{await resp.text()}")
                return None
            result = await resp.json()
            result = result["data"][0]

            return result
