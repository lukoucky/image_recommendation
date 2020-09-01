import os
from flask import Flask, render_template, flash, redirect, request, url_for, send_from_directory, jsonify
from db_model import setup_db, Image
from werkzeug.utils import secure_filename
from utils import is_image, get_all_images_in_dir
from imagenet_similarity import compute_similarity, predict_resnet50
from image_data import ImageData
import time

DBUSER = os.environ['POSTGRES_USER']
DBPASS = os.environ['POSTGRES_PASSWORD']
DBNAME = os.environ['POSTGRES_DB']
DBPORT = '5432'

UPLOAD_FOLDER = 'images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{DBUSER}:{DBPASS}@db:{DBPORT}/{DBNAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'strv'
setup_db(app)

def get_all_images(dirpath, imgs = None):
    if imgs is None:
        imgs = get_all_images_in_dir(dirpath)

    image_data = []
    for img in imgs:
        image_data.append(ImageData(img, 0.2342))

    n = len(image_data)//4
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

        # TODO: 1) Compute features 2) Save to DB 3) Return all images with similarity
        print('Compute features for',save_path)
        features = predict_resnet50(save_path)
        try:
            img = Image(save_path, features[0].tolist())
            img.insert()
        except Exception as e:
            print(e)

        # compute_similarity(save_path)
        return render_template('show_all.html', imgs=get_all_images('images'))
    else:
        return "unsupported file"


@app.route("/filenames", methods=["GET"])
def get_filenames():
    filenames = os.listdir("uploads/")

    #modify_time_sort = lambda f: os.stat("uploads/{}".format(f)).st_atime

    def modify_time_sort(file_name):
        file_path = "uploads/{}".format(file_name)
        file_stats = os.stat(file_path)
        last_access_time = file_stats.st_atime
        return last_access_time

    filenames = sorted(filenames, key=modify_time_sort)
    return_dict = dict(filenames=filenames)
    return jsonify(return_dict)

if __name__ == '__main__': 
    print('Runnign app')
    app.run(debug=True, host='0.0.0.0', port=5555)
