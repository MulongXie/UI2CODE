import pandas as pd
from selenium import webdriver
import cv2
from os.path import join as pjoin
from func_timeout import func_set_timeout, FunctionTimedOut
import time


def draw(label, pic):
    def select_color(item):
        color = (0, 0, 0)
        if item == 'div':
            color = (0, 0, 200)
        elif item == 'input':
            color = (255, 0, 0)
        elif item == 'button':
            color = (180, 0, 0)
        elif item == 'h1':
            color = (0, 255, 0)
        elif item == 'h2':
            color = (0, 180, 0)
        elif item == 'p':
            color = (0, 100, 0)
        elif item == 'a':
            color = (200, 100,)
        elif item == 'img':
            color = (0, 100, 255)
        return color

    count = {}
    for i in range(0, len(label)):
        item = label.iloc[i]
        top_left = (int(item.bx), int(item.by))
        botom_right = (int(item.bx + item.bw), int(item.by + item.bh))
        element = item.element
        color = select_color(item.element)
        if element in count:
            count[element] += 1
        else:
            count[element] = 1
        pic = cv2.rectangle(pic, top_left, botom_right, color, 1)
        cv2.putText(pic, element + str(count[element]), top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)


def fetch_element(ele_name, ele_all):
    elements_dom = driver.find_elements_by_xpath('//' + ele_name)

    for e in elements_dom:
        elements = {'element':ele_name,
                    'bx': e.location['x'],
                    'by': e.location['y'],
                    'bw': e.size['width'],
                    'bh': e.size['height']}
        ele_all = ele_all.append(elements, True)
    return ele_all


@func_set_timeout(60)
def crawl(url):
    driver.get(url)


driver_path = 'D:\webdriver\chromedriver.exe'
root = "E:\Mulong\Datasets\gui\dataset_webpage\page30000"
csv = pd.read_csv('link_30000.csv')
links = csv.Link
fmt = pd.read_csv('format.csv')

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(driver_path, options=options)

start_pos = 3909
end_pos = 15000
success = 3708
begin = time.clock()
for index in range(start_pos, end_pos):
    start_time = time.clock()

    # set output
    path_org = pjoin(root, 'org', str(index) + '.png')
    path_drawn = pjoin(root, 'drawn', str(index) + '.png')
    path_label = pjoin(root, 'label', str(index) + '.csv')
    path_html = pjoin(root, 'html', str(index) + '.html')

    # fetch label format
    element_all = fmt
    # fetch url
    url = 'http://' + links.iloc[index]
    print("\nCrawling " + str(index) + ' ' + url)
    try:
        crawl(url)
        open(path_html, 'w', encoding='utf-8').write(driver.page_source)
    except FunctionTimedOut:
        print("*** Time out ***")
        continue
    except:
        print("*** Link Connection Failed ***")
        driver.quit()
        driver = webdriver.Chrome(driver_path, options=options)
    print("1/3. Successfully Crawling Url")

    # get screenshots
    try:
        body = driver.find_elements_by_tag_name('body')
        S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
        driver.set_window_size(S('Width'), S('Height'))  # May need manual adjustment
        driver.find_element_by_tag_name('body').screenshot(path_org)
    except:
        print("*** Saving Screenshot Failed ***")
        continue
    print("2/3. Successfully Saving Screenshot")

    # get elements
    try:
        element_all = fetch_element('img', element_all)
        element_all = fetch_element('button', element_all)
        element_all = fetch_element('input', element_all)
        element_all.to_csv(path_label)
    except:
        print("*** Catching Element Failed ***")
        continue
    print("3/3. Successfully Fetching Elements")

    # draw results
    pic = cv2.imread(path_org)
    draw(element_all, pic)
    cv2.imwrite(path_drawn, pic)
    # time.sleep(3)

    driver.quit()
    driver = webdriver.Chrome(driver_path, options=options)
    success += 1
    print("Time taken:%.3fs, Total time:%.3fs, Success:[%d/%d]" % ((time.clock() - start_time), (time.clock() - begin), success, index + 1))
    print(time.ctime())

