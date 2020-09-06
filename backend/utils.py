from image_data import ImageData
import os

ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff'}

def is_image(filename):
    '''
    Check if file located in filename is an image.
    It checks only by the extension.
    :param filename: Tested file name
    :return: True if file is image, False otherwise
    '''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMG_EXTENSIONS

def get_all_images_in_dir(dirpath, full_path = False):
    '''
    :param dirpath: Path to directory with images
    :param full_path: If true return name of image names with full path (including dirpath)
    :return: List with all images in directory set in constructor.
    '''
    imgs = []
    for img_path in os.listdir(dirpath):
        if is_image(img_path):
            if full_path:
                imgs.append(os.path.join(dirpath, img_path))
            else:
                imgs.append(img_path)
    return imgs
