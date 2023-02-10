from PIL import Image, ImageDraw, ImageFont

from .util import generate_cache_image_path, convert_to_uri, get_root_path


def split_content(content, content_size_list, max_line_width):
    """清理文字, 转为合适长度的文字列表"""

    current_line_width = 0
    final_content = []
    last_index = 0

    for i in range(len(content)):
        if current_line_width + content_size_list[i] >= max_line_width:
            if i == len(content) - 1:
                # 正好最后一个字超了 直接加
                final_content.append(content[last_index:])
            else:
                final_content.append(content[last_index:i])
                last_index = i
                current_line_width = 0

        else:
            if i == len(content) - 1:
                final_content.append(content[last_index:])
            current_line_width += content_size_list[i]
    return final_content


def get_msg_size(msg, font):
    """获取文字渲染后宽度"""
    size = []
    for t in msg:
        box = font.getbbox(t)
        size.append(box[2] - box[0])
    return size


def text_to_image(text_list):
    """将文字转为图片"""
    font_size = 24

    font = ImageFont.truetype(
        f"{get_root_path()}/data/fonts/SourceHanSansCN-Medium.otf", font_size
    )

    footage_clip_size = 60
    lines_space = 15
    line_padding_left_and_right = 60  # 文字距离最左边距离

    line_height = font_size + lines_space

    footage = Image.open(f"{get_root_path()}/data/images/background.jpg")
    header = footage.crop(box=(0, 0, footage.width, footage_clip_size))
    footer = footage.crop(box=(0, footage.height - footage_clip_size,
                               footage.width, footage.height))

    max_line_width = footage.width - line_padding_left_and_right * 2  # 自己减下边框值
    content = footage.crop(
        box=(0, footage_clip_size, footage.width, line_height + footage_clip_size))

    to_render_text_list = []
    for to_render_text in text_list:
        msg_size = get_msg_size(to_render_text, font)
        to_render_text_list.extend(
            split_content(to_render_text, msg_size, max_line_width))

    image_result = Image.new("RGB", (footage.width, footage_clip_size *
                                     2 + len(to_render_text_list) * line_height), color=(255, 255, 255, 0))
    image_result.paste(im=header, box=(0, 0))

    for idx, text in enumerate(to_render_text_list):
        cache = content.copy()
        draw = ImageDraw.Draw(cache)
        draw.text(xy=(line_padding_left_and_right, 0), text=text, font=font,
                  fill=(125, 97, 85))
        image_result.paste(im=cache, box=(
            0, footage_clip_size + line_height * (idx)))

    image_result.paste(im=footer, box=(
        0, footage_clip_size + line_height * len(to_render_text_list)))
    image_result.show()
    cache_path = generate_cache_image_path()

    image_result.save(cache_path)

    return convert_to_uri(cache_path)


if __name__ == "__main__":
    text1 = ['180天以上未发言的群友有:', '544361711\t论BGM的重要性', '853467208\t造花', '908157828\tRumia', '946501847\t天冰',
             '994380598\t唯不忘相思', '1162159420\t绫绫子想早睡早起', '1799363617\t＝ ＝', '2802670301\tAQ大魔王', '', '是否踢出(请回复 是/否)']

    print(text_to_image(text1))
