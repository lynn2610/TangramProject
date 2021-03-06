#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/8 12:12
# @Author  : Lynn
# @Site    : 
# @File    : run.py
# @Software: PyCharm

from decision import *

def main():
    """
    测试机器人逐步逼近目标。

    返回值：
    ----------
    :return: None
    """
    # assistant.delete_image('images/catching/')
    assistant.save_collected_images('images/catching/')
    start = time.time()
    # 7,33,61
    e_image_path = 'images/mould/61.jpg';
    e_image = cv2.imread(e_image_path)
    decesion = Decision(e_image)  # 传入电子图
    #

    result_path = 'res/res_imgs/' + e_image_path.split('/')[-1]

    e_image_module.set_stack(e_image)

    decesion.do_puzzles()

    # if len(SET) == 7:
    #     decesion.get_datas(result_path)
    # else:
    #     print("LEN SIZE : ", len(SET))

    print('end!!!')
    end = time.time()
    print('time: {}'.format(int(end - start)))


if __name__ == '__main__':
    main()
