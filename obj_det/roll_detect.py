import numpy as np
import time
from pathlib import Path
import os

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_imshow, non_max_suppression, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging
from utils.torch_utils import select_device, time_synchronized
import hashlib
from crnn.crnn_torch_chinese import crnnOcr as ccrnnOcr
from util.qrcode import qrcode
import threading
from util.create_img import no_tax
from util.create_img import use

lock = threading.Lock()
converter = {'invoice_code': 'invoice_code', 'invoice_number': 'invoice_number', 'totalAmount': 'totalAmount',
             'billingDate': 'billingDate', 'checkcode': 'checkCode',
             'QRCode': 'QRCode', 'title': 'title'}
pub_weights = "models/roll/best.pt"
pub_view_img = False
pub_save_txt = False
pub_img_size = 640
pub_nosave = False
pub_project = "images"
pub_device = "cpu"
pub_augment = False
pub_conf_thres = 0.25
pub_iou_thres = 0.24
pub_classes = None
pub_agnostic_nms = False
pub_save_conf = False

# Initialize
set_logging()
device = select_device(pub_device)
half = device.type != 'cpu'  # half precision only supported on CUDA

# Load model
model = attempt_load(pub_weights, map_location=pub_device)  # load FP32 model
stride = int(model.stride.max())  # model stride
imgsz = check_img_size(pub_img_size, s=stride)  # check img_size
if half:
    model.half()  # to FP16


def invoice_detection(file_name=None, invoice=None):
    uid = hashlib.md5(file_name.encode("utf8")).hexdigest()
    i = 0
    qrData = ""
    pub_source = file_name
    source, weights, view_img, save_txt, imgsz = pub_source, pub_weights, pub_view_img, pub_save_txt, pub_img_size
    save_img = True
    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))

    # Directories
    save_dir = Path(pub_project)  # increment run

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = check_imshow()
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz, stride=stride)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
    t0 = time.time()
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        lock.acquire(timeout=3)
        # Inference
        pred = model(img, augment=pub_augment)[0]
        lock.release()

        # Apply NMS
        pred = non_max_suppression(pred, pub_conf_thres, pub_iou_thres, classes=pub_classes, agnostic=pub_agnostic_nms)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
                p, s, im0, frame = path[i], '%g: ' % i, im0s[i].copy(), dataset.count
            else:
                p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # img.jpg
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # img.txt
            s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if pub_save_conf else (cls, *xywh)  # label format
                        with open(txt_path + '.txt', 'a') as f:
                            f.write(('%g ' * len(line)).rstrip() % line + '\n')

                    orgfilename = file_name.rsplit('.', 1)[0].lower()
                    orgfilename = orgfilename.rsplit('/', 1)[1]
                    if save_img or view_img:  # Add bbox to image
                        label = names[int(cls)]
                        newimg = im0[int(xyxy[1]):int(xyxy[3]), int(xyxy[0]): int(xyxy[2])]
                        i = i + 1
                        if "QRCode" == label:
                            qrData = newimg
                        invoice[converter[label]] = ccrnnOcr(newimg)
                        if use == 1:
                            no_tax(label, newimg, invoice[converter[label]])
    for val in converter.values():
        if invoice.get(val) is None:
            invoice[val] = "0"
    qrcode(qrData, invoice)
    return invoice
