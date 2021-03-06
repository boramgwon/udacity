#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import app, db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.
    # make groups by city, state and then use them as filters to create
    # required data set

    locals = []
    venues = Venue.query.all()
    for place in Venue.query.distinct(Venue.city, Venue.state).all():
        locals.append({
            'city': place.city,
            'state': place.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name,
            } for venue in venues if
                venue.city == place.city and venue.state == place.state]
        })
    return render_template('pages/venues.html', areas=locals)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live
    # Music & Coffee"
    term = request.form['search_term']
    sql_term = "%{}%".format(term)
    venues = Venue.query.filter(Venue.name.ilike(sql_term)).all()

    response = {
        'count': len(venues)
    }
    response.update({'data': venues})

    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live
    # Music & Coffee"

    venue = Venue.query.get(venue_id)

    past_shows = list(filter(lambda x: x.start_time < datetime.today(), venue.shows))
    upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), venue.shows))

    past_shows = list(map(lambda x: x.show_artist(), past_shows))
    upcoming_shows = list(map(lambda x: x.show_artist(), upcoming_shows))

    data = venue.format()

    data['past_shows'] = past_shows
    data['past_shows_count'] = len(past_shows)

    data['upcoming_shows'] = upcoming_shows
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    if form.validate():
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

            venue = Venue(
                name=name,
                city=city,
                state=state,
                address=address,
                phone=phone,
                genres=genres,
                website=website,
                facebook_link=facebook_link,
                image_link=image_link,
                seeking_talent=seeking_talent,
                seeking_description=seeking_description)
            db.session.add(venue)
            db.session.commit()
        except BaseException:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            # on unsuccessful db insert, flash an error instead.
            flash(
                'An error occured. Venue ' +
                request.form['name'] +
                ' could not be listed.')
        else:
            # on successful db insert, flash success
            flash(
                'Venue ' +
                request.form['name'] +
                ' was successfully listed!')
        return render_template('pages/home.html')

    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the
    # homepage
    error = False

    try:
        db.session.query(Venue).filter(Venue.id == venue_id).delete()
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print("error on deleting venue!")
    finally:
        db.session.close()
    if error:
        flash('Venue id ' + str(venue_id) + ' was not deleted')
    else:
        flash('Venue id ' + str(venue_id) + ' was deleted')

    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    term = request.form['search_term']
    sql_term = "%{}%".format(term)
    artists = Artist.query.filter(Artist.name.ilike(sql_term)).all()

    response = {
        'count': len(artists)
    }
    response.update({'data': artists})

    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)

    show_artist = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
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
    current_time = datetime.now()
    shows = db.session.query(
        Venue.id.label('venue_id'),
        Venue.name.label('venue_name'),
        Venue.image_link.label('venue_image_link'),
        Show.start_time.label('start_time')).join(Show).filter(
        Show.artist_id == artist_id).all()

    if(shows):
        for show in shows:
            start_time = datetime.strptime(
                show.start_time, '%Y-%m-%d %H:%M:%S')

            if(current_time > start_time):
                past_shows.append(show)
            else:
                upcoming_shows.append(show)

        show_artist.update({
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        })

    return render_template('pages/show_artist.html', artist=show_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.address.data = artist.address
    form.phone.data = artist.phone
    form.image_link.data = artist.image_link
    form.genres.data = artist.genres
    form.website.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    try:
        artist = Artist.query.get(artist_id)

        edit_name = request.form['name']
        if edit_name is not artist.name:
            artist.name = edit_name
        edit_city = request.form['city']
        if edit_city is not artist.city:
            artist.city = edit_city
        edit_state = request.form['state']
        if edit_state is not artist.state:
            artist.state = edit_state
        edit_address = request.form['address']
        edit_phone = request.form['phone']
        if edit_phone is not artist.phone:
            artist.phone = edit_phone
        edit_genres = request.form.getlist('genres')
        if edit_genres is not artist.genres:
            artist.genres = edit_genres
        edit_website = request.form['website']
        if edit_website is not artist.website:
            artist.website = edit_website
        edit_facebook_link = request.form['facebook_link']
        if edit_facebook_link is not artist.facebook_link:
            artist.facebook_link = edit_facebook_link
        edit_image_link = request.form['image_link']
        if edit_image_link is not artist.image_link:
            artist.image_link = edit_image_link
        edit_seeking_venue = 'seeking_venue' in request.form
        if(edit_seeking_venue is not artist.seeking_venue):
            artist.seeking_venue = edit_seeking_venue
        edit_seeking_description = request.form['seeking_description']
        if edit_seeking_description is not artist.seeking_description:
            artist.seeking_description = edit_seeking_description

        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occured while updating Artist ' + request.form['name'])
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = EditVenueForm()
    venue = Venue.query.get(venue_id)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.genres.data = venue.genres
    form.website.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = EditVenueForm(request.form)
    if form.validate():
        error = False
        try:
            venue = Venue.query.get(venue_id)

            edit_name = request.form['name']
            if edit_name is not venue.name:
                venue.name = edit_name
            edit_city = request.form['city']
            if edit_city is not venue.city:
                venue.city = edit_city
            edit_state = request.form['state']
            if edit_state is not venue.state:
                venue.state = edit_state
            edit_address = request.form['address']
            if edit_address is not venue.address:
                venue.address = edit_address
            edit_phone = request.form['phone']
            if edit_phone is not venue.phone:
                venue.phone = edit_phone
            edit_genres = request.form.getlist('genres')
            if edit_genres is not venue.genres:
                venue.genres = edit_genres
            edit_website = request.form['website']
            if edit_website is not venue.website:
                venue.website = edit_website
            edit_facebook_link = request.form['facebook_link']
            if edit_facebook_link is not venue.facebook_link:
                venue.facebook_link = edit_facebook_link
            edit_image_link = request.form['image_link']
            if edit_image_link is not venue.image_link:
                venue.image_link = edit_image_link
            edit_seeking_talent = 'seeking_talent' in request.form
            if edit_seeking_talent is not venue.seeking_talent:
                venue.seeking_talent = edit_seeking_talent
            edit_seeking_description = request.form['seeking_description']
            if edit_seeking_description is not venue.seeking_description:
                venue.seeking_description = edit_seeking_description

            db.session.commit()
        except BaseException:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            flash(
                'An error occured while updating Venue ' +
                request.form['name'])
        else:
            flash(
                'Venue ' +
                request.form['name'] +
                ' was successfully updated!')

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
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    error = False
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        website = request.form['website']
        facebook_link = request.form['facebook_link']
        image_link = request.form['image_link']
        seeking_venue = 'seeking_venue' in request.form
        seeking_description = request.form['seeking_description']

        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            website=website,
            facebook_link=facebook_link,
            image_link=image_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash(
            'An error occured. Artist ' +
            request.form['name'] +
            ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per
    # venue.

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
    # insert form data as a new Show record in the db, instead
    error = False
    try:
        venue_id = request.form['venue_id']
        artist_id = request.form['artist_id']
        start_time = request.form['start_time']

        show = Show(
            venue_id=venue_id,
            artist_id=artist_id,
            start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on successful db insert, flash success
        flash('An error occurred. Show could not be listed.')
    else:
        # on unsuccessful db insert, flash an error instead.
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
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
