#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import ( 
  Flask, render_template,
  request, Response,
  flash, redirect,
  url_for
)
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import func, desc
from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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
  artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()
  venues = Venue.query.order_by(desc(Venue.id)).limit(10).all()
  return render_template('pages/home.html',artists=artists,venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data=[]
  # areas are the Distinct ( City,state) combinations avilable in the Data set
  areas = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  for area in areas:
    city,state = area
    venues_in_area =  Venue.query.filter_by(city=city, state=state).all()
    data.append({
      'city': city,
      'state': state,
      'venues': venues_in_area
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(func.lower(Venue.name).\
    like('%'+search_term.lower()+"%")).all()
  data = []
  
  for venue in venues:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(venue.coming_shows()),
    })
  response ={
    'count': len(data),
    'data' : data
  }
  return render_template(
    'pages/search_venues.html', 
    results=response, 
    search_term=request.form.get('search_term', '')
  )

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  past_shows = db.session.query(Artist,Show).join(Show).join(Venue).\
    filter(
      Show.venue_id == venue_id,
      Show.artist_id == Artist.id,
      Show.start_time <= datetime.now()
    ).all()
  upcoming_shows = db.session.query(Artist,Show).join(Show).join(Venue).\
    filter(
      Show.venue_id == venue_id,
      Show.artist_id == Artist.id,
      Show.start_time > datetime.now()
    ).all() 
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
    "past_shows": [{
      'start_time' : show.start_time.strftime("%m/%d/%Y, %H:%M"),
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link
    } for artist, show in past_shows],
    'past_shows_count': len(past_shows),
    "upcoming_shows": [{
      'start_time' : show.start_time.strftime("%m/%d/%Y, %H:%M"),
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link
    } for artist, show in upcoming_shows],
    'upcoming_shows_count': len(upcoming_shows),
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


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(func.lower(Artist.name).like('%'+search_term.lower()+"%")).all()
  data = []
  
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  response ={
    'count': len(data),
    'data' : data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  past_shows = db.session.query(Venue,Show).join(Show).join(Artist).\
    filter(
      Show.artist_id == artist_id,
      Show.venue_id == Venue.id,
      Show.start_time <= datetime.now()
    ).all()
  upcoming_shows = db.session.query(Venue,Show).join(Show).join(Artist).\
    filter(
      Show.artist_id == artist_id,
      Show.venue_id == Venue.id,
      Show.start_time > datetime.now()
    ).all()
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
      "past_shows": [{
        'start_time' : show.start_time.strftime("%m/%d/%Y, %H:%M"),
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link
      }for venue,show in past_shows],
      "past_shows_count":len(past_shows),
      "upcoming_shows": [{
        'start_time' : show.start_time.strftime("%m/%d/%Y, %H:%M"),
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link
      }for venue,show in upcoming_shows],
      "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try :
    artist=Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.website = request.form.get('website_link')
    artist.facebook_link = request.form.get('facebook_link')
    if request.form.get('seeking_venue') in ('y', True, 't', 'True'):
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False
    artist.seeking_description = request.form.get('seeking_description')
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form.get('image_link')
    db.session.commit()
    flash('Artist ' + new_artist.name + ' was successfully Updated!')
  except :
    db.session.rollback()
    flash('An error occurred. Artist' + request.form['name'] + ' could not be Updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id) 
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try :
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.phone = request.form.get('phone')
    venue.address = request.form.get('address')
    venue.website = request.form.get('website_link')
    venue.facebook_link = request.form.get('facebook_link')
    if request.form.get('seeking_talent') in ('y', True, 't', 'True'):
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False
    venue.seeking_description = request.form.get('seeking_description')
    venue.image_link = request.form.get('image_link')
    venue.genres = request.form.getlist('genres')
    db.session.commit()
    flash('Venue ' + new_venue.name + ' was successfully Updated!')
  except :
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be Updated.')
  finally:
    db.session.close()
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
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except :
    db.session.rollback()
    flash('An error occurred Show could not be listed.')
  finally:
    db.session.close()
  return redirect(url_for('shows'))

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
