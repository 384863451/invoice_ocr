import zxing as zxing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image
from six import BytesIO
import time
from selenium.webdriver import ActionChains


def get_url(url):
    browser = webdriver.Chrome("D:\\pycharm\\invoice_ocr\\driver\\chromedriver.exe")
    browser.get(url)
    browser.maximize_window()
    time.sleep(5)
    #aaa = browser.find_element_by_xpath("//*[@class='login-by-item-app hiddenAppScan']").click()
    browser.implicitly_wait(10)
    wait = WebDriverWait(browser,10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_radar_btn')))
    btn = browser.find_element_by_css_selector('.geetest_radar_btn')
    btn.click()
    time.sleep(0.5)
    return browser

def get_position(img_label):
    location = img_label.location
    size = img_label.size
    top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
        'width']
    return (left, top, right, bottom)

def get_screenshot(browser):
    screenshot = browser.get_screenshot_as_png()
    f = BytesIO()
    f.write(screenshot)
    return Image.open(f)

def get_position_scale(browser,screen_shot):
    height = browser.execute_script('return document.documentElement.clientHeight')
    width = browser.execute_script('return document.documentElement.clientWidth')
    x_scale = screen_shot.size[0] / (width+10)
    y_scale = screen_shot.size[1] / (height)
    return (x_scale,y_scale)

def get_slideimg_screenshot(screenshot,position,scale):
    x_scale,y_scale = scale
    position = [position[0] * x_scale, position[1] * y_scale, position[2] * x_scale, position[3] * y_scale]
    return screenshot.crop(position)

def compare_pixel(img1,img2,x,y):
    pixel1 = img1.load()[x,y]
    pixel2 = img2.load()[x,y]
    threshold = 50
    if abs(pixel1[0]-pixel2[0])<=threshold:
        if abs(pixel1[1]-pixel2[1])<=threshold:
            if abs(pixel1[2]-pixel2[2])<=threshold:
                return True
    return False


def compare(full_img,slice_img):
    left = 0
    for i in range(full_img.size[0]):
        for j in range(full_img.size[1]):
            if not compare_pixel(full_img,slice_img,i,j):
                return i
    return left

def get_track(distance):
    """
    根据偏移量获取移动轨迹
    :param distance: 偏移量
    :return: 移动轨迹
    """
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算间隔
    t = 0.2
    # 初速度
    v = 0

    while current < distance:
        if current < mid:
            # 加速度为正 2
            a = 4
        else:
            # 加速度为负 3
            a = -3
        # 初速度 v0
        v0 = v
        # 当前速度 v = v0 + at
        v = v0 + a * t
        # 移动距离 x = v0t + 1/2 * a * t^2
        move = v0 * t + 1 / 2 * a * t * t
        # 当前位移
        current += move
        # 加入轨迹
        track.append(round(move))
    return track


def move_to_gap(browser,slider, tracks):
    """
    拖动滑块到缺口处
    :param slider: 滑块
    :param tracks: 轨迹
    :return:
    """
    ActionChains(browser).click_and_hold(slider).perform()
    for x in tracks:
        ActionChains(browser).move_by_offset(xoffset=x, yoffset=0).perform()
    time.sleep(0.5)
    ActionChains(browser).release().perform()

if __name__ == '__main__':
    path = "C:\\Users\\38486\\Desktop\\image\\qr\\big.png"
    reader = zxing.BarCodeReader()
    barcode = reader.decode(path)
    url = barcode.parsed
    print(url)

