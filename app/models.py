from sqlalchemy import Column, String, Integer, Boolean, DateTime
from datetime import datetime
from app import db

"""
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
"""


def db_reset():
    db.drop_all()
    db.create_all()


def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class Album(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), index=True, nullable=False)
    url = Column(String(500), nullable=False)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    user_id = Column(String(50))
    last_time_viewed = Column(DateTime, default=datetime.utcnow)
    last_photo_viewed = Column(String(300))
    images = db.relationship("Image", backref="album", lazy="dynamic")

    def __repr__(self):
        return "<Album {} {} {} {} {}>".format(
            self.name,
            self.url,
            self.user_id,
            self.last_time_viewed,
            self.last_photo_viewed,
        )

    def __init__(self, name, url, user_id="ANON"):
        self.name = name
        self.url = url
        self.user_id = user_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "images": self.images,
        }


class Image(db.Model):
    id = Column(Integer, primary_key=True)
    url = Column(String(300), nullable=False)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    viewed = Column(Boolean)
    album_id = Column(Integer, db.ForeignKey("album.id"), nullable=False)

    def __repr__(self):
        return "<Image {} {} {}>".format(self.album_id, self.url, self.viewed)

    def __init__(self, url, album_id, viewed=False):
        self.url = url
        self.album_id = album_id
        self.viewed = viewed

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "url": self.url,
            "timestamp": self.timestamp,
            "album_id": self.album_id,
            "viewed": self.viewed,
        }
