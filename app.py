from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text,select
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Set a secret key for session management
db = SQLAlchemy(app)

@app.before_request
def before_request():
    # Ensure foreign key constraints are enabled in SQLite
    db.session.execute(text('PRAGMA foreign_keys = ON'))

# Define Location model
class Location(db.Model):
    __tablename__ = 'location'
    location_id = db.Column(db.String, primary_key=True)

# Define Product model
class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.String, primary_key=True)
    location_id = db.Column(db.String, db.ForeignKey('location.location_id', ondelete='SET NULL'))
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # Set default and update timestamps
