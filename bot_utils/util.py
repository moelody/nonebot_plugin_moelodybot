import datetime
from pathlib import Path
import re
import deepl

from ..config import deepl_key


def generate_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-4]


def get_root_path():
    return str(Path(__file__).parent.parent.resolve())


def generate_cache_image_path():
    return Path(__file__).parent.parent.resolve() / "data/cache" / f'{generate_timestamp()}.jpg'


def convert_to_uri(filepath):
    return Path(filepath).as_uri()


def clean_link(link: str):
    """清理链接

    Args:
        link (str): 原始链接, 如 https://music.163.com/#/song?id=399249&userid=132242222

    Returns:
        [type]: str, 清理后的链接,如 https://music.163.com/#/song
    """
    link = re.findall(r'(https?://\S+)', link)[0]
    return re.sub(r'\?.*$', '', link)


def tran_deepl_pro(text: str):
    translator = deepl.Translator(deepl_key)
    result = translator.translate_text(text, target_lang="ZH")
    return result.text if isinstance(result, deepl.TextResult) else "翻译报错,请联系管理员"


print(tran_deepl_pro("hello world"))
