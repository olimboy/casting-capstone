import os
from sqlalchemy import Column, String, Integer, Date, ForeignKey
from flask_sqlalchemy import SQLAlchemy

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


class Association(db.Model):
    __tablename__ = 'association'
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True)
    actor_id = Column(Integer, ForeignKey('actors.id', ondelete='CASCADE'), primary_key=True)
    movie = db.relationship("Movie", back_populates="actors")
    actor = db.relationship("Actor", back_populates="movies")

    def format(self, extra=False):
        return {
            'movie': self.movie.format(extra),
            'actor': self.actor.format(extra)
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


#
# association_table = Table('association', db.Model.metadata,
#                           Column('movie_id', Integer, ForeignKey('movies.id')),
#                           Column('actor_id', Integer, ForeignKey('actors.id'))
#                           )


class Movie(db.Model):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(80), nullable=False)
    release_date = Column(Date)
    actors = db.relationship("Association", back_populates="movie", cascade="all, delete")

    def format(self, extra=True):
        data = {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date,
        }
        if extra:
            data['actors'] = [rel.actor.format(False) for rel in self.actors]
        return data

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Actor(db.Model):
    __tablename__ = 'actors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10))
    movies = db.relationship("Association", back_populates="actor", cascade="all, delete")

    def format(self, extra=True):
        data = {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
        }
        if extra:
            data['movies'] = [rel.movie.format(False) for rel in self.movies]
        return data

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
