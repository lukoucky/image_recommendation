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
    imagenet_fetures = db.Column(db.ARRAY(db.Float()))

    def __init__(self, name, imagenet_fetures):
        self.name = name
        self.imagenet_fetures = imagenet_fetures

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'{self.name}[{self.imagenet_fetures[0]}, {self.imagenet_fetures[1]}, {self.imagenet_fetures[2]}, ...]'

def database_initialization_sequence():
    db.create_all()
    features = np.random.rand(1000)
    test_rec = Image('test_img',features)

    db.session.add(test_rec)
    db.session.rollback()
    db.session.commit()
