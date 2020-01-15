import time

is_ctpn = False
is_uied = True
is_merge = True

# set input image path
PATH_IMG_INPUT = 'data\\input\\5.png'
# outputs
PATH_LABEL_COMPO = 'data\\output\\compo.json'
PATH_LABEL_TEXT = 'data\\output\\ocr.txt'
PATH_CTPN_DRAWN = 'data\\output\\ctpn.png'
PATH_UIED_DRAWN = 'data\\output\\uied.png'
PATH_UIED_BIN = 'data\\output\\gradient.png'
PATH_MERGE_IMG = 'data\\output\\merged.png'
PATH_MERGE_LABEL = 'data\\output\\merged.txt'
PATH_COMPONENT = 'data\\output\\components'

# clip image, maximum height and width
img_section = (3000, 1500)

start = time.clock()

if is_ctpn:
    import ocr
    ocr.ctpn(PATH_IMG_INPUT, PATH_LABEL_TEXT, PATH_CTPN_DRAWN, img_section)
if is_uied:
    import ui
    ui.uied(PATH_IMG_INPUT, PATH_LABEL_COMPO, PATH_UIED_DRAWN, PATH_UIED_BIN, img_section)
if is_merge:
    import merge
    merge.incorporate(PATH_IMG_INPUT, PATH_LABEL_COMPO, PATH_LABEL_TEXT, PATH_MERGE_IMG, PATH_MERGE_LABEL, img_section, is_clip=False, clip_path=PATH_COMPONENT)

print('Time Taken:%.3f s\n' % (time.clock() - start))
