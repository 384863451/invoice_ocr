from obj_det.detect import invoice_detection as det
from obj_det.tra_detect import invoice_detection as tra
from obj_det.vat_detect import invoice_detection as vat
from obj_det.taxi_detect import invoice_detection as taxi
from obj_det.roll_detect import invoice_detection as roll
from obj_det.title_detect import invoice_detection as title
from obj_det.evat_detect import invoice_detection as evat
from obj_det.no_tax_detect import invoice_detection as noVat
from single_ocr.opencv_direction import angle_detect_dnn
from crnn.crnn_torch import crnnOcr as crnnOcr
from crnn.crnn_torch_chinese import crnnOcr as ccrnnOcr


class TextOcrModel(object):
    def __init__(self):
        self.ocrModel = crnnOcr
        self.chineseModel = ccrnnOcr
        self.textModel = None
        self.angleModel = angle_detect_dnn
        self.det = det
        self.tra = tra
        self.vat = vat
        self.taxi = taxi
        self.roll = roll
        self.title = title
        self.evat = evat
        self.noVat = noVat


context = TextOcrModel()
