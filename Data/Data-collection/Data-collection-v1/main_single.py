import lib.img_drawLabel as draw
import lib.img_segment as seg
import lib.web_catchElementInfo as catch
import lib.web_crawl as crawl
import lib.file_utils as file

import pandas as pd
import os
import time
from func_timeout import func_set_timeout, FunctionTimedOut

start_time = time.clock()
is_segment = False
is_draw_label = True
# set the web crawler
url = "https://www.bbc.com/"
# set path
img_org_path = 'data/org.png'
img_drawn_path = 'data/drawn.png'
img_segment_path = 'data/segment'
label_path = 'data/label.csv'
driver_path = 'D:/webdriver'
# set the format of label
libel_format = pd.read_csv('data/format.csv', index_col=0)

# catch label and screenshot img and segment them into smaller size
img, label = None, None
catch_success = False
try:
    img, label = catch.catch(url, label_path, img_org_path, libel_format, driver_path)
except FunctionTimedOut:
    print('Catch Time Out')

# segment the lengthy images
if is_segment and img is not None:
    seg.segment_img(img, 600, img_segment_path, 0)
# read and draw label on segment img
if is_draw_label and img is not None and label is not None:
    draw.label(label, img, img_drawn_path)

end_time = time.clock()
print("*** Time taken:%ds ***" % int(end_time - start_time))
