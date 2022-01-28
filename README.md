# 混合报销票据识别
  识别文件类型：图片，pdf，ofd
  识别类型：增值税专用发票, 增值税普通发票, 增值税电子专用发票, 增值税电子普通发票, 增值税普通发票（卷式）, 非税财政电子票据, 过路费发票, 火车票, 飞机票, 客运票, 出租车票, 定额, 通用机打发票
## 环境
   1. python3.5/3.6
   2. 依赖项安装：pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 
   3. 有GPU环境的可修改安装requirements.txt对应版本的tensorflow-gpu，config.py文件中控制GPU的开关
## 模型架构
    YOLOv5 + CRNN + CTC
   
## 模型
   1. 模型下载地址：链接：
   2. 将下载完毕的模型文件夹models放置于项目根目录下
## 服务启动
   1. 控制台 python manage.py runserver 127.0.0.1:8080
   2. 端口可自行修改
   3. 服务调用地址：http://*.*.*.*: [端口号]/detection，例：http://127.0.0.1:8080/detection
## 测试demo
   1. 测试工具：postman，可自行下载安装
   2. 增值税电子普票测试结果
   
![Image text](https://github.com/guanshuicheng/invoice/blob/master/test-invoice/%E7%94%B5%E5%AD%90%E5%8F%91%E7%A5%A8-test.png)
   
   3. 增值税专用普票测试结果
   
![Image text](https://github.com/guanshuicheng/invoice/blob/master/test-invoice/%E5%A2%9E%E5%80%BC%E7%A8%8E%E4%B8%93%E7%94%A8%E5%8F%91%E7%A5%A8-test.png)

   4. 增值税普通普票测试结果

![Image text](https://github.com/guanshuicheng/invoice/blob/master/test-invoice/%E5%A2%9E%E5%80%BC%E7%A8%8E%E6%99%AE%E9%80%9A%E5%8F%91%E7%A5%A8-test.jpg)

# 代码执行过程说明
- 使用django命令启动
- 首先对图片做处理,可以接收的参数为图片文件，图片base64编码，图片下载地址
- 图片中发票定位,并把识别结果放到list
- 判断对应的发票类型进一步识别发票具体部位。
- 识别到关键部位通过crnn识别具体信息
- 电子发票特别优化，可以识别pdf和ofd

   
## 后期开发计划
- 增值税发票只识别了五要素，后续打算结合发票查验直接获取全票面
- 其他发票都只识别了几个部位，后期有空完善
- crnn使用了chineseocr项目自带的，打算专门针对发票要素只训练需要的文字

## 参考
chineseocr https://github.com/chineseocr/chineseocr

##总结
新手做着玩，代码写的很乱。
