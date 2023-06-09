
import contextlib
import cv2
import imageio.v2 as imageio
import glob

import numpy as np

from .util import get_root_path


def is_dragon(file_path):

    det = DragonDetector()
    img = cv2.imread(str(file_path))
    return bool(det.is_dragon_image(img))


def read_img(name):
    if not name.endswith(".gif"):
        return cv2.cvtColor(imageio.imread(name), cv2.COLOR_RGB2BGR)
    gif = imageio.mimread(name)
    return cv2.cvtColor(gif[0], cv2.COLOR_RGB2BGR)


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]
    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image
    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)
    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


def minEnclosingCircleArea(pts):
    _, r = cv2.minEnclosingCircle(pts)
    return r * r * np.pi


class DragonDetector(object):
    def __init__(self, template_image_pattern='template*.png', image_resolutions=[20, 60, 100, 200, 400], match_point_threshold=5, circle_area_threshold=0.2):
        template_path = f"{get_root_path()}/data/images/dragon_template/{template_image_pattern}"
        self.templates = [read_img(fn)
                          for fn in glob.glob(template_path)]

        self.match_point_threshold = match_point_threshold
        self.circle_area_threshold = circle_area_threshold
        self.image_resolutions = image_resolutions
        self.sift = cv2.SIFT_create()
        self.template_sifts = [(self.sift.detectAndCompute(
            img, None), img.shape) for img in self.templates]
        # FLANN parameters
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)   # or pass empty dictionary
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)
        # print(f' -- {len(self.templates)} dragon templates loaded')

    def is_dragon_impl(self, kps, imgnp):
        # 解包关键点和模板形状
        (kp1, des1), template_shape = kps

        # 使用 SIFT 算法计算图像关键点和描述符
        kp2, des2 = self.sift.detectAndCompute(imgnp, None)
        try:
            matches = self.flann.knnMatch(des1, des2, k=2)
        except Exception:
            return False
        good = [m for m, n in matches if m.distance < 0.7 * n.distance]
        if len(good) > self.match_point_threshold:
            src_pts = np.float32(
                [kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32(
                [kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            h, w, d = template_shape
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1],
                             [w - 1, 0]]).reshape(-1, 1, 2)
            with contextlib.suppress(Exception):
                dst = cv2.perspectiveTransform(pts, M)
                if cv2.contourArea(dst) > self.circle_area_threshold * minEnclosingCircleArea(dst):
                    return True
        return False

    def is_dragon_image(self, img_np):
        found = False
        for template in self.template_sifts:
            for w in self.image_resolutions:
                found = found or self.is_dragon_impl(
                    template, image_resize(img_np, width=w, inter=cv2.INTER_LINEAR))
        return found


class DragonDetectorFast(DragonDetector):
    def __init__(self):
        super().__init__('template1.png', [200])


if __name__ == '__main__':
    print(is_dragon("test1.jpg"))
