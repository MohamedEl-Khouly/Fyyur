import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# USER and PASSWORD are set as enviroment variables in The enviroment.  
# Replace with your Postgres user and password
USER = os.environ.get('POSTGRES_USER')
PASSWORD = os.environ.get('POSTGRES_PASS')
SQLALCHEMY_DATABASE_URI = f'postgres://{USER}:{PASSWORD}@localhost:5432/fyyurapp'
