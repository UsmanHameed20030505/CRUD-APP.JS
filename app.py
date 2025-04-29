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
def product_balance():
    # Query Balance table and order by timestamp for sorting
    balance_data = db.session.execute(text("""
        SELECT B.product_id, B.warehouse, B.quantity, P.timestamp
        FROM Balance B
        JOIN Product P ON B.product_id = P.product_id
        ORDER BY P.timestamp DESC
    """)).fetchall()

    # Organize data for HTML display (sorting handled in SQL query)
    balance_dict = {}
    for row in balance_data:
        warehouse = row.warehouse
        product_id = row.product_id
        quantity = row.quantity
        timestamp = row.timestamp
# Structure to group balances by warehouse and product
        if warehouse not in balance_dict:
            balance_dict[warehouse] = {'balances': {}}
        balance_dict[warehouse]['balances'][product_id] = {
            'quantity': quantity,
            'timestamp': timestamp
        }

    # Pass the organized data to the HTML template
    return render_template('product_balance.html', balance_data=balance_dict)

@app.route('/products', methods=['GET'])
def view_products():
    products = Product.query.all()
    return render_template('view_product.html', products=products)

from flask import flash, redirect, render_template, request, url_for
from datetime import datetime

@app.route('/movement/edit/<movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    movement = ProductMovement.query.get(movement_id)
if movement is None:
        flash('Movement not found!', 'error')
        return redirect(url_for('view_movements'))

    if request.method == 'POST':
        # Get data from the form
        product_id = request.form.get('product_id')
        from_location = request.form.get('from_location_hidden')  # Use the correct key for hidden field
        to_location = request.form.get('to_location')
        quantity = request.form.get('quantity')
