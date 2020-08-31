import time
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


class students(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    addr = db.Column(db.String(200))

    def __init__(self, name, city, addr):
        self.name = name
        self.city = city
        self.addr = addr

    def insert(self):
        db.session.add(self)
        db.session.commit()


def database_initialization_sequence():
    db.create_all()
    test_rec = students(
            'John Doe',
            'Los Angeles',
            '123 Foobar Ave')

    db.session.add(test_rec)
    db.session.rollback()
    db.session.commit()