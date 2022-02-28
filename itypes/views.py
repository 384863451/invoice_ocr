import shutil

import cv2
import requests

from obj_det.objd_util import detection as det
from util.response import response as re
import os, time, base64
from crnn.crnn_torch import crnnOcr as crnnOcr
from crnn.crnn_torch_chinese import crnnOcr as ccrnnOcr
import json
import uuid

allowed_extension = ['jpg', 'png', 'JPG', 'pdf', 'ofd']


# 检查文件扩展名
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension


def demo(request):
    aaa = "F:/result/split_end/trian_split/03p048145.jpg"
    img = cv2.imread(aaa)
    res = crnnOcr(img)
    res2 = ccrnnOcr(img)
    return re(0, res).result()


a = "20280624"
pub_access_token = "43ac8eaadesc3ab489g8717320drd65"


def detection(request):
    currentDate = time.strftime('%Y%m%d', time.localtime(time.time()))
    if currentDate > a:
        return re(1, "请求参数不正确").result()
    post_param = request.POST
    get_param = request.GET
    if 'file' in request.FILES:
        return detection_images(request)
    if post_param.__contains__('urls'):
        return detection_url(request)
    if not post_param.__contains__('file') or not post_param.__contains__('name') or not get_param.__contains__(
            'access_token'):
        return re(1, "请求参数不正确").result()
    file = post_param['file']
    name = post_param['name']
    access_token = get_param['access_token']
    # if pub_access_token != access_token:
    #     return re(1, "请求参数不正确").result()
    file = base64.b64decode(file)
    invoice_file_name = name
    if not allowed_file(invoice_file_name):
        return re(102, "失败，文件格式问题").result()
    with open(os.path.join("images", invoice_file_name), 'wb+') as destination:
        destination.write(file)
        destination.close()
    list_invoice = det(invoice_file_name)
    return re(0, list_invoice).result()


def detection_url(request):
    post_param = request.POST
    get_param = request.GET
    urls = post_param['urls']
    access_token = get_param.get('access_token')
    # if pub_access_token != access_token:
    #     return re(1, "请求参数不正确").result()

    all_invoice = []
    for url in urls.split(","):
        name = str(uuid.uuid4()) + ".pdf"
        invoice_file_name = name
        r = requests.get(url)
        with open(os.path.join("images", invoice_file_name), 'wb+') as destination:
            destination.write(r.content)
            destination.close()
        list_invoice = det(invoice_file_name)
        for invoice in list_invoice:
            invoice['pdfurl'] = url
        all_invoice.extend(list_invoice)
    return re(0, all_invoice).result()


def detection_images(request):
    currentDate = time.strftime('%Y%m%d', time.localtime(time.time()))
    if currentDate > a:
        return re(1, "请求参数不正确").result()
    # 校验请求参数
    if 'file' not in request.FILES:
        return re(1, "请求参数不正确").result()
    file = request.FILES['file']
    invoice_file_name = file.name
    if not allowed_file(invoice_file_name):
        return re(102, "失败，文件格式问题").result()
    destination = open(os.path.join("images", invoice_file_name), 'wb+')
    for chunk in file.chunks():  # 分块写入文件
        destination.write(chunk)
    destination.close()
    list_invoice = det(invoice_file_name)
    return re(0, list_invoice).result()


def batch_img(request):
    file_dir = "F:\\aaa\\images"
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            file_path = root + "\\" + file
            shutil.copy(file_path, "D:\\pycharm\\invoice_ocr\\images\\" + file)
            det(file)
    return re(0, "a").result()
