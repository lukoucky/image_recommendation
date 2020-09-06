import time
import numpy as np
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def setup_db(app):
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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    feture_vector = db.Column(db.ARRAY(db.Float()))

    def __init__(self, name, feture_vector):
        self.name = name
        self.feture_vector = feture_vector

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'{self.name}[{self.feture_vector[0]}, {self.feture_vector[1]}, {self.feture_vector[2]}, ...]'

def database_initialization_sequence():
    db.create_all()
    features = np.random.rand(81)
    test_rec = Image('test_img',features)

    db.session.add(test_rec)
    db.session.rollback()
    db.session.commit()
