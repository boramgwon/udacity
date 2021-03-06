import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# connect to a local postgresql database
app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venues'

  # implement any missing fields, as a database migration using Flask-Migrate
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  phone = db.Column(db.String(120))
  address = db.Column(db.String(120))
  facebook_link = db.Column(db.String(120))    
  website = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(120))
  shows = db.relationship('Show', backref='venue_shows', cascade='all, delete-orphan', passive_deletes=True)

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'genres': self.genres,
      'address': self.address,
      'city': self.city,
      'state': self.state,
      'phone': self.phone,
      'website': self.website,
      'facebook_link': self.facebook_link,
      'seeking_talent': self.seeking_talent,
      'seeking_description': self.seeking_description,
      'image_link': self.image_link
  }


class Artist(db.Model):
  __tablename__ = 'artists'

  # implement any missing fields, as a database migration using Flask-Migrate
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  phone = db.Column(db.String(120))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(120))
  shows = db.relationship('Show', backref='artist_shows', cascade='all, delete-orphan', passive_deletes=True)

# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True, nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete="CASCADE"), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete="CASCADE"), nullable=False)
  start_time = db.Column(db.String, nullable=False)
  venues = db.relationship('Venue', backref='venues')
  artists = db.relationship('Artist', backref='artists')
