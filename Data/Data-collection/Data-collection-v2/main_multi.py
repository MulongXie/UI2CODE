import lib.img_drawLabel as draw
import lib.img_segment as seg
import lib.web_catchElementInfo as catch

import pandas as pd
import os
import time
from func_timeout import func_set_timeout, FunctionTimedOut
from selenium import webdriver

is_segment = False
is_draw_label = True

driver_path = 'D:\webdriver'
browser = 'Chrome'
data_position = 'E:\Mulong\Datasets\gui\dataset_webpage\page30000'
label_format = pd.read_csv(os.path.join(data_position, 'format.csv'), index_col=0)

html_root = os.path.join(data_position, 'html')
label_root = os.path.join(data_position, 'label')
img_root = os.path.join(data_position, 'org')
drawn_root = os.path.join(data_position, 'drawn')
segment_root = os.path.join(data_position, 'segment')


def setup_output_folders():
    os.makedirs(html_root, exist_ok=True)
    os.makedirs(label_root, exist_ok=True)
    os.makedirs(img_root, exist_ok=True)
    os.makedirs(drawn_root, exist_ok=True)
    os.makedirs(segment_root, exist_ok=True)

if __name__ == '__main__':
    # initialize the webdriver to get the full screen-shot and attributes
    if browser == 'PhantomJS':
        driver = webdriver.PhantomJS(executable_path=os.path.join(driver_path, 'phantomjs.exe'))
    elif browser == 'Chrome':
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # do not show the browser every time
        driver = webdriver.Chrome(executable_path=os.path.join(driver_path, 'chromedriver.exe'), options=options)

    # read links
    csv = pd.read_csv(os.path.join(data_position, 'link_30000.csv'))
    links = csv.Link
    print("*** %d Links Fetched ***\n" % len(links))

    setup_output_folders()
    start_pos = 0
    end_pos = 100
    bad_link = 0
    for index in range(start_pos, len(links)):
        img, label = None, None
        start_time = time.clock()
        # set path
        html_path = os.path.join(img_root, str(index) + '.html')
        label_path = os.path.join(label_root, str(index) + '.csv')
        img_org_path = os.path.join(img_root, str(index) + '.png')
        # catch label and screenshot img and segment them into smaller size
        url = 'http://www.' + links.iloc[index] if 'http://' not in links.iloc[index] else links.iloc[index]
        try:
            img, label = catch.catch(url, html_path, label_path, img_org_path, label_format, driver)
            # segment the lengthy images
            if is_segment and img is not None:
                img_segment_path = os.path.join(segment_root, str(index))
                seg.segment_img(img, 600, img_segment_path, 0)
            # read and draw label on segment img
            if is_draw_label and img is not None and label is not None:
                img_drawn_path = os.path.join(drawn_root, str(index) + '.png')
                draw.label(label, img, img_drawn_path)

        except FunctionTimedOut:
            print('*** Catch Time Out:%d ***\n' % bad_link)
            bad_link += 1
            continue

        except Exception as e:
            bad_link += 1
            print('*** Fetching Failed:%d ***\n' % bad_link)
            continue

        end_time = time.clock()
        print("*** %d Time taken:%ds ***\n" % (index, int(end_time - start_time)))

        if index > end_pos:
            break
