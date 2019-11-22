import time

is_ctpn = False
is_uied = True
is_merge = True

PATH_IMG_INPUT = 'data\\input\\1.png'
PATH_LABEL_COMPO = 'data\\output\\compo.json'
PATH_LABEL_TEXT = 'data\\output\\ocr.txt'
PATH_CTPN_DRAWN = 'data\\output\\ctpn.png'
PATH_UIED_DRAWN = 'data\\output\\uied.png'
PATH_UIED_BIN = 'data\\output\\gradient.png'
PATH_MERGE = 'data\\output\\merged.png'
PATH_COMPONENT = 'data\\output\\components'
img_section = (3000, 1500)  # selected img section, height and width

start = time.clock()

if is_ctpn:
    import ocr
    ocr.ctpn(PATH_IMG_INPUT, PATH_LABEL_TEXT, PATH_CTPN_DRAWN, img_section)
if is_uied:
    import ui
    ui.uied(PATH_IMG_INPUT, PATH_LABEL_COMPO, PATH_UIED_DRAWN, PATH_UIED_BIN, img_section)
if is_merge:
    import merge
    merge.incorporate(PATH_IMG_INPUT, PATH_LABEL_COMPO, PATH_LABEL_TEXT, PATH_MERGE, img_section, is_clip=True, clip_path=PATH_COMPONENT)

print('Time Taken:%.3f s\n' % (time.clock() - start))
