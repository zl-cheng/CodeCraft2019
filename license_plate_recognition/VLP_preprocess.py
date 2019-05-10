import os
from math import tan, atan
# import itertools
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches

class VLPPreProcess(object):
    def __init__(self, target_w, target_h, target_channel):
        self.w = target_w
        self.h = target_h
        self.c = target_channel

    def proper_binarization(self, image):
        image = cv2.medianBlur(image, 5)
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        retval, imgae_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_OTSU)

        # 去除背景，尝试3次
        for i in range(3):
            n, img_area, bboxs, _ = cv2.connectedComponentsWithStats(imgae_binary, connectivity=4)
            valid_cnt = 0
            for i in range(1, n):
                if self.is_connected_component_valid(bboxs[i]):
                    valid_cnt += 1
            # 一共9个字符，如果连通区域小于x个，证明是错误二值化（背景前景二值化了
            if valid_cnt < 4:
                # 删除背景，再次二值化
                image_gray[imgae_binary > 0] = max(image_gray[imgae_binary == 0].mean() - 20, 0)
                retval, imgae_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_OTSU)
            else:
                break

        return imgae_binary

    def is_connected_component_valid(self, bbox):
        w = bbox[2]
        h = bbox[3]
        n_pixels = bbox[-1]
        if w * h < 400:
            return False
        if n_pixels < 50:
            return False
        if w > 120:
            return False
        if h > 60 or h < 15:
            return False

        return True

    def get_connected_components(self, image):
        n, img_area, bboxs, _ = cv2.connectedComponentsWithStats(image, connectivity=4)
        img_area = img_area.astype(np.uint8)
        # 删除一些不合理的连通区域
        for i in range(1, n):   # 第0个元素是背景，像素==0
            if not self.is_connected_component_valid(bboxs[i]):
                img_area[img_area == i] = 0

        return img_area

    def find_updown_points(self, image):
        up_points = []
        down_points = []

        for label in np.unique(image):
            is_, js = np.where(image == label)
            i_min = is_.min()
            j_min = js[np.where(is_ == i_min)[0][0]]

            i_max = is_.max()
            j_max = js[np.where(is_ == i_max)[0][0]]
            
            if i_min > 0:
                up_points.append([i_min, j_min])
            if i_max < image.shape[0]:
                down_points.append([i_max, j_max])

        up_points = np.array(up_points)
        down_points = np.array(down_points)

        # 删除异常值
        if up_points.shape[0] >= 3:
            up_points = up_points[np.abs(up_points[:, 0] - up_points[:, 0].mean()) < 10, :]
        if down_points.shape[0] >= 3:
            down_points = down_points[np.abs(down_points[:, 0] - down_points[:, 0].mean()) < 10, :]

        return up_points, down_points
    
    def ploy_line_and_get_horizontal_angle(self, up_points, down_points):
        # p[0] = k, p[1] = b
        pu = (1, 0)
        pd = (1, 0)
        if up_points.shape[0] >= 3:
            pu = np.polyfit(up_points[:,1], up_points[:, 0], 1)
        if down_points.shape[0] >= 3:
            pd = np.polyfit(down_points[:,1], down_points[:, 0], 1)

        p = pu if abs(pu[0]) < abs(pd[0]) else pd
        angle = atan(p[0]) if p[0] != 0 else 0
        angle = angle / np.pi * 180

        if angle < 20:
            return angle # 返回角度值
        else:
            return 0

    def rotate_bound(self, image, angle):
        h = image.shape[0]
        w = image.shape[1]
        (cX, cY) = (w // 2, h // 2)
    
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        
        image = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

        return image

    def shear_bound(self, image, angle):
        h = image.shape[0]
        w = image.shape[1]
        angle = angle / 180 * np.pi
        M = np.float64([[1, tan(angle), 0], [0, 1, 0]])
        image = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        return image

    def clahe_bound(self, image):
        try:
            self.clahe
        except AttributeError:
            self.clahe = cv2.createCLAHE(clipLimit=5, tileGridSize=(8, 8))

        image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        image[:, :, 0] = self.clahe.apply(image[:, :, 0])
        image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)

        return image

    def vertical_cost(self, image_area):
        # 垂直代价是每个字符的宽度，优化到最小就得到垂直失真角度了
        cost = 0
        n, image_area, bboxs, _ = cv2.connectedComponentsWithStats(image_area, connectivity=4)
        for i in range(1, n):
            cost += bboxs[i][2]
            
        return cost

    def get_vertical_angle(self, image_area):
        shear_angles = list(range(-20, 20))
        costs = []

        for angle in shear_angles:
            sheared_img = self.shear_bound(image_area, angle)
            costs.append(self.vertical_cost(sheared_img))
            
        shear_angle = shear_angles[costs.index(min(costs))]
        return shear_angle

    def image_correct(self, image):
        img_binary = self.proper_binarization(image)
        img_area = self.get_connected_components(img_binary)
        n, _, _, _ = cv2.connectedComponentsWithStats(img_area, connectivity=4)
        if n >= 4:
            up_points, down_points = self.find_updown_points(img_area)
            horizontal_angle = self.ploy_line_and_get_horizontal_angle(up_points, down_points)
            img_area_rotated = self.rotate_bound(img_area, horizontal_angle)
            vertical_angle = self.get_vertical_angle(img_area_rotated)

            image = self.shear_bound(self.rotate_bound(image, horizontal_angle), vertical_angle)
        
        if image.shape[1] != self.h or image.shape[2] != self.w:
            image = cv2.resize(image, (self.w, self.h))
            
        if self.c == 1:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = image.transpose(1, 0)
            image = image.astype(np.float32)
            image = cv2.normalize(image, None, 0, 1, cv2.NORM_MINMAX)
            image = image[:,:,np.newaxis]
        else:
            image = image.transpose(1, 0, 2)
            image = self.clahe_bound(image)
            image = image.astype(np.float32)
            image = cv2.normalize(image, None, 0, 1, cv2.NORM_MINMAX)
            # 输出去中心化的数据
            image = image - np.array([0.16831076, 0.16831076, 0.16831076], dtype=np.float32)
            image = image / np.array([0.34511185, 0.30767402, 0.2996498], dtype=np.float32)
 
        return image


if __name__ == '__main__':
    vp = VLPPreProcess(356, 70, 3)

    img_dir = r"./data/train-data/"
    file_list = os.listdir(img_dir)
    c = np.random.choice(len(file_list))
    test_file = img_dir + file_list[c]
    print("choose image: ", file_list[c])
    # 原始图像
    test_img = cv2.imread(test_file)
    clane_img = vp.image_correct(test_img)
    plt.subplot(10, 1, 1)
    plt.imshow(test_img)

    # 二值化图像
    img_binary = vp.proper_binarization(test_img)
    plt.subplot(10, 1, 2)
    plt.imshow(img_binary)

    # 有效连通区域
    img_area = vp.get_connected_components(img_binary)
    n, img_area, bboxs, _ = cv2.connectedComponentsWithStats(img_area, connectivity=4)
    img_area = img_area.astype(np.uint8)
    plt.subplot(10, 1, 3)
    plt.imshow(img_area)
    for i in range(1, n):
        currentAxis = plt.gca()
        bbox = bboxs[i]
        w = bbox[3] - bbox[1]
        h = bbox[2] - bbox[0]
        rect = patches.Rectangle((bbox[0], bbox[1]), bbox[2], bbox[3], linewidth=1, edgecolor='r', facecolor='none')
        currentAxis.add_patch(rect)

    # plt.show()

    # 上/下直线拟合点
    up_points, down_points = vp.find_updown_points(img_area)
    plt.plot(up_points[:,1], up_points[:, 0], '.', c='r')
    plt.plot(down_points[:,1], down_points[:, 0], '.', c='w')

    # 计算水平角度
    horizontal_angle = vp.ploy_line_and_get_horizontal_angle(up_points, down_points)
    print("horizontal_angle is: ", horizontal_angle)

    # 矫正连通图
    img_area_rotated = vp.rotate_bound(img_area, horizontal_angle)
    plt.subplot(10, 1, 4)
    plt.imshow(img_area_rotated)

    # 计算水平失真角度
    vertical_angle = vp.get_vertical_angle(img_area_rotated)
    print("vertical_angle is: ", vertical_angle)
    img_sheared = vp.shear_bound(img_area_rotated, vertical_angle)
    plt.subplot(10, 1, 5)
    plt.imshow(img_sheared)

    # 矫正原始图像
    test_img_corrected = vp.image_correct(test_img)
    plt.subplot(10, 1, 6)
    plt.imshow(test_img_corrected)

    plt.show()
