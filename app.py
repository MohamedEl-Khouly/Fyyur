#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.exc import SQLAlchemyError
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#Models are the database schema
#They are built using Flask-sqlAlchemy ORM
#The app has Three models(tables)
####1. Venue: holds data of venues and holds one-many relationship with shows
####2. Aritist: holds data for artist and holds one-many relationship with shows
####3. Show: holds data for Shows and relate artist to venue in a many-many relationship
#Some helper methods are defined in Venue and Artist to help in querries 

class Venue(db.Model):
    __tablename__ = 'venues'

    # Table Columns
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text, nullable=True)

    # Relationship defination
    shows = db.relationship(
      'Show',
      backref='venue',
      lazy=True,
      cascade='all, delete-orphan'
    )

    def __repr__(self):
      massege = f'< Venue {self.id}\nname: {self.name}\narea: {self.city},{self.state}\nphone: {self.phone}\naddress: {self.address}\nseeking Talent: {self.seeking_talent}\ngenres: {self.genres}>'
      return massege
    
    #helper methods
    # ___________________________ 
    #List of Id's for past shows
    def past_shows(self):
      currentTime = datetime.now()
      shows = [show for show in self.shows if show.start_time <= datetime.now()]
      return shows
      
    #List of Id's for coming shows
    def coming_shows(self):
      shows = [show for show in self.shows if show.start_time > datetime.now()]
      return shows


class Artist(db.Model):
    __tablename__ = 'artists'

    # Table Columns
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text, nullable=True)

    # Relationship 
    shows = db.relationship(
      'Show',
      backref='artist',
      lazy=True,
      cascade='all, delete-orphan'
    )

    def __repr__(self):
      massege = f'< Artist {self.id}\nname: {self.name}\narea: {self.city},{self.state}\nphone: {self.phone}\nseeking_venue: {self.seeking_venue}\ngenres: {self.genres}>'
      return massege
    
    #helper methods
    # ___________________________ 
    #List of Id's for past shows
    def past_shows(self):
      currentTime = datetime.now()
      #shows = self.shows.query.filter_by(Show.start_time <= currentTime).all()
      shows = [show for show in self.shows if show.start_time <= datetime.now()]
      return shows

    #List of Id's for coming shows
    def coming_shows(self):
      shows = [show for show in self.shows if show.start_time > datetime.now()]
      #shows = self.shows.query.filter_by(Show.start_time > currentTime).all()
      return shows

class Show(db.Model):
  __tablename__ = 'shows'


  # Table Columns
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  venue_id = db.Column(
    db.Integer,
    db.ForeignKey('venues.id'),
    nullable=False
  )
  artist_id = db.Column(
    db.Integer,
    db.ForeignKey('artists.id'),
    nullable=False
  )


  def __repr__(self):
    massege = f'< Show {self.id}\n Starts at {self.start_time}\nartist {self.artist_id}\n venue {self.venue_id}>'
    return massege

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
  data=[]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  if venue:
      past_shows = []
  for show in venue.past_shows():
    artist = Artist.query.get(show.artist_id)
    past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
    })
    
  upcoming_shows = []
  for show in venue.coming_shows():
    artist = Artist.query.get(show.artist_id)
    upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
    })

    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": True if venue.seeking_talent in (True, 't', 'True') else False,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link if venue.image_link else "",
      "past_shows" : past_shows,
      "upcoming_shows" : upcoming_shows
    }
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try :
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    address = request.form.get('address')
    website_link = request.form.get('website_link')
    facebook_link = request.form.get('facebook_link')
    if request.form.get('seeking_talent') in ('y', True, 't', 'True'):
      seeking_talent = True
    else:
      seeking_talent = False
    seeking_description = request.form.get('seeking_description')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    new_venue = Venue(
      name= name,
      city= city,
      state= state,
      phone= phone,
      address= address,
      facebook_link=facebook_link,
      website= website_link,
      seeking_talent= seeking_talent,
      seeking_description= seeking_description,
      genres= genres,
      image_link=image_link
    )
    print(new_venue)
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + new_venue.name + ' was successfully listed!')
  except :
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/venues.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  past_shows = []
  for show in artist.past_shows():    
    venue = Venue.query.get(show.venue_id)
    past_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(show.start_time)
    })
  coming_shows = []
  for show in artist.coming_shows():
    venue = Venue.query.get(show.venue_id)
    coming_shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time)
    })
  data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "seeking_venue": True if artist.seeking_venue in ('y', True, 't', 'True') else False,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link, 
      "facebook_link": artist.facebook_link,
      "website_link": artist.website,
      "past_shows": past_shows,
      "upcoming_shows": coming_shows
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={}
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={}
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try :
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    website_link = request.form.get('website_link')
    facebook_link = request.form.get('facebook_link')
    if request.form.get('seeking_venue') in ('y', True, 't', 'True'):
      seeking_venue = True
    else:
      seeking_venue = False
    seeking_description = request.form.get('seeking_description')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    new_artist = Artist(
      name= name,
      city= city,
      state= state,
      phone= phone,
      facebook_link=facebook_link,
      website= website_link,
      seeking_venue= seeking_venue,
      seeking_description= seeking_description,
      genres= genres,
      image_link= image_link
    )
    print(new_artist)
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + new_artist.name + ' was successfully listed!')
  except :
    db.session.rollback()
    flash('An error occurred. Artist' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/artists.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data=[]
  shows= Show.query.all()
  for show in shows:
    data.append({
      'start_time': str(show.start_time),
      'venue_id': show.venue_id,
      'artist_id': show.artist_id,
      'venue_name': show.venue.name,
      'artist_name':show.artist.name,
      'artist_image_link':show.artist.image_link,
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  form.artist_id.choices = [(artist.id,artist.name) for artist in Artist.query]
  form.venue_id.choices = [(venue.id, venue.name + f' ({venue.city}, {venue.state})') for venue in Venue.query]
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    start_time = request.form.get('start_time')
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    new_show = Show(
      start_time= start_time,
      venue_id= venue_id,
      artist_id= artist_id
    )
    print(Show)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except :
    db.session.rollback()
    flash('An error occurred Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/shows.html')

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
