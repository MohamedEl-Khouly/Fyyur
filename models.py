from flask_sqlalchemy import SQLAlchemy

db =  SQLAlchemy()

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
