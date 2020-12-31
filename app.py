#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import Flask, abort, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue_shows', cascade='all, delete-orphan', passive_deletes=True)

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    address = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist_shows', cascade='all, delete-orphan', passive_deletes=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
   __tablename__ = 'shows'

   venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete="CASCADE"), primary_key=True)
   artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete="CASCADE"), primary_key=True)
   start_time = db.Column(db.String, nullable=False)
   venues = db.relationship('Venue', backref='venues')
   artists = db.relationship('Artist', backref='artists')

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  # make groups by city, state and then use them as filters to create required data set
  data = []
  groups = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state)

  for group in groups:
    venues = Venue.query.filter_by(city=group.city, state=group.state).all()
    data.append({ 'city':group.city, 'state':group.state, 'venues': venues })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  term = request.form['search_term']
  sql_term = "%{}%".format(term)
  venues = Venue.query.filter(Venue.name.ilike(sql_term)).all()
  
  response = {
    'count': len(venues)
  }
  response.update({ 'data': venues })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  #venue = db.session.query(Venue).get(venue_id)
  print("venue_id: " + str(venue_id))

  genres = venue.genres
  print("genres original: " + str(genres))

  new_genres = ['Jazz', 'Reggae', 'Swing', 'Classical', 'Folk']
  print("genres new: " + str(new_genres))

  show_venue = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows_count': 0,
    'upcoming_shows_count': 0
  }
  
  # query shows data by venue id filter and then set them either past shows or upcoming shows 
  # based on comparision with current time 
  past_shows = []
  upcoming_shows = []
  shows = Show.query.filter_by(venue_id=venue_id).all()
  shows_count = len(shows)
 
  if(shows_count):
    for show in shows:
      artist = Artist.query.get(show.artist_id)
      
      start_time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
      current_time = datetime.now()

      if(current_time > start_time):
        past_shows.append({ 
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': show.start_time
        })
      else:
        upcoming_shows.append({ 
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': show.start_time
        }) 

    show_venue.update({'past_shows' : past_shows })
    show_venue.update({'upcoming_shows' : upcoming_shows })
    show_venue.update({'past_shows_count' : len(past_shows)})
    show_venue.update({'upcoming_shows_count' : len(upcoming_shows)})

  return render_template('pages/show_venue.html', venue=show_venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
 
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    seeking_talent = 'seeking_talent' in request.form
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, 
                    genres=genres, website=website, facebook_link=facebook_link, 
                    image_link=image_link, seeking_talent=seeking_talent,
                    seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue = Venue.query.get(venue_id)
  venue_name = venue.name
  print("Deleting venue named (" + venue_name + "), ID: " + str(venue_id))

  error = False
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print("error on deleteting venue!")
  finally:
    db.session.close()
  if error:
    flash('Venue ' + venue_name + ' was not deleted')
  else:
    flash('Venue ' + venue_name + ' was deleted')
  
  return redirect(url_for('index'))
 
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  term = request.form['search_term']
  sql_term = "%{}%".format(term)
  artists = Artist.query.filter(Artist.name.ilike(sql_term)).all()
  
  response = {
    'count': len(artists)
  }
  response.update({ 'data': artists })

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  print("artist_id: " + str(artist_id))
  artist = Artist.query.get(artist_id)
  show_artist = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'address': artist.address,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows_count': 0,
    'upcoming_shows_count': 0
  }
  
  # query shows data by artist id filter and then set them either past shows or upcoming shows 
  # based on comparision with current time 
  past_shows = []
  upcoming_shows = []
  shows = Show.query.filter_by(artist_id=artist_id).all()
  shows_count = len(shows)
 
  if(shows_count):
    for show in shows:
      venue = Venue.query.get(show.venue_id)
      
      start_time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
      current_time = datetime.now()

      if(current_time > start_time):
        past_shows.append({ 
          'venue_id': venue.id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': show.start_time
        })
      else:
        upcoming_shows.append({ 
          'venue_id': venue.id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': show.start_time
        }) 

    show_artist.update({'past_shows' : past_shows })
    show_artist.update({'upcoming_shows' : upcoming_shows })
    show_artist.update({'past_shows_count' : len(past_shows)})
    show_artist.update({'upcoming_shows_count' : len(upcoming_shows)})
  
  return render_template('pages/show_artist.html', artist=show_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    artist = Artist.query.get(artist_id)

    edit_name = request.form['name']
    if 'edit_name':
      artist.name = edit_name
    edit_city = request.form['city']
    if 'edit_city':
      artist.city = edit_city
    edit_state = request.form['state']
    if 'edit_state':
      artist.state = edit_state
    edit_address = request.form['address']
    if 'edit_address':
      artist.address = edit_address
    edit_phone = request.form['phone']
    if 'edit_phone':
      artist.phone = edit_phone
    edit_genres = request.form.getlist('genres')
    if 'edit_genres':
      artist.genres = edit_genres
    edit_website = request.form['website']
    if 'edit_website':
      artist.website = edit_website
    edit_facebook_link = request.form['facebook_link']
    if 'edit_facebook_link':
      artist.facebook_link = edit_facebook_link
    edit_image_link = request.form['image_link']
    if 'edit_image_link':
      artist.image_link = edit_image_link
    edit_seeking_venue = 'seeking_venue' in request.form
    if('edit_seeking_venue' != artist.seeking_venue):
      artist.seeking_venue = edit_seeking_venue
    edit_seeking_description = request.form['seeking_description']
    if 'edit_seeking_description':
      artist.seeking_description = edit_seeking_description

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print('error')
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    print('error')
    flash('An error occured while updating Artist ' + request.form['name'])
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    venue = Venue.query.get(venue_id)

    edit_name = request.form['name']
    if 'edit_name':
      venue.name = edit_name
    edit_city = request.form['city']
    if 'edit_city':
      venue.city = edit_city
    edit_state = request.form['state']
    if 'edit_state':
      venue.state = edit_state
    edit_address = request.form['address']
    if 'edit_address':
      venue.address = edit_address
    edit_phone = request.form['phone']
    if 'edit_phone':
      venue.phone = edit_phone
    edit_genres = request.form.getlist('genres')
    if 'edit_genres':
      venue.genres = edit_genres
    edit_website = request.form['website']
    if 'edit_website':
      venue.website = edit_website
    edit_facebook_link = request.form['facebook_link']
    if 'edit_facebook_link':
      venue.facebook_link = edit_facebook_link
    edit_image_link = request.form['image_link']
    if 'edit_image_link':
      venue.image_link = edit_image_link
    edit_seeking_talent = 'seeking_talent' in request.form
    if 'edit_seeking_talent' != venue.seeking_talent:
      venue.seeking_talent = edit_seeking_talent
    edit_seeking_description = request.form['seeking_description']
    if 'edit_seeking_description':
      venue.seeking_description = edit_seeking_description

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occured while updating Venue ' + request.form['name'])
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    seeking_venue = 'seeking_venue' in request.form
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state, address=address, phone=phone, genres=genres, 
                      website=website, facebook_link=facebook_link, image_link=image_link,
                      seeking_venue=seeking_venue, seeking_description=seeking_description
                    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occured. Artist ' + request.form['name'] + ' could not be listed.')
  else: 
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  shows = Show.query.all()
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    data.append({ 
      'venue_id': venue.id,
      'venue_name': venue.name,
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time
     })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']
    
    show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on successful db insert, flash success
    flash('An error occurred. Show could not be listed.')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''