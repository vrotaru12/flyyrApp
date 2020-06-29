#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from sqlalchemy import func, distinct
from flask_migrate import Migrate
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import distinct
import psycopg2
import datetime


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#########################################################################
#MENThOR :Missing the requirement on using flask-migrate: you need to call:
#migrate = Migrate(app, db)
#########################################################################

# TODO: connect to a local postgresql database ----#DONE in config.py
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
show = db.Table('show',
  db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
  db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True), 
  db.Column('start_time', db.String)
)
  ################################ MENThOR #########################################
  #Implementing a many-to-many relationship is the correct way to go! However the syntax is slightly incorrect. Video 16 for Lesson 7 is a great resource for this.
  # The documentation on many-to-many relationship for SQLAlchemy is actually a wonderful and easy-to-read reference as well:
  # https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#many-to-many   
  # Specifically to your code here, you should declare relationship only with aritsts, not shows. 
  # This is because the Show class is the association table and only need to appear in the "secondary" field.
  ################################ MENThOR #########################################

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue =  db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))
    products = db.relationship('Venue', secondary=show, backref=db.backref('shows', lazy=True))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Venue(db.Model):
    __tablename__ = 'venue'
     ################################ MENThOR #########################################
    #past_shows, upcoming_shows and their count should NOT be stand-alone fields - whether a show is upcoming or past is determined by the current time - i.e., 
    # depends on when the request is made, a show could be upcoming or past.
    #You should implement just a relationship with a show field, and determine/query for past and upcoming shows, based on the time.
    #########################################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))
  
#db.create_all()

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

  ################################ MENThOR #########################################
  #  This is not quite what we want - venues should be categorized into their respective city and state - i.e. if two venues are in the same city and state, 
  # they should be listed under the same heading.
  # This is a tricky part to get it working and there are many potential ways to get it working. 
  # When I was approaching this problem, I made use of the "distinct" query and get all the distinct pairs of (State, City) first, 
  # then get the Venue objects corresponding to each pair.
  ################################ MENThOR #########################################
  obj = db.session.query(Venue.name, Venue.id, Venue.city, Venue.state).distinct(Venue.city,Venue.state).order_by(Venue.city,Venue.state)
  allobj = Venue.query.all()
  data = []
  for i in obj:
    venues = []
    data.append(i)
    for j in allobj:
      if(i.city == j.city):
        venues.append({"id":j.id,"name":j.name})
    data.append({"venues":venues})

  
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

   ################################ MENThOR #########################################
  #    Search needs to be case-insensitive - using contains() couldn't quite achieve that. Take a look at ilike here:
  # https://docs.sqlalchemy.org/en/13/orm/internals.html?highlight=ilike#sqlalchemy.orm.attributes.QueryableAttribute.ilike
  ################################ MENThOR #########################################
  subs = request.form.get('search_term')
  ob = Venue.query.filter(Venue.name.ilike('%'+subs+'%'))
  if ob.count() > 0:
    response ={
      "count": ob.count() ,
      "data": ob
    }
  else:
    response={"count": 0}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #data=Venue.query.filter(Venue.id == venue_id)
  
  connection = psycopg2.connect('dbname=mydb user=postgres password=pasolvon12')
  cursor = connection.cursor() 
  cursor1 = connection.cursor()
  cursor.execute('SELECT *from show where venue_id='+str(venue_id)+';')
  obj1 = cursor.fetchall()
  past_shows = []
  upcoming_shows = []
  for i in obj1:
    cursor1.execute('SELECT *from artist where id='+str(i[0])+';')
    artist_name = cursor1.fetchall()[0]
    if i[2] < datetime.datetime.now():
      past_shows.append({
      "artist_id": i[0],
      "artist_name": artist_name[1],
      "artist_image_link": artist_name[6],
      "start_time": str(i[2])})
    else:
      upcoming_shows.append({
      "artist_id": i[0],
      "artist_name": artist_name[1],
      "artist_image_link": artist_name[6],
      "start_time": str(i[2])})

  allobj = Venue.query.filter(Venue.id == venue_id)[0]
  
  data = {
    "id": allobj.id,
    "name":allobj.name,
    "genres": allobj.genres,
    "address": allobj.address,
    "city": allobj.city,
    "state":allobj.state,
    "phone": allobj.phone,
    "website":allobj.website,
    "facebook_link": allobj.facebook_link,
    "seeking_talent": allobj.seeking_talent,
    "seeking_description": allobj.seeking_description,
    "image_link":allobj.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    }
  ################################ MENThOR #########################################
  #While this certainly works, it is strongly preferable to use SQL query syntax.
  ################################ MENThOR #########################################
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST']) #vr done
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name = request.get_json()['name']
    city = request.get_json()['city']
    state = request.get_json()['state']
    address = request.get_json()['address']
    phone = request.get_json()['phone']
    genres = request.get_json()['genres']
    facebook_link = request.get_json()['facebook_link']
    insert = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link)
    db.session.add(insert)
    db.session.commit()
    flash('Venue ' +request.form['name']+'was successfully listed!')
  ################################ MENThOR #########################################
  #If you return here, the session will never be closed as finally is not called.
  ################################ MENThOR #########################################

  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue  could not be listed.')
    return False 
    ################################ MENThOR #########################################
    #When an error is encountered, you still need to return something or abort with an error.
    ################################ MENThOR #########################################
   
  finally:
    db.session.close()
    
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter(Venue.id==venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists') #vr done
def artists():
 # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  subs = request.form.get('search_term')
  ob = Artist.query.filter(Artist.name.ilike('%'+subs+'%'))
  if ob.count() > 0:
    response ={
      "count": ob.count() ,
      "data": ob
    }
  else:
    response={"count": 0}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #data = Artist.query.filter(Artist.id == artist_id)[0]

  connection = psycopg2.connect('dbname=mydb user=postgres password=pasolvon12')
  cursor = connection.cursor() 
  cursor1 = connection.cursor()
  cursor.execute('SELECT *from show where artist_id='+str(artist_id)+';')
  obj1 = cursor.fetchall()
  past_shows = []
  upcoming_shows = []
  for i in obj1:
    cursor1.execute('SELECT *from artist where id='+str(i[0])+';')
    artist_name = cursor1.fetchall()[0]
    if i[2] < datetime.datetime.now():
      past_shows.append({
      "artist_id": i[0],
      "artist_name": artist_name[1],
      "artist_image_link": artist_name[6],
      "start_time": str(i[2])})
    else:
      upcoming_shows.append({
      "artist_id": i[0],
      "artist_name": artist_name[1],
      "artist_image_link": artist_name[6],
      "start_time": str(i[2])})

  allobj = Artist.query.filter(Artist.id == artist_id)[0]
  
  data = {
    "id": allobj.id,
    "name":allobj.name,
    "genres": allobj.genres,
    "city": allobj.city,
    "state":allobj.state,
    "phone": allobj.phone,
    "website":allobj.website,
    "facebook_link": allobj.facebook_link,
    "seeking_venue": allobj.seeking_venue,
    "seeking_description": allobj.seeking_description,
    "image_link":allobj.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id)[0]
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    name = request.get_json()['name']
    genres = request.get_json()['genres']
    city = request.get_json()['city']
    state = request.get_json()['state']
    phone = request.get_json()['phone']
    facebook_link = request.get_json()['facebook_link']


    v = Venue.query.get(venue_id)

    v.name = name
    v.genres = genres
    v.city = city
    v.state = state
    v.phone = phone
    v.facebook_link = facebook_link
    db.session.commit()

    
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  obj = Venue.query.filter(Venue.id == venue_id)[0]
  return render_template('forms/edit_venue.html', form=form, venue=obj)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    name = request.get_json()['name']
    genres = request.get_json()['genres']
    address = request.get_json()['address']
    city = request.get_json()['city']
    state = request.get_json()['state']
    phone = request.get_json()['phone']
    facebook_link = request.get_json()['facebook_link']


    v = Venue.query.get(venue_id)

    v.name = name
    v.genres = genres
    v.address = address
    v.city = city
    v.state = state
    v.phone = phone
    v.facebook_link = facebook_link
    db.session.commit()

    
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST']) #vr done
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  aerror = False
  try:
    aname = request.get_json()['name']
    acity = request.get_json()['city']
    astate = request.get_json()['state']
    aphone = request.get_json()['phone']
    agenres = request.get_json()['genres']
    afacebook_link = request.get_json()['facebook_link']
    sendData= Artist(name=aname, city=acity, state=astate,  phone=aphone, genres=agenres, facebook_link=afacebook_link)
    db.session.add(sendData)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return jsonify({
      'name':sendData.name,
      'city':sendData.city,
      'state':sendData.state,
      'phone':sendData.phone,
      'genres':sendData.genres,
      'facebook_link':sendData.facebook_link
      
    })
    
    
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist could not be listed.')
    print(sys.exc_info())
    return False
  finally:
    db.session.close()
  # on successful db insert, flash success
 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  connection = psycopg2.connect('dbname=mydb user=postgres password=pasolvon12')
  cursor = connection.cursor()
  cursor.execute('SELECT *from show;')
  data = []
  obj = cursor.fetchall()
  for i in obj:
    data.append({
      "venue_id": i[1],#Venue.query.filter(Venue.id == i[1])[0].id,
      "venue_name":Venue.query.filter(Venue.id == i[1])[0].name,
      "artist_id": i[0],#Artist.query.filter(Artist.id == i[0])[1].id,
      "artist_name":Artist.query.filter(Artist.id == i[0])[0].name,
      "artist_image_link":Artist.query.filter(Artist.id == i[0])[0].image_link,
      "start_time": str(i[2])
    })
  
     ################################ MENThOR #########################################
      # This need to be actual data. To make the start_time usable to the template, you would need to convert it to string.
      #  Take a look at https://www.programiz.com/python-programming/datetime/strftime for a nice intro on the strftime function for DateTime class on Python. 
      # You can call strftime() on datetime and pass in a string to specify the specific output you would like.
      ################################ MENThOR #########################################
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create',methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.get_json()['artist_id']
    venue_id = request.get_json()['venue_id']
    start_time = request.get_json()['start_time']
    users.insert().values({"artist_id": artist_id, "venue_id": venue_id, "start_time":start_time})
    flash('Show was successfully listed!')
    return True
  except:
    error = True
    # db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    return False
  finally:
    db.session.close()
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
