from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db = SQLAlchemy()

class Show(db.Model):
    __tablename__ = "shows"
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
  shows= db.relationship('Show', cascade = "all,delete", backref='venues', lazy='joined')
  
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
  shows = db.relationship('Show', cascade = "all,delete", backref='artists', lazy='joined')


  def __repr__(self):
    return f'<Artist {self.id} {self.name}'
