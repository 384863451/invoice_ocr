import cv2
import random
import os

use = 0

def no_tax(label, img, res):
    if res is None:
        res = ""
    if ":" in res:
        res = ""
    dir = "F:\\crnn_demo"
    ran = round(random.uniform(0, 10000), 2)
    if not os.path.exists(dir + "\\" + label):
        os.makedirs(dir + "\\" + label)
    cv2.imencode('.png', img)[1].tofile(dir + "\\" + label + "\\" + res + "_" + str(ran) + ".png")