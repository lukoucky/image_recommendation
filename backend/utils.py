from image_data import ImageData
import os

ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff'}

def is_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMG_EXTENSIONS

def get_all_images_in_dir(dirpath, full_path = False):
    imgs = []
    for img_path in os.listdir(dirpath):
        if is_image(img_path):
            if full_path:
                imgs.append(os.path.join(dirpath, img_path))
            else:
                imgs.append(img_path)
    return imgs

def get_image_data_for_dir(dirpath):
    imgs = get_all_images_in_dir(dirpath)
    image_data = []
    for img in imgs:
        image_data.append(ImageData(img, 0.2342))
    return image_data
