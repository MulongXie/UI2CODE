from os.path import join as pjoin
import os

import main_uied as uied
import main_2code as code

if __name__ == '__main__':
    input_img_path = 'data/input/x.png'
    name = input_img_path.split('/')[-1][:-4]

    output_dir_uied = pjoin('data/output', name, 'uied')
    output_dir_code = pjoin('data/output', name, 'code')

    uied.element_detection(input_path_img=input_img_path, output_root=output_dir_uied)
    code.generate_code(img_path=input_img_path, uied_path=pjoin(output_dir_uied, 'compo.json'), output_dir=output_dir_code)
