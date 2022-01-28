#coding:utf-8
import torch
import numpy as np
from torch.autograd import Variable 
from crnn.utils import strLabelConverter, resizeNormalize
from crnn.network_torch import CRNN
from crnn import keys
from collections import OrderedDict
from crnn.config import ocrModel_chinese, GPU
from PIL import Image
import cv2
import threading

lock = threading.Lock()
def crnnSource():
    """
    加载模型
    """
    alphabet = keys.alphabetChinese##中英文模型
        
    converter = strLabelConverter(alphabet)
    model = CRNN(32, 1, len(alphabet)+1, 256, 1,lstmFlag=True).cpu()
    
    trainWeights = torch.load(ocrModel_chinese,map_location=lambda storage, loc: storage)
    modelWeights = OrderedDict()
    for k, v in trainWeights.items():
        name = k.replace('module.','') # remove `module.`
        modelWeights[name] = v
    # load params
  
    model.load_state_dict(modelWeights)

    return model,converter

##加载模型
model,converter = crnnSource()
model.eval()
def crnnOcr(image):
       """
       crnn模型，ocr识别
       image:PIL.Image.convert("L")
       """
       pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
       image = pil_img.convert('L')
       scale = image.size[1]*1.0 / 32
       w = image.size[0] / scale
       w = int(w)
       transformer = resizeNormalize((w, 32))
       image = transformer(image)
       image = image.astype(np.float32)
       image = torch.from_numpy(image)
       
       if torch.cuda.is_available() and GPU:
           image   = image.cuda()
       else:
           image   = image.cpu()
            
       image       = image.view(1,1, *image.size())
       image       = Variable(image)
       lock.acquire(timeout=3)
       preds       = model(image)
       lock.release()
       _, preds    = preds.max(2)
       preds       = preds.transpose(1, 0).contiguous().view(-1)
       sim_pred    = converter.decode(preds)
       return sim_pred
       

