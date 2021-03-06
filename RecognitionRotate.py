import cv2

import numpy as np
import imutils

from Point import *
import ColorList
import config as cfg
class ColorContourRecognition:
    """该类完成以下基本操作：
        2. 亮度对比度调整
        4. 图像读取
        3. 形态学、二值化处理
        5. 获取目标颜色部分的二值图
        6. 寻找轮廓并粗略过滤
        7. 获取第一阶段处理结果（上述操作的总和）
        """

    # def __init__(self, id, cap, path):
    #     self.id = id  # 标志实物图
    #     # _, self.image = cap.read()  # 从摄像头读取
    #     self.image = self.readImage(cap, path)
    #     self.cnts = []
    #     self.cnt_num = 0
    #     self.centerP = Point(0, 0)  # 形状的中心点

    def __init__(self, id, img):
        self.id = id  # 标志实物图

        if self.id == 0:
            img = self.adjustContrastBrightness(img, 1.15, -10)
        self.image = img

        self.cnts = []
        self.cnt_num = 0
        self.centerP = Point(0, 0)  # 形状的中心点
        # cv2.imshow("adjusted", self.image)
        # cv2.waitKey(0)

    def getImage(self):
        return self.image

    def adjustContrastBrightness(self, src, a, g):
        """亮度、对比度调整"""
        h, w, ch = src.shape  # 获取shape的数值，height和width、通道
        # 新建全零图片数组src2,将height和width，类型设置为原图片的通道类型(色素全为零，输出为全黑图片)
        src2 = np.zeros([h, w, ch], src.dtype)
        dst = cv2.addWeighted(src, a, src2, 1 - a, g)
        return dst

    def postprocessMorphology(self, image):
        """形态学、二值化处理"""
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        # 进行闭运算，形成封闭图形
        closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        # 腐蚀图像
        closed = cv2.erode(closed, None, iterations=2)
        # 膨胀图像
        thresh = cv2.dilate(closed, None, iterations=2)
        blurred = cv2.GaussianBlur(thresh, (5, 5), 0)
        ret, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)
        return thresh

    def readImage(self, cap, path):
        """图像读取"""
        if path == None:
            ret, image = cap.read()
        else:
            image = cv2.imread(path)

        if self.id == 0:
            image = self.adjustContrastBrightness(image, 1.1, -10)
        cv2.imwrite("images/template/01.jpg", image)
        return image

    def getColorPart(self, colorIndict):
        """获取目标颜色部分的二值图"""
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        colordic = ColorList.getColorList(self.id)
        for d in colordic:
            if d == colorIndict:
                if len(colordic[d]) == 4:
                    mask1 = cv2.inRange(hsv, colordic[d][0], colordic[d][1])
                    mask2 = cv2.inRange(hsv, colordic[d][2], colordic[d][3])
                    thresh = cv2.addWeighted(mask1, 1, mask2, 1, 0)
                else:
                    thresh = cv2.inRange(hsv, colordic[d][0], colordic[d][1])
                break
        thresh = self.postprocessMorphology(thresh)

        # cv2.imshow(d, thresh)
        # cv2.waitKey(0)

        return self.image, thresh, hsv

    def getColorPart2(self, colorIndict, img):
        """获取目标颜色部分的二值图"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        colordic = ColorList.getColorList(self.id)
        for d in colordic:
            if d == colorIndict:
                if len(colordic[d]) == 4:
                    mask1 = cv2.inRange(hsv, colordic[d][0], colordic[d][1])
                    mask2 = cv2.inRange(hsv, colordic[d][2], colordic[d][3])
                    thresh = cv2.addWeighted(mask1, 1, mask2, 1, 0)
                else:
                    thresh = cv2.inRange(hsv, colordic[d][0], colordic[d][1])
                break
        thresh = self.postprocessMorphology(thresh)

        # cv2.imshow(d, thresh)
        # cv2.waitKey(0)

        return img, thresh, hsv

    def getAvgHsv(self, hsv, cX, cY):
        w = 50
        minx = cX - w
        miny = cY - w
        avg_tmp = 0
        for i in range(0, 100):
            for j in range(0, 100):
                avg_tmp = avg_tmp + hsv[miny + i, minx + j][0]
        # print(avg_tmp)
        avg_tmp = avg_tmp / 10000
        avg_h = avg_tmp
        return avg_h

    def avg_cal(self, img, thresh, hsv):
        h, w, ch = img.shape
        area = (thresh / 255).sum()
        all_pixel = w * h
        img_no_background = []
        img_no_background_h = thresh / 255 * hsv[:, :, 0]
        img_no_background_s = thresh / 255 * hsv[:, :, 1]
        img_no_background_v = thresh / 255 * hsv[:, :, 2]
        avg_h = np.round(np.mean(img_no_background_h) * all_pixel / area, 2)
        avg_s = np.round(np.mean(img_no_background_s) * all_pixel / area, 2)
        avg_v = np.round(np.mean(img_no_background_v) * all_pixel / area, 2)

        # img_no_background.append([avg_h, avg_s, avg_v])
        return [avg_h, avg_s, avg_v]

    def judgethresh(self, color, avg, pre_cnt_num, c):
        color_min = color + '_min'
        color_max = color + '_max'
        if cfg.color_threshold[color_min][0] < avg[0] < cfg.color_threshold[color_max][0] and  \
            cfg.color_threshold[color_min][1] < avg[1] < cfg.color_threshold[color_max][1] and \
            cfg.color_threshold[color_min][2] < avg[2] < cfg.color_threshold[color_max][2]:
                self.cnts.append(c)
                cv2.drawContours(self.image, [c], -1, (0, 255, 0), 1)
                return True
        else:
            return False

    def areathresh(self, area, color):  # 面积过滤
        if cfg.area_thresh[color] < area:
            return True
        else:
            return False

    def getContours(self, color):
        """寻找轮廓并粗略过滤"""
        self.image, thresh, hsv = self.getColorPart(color)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        # cnt 表示轮廓上的所有点
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        pre_cnt_num =0
        avg_all = []
        for c in cnts:
            area = cv2.contourArea(c)
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            if self.areathresh(area, color):   # 对区域进行初步筛选，过滤掉一些很小的
                if self.id == 0:
                    x, y, w, h = cv2.boundingRect(c)  # offsets - with this you get 'mask'
                    part = self.image[y:y + h, x:x + w]
                    part_img, part_thresh, part_hsv = self.getColorPart2(color, part)
                    # cv2.imshow("thresh", part_thresh)
                    # cv2.waitKey(0)®
                    avg = self.avg_cal(part_img, part_thresh, part_hsv)
                    print(avg)
                    f = self.judgethresh(color, avg, pre_cnt_num, c)
                # if f:
                #     print("color:{0},area:{1}".format(color, area))
                else:
                    self.cnts.append(c)
                    cv2.drawContours(self.image, [c], -1, (0, 255, 0), 1)
            else:
                pass
        self.cnt_num = len(self.cnts)
        # for c in self.cnts:
        #     cv2.drawContours(self.image, [c], -1, (255, 255, 0), 1)
        # cv2.imshow("getContours01", self.image)
        # cv2.waitKey(0)
        return self.image

    def getAccurateContours(self, color):
        """获取第一阶段处理结果（上述操作的总和）"""
        self.getContours(color)

        return self.image


class ShapeRecognition(ColorContourRecognition):
    """该类继承ColorShapeRecognition,在颜色处理的基础上，进一步进行形状判别
        完成以下操作：
        1. 轮廓逼近
        2. 获取一个轮廓逼近得到的角点
        3. 为图形框出最小矩形
        4. 根据一个轮廓来判断形状
        5. 第二阶段，根据形状过滤掉一部分轮廓
        6. 第三阶段，对颜色、形状相同的轮廓根据尺寸来进行最后一步筛选
        7. 三个阶段完整的识别过程
        """

    def __init__(self, id, img):
        self.shape = ''
        self.vertex = []
        self.hypotenusAngle = 0
        self.centerVector = (0, 0)
        ColorContourRecognition.__init__(self, id, img)

    def getDeviationAngle(self):
        """ 返回斜边角度 """
        p = Point(0, 0)
        slope = p.getSlope(self.vertex[0], self.vertex[1], self.id, 10)
        self.hypotenusAngle = p.angle(slope)

        return self.hypotenusAngle



    def getApprox(self, cnt):  # 轮廓逼近

        epsilon = 0.08 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)  # 得到逼近的顶点

        return approx

    def getPreVertex(self, cnt):
        """获取一个轮廓逼近得到的角点"""
        tempVertexs = []
        approx = self.getApprox(cnt)
        corners = len(approx)   # 分析顶点数

        if corners == 3 or corners == 4:
            for cornerIndex in range(0, corners):
                singleTempVertex = Point(approx[cornerIndex][0][0], approx[cornerIndex][0][1])
                tempVertexs.append(singleTempVertex)
                cv2.circle(self.image,
                           (tempVertexs[cornerIndex].x, tempVertexs[cornerIndex].y), 2,
                           (255, 0, 0), 2)
        else:
            for cornerIndex in range(0, corners):
                singleTempVertex = Point(approx[cornerIndex][0][0], approx[cornerIndex][0][1])
                tempVertexs.append(singleTempVertex)
                cv2.circle(self.image,
                           (tempVertexs[cornerIndex].x, tempVertexs[cornerIndex].y), 2,
                           (255, 0, 0), 2)
            pass  # tempVertexs为空
        return tempVertexs, approx

    def getMinRect(self, approx):
        """为图形框出最小矩形"""
        rect = cv2.minAreaRect(approx)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        w = rect[1][0]
        h = rect[1][1]
        wh_ratio = w / float(h)  # 计算长宽比
        # cv2.drawContours(self.image, [box], 0, (0, 0, 255), 2)
        return box, rect, wh_ratio

    def shapeAlysis(self, cnt):
        """根据一个轮廓来判断形状"""
        tempVertexs, approx = self.getPreVertex(cnt)
        if tempVertexs == []:  # 轮廓不是三个顶点或四个顶点时
            self.shape = 'none'
        else:
            corners = len(tempVertexs)
            # print("corners",corners)
            p = Point(0, 0)
            if corners == 4:
                box, rect, wh_ratio = self.getMinRect(approx)
                # print("wh",wh_ratio)
                if 0.7 <= wh_ratio <= 2.0:
                    self.shape = 'square'
                    tempVertexs,isError = p.numberVertexuadrangle(0, tempVertexs, box)
                    if isError == -1:
                        self.shape = 'none'
                        return tempVertexs, self.shape
                else:  # 根据两组对边平行的四边形是平行四边形
                    tempVertexs,isError = p.numberVertexuadrangle(1, tempVertexs, box)
                    # print("isError",isError)
                    if isError == -1:
                        self.shape = 'none'
                        return tempVertexs,self.shape
                    # print("temp",tempVertexs)
                    if p.parallelogramJudge(tempVertexs):
                        self.shape = 'parallelogram'  # 不要忘记考虑False的情况
                    else:
                        print("dsl")
                        self.shape = 'none'
            else:
                tempVertexs = p.numberVertexTriangle(tempVertexs)  # 对三角形进行编号
                if p.triangleJudge(tempVertexs):
                    self.shape = 'triangle'  # 不要忘记考虑False的情况
                else:
                    self.shape = 'none'
            # 测试编号是否正确
            # for i in range(0, len(tempVertexs)):
            #     cv2.putText(self.image, str(i), (tempVertexs[i].x, tempVertexs[i].y),
            #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        # print("shape",self.shape)
        return tempVertexs, self.shape


    def preliminarynalysis(self, shapeGoal):
        """ 第二阶段，根据形状过滤掉一部分轮廓"""
        tempVertexsfiltered = []
        tempCnt = []
        k = 0
        # for i in range(0,len(self.cnts)):
        # tempCnt = self.cnts

        while k < len(self.cnts):
            c = self.cnts[k]
            tempVertexs, shapeTemp = self.shapeAlysis(c)
            print("第二次过滤，形状：", shapeTemp)
            k += 1
            if shapeTemp == 'none':
                print("形状为空")
                continue
            if shapeTemp == shapeGoal:
                tempCnt.append(c)
                tempVertexsfiltered.append(tempVertexs)
                # cv2.drawContours(self.image, [c], -1, (0, 0, 255), 1)
                # for i in range(0, len(tempVertexs)):
                #     cv2.putText(self.image, str(i), (tempVertexs[i].x, tempVertexs[i].y),
                #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

        self.cnts = []
        self.cnts = tempCnt
        self.cnt_num = len(self.cnts)
        # cv2.imshow("filteredImage", self.image)
        # cv2.waitKey(0)
        return tempVertexsfiltered, self.image

    def ultimateFilter(self, colorGoal, shapeGoal):
        """最后一步筛选，当出现两个轮廓，形状、颜色均相同时"""
        temVertex, _ = self.preliminarynalysis(shapeGoal)
        goalIndex = 0
        index_temp = []
        if self.cnt_num == 1:
            pass
        elif self.cnt_num == 0:
            print("没有检测到轮廓！")
            # exit()
        else:  # 针对粉色和紫色、红色和橙色
            print("before self.cntnum",self.cnt_num)
            goalArea = cv2.contourArea(self.cnts[0])
            # 针对粉色和紫色，目标一定是多个轮廓中面积最大的一个
            if colorGoal == 'pink' or colorGoal == 'purple' or colorGoal == 'orange':
                if colorGoal == 'purple':
                    image_temp = self.image
                    real_temp = ShapeRecognition(0, image_temp)
                    real_temp.getContours('pink')
                    # print("this is real_temp", real_temp.cnts)
                    cnts_temp= []
                    vertex_temp= []
                    M_temp = cv2.moments(real_temp.cnts[0])
                    cX_temp = int(M_temp["m10"] / M_temp["m00"])
                    cY_temp = int(M_temp["m01"] / M_temp["m00"])
                    for cntIndex in range(0, self.cnt_num):
                        M = cv2.moments(self.cnts[cntIndex])
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        if abs(cX-cX_temp) <= 10 and abs(cY-cY_temp) <= 10:
                            print("pass...")
                            pass
                        else:
                            print("this is cntindex",cntIndex)
                            index_temp.append(cntIndex)
                elif colorGoal == 'pink':
                    image_temp = self.image
                    real_temp = ShapeRecognition(0, image_temp)
                    real_temp.getContours('purple')
                    # print("this is real_temp", real_temp.cnts)
                    cnts_temp = []
                    vertex_temp = []
                    M_temp = cv2.moments(real_temp.cnts[0])
                    cX_temp = int(M_temp["m10"] / M_temp["m00"])
                    cY_temp = int(M_temp["m01"] / M_temp["m00"])
                    for cntIndex in range(0, self.cnt_num):
                        M = cv2.moments(self.cnts[cntIndex])
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        if abs(cX - cX_temp) <= 10 and abs(cY - cY_temp) <= 10:
                            print("pass...")
                            pass
                        else:
                            print("this is cntindex", cntIndex)
                            index_temp.append(cntIndex)
                if len(index_temp) > 1:
                    print("self.cnt_num>1")
                    for cntIndex in index_temp:
                        area = cv2.contourArea(self.cnts[cntIndex])
                        if area >= goalArea:
                            goalArea = area
                            goalIndex = cntIndex
                elif len(index_temp) == 1:
                    goalIndex = index_temp[0]
                else:
                    pass

            elif colorGoal == 'red':
                for cntIndex in range(0, self.cnt_num):
                    area = cv2.contourArea(self.cnts[cntIndex])
                    if area <= goalArea:
                        goalArea = area
                        goalIndex = cntIndex
                    else:
                        pass

            else:
                print('ultimateFilter:', colorGoal, ' : 出错！！')
                pass

            tempCnt = self.cnts[goalIndex]
            self.cnts = []
            self.cnts.append(tempCnt)
            self.cnt_num = len(self.cnts)


        if self.cnt_num == 1:
            self.vertex = temVertex[goalIndex]  # 获取最终排序好的顶点
            c = self.cnts[0]
            cv2.drawContours(self.image, [c], -1, (0, 0, 0), 1)
            # for i in range(0, 3):
            #     cv2.putText(self.image, str(i), (self.vertex[i].x, self.vertex[i].y),
            #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
            y, x = self.image.shape[:2]
            centerImage = (x / 2, y / 2)  # 图像中心点
            M = cv2.moments(self.cnts[0])
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            self.centerP.x = cX
            self.centerP.y = cY
            cv2.circle(self.image,(cX,cY),1,(255,0,0),1)
            self.centerVector = (centerImage[0] - cX, centerImage[1] - cY)  # 位移矢量
            self.getDeviationAngle()  # 计算斜边角度
        else:
            cv2.imwrite('images/template/wrong.jpg', self.image)
            print("最终轮廓数：", self.cnt_num)

            # exit()

        cv2.imshow("FinallyImage", self.image)
        cv2.waitKey(0)

        return self.centerVector


    def completeRecognition(self, colorGoal, shapeGoal):
        """ 完整的识别过程"""
        self.getAccurateContours(colorGoal)  # 第一次简单过滤掉很小的区域
        self.preliminarynalysis(shapeGoal)   # 第二次根据形状过滤
        self.ultimateFilter(colorGoal, shapeGoal)  # 第三次根据面积过滤


class Rotate:

    def __init__(self):

        self.rotateAngle = 0

    def getRotateAngle(self, capImage, mouldImage, shapeGoal):
        """ 获取旋转角度 """
        deviationAngle = capImage.hypotenusAngle - mouldImage.hypotenusAngle
        print("capImage hypotenusAngle:", capImage.hypotenusAngle)
        print("mould hypotenusAngle:", mouldImage.hypotenusAngle)
        print("deviationAngle:", deviationAngle)
        self.rotateAngle = deviationAngle
        overturnFlag = self.whetherOverturn(capImage, mouldImage, shapeGoal)  # 是否需要翻转，True翻转
        if overturnFlag:

            # self.rotateAngle = deviationAngle + 180
            if deviationAngle > 0:
                """1. a-b>0 同时需要翻转"""
                deviationAngle = 180 - deviationAngle
            else:
                """2. a-b<0 同时需要翻转"""
                deviationAngle = 180 + deviationAngle
                overturnFlag = False

        """
        3. a-b<0 不需要翻转 逆时针
        4. a-b>0 不需要翻转 顺时针
        """
        self.rotateAngle = (deviationAngle, overturnFlag)

        return self.rotateAngle

    def whetherOverturn(self, capImage, mouldImage, shapeGoal):
        """ 判断是否需要翻转"""
        overturnFlag = False

        if shapeGoal == 'triangle':
            self.rotate(3, capImage)

            if 0 <= mouldImage.hypotenusAngle <= 45 or 135 <= mouldImage.hypotenusAngle <= 180:
                if (capImage.vertex[2].y < capImage.centerP.y and mouldImage.vertex[2].y < mouldImage.centerP.y) or (
                        capImage.vertex[2].y > capImage.centerP.y and mouldImage.vertex[2].y > mouldImage.centerP.y):
                    pass
                else:
                    overturnFlag = True
            elif 45 < mouldImage.hypotenusAngle <= 90 or 90 < mouldImage.hypotenusAngle < 135:
                if (capImage.vertex[2].x < capImage.centerP.x and mouldImage.vertex[2].x < mouldImage.centerP.x) or (
                        capImage.vertex[2].x > capImage.centerP.x and mouldImage.vertex[2].x > mouldImage.centerP.x):
                    pass
                else:
                    overturnFlag = True

        return overturnFlag



    def rotate(self, numVertex, image):

        rotateAngle = self.rotateAngle
        if rotateAngle < 0:
            rotateAngle = abs(rotateAngle)
            rotateAngle = math.radians(rotateAngle)
            rotateAngle = -1 * rotateAngle
        elif rotateAngle > 0:
            rotateAngle = math.radians(rotateAngle)

        for vertexIndex in range(0, numVertex):
            image.vertex[vertexIndex] = self.rotatePoint(image.vertex[vertexIndex], image.centerP, rotateAngle)


        return image.vertex


    def rotatePoint(self, p, pCenter, theta):
        """ 某一点逆时针旋转theta（弧度）"""
        pRotated = Point(0, 0)
        pRotated.x = pCenter.x + (p.x - pCenter.x) * math.cos(theta) - (p.y - pCenter.y) * math.sin(theta)
        pRotated.y = pCenter.y + (p.x - pCenter.x) * math.sin(theta) + (p.y - pCenter.y) * math.cos(theta)
        return pRotated


def select(real_image):
    for i in range(0, 1):
        if i == 0:
            colorGoal = 'pink'
            shapeGoal = 'triangle'
        elif i == 1:
            colorGoal = 'red'
            shapeGoal = 'triangle'
        elif i == 2:
            colorGoal = 'orange'
            shapeGoal = 'triangle'
        elif i == 3:
            colorGoal = 'yellow'
            shapeGoal = 'parallelogram'
        elif i == 4:
            colorGoal = 'green'
            shapeGoal = 'triangle'
        elif i == 5:
            colorGoal = 'blue'
            shapeGoal = 'square'
        elif i == 6:
            colorGoal = 'purple'
            shapeGoal = 'triangle'
        # print(colorGoal)
        # mould = ShapeRecognition(1, mould_image)
        # mould.completeRecognition(colorGoal, shapeGoal)
        real = ShapeRecognition(0, real_image)
        real.completeRecognition(colorGoal, shapeGoal)
        # print('mould vector:', mould.centerVector)
        # print('real vector:', real.centerVector)
        # rotate = Rotate()
        # angle = rotate.getRotateAngle(real, mould, shapeGoal)
        # print(colorGoal + " angle", angle)
    # cv2.imwrite("images/results/1.jpg", real.getImage())
    # return image
def testCamera():
    cto = 1
    if cto == 0:
        """ 摄像头测试 """
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
        print('启动摄像头...')
        # return cap
        ret, real_image = cap.read()
    elif cto == 1:
        for i in range(59,60):
            print(i)
            path = "images/catching/" + str(i)+".jpg"
        #     # # path = '/Users/xiaoxiao/Desktop/七巧板/图像采集/20190121201529/'+str(i)+'.jpg'
        #     # print(path)
            real_image = cv2.imread(path)
            select(real_image)





if __name__ == '__main__':
    testCamera()