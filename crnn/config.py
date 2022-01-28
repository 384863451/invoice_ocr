import os

pwd = os.getcwd()
GPU = False
ocrModel_chinese = os.path.join(pwd,"models", "ocr-lstm.pth")
ocrModel = os.path.join(pwd,"models", "ocr-english.pth")
