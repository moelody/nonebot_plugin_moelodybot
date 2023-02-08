import random
from pathlib import Path

from PIL import Image

from .util import generate_timestamp


async def handle_image(src):
    src = Path(src).resolve()
    image = Image.open(src)

    image_copy = image.copy()
    width = 1
    clip = 20
    image_new = Image.new('RGB', (width, width), (0, 0, 255))
    image_width = image.width
    image_height = image.height

    box = (3, 3, image_width - 3, image_height - 3)

    for i in range(5):
        rnd_w = random.randint(1, image_width - width)
        rnd_h = random.randint(1, clip * 2)
        # rnd = random.randint(width, image.width - width)
        if rnd_h > clip:
            rnd_h = image_height - rnd_h + clip
        image_copy.paste(
            image_new, (rnd_w, rnd_h, rnd_w + width, rnd_h + width))

    im_crop = image_copy.crop(box)
    out = r'/www/wwwroot/project/Robot/nobotX/plugins/data/images/temp/' + \
        generate_timestamp() + src.suffix
    im_crop.save(out, quality=50)
    return out
