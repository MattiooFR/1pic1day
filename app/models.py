from sqlalchemy import Column, String, Integer, Boolean, DateTime
from datetime import datetime
from app import db

"""
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
"""


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


class Album(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), index=True, nullable=False)
    url = Column(String(500), nullable=False)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    user_id = Column(String(50))
    images = db.relationship("Image", backref="album", lazy="dynamic")

    def __repr__(self):
        return "<Album {} {} {} {}>".format(
            self.name, self.url, self.user_id, self.images
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
    url = Column(String(500), nullable=False)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    viewed = Column(Boolean)
    album_id = Column(Integer, db.ForeignKey("album.id"))

    def __repr__(self):
        return "<Album {} {} {}>".format(self.album_id, self.url, self.viewed)

    def __init__(self, url, album, viewed=False):
        self.url = url
        self.album_id = album.id
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
