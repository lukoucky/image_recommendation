import os
import numpy as np
from flask import Flask, render_template, flash, redirect, request, url_for, send_from_directory, jsonify
from db_model import setup_db, Image
from werkzeug.utils import secure_filename
from utils import is_image, get_all_images_in_dir
from imagenet_similarity import similarity_resnet50, predict_resnet50, similarity_nasnet_large
from image_data import ImageData
from sklearn.neighbors import NearestNeighbors
import time
import pickle

DBUSER = os.environ['POSTGRES_USER']
DBPASS = os.environ['POSTGRES_PASSWORD']
DBNAME = os.environ['POSTGRES_DB']
DBPORT = '5432'

UPLOAD_FOLDER = 'images'
MAX_IMAGES = 30

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{DBUSER}:{DBPASS}@db:{DBPORT}/{DBNAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'strv'
setup_db(app)

# TODO: Add some limit to number of sent pictures
def get_all_images(dirpath, imgs = None):

    image_data = []

    if imgs is None:
        imgs = get_all_images_in_dir(dirpath)
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
    # TODO: Replace list dir with call search for similar images
    return render_template('show_all.html', imgs=get_all_images('images'))

@app.route('/img/<path:filename>')
def send_img(filename):
    print('send file with path:', filename)
    return send_from_directory('images', filename)

@app.route('/static/<path:filename>')
def send_static(filename):
    print('send file with path:', filename)
    return send_from_directory('static', filename)

@app.route("/sendfile", methods=["POST"])
def send_file():
    fileob = request.files["file2upload"]
    filename = secure_filename(fileob.filename)
    if is_image(filename):
        save_path = "{}/{}_{}".format(app.config["UPLOAD_FOLDER"], time.time(), filename)
        fileob.save(save_path)

        # open and close to update the access time.
        with open(save_path, "r") as f:
            pass

        print('Compute features for',save_path)
        features = predict_resnet50(save_path)
        try:
            img = Image(save_path, features.tolist())
            img.insert()
        except Exception as e:
            print(e)

        return jsonify({ 'image_name': save_path })
    else:
        # TODO: Inform about error
        return jsonify({ 'image_name': '/' })

@app.route('/show_similar/<path:file_name>', methods=['GET'])
def show_similar(file_name):
    # prepare_features_to_db('images')
    # images = get_differences(file_name)
    images = get_NN_diff(file_name)
    return render_template('show_similar.html', imgs=get_all_images('images', images), new_img=os.path.basename(file_name))


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


def get_differences(file_name):
    similar: dict = {}
    my_image = Image.query.filter(Image.name == file_name).one_or_none()
    if my_image is None:
        return similar

    my_features = np.array(my_image.imagenet_fetures)

    for image in Image.query.all():
        if not image.name == file_name:
            diff = np.linalg.norm(image.imagenet_fetures-my_features)
            similar[image.name] = diff

    return similar

def get_NN_diff(file_name):
    similar: dict = {}
    my_image = Image.query.filter(Image.name == file_name).one_or_none()
    if my_image is None:
        return similar

    my_features = np.array(my_image.imagenet_fetures)

    feature_list, names = get_feature_list()
    neighbors = NearestNeighbors(n_neighbors=20, algorithm='brute', metric='euclidean').fit(feature_list)
    distances, indices = neighbors.kneighbors([my_features])

    for i in range(len(distances[0])):
        similar[names[indices[0][i]]] = distances[0][i]

    return similar


def get_feature_list():
    feature_list = []
    names = []
    for image in Image.query.all():
        feature_list.append(image.imagenet_fetures)
        names.append(image.name)

    return (feature_list, names)

if __name__ == '__main__': 
    print('Running app')
    app.run(debug=True, host='0.0.0.0', port=5555)
