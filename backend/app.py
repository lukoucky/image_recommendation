import os
import time
import numpy as np
from flask import Flask, render_template, flash, redirect, request, url_for, send_from_directory, jsonify
from db_model import setup_db, Image
from werkzeug.utils import secure_filename
from utils import is_image, get_all_images_in_dir
from image_data import ImageData
from instance_segmentation_model import InstanceSegmentationModel
from sklearn.neighbors import NearestNeighbors
from dataset import Dataset
import tensorflow as tf
import random
import pickle

# Database access env variables
DBUSER = os.environ['POSTGRES_USER']
DBPASS = os.environ['POSTGRES_PASSWORD']
DBNAME = os.environ['POSTGRES_DB']
DBPORT = '5432'

UPLOAD_FOLDER = 'images'
MAX_IMAGES = 30

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
        image_name = "{}_{}".format(time.time(), filename)
        save_path = "{}/{}".format(app.config["UPLOAD_FOLDER"], image_name)
        file_object.save(save_path)

        # open and close to update the access time.
        with open(save_path, "r") as f:
            pass

        graph = tf.compat.v1.get_default_graph()
        with graph.as_default():
            features = model.predict(save_path)

        try:
            f_list = [float(v) for v in features]
            print('Saving feature list', f_list)
            print(type(f_list[0]))
            img = Image(image_name, f_list)
            img.insert()
        except Exception as e:
            print(e)

        return jsonify({ 'image_name': image_name })
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
    img_url = f'/image/{os.path.basename(file_name)}'
    return render_template('show_similar.html', imgs=get_all_images('images', images), new_img=img_url, objects=objects)


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
    objects = get_objects_on_image(image_name)
    images = get_similar_images(image_name, MAX_IMAGES+1)
    if image_name in images:
        images.pop(image_name, None)

    return images, objects

def get_objects_on_image(image_name):
    '''
    :param image_name: Name of image for object search
    :return: Dictionary where key is name of object on image and value it probablity 
    '''
    objects = dict()

    my_image = Image.query.filter(Image.name == image_name).one_or_none()
    if my_image is None:
        return objects

    feature = my_image.feature_vector

    for category, score in enumerate(feature):
        if score > 0:
            objects[model.categories[category]] = score
    return objects

def get_similar_images(image_name, n=10):
        '''
        For given image_name returns most simailar images in database.
        :param image_name: Image name of searched image
        :return: Dictionary where keys are the names of images and value are similarity
                 score to original image
        '''
        similar: dict = {}

        my_image = Image.query.filter(Image.name == image_name).one_or_none()
        if my_image is None:
            return similar

        my_features = my_image.feature_vector

        feature_list, names = get_feature_list()

        neighbors = NearestNeighbors(n_neighbors=n, algorithm='brute', metric='euclidean').fit(feature_list)
        distances, indices = neighbors.kneighbors([my_features])
        
        for i in range(len(distances[0])):
            similar[names[indices[0][i]]] = distances[0][i]

        return similar

def get_feature_list():
    '''
    :return: Tuple where first item is list of features for all images and second item is list with image names
    '''
    feature_list = []
    names = []
    for image in Image.query.all():
        feature_list.append(image.feature_vector)
        names.append(image.name)

    return (feature_list, names)

def fill_database():
    '''
    Helper method to populate database with precomputed features saved to pickle
    '''
    feature_list = pickle.load(open('features_coco_segment.pickle', 'rb'))
    names = pickle.load(open('imagenames_coco_segment.pickle', 'rb'))
    for i, name in enumerate(names):
        f_list = [float(v) for v in feature_list[i]]
        img = Image(name, f_list)
        img.insert()

if __name__ == '__main__':
    print('Setting up model and dataset')
    model = InstanceSegmentationModel('mask_rcnn_coco.h5')
    data = Dataset('coco_segment', '/home/backend/image', model)
    data.load_features()
    print('Running Image Segmentation backend')
    app.run(debug=False, host='0.0.0.0', port=5555, threaded=False)
