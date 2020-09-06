import time
import pickle
import numpy as np
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def setup_db(app):
    '''
    Set up db model and connect it with flask app
    '''
    db.app = app
    db.init_app(app )
    dbstatus = False
    while dbstatus == False:
        try:
            print('Create all')
            db.create_all()
        except:
            print('Sleep')
            time.sleep(2)
        else:
            dbstatus = True
    database_initialization_sequence()


class Image(db.Model):
    '''
    Model for Image in database
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    feature_vector = db.Column(db.ARRAY(db.Float()))

    def __init__(self, name, feature_vector):
        self.name = name
        self.feature_vector = feature_vector

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'{self.name}[{self.feature_vector[0]}, {self.feature_vector[1]}, {self.feature_vector[2]}, ...]'

def database_initialization_sequence():
    '''
    Initialize database
    '''
    db.create_all()
    fill_database()

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