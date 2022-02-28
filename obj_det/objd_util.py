import cv2
import time
import fitz
import threading
from util.ofd_util import get_info
from obj_det.ocr_context import context

lock = threading.Lock()

allowed_extension = ['jpg', 'png', 'JPG', 'pdf', 'ofd']
image_extension = ['jpg', 'png', 'JPG']
pdf_extension = ['pdf']
ofd_extension = ['ofd']

vat_names = ['01', '04']
e_vat_names = ['08', '10', '14']
tra_names = ['88']
taxi_names = ['92']
roll_names = ['11']
no_tax_names = ['81']


# 检查文件扩展名
def allowed_file(filename, type_extension):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in type_extension


def time_synchronized():
    return time.time()


def rotate(img, invoice):
    angle = context.angleModel(img)
    if angle != 0:
        index = 3 - angle / 90
        img = cv2.rotate(img, int(index))
        cv2.imwrite(invoice['file_path'], img)


def process_image(file_name):
    result = []
    list_invoice = context.det(file_name)
    for invoice in list_invoice:
        invoice_type = invoice['invoiceType']
        img = cv2.imread(invoice['file_path'])
        rotate(img, invoice)
        if str(invoice_type) in vat_names or str(invoice_type) in e_vat_names:
            context.title(file_name=invoice['file_path'], invoice=invoice)
            invoice_type = invoice['invoiceType']
        if str(invoice_type) in tra_names:
            context.tra(file_name=invoice['file_path'], invoice=invoice)
            result.append(invoice)
        if str(invoice_type) in vat_names:
            context.vat(file_name=invoice['file_path'], invoice=invoice, context=context)
            result.append(invoice)
        if str(invoice_type) in e_vat_names:
            context.evat(file_name=invoice['file_path'], invoice=invoice, context=context)
            result.append(invoice)
        if str(invoice_type) in taxi_names:
            context.taxi(file_name=invoice['file_path'], invoice=invoice)
            result.append(invoice)
        if str(invoice_type) in roll_names:
            context.roll(file_name=invoice['file_path'], invoice=invoice)
            result.append(invoice)
        if str(invoice_type) in no_tax_names:
            context.noVat(file_name=invoice['file_path'], invoice=invoice, context=context)
            result.append(invoice)
    return result


def process_pdf(file_name):
    #  打开PDF文件，生成一个对象
    doc = fitz.open("images/" + file_name)
    name = file_name.split(".")[0]
    result = []
    for pg in range(doc.pageCount):
        file_name = name + str(pg)
        page = doc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为2，这将为我们生成分辨率提高四倍的图像。
        zoom_x = 2.0
        zoom_y = 2.0
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pm = page.getPixmap(matrix=trans, alpha=False)
        pm.writePNG('images/%s.png' % file_name)
        file_name_curr = '%s.png' % file_name
        invoices = process_image(file_name_curr)
        result.extend(invoices)
    return result


def process_ofd(file_name):
    result = get_info("images/" + file_name, "images/zip" + file_name.split(".")[0])
    invoices = []
    checkcode = result.get('校验码')
    invoiceType = '10'
    invoice_type_name = '增值税电子普通发票'
    if checkcode == '' or checkcode is None:
        invoiceType = '08'
        invoice_type_name = '增值税电子专用发票'
    invoice = {"invoiceType": invoiceType, "invoice_type_name": invoice_type_name, "file_path": 'demo',
               "coordinate": [], 'invoice_code': result['发票代码'], 'invoice_number': result['发票号码'],
               'totalAmount': result['合计金额'], 'billingDate': result['开票日期'],
               'checkCode': result['校验码'].replace(" ", "")}

    invoices.append(invoice)
    return invoices


def detection(file_name):
    if allowed_file(file_name, image_extension):
        return process_image(file_name)
    if allowed_file(file_name, pdf_extension):
        return process_pdf(file_name)
    if allowed_file(file_name, ofd_extension):
        return process_ofd(file_name)
