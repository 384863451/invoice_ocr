# -*- coding:utf-8 -*-
import time,os.path,requests,re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams,LTTextBoxHorizontal,LTImage,LTCurve,LTFigure
from pdfminer.pdfpage import PDFTextExtractionNotAllowed,PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from docx import Document
import fitz
document = Document()

'''
pip install pdfminer3k
pip install pdfminer.six 安装这个引入的内容不会报错
'''

class CPdf2TxtManager():

    def changePdfToText(self, filePath):
        res = {"state": 0}
        context = ""
        # 以二进制读模式打开
        file = open(filePath, 'rb')
        #用文件对象来创建一个pdf文档分析器
        praser = PDFParser(file)
        # 创建一个PDF文档对象存储文档结构,提供密码初始化，没有就不用传该参数
        doc = PDFDocument(praser, password='')
        ##检查文件是否允许文本提取
        if not doc.is_extractable:
            raise PDFTextExtractionNotAllowed

        # 创建PDf 资源管理器 来管理共享资源，#caching = False不缓存
        rsrcmgr = PDFResourceManager(caching = False)
        # 创建一个PDF设备对象
        laparams = LAParams()
        # 创建一个PDF页面聚合对象
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解析器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # 获得文档的目录（纲要）,文档没有纲要会报错
        #PDF文档没有目录时会报：raise PDFNoOutlines  pdfminer.pdfdocument.PDFNoOutlines
        # print(doc.get_outlines())

        # 获取page列表
        print(PDFPage.get_pages(doc))
        # 用来计数页面，图片，曲线，figure，水平文本框等对象的数量
        num_page, num_image, num_curve, num_figure, num_TextBoxHorizontal = 0, 0, 0, 0, 0
        # 循环遍历列表，每次处理一个page的内容
        for page in PDFPage.create_pages(doc):
            num_page += 1  # 页面增一
            # 利用解释器的process_page()方法解析读取单独页数
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            fileNames = os.path.splitext(filePath)
            # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象
            # 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等
            for x in layout:
                if hasattr(x, "get_text") or isinstance(x, LTTextBoxHorizontal):
                    results = x.get_text().replace(u'\xa0', u' ')
                    if '作废' in results or '作 废' in results or  "作  废" in results:
                        res['state'] = "2"
                    context = context + results
                # 如果x是水平文本对象的话
                if isinstance(x, LTTextBoxHorizontal):
                    num_TextBoxHorizontal += 1  # 水平文本框对象增一
                if isinstance(x, LTImage):  # 图片对象
                    num_image += 1
                if isinstance(x, LTCurve):  # 曲线对象
                    num_curve += 1
                if isinstance(x, LTFigure):  # figure对象
                    num_figure += 1

        print('对象数量：%s,页面数：%s,图片数：%s,曲线数：%s,'
              '水平文本框：%s,'%(num_figure,num_page,num_image,num_curve,num_TextBoxHorizontal))
        if '红' in context and '字' in context and '冲' in context and '销' in context:
            res['state'] = "3"
        return res

def parse(path):
    pdf2TxtManager = CPdf2TxtManager()
    return pdf2TxtManager.changePdfToText(path)
