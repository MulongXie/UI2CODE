from selenium import webdriver
import pandas as pd
import time
import os
import cv2
import numpy as np
from PIL import Image
from os.path import join as pjoin
from func_timeout import func_set_timeout


# refine the data
def compo_filter(compo, body_size):
    # ignore all hidden elements
    display = compo.value_of_css_property('display')
    if display == 'none':
        return False
    # ignore all nonsense elements
    if compo.size['width'] == 0 or compo.size['height'] == 0 or compo.location['x'] < 0 or compo.location['y'] < 0:
        return False
    # ignore too large element
    if compo.size['width'] + compo.location['x'] > body_size['width']:
        return False
    # if compo.size['height'] + compo.location['y'] > body_size['height']:
    #     return False
    # ignore too small element
    if compo.size['width'] * compo.size['height'] < 100:
        return False
    return True


# take fully loaded screenshot
def save_screenshot_scroll(driver, output_path):
    # scroll down to the bottom and scroll back to the top
    # ensure all element fully loaded
    driver.execute_script("""
        (function () {
            var y = 0;
            var step = 100;
            window.scroll(0, 0);

            function f() {
                if (y < document.body.scrollHeight) {
                    y += step;
                    window.scroll(0, y);
                    setTimeout(f, 100);
                } else {
                    window.scroll(0, 0);
                    document.title += "scroll-done";
                }
            }
            setTimeout(f, 1000);
        })();
    """)
    for i in range(30):
        if "scroll-done" in driver.title:
            break
        time.sleep(10)
    driver.save_screenshot(output_path)


def save_screenshot_maxlength(driver, output_path):
    width = driver.execute_script("return document.documentElement.scrollWidth")
    height = driver.execute_script("return document.documentElement.scrollHeight")
    driver.set_window_size(width, height)
    driver.save_screenshot(output_path)


def save_screenshot_splicing(driver, output_path):
    window_height = driver.get_window_size()['height']  # 窗口高度
    page_height = driver.execute_script('return document.documentElement.scrollHeight')  # 页面高度
    driver.save_screenshot('temp.png')
    if page_height > window_height:
        n = page_height // window_height  # 需要滚动的次数
        base_mat = np.atleast_2d(Image.open('temp.png'))  # 打开截图并转为二维矩阵

        for i in range(n):
            driver.execute_script('document.documentElement.scrollTop=' + str(window_height * (i + 1)) + ';')
            time.sleep(.5)
            driver.save_screenshot('temp.png')  # 保存截图
            mat = np.atleast_2d(Image.open('temp.png'))  # 打开截图并转为二维矩阵
            base_mat = np.append(base_mat, mat, axis=0)  # 拼接图片的二维矩阵
        Image.fromarray(base_mat).save(output_path)
    os.remove('temp.png')


def get_element(elements, df, driver):
    # get body size for compo filter
    body = driver.find_elements_by_tag_name('body')
    body_size = [b.size for b in body]
    # get all components
    for element in elements:
        compos = driver.find_elements_by_xpath('//' + element)
        for compo in compos:
            if not compo_filter(compo, body_size[0]):
                continue
            dic = {'element': element, 'bx': compo.location['x'], 'by': compo.location['y'],
                   'bw': compo.size['width'], 'bh': compo.size['height']}
            df = df.append(dic, True)
    return df


# fetch the elements information into csv
# save the screenshot
# save the html page
@func_set_timeout(60)
def catch(url, out_html, out_elements, out_img, label_format, driver):
    print("*** catching element from %s ***" % url)
    print(time.ctime())
    label = label_format

    # connect the url
    try:
        driver.maximize_window()
        driver.set_page_load_timeout(50)
        driver.get(url)
        open(out_html, 'w', encoding='utf-8').write(driver.page_source)
        print('Link Connected Successfully')
    except:
        print('Link Connected Failed')
        return None, None

    # fetch the attributes
    elements = ['button', 'img', 'input']
    label = get_element(elements, label, driver)
    if len(label) > 0:
        label.to_csv(out_elements)

    # fetch the screenshot
    try:
        save_screenshot_maxlength(driver, out_img)
        img = cv2.imread(out_img)
        print("Save Screenshot Successfully")
        return img, label
    except:
        print("Save Screenshot Failed")
        return None, None

