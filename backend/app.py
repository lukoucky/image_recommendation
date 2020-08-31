import os
from flask import Flask, render_template, flash, redirect, request, url_for, send_from_directory, jsonify
from db_model import setup_db, students
from werkzeug.utils import secure_filename

DBUSER = os.environ['POSTGRES_USER']
DBPASS = os.environ['POSTGRES_PASSWORD']
DBNAME = os.environ['POSTGRES_DB']
DBPORT = '5432'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{DBUSER}:{DBPASS}@db:{DBPORT}/{DBNAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'strv'
setup_db(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['city'] or not request.form['addr']:
            flash('Please enter all the fields', 'error')
        else:
            student = students(
                    request.form['name'],
                    request.form['city'],
                    request.form['addr'])
            student.insert()

            flash('Record was succesfully added')
            return redirect(url_for('home'))
    return render_template('show_all.html', students=students.query.all())

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
    save_path = "{}/{}".format(app.config["UPLOAD_FOLDER"], filename)
    fileob.save(save_path)

    # open and close to update the access time.
    with open(save_path, "r") as f:
        pass

    return "successful_upload"


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
