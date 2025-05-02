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
 # Update the movement details in the database
        try:
            # Update only the movement details without affecting product quantity or location
            movement.product_id = product_id
            movement.from_location = from_location
            movement.to_location = to_location
            movement.timestamp = datetime.now()  # Update the timestamp to the current time
            
            db.session.commit()  # Commit the changes
            flash('Movement updated successfully!', 'success')
            return redirect(url_for('view_movements'))
        except Exception as e:
            db.session.rollback()  # Rollback on error
            flash('Error updating movement: {}'.format(str(e)), 'error')
            return redirect(url_for('view_movements'))
# If GET request, fetch the movement details for editing
    locations = Location.query.all()
    products = Product.query.all()

    return render_template('edit_movement.html', movement=movement, locations=locations, products=products)

@app.route('/product/move', methods=['POST'])
def move_product_view():
    data = request.form
    product_id = data['product_id']
    to_location = data['to_location']
    quantity = int(data['quantity'])

    existing_product = Product.query.filter_by(product_id=product_id).first()

    if existing_product:
        if existing_product.quantity < quantity:
            flash('Error: Not enough stock to move!', 'error')
            return redirect('/products')
        
        existing_product.quantity -= quantity

        existing_product_to = Product.query.filter_by(
            product_id=product_id, 
            location_id=to_location
        ).first()

        if existing_product_to:
            existing_product_to.quantity += quantity
        else:
            new_product = Product(
                product_id=product_id,
                location_id=to_location,
                quantity=quantity
            )
            db.session.add(new_product)

        db.session.commit()
        flash('Product moved successfully!', 'success')
        return redirect('/products')
    else:
        flash('Error: Product not found!', 'error')
        return redirect('/products')

@app.route('/product/edit/<product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    product = Product.query.get(product_id)
    locations = Location.query.all()
    
    if product is None:
        flash('Product not found', 'error')
        return redirect('/products')
    
if request.method == 'POST':
        new_product_id = request.form.get('product_id')
        location_id = request.form.get('location_id')
        quantity = request.form.get('quantity')

        if 'delete' in request.form:
            db.session.delete(product)
            db.session.commit()
            flash('Product deleted successfully!', 'success')
            return redirect('/products')

        existing_product = Product.query.filter_by(product_id=new_product_id).first()
        if existing_product and existing_product.product_id != product.product_id:
            flash('Product ID already exists. Please choose a different one.', 'error')
            return redirect(f'/product/edit/{product.product_id}')

        product.product_id = new_product_id
        product.location_id = location_id
        product.quantity = quantity
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect('/products')

    return render_template('edit_product.html', product=product, locations=locations)
@app.route('/movement/add', methods=['GET', 'POST'])
def add_movement_view():
    if request.method == 'POST':
        movement_id = request.form['movement_id']
        product_id = request.form['product_id']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        quantity = request.form.get('quantity', 0)

        # Ensure quantity is an integer
        try:
            quantity = int(quantity)
        except ValueError:
            quantity = 0  # Default to 0 if conversion fails

        print(f"Adding movement: ID={movement_id}, Product ID={product_id}, From={from_location}, To={to_location}, Quantity={quantity}")
   new_movement = ProductMovement(
            movement_id=movement_id,
            product_id=product_id,
            from_location=from_location,
            to_location=to_location,
            quantity=quantity
        )

        try:
            db.session.add(new_movement)
            db.session.commit()
            print("Movement added successfully.")
        except Exception as e:
            db.session.rollback()  # Roll back the session in case of error
            print("Error adding movement:", str(e))  # Log the exception

        return redirect(url_for('view_movements'))  # Redirect to the movements view

    products = Product.query.all()  # Fetch all products
    locations = Location.query.all()  # Fetch all locations

    return render_template('add_movement.html', products=products, locations=locations)
@app.route('/get_current_quantity', methods=['GET'])
def get_current_quantity():
    product_id = request.args.get('product_id')
    from_location = request.args.get('from_location')
    
    current_quantity = db.session.execute(
        select(Product.quantity)
        .where(Product.product_id == product_id)
        .where(Product.location_id == from_location)
    ).scalar()

    return jsonify({'quantity': current_quantity})


@app.route('/api/current_location', methods=['GET'])
def get_current_location():
    product_id = request.args.get('product_id')
    if not product_id:
        return jsonify({"error": "Product ID is required."}), 400

    product = Product.query.filter_by(product_id=product_id).first()
    if product and product.location_id:
        return jsonify({"current_location": product.location_id})
    
    return jsonify({"current_location": None})
@app.route('/api/locations', methods=['GET'])
def get_locations():
    product_id = request.args.get('product_id')
    from_location = request.args.get('from_location')  # Get from_location if provided
    if not product_id:
        return jsonify({"error": "Product ID is required."}), 400

    # Fetch all locations that are associated with the product
    locations = Location.query.all()  # Or fetch filtered locations as needed

    # Prepare the list of locations to return as JSON, excluding from_location
    location_list = [
        {"location_id": loc.location_id} 
        for loc in locations 
        if loc.location_id != from_location  # Exclude the from_location
    ]

    return jsonify({"locations": location_list})
