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
import threading

lock = threading.Lock()

converter = {'01':'增值税专用发票', '04': '增值税普通发票', '08': '增值税电子专用发票', '10': '增值税电子普通发票', '11': '增值税普通发票（卷式）', '81': '非税财政电子票据', '86': '过路费发票', '88': '火车票', '89': '飞机票', '90':'客运票', '92':'出租车票', '93':'定额', '95':'通用机打发票'}
pub_weights = "models/mutipart/best.pt"
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


def invoice_number_process(img):
    height, width, _ = img.shape
    for i in range(height):
        for j in range(width):
            dot = img[i, j]
            dot0 = dot[0]
            dot1 = dot[1]
            dot2 = dot[2]
            if dot2 < dot1 or dot2 < dot0:
                img[i, j] = [0, 0, 0]
                continue
    return img


def invoice_detection(file_name=None):
    i = 0
    invoices = []
    pub_source = "images/" + file_name
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

        # Inference
        lock.acquire(timeout=3)
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
                    type = file_name.rsplit('.', 1)[1].lower()
                    if save_img or view_img:  # Add bbox to image
                        label = names[int(cls)]
                        newimg = im0[int(xyxy[1]):int(xyxy[3]), int(xyxy[0]): int(xyxy[2])]
                        dir = "images/" + orgfilename
                        if not os.path.exists(dir):
                            os.makedirs(dir)
                        newPath = dir + "/" + str(i) + "_" + orgfilename + "." + type
                        cv2.imwrite(newPath, newimg)
                        i = i + 1
                        coordinate = [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3]), int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])]
                        json = {"invoiceType": label, "invoice_type_name": converter[label], "file_path": newPath, "coordinate": coordinate}
                        invoices.append(json)
    return invoices
