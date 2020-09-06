import os
import numpy as np
from flask import Flask, render_template, flash, redirect, request, url_for, send_from_directory, jsonify
from db_model import setup_db, Image
from werkzeug.utils import secure_filename
from utils import is_image, get_all_images_in_dir
from image_data import ImageData
from instance_segmentation_model import InstanceSegmentationModel
from dataset import Dataset
import random

# Database access env variables
DBUSER = os.environ['POSTGRES_USER']
DBPASS = os.environ['POSTGRES_PASSWORD']
DBNAME = os.environ['POSTGRES_DB']
DBPORT = '5432'

UPLOAD_FOLDER = 'images'
MAX_IMAGES = 60

# Model and Dataset classes instance filled in main method at the bottom
data = None
model = None

# Setup flask app and connect it to database
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{DBUSER}:{DBPASS}@db:{DBPORT}/{DBNAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'strv'
setup_db(app)

def get_all_images(dirpath, imgs = None):
    '''
    Prepares images for display in 4 columns on web page
    :param dirpath: Path to folder with images
    :param imgs: List of images. Optional parameter. If set images are taken from this list.
                 If not images are taken from dirpath
    :return: List with four items - each item is another list with almost the same number of images.
    '''
    image_data = []
    if imgs is None:
        imgs = get_all_images_in_dir(dirpath)
        random.shuffle(imgs)
        for img in imgs:
            image_data.append(ImageData(img, 0.0))
    else:
        for img_path, similarity in imgs.items():
            image_data.append(ImageData(os.path.basename(img_path), similarity)) 
        image_data = sorted(image_data, key=lambda x: x.similarity, reverse=False)
    
    image_data = image_data[0:MAX_IMAGES]
    n = len(image_data)//4
    if len(image_data)%4 > 1:
        n += 1
    all_imgs = [image_data[0:n], image_data[n:2*n], image_data[2*n:3*n], image_data[3*n:]]
    return all_imgs

@app.route('/', methods=['GET'])
def home():
    '''
    Endpoint for index page. Shows random images from database.
    '''
    return render_template('show_all.html', imgs=get_all_images('images'))

@app.route('/image/<path:filename>')
def send_img(filename):
    '''
    Endpoint for static images
    :param filename: Image file name (just image, without complete path)
    '''
    print('Sending image with path:', filename)
    return send_from_directory('images', filename)

@app.route('/static/<path:filename>')
def send_static(filename):
    '''
    Endpoint for static files other than images
    :param filename: File name
    '''
    print('Sending file with path:', filename)
    return send_from_directory('static', filename)

@app.route("/upload_file", methods=["POST"])
def upload_file():
    """
    API Endpoint for image uploading. Expects request with field 'file_to_upload'
    that contains image. If the file is image it is saved, features are extracted 
    and stored in database.
    :return: JSON with name of image in backend database
    """
    file_object = request.files['file_to_upload']
    filename = secure_filename(file_object.filename)
    if is_image(filename):
        save_path = "{}/{}_{}".format(app.config["UPLOAD_FOLDER"], time.time(), filename)
        file_object.save(save_path)

        # open and close to update the access time.
        with open(save_path, "r") as f:
            pass

        print(f'Computing features for {save_path}')
        # TODO: Prediction
        features = model.predict(save_path)
        try:
            img = Image(save_path, features)
            img.insert()
        except Exception as e:
            print(e)

        return jsonify({ 'image_name': save_path })
    else:
        # TODO: Inform about error
        return jsonify({ 'image_name': '/' })

@app.route('/get_similar/<path:file_name>', methods=['GET'])
def get_similar(file_name):
    '''
    API Endpoint for similarity search. Expects name of image already in datase.
    :param filename: Name of image that is alreade processed in database
    :return: JSON with list of similar images and objects found on selected image
    '''
    images, objects = predict_similar_images(file_name)
    obj_dict = {}
    for obj in objects.keys():
        obj_dict[obj] = float(objects[obj])
    return jsonify({ 'images' : list(images.keys()), 'objects' : obj_dict })

@app.route('/predict_similar/<path:file_name>', methods=['GET'])
def predict_similar(file_name):
    '''
    Endpoint for similarity search. Expects name of image already in datase.
    :param filename: Name of image that is alreade processed in database
    Returns webpage with similarity prediction for selected image
    '''
    images, objects = predict_similar_images(file_name)
    return render_template('show_similar.html', imgs=get_all_images('images', images), new_img=f'/image/{file_name}', objects=objects)


@app.route('/predict_random_image', methods=['GET'])
def predict_random_image():
    '''
    Returns webpage with similarity prediction for random image from database
    '''
    img = data.get_random_image()
    images, objects = predict_similar_images(img)
    return render_template('show_similar.html', imgs=get_all_images('images', images), new_img=f'/image/{img}', objects=objects)

def predict_similar_images(image_name):
    '''
    Predicts similar images to image_name from database
    :param image_name: Name of image for prediction
    :return: Tuple with first parameter list of similar images and second objects on searched image
    '''
    objects = data.get_objects_on_image(image_name)
    images = data.get_similar_images(image_name, MAX_IMAGES+1)
    if image_name in images:
        images.pop(image_name, None)
    else:
        images.pop(-1)
    return images, objects

def prepare_features_to_db(dirpath):
    imgs = get_all_images_in_dir(dirpath, True)
    feature_list = []
    for image in imgs:
        features = predict_resnet50(image)
        feature_list.append(features)
        img = Image(image, features.tolist())
        img.insert()
    pickle.dump(feature_list, open('features-2.pickle', 'wb'))
    pickle.dump(imgs, open('filenames-2.pickle','wb'))

def get_feature_list():
    feature_list = []
    names = []
    for image in Image.query.all():
        feature_list.append(image.imagenet_fetures)
        names.append(image.name)

    return (feature_list, names)

if __name__ == '__main__':
    print('Setting up model and dataset')
    model = InstanceSegmentationModel('mask_rcnn_coco.h5')
    data = Dataset('coco_segment', '/home/backend/image', model)
    print('Running Image Segmentation backend')
    app.run(debug=True, host='0.0.0.0', port=5555)
