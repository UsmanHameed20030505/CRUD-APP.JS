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
# Define ProductMovement model
class ProductMovement(db.Model):
    __tablename__ = 'product_movement'
    
    movement_id = db.Column(db.String, primary_key=True)
    product_id = db.Column(db.String, db.ForeignKey('product.product_id'), nullable=False)
    from_location = db.Column(db.String, db.ForeignKey('location.location_id'), nullable=False)
    to_location = db.Column(db.String, db.ForeignKey('location.location_id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, movement_id, product_id, from_location, to_location, quantity=0):
        self.movement_id = movement_id
        self.product_id = product_id
        self.from_location = from_location
        self.to_location = to_location
        self.quantity = quantity

@app.route('/home')
def home_view():
    return render_template('home.html')

@app.route('/')
def index():
    return redirect('/home')

from sqlalchemy import text

@app.route('/product/balance', methods=['GET'])
