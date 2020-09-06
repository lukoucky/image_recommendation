import time
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
    features = np.random.rand(81).tolist()
    test_rec = Image('test_img',features)

    db.session.add(test_rec)
    db.session.rollback()
    db.session.commit()
