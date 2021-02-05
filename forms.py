from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import (
  StringField,
  SelectField,
  SelectMultipleField,
  DateTimeField
)
from wtforms.validators import DataRequired, AnyOf, URL, Regexp
from wtforms.fields.core import BooleanField
from enums import State, Genre

class ShowForm(Form):
    artist_id = SelectField(
        'artist_id',
        validators=[DataRequired()],
        coerce= int
    )
    venue_id = SelectField(
        'venue_id',
        validators=[DataRequired()],
        coerce= int
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', 
        validators=[DataRequired()]
    )
    city = StringField(
        'city', 
        validators=[DataRequired()]
    )
    state = SelectField(
        'state', 
        validators=[DataRequired()],
        choices= State.choices()
    )
    address = StringField(
        'address',
        validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[
          DataRequired(),
          Regexp(
            '^\d{3}-\d{3}-\d{4}$',
            message='phone is not in the correct format: ' + 'xxx-xxx-xxxx'
          )
        ]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired()],
        choices= Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', 
        validators=[URL()]
    )
    website_link = StringField(
        'website_link', 
        validators=[URL()]
    )    
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    
    seeking_description = StringField(
        'seeking_description'
    )

class ArtistForm(Form):
    name = StringField(
        'name', 
        validators=[DataRequired()]
    )
    city = StringField(
        'city', 
        validators=[DataRequired()]
    )
    state = SelectField(
        'state', 
        validators=[DataRequired()],
        choices= State.choices()
    )
    genres = SelectMultipleField(
        'genres', 
        validators=[DataRequired()],
        choices= Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link',
         validators=[URL()]
    )
    phone = StringField(
        'phone',
        validators=[
          Regexp(
            '^\d{3}-\d{3}-\d{4}$',
            message='phone is not in the correct format: ' + 'xxx-xxx-xxxx'
          )
        ]
    )
    image_link = StringField(
        'image_link'
    )
    website_link = StringField(
        'website_link', 
        validators=[URL()]
    )
    seeking_venue = BooleanField(
        'seeking_venue'        
    )
    seeking_description = StringField(
        'seeking_description'
    )
