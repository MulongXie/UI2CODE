import main_uied as uied
import main_2code as code

if __name__ == '__main__':
    uied.element_detection('Data/data/input/9.png', 'Data/data/output')
    code.code_generation(img_path='../Data/data/input/9.png', detection_json_path='../Data/data/output/compo.json', output_page_path='Data/data/output/page')
