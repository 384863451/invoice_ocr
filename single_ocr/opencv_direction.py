import cv2
import os
import numpy as np
import threading

lock = threading.Lock()

pwd = os.getcwd()
AngleModelPb = os.path.join(pwd, "models", "saved_model.pb")
AngleModelPbtxt = os.path.join(pwd, "models", "saved_model.pbtxt")
angleNet = cv2.dnn.readNetFromTensorflow(AngleModelPb,AngleModelPbtxt)##dnn 文字方向检测

def angle_detect_dnn(img, adjust=True):
    """
    文字方向检测
    """
    h, w = img.shape[:2]
    ROTATE = [0, 90, 180, 270]
    if adjust:
        thesh = 0.05
        xmin, ymin, xmax, ymax = int(thesh * w), int(thesh * h), w - int(thesh * w), h - int(thesh * h)
        img = img[ymin:ymax, xmin:xmax]  ##剪切图片边缘

    inputBlob = cv2.dnn.blobFromImage(img,
                                      scalefactor=1.0,
                                      size=(224, 224),
                                      swapRB=True,
                                      mean=[103.939, 116.779, 123.68], crop=False)
    lock.acquire(timeout=30)
    angleNet.setInput(inputBlob)
    pred = angleNet.forward()
    lock.release()
    index = np.argmax(pred, axis=1)[0]
    return ROTATE[index]