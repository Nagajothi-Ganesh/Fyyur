#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import flask
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from pytz import timezone
from datetime import datetime
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

migrate = Migrate(app,db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue_artist(db.Model):
    __tablename__ = "venue_artist"
    id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime(timezone=True), nullable=True, default=datetime.utcnow())
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    
 
class Venue(db.Model):
  __tablename__ = "venues"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  image_link = db.Column(db.String(500))
  website_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean,default=False)
  seeking_desc = db.Column(db.String(200))
  venue_artist = db.relationship('Venue_artist', cascade = "all,delete", backref='venue_parent', lazy=True)
  
  def __repr__(self):
    return f'<Venue {self.id} {self.name}'
    
class Artist(db.Model):
  __tablename__ = "artists"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
  image_link = db.Column(db.String(500))
  website_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean,default=False)
  seeking_desc = db.Column(db.String(200))
  venue_artist = db.relationship('Venue_artist', cascade = "all,delete", backref='artist_parent', lazy=True)


  def __repr__(self):
    return f'<Artist {self.id} {self.name}'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  error = False
  try:
    venues_list = Venue.query.order_by('city','state').all()
    if bool(venues_list):
      venues_hold = {}
      venues_dict = []
      data = []
      item = {}
      todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
      
      c_city = venues_list[0].city
      s_state = venues_list[0].state
      for venues in venues_list:
        upcoming_shows = Venue_artist.query.filter(Venue_artist.venue_id == venues.id, Venue_artist.start_time > todays_datetime).all()
        if (venues.city == c_city and venues.state == s_state):
          item = {
            "city" : venues.city,
            "state" : venues.state,
            "venues" : []
          }
          venues_hold = {
            "id" : venues.id,
            "name" : venues.name,
            "num_upcoming_shows" : upcoming_shows
          }
          venues_dict.append(venues_hold)
        else:
          item["venues"] = venues_dict
          data.append(item)
          c_city = venues.city
          s_state = venues.state
          item = {
            "city" : venues.city,
            "state" : venues.state,
            "venues" : []
          }
          venues_hold = {}
          venues_dict = []  
          venues_hold = {
            "id" : venues.id,
            "name" : venues.name,
            "num_upcoming_shows" : upcoming_shows
          }
          venues_dict.append(venues_hold)
      item["venues"] = venues_dict
      data.append(item)

      return render_template('pages/venues.html', areas=data)
    else:
      flash("No Venues to list.")
      return render_template('pages/home.html')
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())

  finally:
    db.session.close()
      

@app.route('/venues/search', methods=['POST'])
def search_venues():
  error = False
  venue_hold = []
  body = {}
  try:
    search_term=request.form.get('search_term', '')
    venue_list = Venue.query.filter(func.lower(Venue.name).like("%" + func.lower(search_term) + "%")).all()
    result_count = len(venue_list)
    for venue in venue_list:
      result = {
        "id": venue.id,
        "name": venue.name,
      }
      venue_hold.append(result)
    response = {
      "count": result_count,
      "data": venue_hold
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
    
  
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  error = False
  try:
    hold_updict = []
    hold_ptdict = []
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    venue_details = Venue.query.get(venue_id)
    up_shows = Venue_artist.query.filter(Venue_artist.venue_id == venue_id, Venue_artist.start_time > todays_datetime).all()
    upshows_count = len(up_shows)
    for show in up_shows:
      artist_det = Artist.query.get(show.artist_id)
      hold_upshow = {
        "artist_id": artist_det.id,
        "artist_name": artist_det.name,
        "artist_image_link": artist_det.image_link,
        "start_time": str(show.start_time)
      }
      hold_updict.append(hold_upshow)
    pt_shows = Venue_artist.query.filter(Venue_artist.venue_id == venue_id, Venue_artist.start_time < todays_datetime).all()
    past_count = len(pt_shows)
    for show in pt_shows:
      artist_det = Artist.query.get(show.artist_id)
      hold_ptshow = {
        "artist_id": artist_det.id,
        "artist_name": artist_det.name,
        "artist_image_link": artist_det.image_link,
        "start_time": str(show.start_time)
      }
      hold_ptdict.append(hold_ptshow)
    
    data={
      "id": venue_details.id,
      "name": venue_details.name,
      "genres": venue_details.genres,
      "address": venue_details.address,
      "city": venue_details.city,
      "state": venue_details.state,
      "phone": venue_details.phone,
      "website": venue_details.website_link,
      "facebook_link": venue_details.facebook_link,
      "seeking_talent": venue_details.seeking_talent,
      "seeking_desc": venue_details.seeking_desc,
      "image_link": venue_details.image_link,
      "past_shows": hold_ptdict,
      "upcoming_shows": hold_updict,
      "past_shows_count": past_count,
      "upcoming_shows_count": upshows_count,
    }
    
    return render_template('pages/show_venue.html', venue=data)
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
  finally:
    db.session.close()

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm(request.form)
  new_venue = Venue()

  try:
    if form.validate_on_submit():
      form.populate_obj(new_venue)
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
    else:
      error = True 
      if form.errors:
        for key,value in form.errors.items():
          flash("Error occurred in the field {}. Error is {}".format(f'{key}',f'{value}'))
      return render_template('forms/new_venue.html', form=form)
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
    db.session.rollback()
  finally:
    db.session.close()

@app.route('/venuesdel/<int:venue_id>')
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        error = True
        print("Exception occurred: {}".format(e))
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return render_template('pages/home.html')
  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  error = False
  data= []
  try:
    artist_list = Artist.query.order_by('name').all()
    if bool(artist_list):
      for artists in artist_list:
        item = {
          "id" : artists.id,
          "name" : artists.name,
        }
        data.append(item)
      
      return render_template('pages/artists.html', artists=data)
    else:
      flash("No Artists to list.")
      return render_template('pages/home.html')
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
  finally:
    db.session.close()

@app.route('/artists/search', methods=['POST'])
def search_artists():

  error = False
  artist_hold = []
  body = {}
  try:
    search_term=request.form.get('search_term', '')
    artist_list = Artist.query.filter(func.lower(Artist.name).like("%" + func.lower(search_term) + "%")).all()
    result_count = len(artist_list)
    for artist in artist_list:
      result = {
        "id": artist.id,
        "name": artist.name,
      }
      artist_hold.append(result)
    response = {
      "count": result_count,
      "data": artist_hold
    }
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info()) 
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  error = False
  try:
    hold_updict = []
    hold_ptdict = []
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    artist_details = Artist.query.get(artist_id)
    up_shows = Venue_artist.query.filter(Venue_artist.artist_id == artist_id, Venue_artist.start_time > todays_datetime).all()
    upshows_count = len(up_shows)
    for show in up_shows:
      venue_det = Venue.query.get(show.venue_id)
      hold_upshow = {
        "venue_id": venue_det.id,
        "venue_name": venue_det.name,
        "venue_image_link": venue_det.image_link,
        "start_time": str(show.start_time)
      }
      hold_updict.append(hold_upshow)
    pt_shows = Venue_artist.query.filter(Venue_artist.artist_id == artist_id, Venue_artist.start_time < todays_datetime).all()
    past_count = len(pt_shows)
    for show in pt_shows:
      venue_det = Venue.query.get(show.venue_id)
      hold_ptshow = {
        "venue_id": venue_det.id,
        "venue_name": venue_det.name,
        "venue_image_link": venue_det.image_link,
        "start_time": str(show.start_time)
      }
      hold_ptdict.append(hold_ptshow)
      
    data={
      "id": artist_details.id,
      "name": artist_details.name,
      "genres": artist_details.genres,
      "city": artist_details.city,
      "state": artist_details.state,
      "phone": artist_details.phone,
      "website": artist_details.website_link,
      "facebook_link": artist_details.facebook_link,
      "seeking_venue": artist_details.seeking_venue,
      "seeking_desc": artist_details.seeking_desc,
      "image_link": artist_details.image_link,
      "past_shows": hold_ptdict,
      "upcoming_shows": hold_updict,
      "past_shows_count": past_count,
      "upcoming_shows_count": upshows_count,
    }

    return render_template('pages/show_artist.html', artist=data)
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
  finally:
    db.session.close()

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  error = False
  try: 
    result = Artist.query.get(artist_id)
    artist={  
     "id": result.id,
     "name": result.name,
   }
  
    form = ArtistForm(obj=result)
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
  finally:
    db.session.close()
    
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  error = False
  try:
    form = ArtistForm(request.form)
    print(form.seeking_desc)
    new_artist = Artist.query.get(artist_id)
    if form.validate_on_submit():
      form.populate_obj(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))
    else:
      error = True 
      if form.errors:
        for key,value in form.errors.items():
          flash("Error occurred in the field {}. Error is {}".format(f'{key}',f'{value}'))
      return render_template('forms/new_artist.html', form=form)
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
    db.session.rollback()
  finally:
    db.session.close()

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  error = False
  try:
    result = Venue.query.get(venue_id)
    venue={  
     "id": result.id,
     "name": result.name,
    }
    form = VenueForm()
    form = VenueForm(obj=result)
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
    db.session.rollback()
  finally:
    db.session.close()  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    form = VenueForm(request.form)
    new_venue = Venue.query.get(venue_id)
    if form.validate_on_submit():
      form.populate_obj(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_venue', venue_id=venue_id))
    else:
      error = True 
      if form.errors:
        for key,value in form.errors.items():
          flash("Error occurred in the field {}. Error is {}".format(f'{key}',f'{value}'))
      return render_template('forms/new_venue.html', form=form)
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
    db.session.rollback()
  finally:
    db.session.close()
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    form = ArtistForm(request.form)
    new_artist = Artist()
    if form.validate_on_submit():
      print(form)
      form.populate_obj(new_artist)
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
    else:
      error = True 
      if form.errors:
        for key,value in form.errors.items():
          flash("Error occurred in the field {}. Error is {}".format(f'{key}',f'{value}'))
      return render_template('forms/new_artist.html', form=form)
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
    db.session.rollback()
  finally:
    db.session.close()

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  error = False
  data = []
  try:
    shows_list = db.session.query(
      Venue.name.label('venue_name'), 
      Artist.name.label('artist_name'),
      Artist.image_link.label('artist_image'), 
      Venue_artist.id.label('venart_id'), 
      Venue_artist.venue_id.label('venue_id'), 
      Venue_artist.artist_id.label('artist_id'), 
      Venue_artist.start_time.label('start_time')
    ).filter(
         Venue.id == Venue_artist.venue_id,
    ).filter(
         Artist.id == Venue_artist.artist_id,
    ).all()
    
    if bool(shows_list):
      for shows in shows_list:
        item = {
          "venue_id": shows.venue_id,
          "venue_name": shows.venue_name,
          "artist_id": shows.artist_id,
          "artist_name": shows.artist_name,
          "artist_image_link": shows.artist_image,
          "start_time": str(shows.start_time)
        }
        data.append(item)
  
      return render_template('pages/shows.html', shows=data)
    else:
      flash("No Shows to list.")
      return render_template('pages/home.html')
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
    db.session.rollback()
  finally:
    db.session.close()

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    form = ShowForm(request.form)
    new_show = Venue_artist()
    if form.validate_on_submit():
      form.populate_obj(new_show)
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
    else:
      error = True 
      if form.errors:
        for key,value in form.errors.items():
          flash("Error occurred in the field {}. Error is {}".format(f'{key}',f'{value}'))
      return render_template('forms/new_show.html', form=form)
  except Exception as e:
    error = True
    print("Exception occurred: {}".format(e))
    db.session.rollback()
  finally:
    db.session.close()


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
