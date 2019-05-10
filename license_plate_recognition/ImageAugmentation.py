import os
from math import tan, atan
# import itertools
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches

class ImageAugmentation(object):
    def __init__(self, is_train=True):
        self.is_train = is_train

    def do_rotate(self, image, angle):
        h = image.shape[0]
        w = image.shape[1]

        (cX, cY) = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        image = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

        return image

    def do_shear(self, image, angle):
        h = image.shape[0]
        w = image.shape[1]

        angle = angle / 180 * np.pi
        M = np.float64([[1, tan(angle), 0], [0, 1, 0]])
        image = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

        return image

    def do_padding(self, image, pixels):
        h = image.shape[0]
        w = image.shape[1]
        image = cv2.copyMakeBorder(image, pixels, pixels, pixels, pixels, borderType=cv2.BORDER_REPLICATE)
        image = cv2.resize(image, (w, h))

        return image

    def do_shift(self, image, pixels):
        h = image.shape[0]
        w = image.shape[1]

        M = np.float64([[1, 0, 0], [0, 1, pixels]])
        image = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

        return image

    def transform(self, image):
        # 输入图像是竖着的（转置过的图像
        image = image.transpose(1, 0, 2)

        p = np.random.rand()
        if p > 0.5:
            p = np.random.rand()
            if p > 0.5:
                pixels = 15 * np.random.rand()
                image = self.do_padding(image, 15)
                image = self.do_shift(image, pixels)

        p = np.random.rand()
        if p > 0.5:
            p = np.random.rand()
            if p > 0.5:
                angle = 4 * ((np.random.rand() - 0.5) * 2)
                image = self.do_rotate(image, angle)
            else:
                angle = 8 * ((np.random.rand() - 0.5) * 2)
                image = self.do_shear(image, angle)

        p = np.random.rand()
        if p > 0.5:
            factory = 0.8 + 0.2 * np.random.rand()
            image = image * factory
        
        return image.transpose(1, 0, 2)

if __name__ == '__main__':
    ia = ImageAugmentation()

    img_dir = r"./data/train-data/"
    file_list = os.listdir(img_dir)
    c = np.random.choice(len(file_list))
    test_file = img_dir + file_list[c]
    print("choose image: ", file_list[c])
    # 原始图像
    test_img = cv2.imread(test_file)
    plt.subplot(10, 1, 1)
    plt.imshow(test_img)
    test_img = test_img.transpose(1, 0, 2)
    test_img = test_img.astype(np.float32) / 255
    img_trans = ia.transform(test_img)
    img_trans = img_trans.transpose(1, 0, 2)
    plt.subplot(10, 1, 2)
    plt.imshow(img_trans)
    plt.show()