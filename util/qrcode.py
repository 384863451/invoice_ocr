import cv2
import zxing as zxing
import uuid
from obj_det.detect import converter as multype


def qrcode(img, invoice):
    try:
        id = uuid.uuid4()
        path = "images/qrcode/" + str(id) + ".jpg"
        h, w, _ = img.shape
        newimage = cv2.resize(img, (w * 2, h * 2), cv2.INTER_LINEAR)
        cv2.imwrite(path, newimage)
        reader = zxing.BarCodeReader()
        barcode = reader.decode(path)
        data = barcode.parsed
        datas = data.split(",")
        if datas[2] != '' and datas[2] != None:
            invoice['invoice_code'] = datas[2]
        if datas[3] != '' and datas[3] != None:
            invoice['invoice_number'] = datas[3]
        if datas[4] != '' and datas[4] != None:
            invoice['totalAmount'] = "￥" + datas[4]
        if datas[5] != '' and datas[5] != None:
            invoice['billingDate'] = datas[5][0:4] + "年" + datas[5][4:6] + "月" + datas[5][6:8] + "日"
        if datas[1] == "04" or datas[1] == "10" or datas[1] == "11":
            invoice['checkCode'] = datas[6]
        if invoice['invoiceType'] != "14":
            invoice['invoiceType'] = datas[1]
            invoice['invoice_type_name'] = multype[datas[1]]
        return True
    except Exception as e:
        print("二维码未识别" + str(e))
        return False


def qrcode_no_tax(img, invoice):
    try:
        img = cv2.resize(img, (300, 300))
        id = uuid.uuid4()
        path = "images/qrcode/" + str(id) + ".jpg"
        cv2.imwrite(path, img)
        reader = zxing.BarCodeReader()
        barcode = reader.decode(path)
        data = barcode.parsed
        if "http" in data:
            paramOrg = data.split("?")[1]
            param_2s = paramOrg.split("&")
            for param_2 in param_2s:
                param = param_2.split("=")
                invoice[param[0]] = param[1]
        return True
    except Exception as e:
        print("二维码未识别" + str(e))
        return False
