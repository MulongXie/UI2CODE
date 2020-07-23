import lib.img_drawLabel as draw
import lib.img_segment as seg
import lib.web_catchElementInfo as catch

import pandas as pd
import os
from os.path import join as pjoin
import time
from func_timeout import func_set_timeout, FunctionTimedOut
from selenium import webdriver

start_time = time.clock()

# Function selection
is_segment = False
is_draw_label = True

# set the web crawler
driver_path = 'D:/webdriver'
url = "http://www.youtube.com"
browser = 'Chrome'

# catch label and screenshot img and segment them into smaller size
if __name__ == '__main__':
    img, label = None, None
    out_html = 'data/0.html'
    out_elements = 'data/0.csv'
    out_img = 'data/0.png'

    # initialize the webdriver to get the full screen-shot and attributes
    if browser == 'PhantomJS':
        driver = webdriver.PhantomJS(executable_path=os.path.join(driver_path, 'phantomjs.exe'))
    elif browser == 'Chrome':
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  # do not show the browser every time
        driver = webdriver.Chrome(executable_path=os.path.join(driver_path, 'chromedriver.exe'), options=options)

    # set the format of label
    label_format = pd.read_csv('format.csv', index_col=0)
    try:
        img, label = catch.catch(url, out_html, out_elements, out_img, label_format, driver)
        # read and draw label on segment img
        if is_draw_label and img is not None and label is not None:
            img_drawn_path = 'data/0_drawn.png'
            draw.label(label, img, img_drawn_path)
        # segment the lengthy images
        if is_segment and img is not None:
            img_segment_dir = '/segment'
            seg.segment_img(img, 600, img_segment_dir, 0)

    except FunctionTimedOut:
        print('Catch Time Out')

end_time = time.clock()
print("*** Time taken:%ds ***" % int(end_time - start_time))
