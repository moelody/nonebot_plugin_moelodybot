import datetime
from pathlib import Path
import re


def generate_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-4]


def get_root_path():
    return str(Path(__file__).parent.parent.resolve())


def generate_cache_image_path():
    return str(Path(__file__).parent.parent.resolve() / "data/cache") + "/" + generate_timestamp() + ".jpg"


def convert_to_uri(filepath):
    return Path(filepath).as_uri()


def clean_link(link):
    link = re.findall(r'(https?://\S+)', link)[0]
    return re.sub(r'\?.*$', '', link)
