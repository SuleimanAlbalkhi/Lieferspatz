from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ändern Sie dies in der Produktion!

# Verbindung zur Datenbank herstellen
conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()

# Tabellen erstellen (nur einmal ausführen)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Restaurants (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        username TEXT NOT NULL,
        address TEXT NOT NULL,
        description TEXT,
        image_path TEXT,
        password_hash TEXT NOT NULL,
        opening_time TIME  NOT NULL,
        closing_time TIME  NOT NULL,
        delivery_radius TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        username TEXT NOT NULL,
        address TEXT NOT NULL,
        postal_code INTEGER  NOT NULL,
        password_hash TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS MenuItems (
        id INTEGER PRIMARY KEY,
        restaurant_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price FLOAT NOT NULL,
        image_path TEXT,
        FOREIGN KEY(restaurant_id) REFERENCES Restaurants(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        restaurant_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        note TEXT,
        total_price FLOAT NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status Text,
        FOREIGN KEY(user_id) REFERENCES Users(id),
        FOREIGN KEY(restaurant_id) REFERENCES Restaurants(id),
        FOREIGN KEY(item_id) REFERENCES MenuItems(id)
    )
''')



conn.commit()
conn.close()

# Begrüßungsseite und Auswahl des Benutzertyps
@app.route('/', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        user_type = request.form['user_type']
        if user_type == 'user':
            return redirect(url_for('login_user'))
        elif user_type == 'restaurant':
            return redirect(url_for('login_restaurant'))

    return render_template('welcome.html')

# Route für die Anmeldung von Benutzern
@app.route('/login/user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        
        cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
        user = cursor.fetchone()

        # Überprüfen, ob der Benutzer existiert und das Passwort korrekt ist
        if user and check_password_hash(user[6], password):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard_user'))

    return render_template('login_user.html')

# Route für die Anmeldung von Restaurants
@app.route('/login/restaurant', methods=['GET', 'POST'])
def login_restaurant():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        
        cursor.execute("SELECT * FROM Restaurants WHERE username=?", (username,))
        restaurant = cursor.fetchone()

        # Überprüfen, ob das Restaurant existiert und das Passwort korrekt ist
        if restaurant and check_password_hash(restaurant[6], password):
            session['restaurant_id'] = restaurant[0]

            return redirect(url_for('dashboard_restaurant'))

    return render_template('login_restaurant.html')

# Route für die Registrierung von Benutzern
@app.route('/register/user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        address = request.form['address']
        postal_code = request.form['postal_code']
        password = request.form['password']

        # Passwort hashen
        password_hash = generate_password_hash(password)


        
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Benutzer in die Datenbank einfügen
        cursor.execute("INSERT INTO Users (first_name, last_name, username, address, postal_code, password_hash) VALUES (?, ?, ?, ?, ?, ?)",
               (first_name, last_name, username, address, postal_code, password_hash))


        
        conn.commit()
        conn.close()
        

        return redirect(url_for('login_user'))

    return render_template('register_user.html')

# Route für die Registrierung von Restaurants
@app.route('/register/restaurant', methods=['GET', 'POST'])
def register_restaurant():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        address = request.form['address']
        description = request.form['description']
        image_path = request.form['image_path']
        password = request.form['password']
        opening_time = request.form['opening_time']
        closing_time = request.form['closing_time']
        delivery_radius = request.form['delivery_radius']

        # Split the comma-separated string into a list of permissible postal codes
        delivery_radius_list = [code.strip() for code in delivery_radius.split('/n')]

        # Convert the list to a comma-separated string for storage in the database
        delivery_radius_str = ','.join(delivery_radius_list)

        # Passwort hashen
        password_hash = generate_password_hash(password)

        
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        
        cursor.execute("INSERT INTO Restaurants (name, address, username, description, image_path, password_hash, opening_time, closing_time, delivery_radius) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (name, address, username, description, image_path, password_hash, opening_time, closing_time, delivery_radius or ''))



        
        conn.commit()
        conn.close()

        
        return redirect(url_for('login_restaurant'))

    return render_template('register_restaurant.html')



@app.route('/menu', methods=['GET'])
def view_menu():
    if session.get('restaurant_id'):
        restaurant_id = session['restaurant_id']

        
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Speisekarte des Restaurants abrufen
        cursor.execute("SELECT * FROM MenuItems WHERE restaurant_id=?", (restaurant_id,))
        menu_items = cursor.fetchall()

        
        print(f"Retrieved menu items: {menu_items}")

        
        conn.close()

        return render_template('view_menu.html', menu_items=menu_items)

    return redirect(url_for('login_restaurant'))
               


@app.route('/add_item', methods=['GET', 'POST'])
def add_menu_item():
    if 'restaurant_id' in session:
        file_path = None  
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']

         

            
            restaurant_id = session['restaurant_id']

            
            conn = sqlite3.connect('mydatabase.db')
            cursor = conn.cursor()

            cursor.execute("INSERT INTO MenuItems (name, description, price, image_path, restaurant_id) VALUES (?, ?, ?, ?, ?)",
                           (name, description, price, file_path, restaurant_id))

            
            conn.commit()
            conn.close()

            flash('Item wurde zur Speisekarte hinzugefügt.', 'success')

        return render_template('add_menu_item.html')

    return redirect(url_for('login_restaurant'))

@app.route('/remove_item/<int:item_id>', methods=['GET'])
def remove_menu_item(item_id):
    if 'restaurant_id' in session:
        
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        
        cursor.execute("DELETE FROM MenuItems WHERE id=?", (item_id,))

        
        conn.commit()
        conn.close()

        flash('Item wurde von der Speisekarte entfernt.', 'success')

        return redirect(url_for('view_menu'))

    return redirect(url_for('login_restaurant'))

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    if 'restaurant_id' in session:
        
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        
        file_path = None

        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']

            

            
            cursor.execute("UPDATE MenuItems SET name=?, description=?, price=?, image_path=? WHERE id=?",
                           (name, description, price, file_path, item_id))

            
            conn.commit()
            conn.close()

            flash('Item wurde aktualisiert.', 'success')
            return redirect(url_for('view_menu'))

        
        cursor.execute("SELECT * FROM MenuItems WHERE id=?", (item_id,))
        menu_item = cursor.fetchone()

        
        conn.close()

        return render_template('edit_menu_item.html', menu_item=menu_item)

    return redirect(url_for('login_restaurant'))




@app.route('/delete_restaurant/<int:restaurant_id>', methods=['GET'])
def delete_restaurant(restaurant_id):
    
    if 'restaurant_id' in session:
        logged_in_restaurant_id = session['restaurant_id']

        
        if logged_in_restaurant_id == restaurant_id:
            
            conn = sqlite3.connect('mydatabase.db')
            cursor = conn.cursor()

            
            cursor.execute("DELETE FROM Restaurants WHERE id=?", (restaurant_id,))

           
            conn.commit()
            conn.close()

            
            flash('The restaurant has been successfully deleted.', 'success')

            
            return redirect(url_for('welcome'))

    
    return redirect(url_for('login_restaurant'))



# Dashboard for logged-in Restaurants
@app.route('/dashboard/restaurant')
def dashboard_restaurant():
    if 'restaurant_id' in session:
        restaurant_id = session['restaurant_id']

        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        
        cursor.execute("SELECT id, name FROM Restaurants WHERE id=?", (restaurant_id,))
        restaurant = cursor.fetchone()

        conn.close()

        restaurant_info = None  
        if restaurant:
            restaurant_info = {
                'id': restaurant[0],
                'name': restaurant[1],
            }
            session['restaurant_name'] = restaurant_info['name']

        return render_template('dashboard_restaurant.html', restaurant_info=restaurant_info)

    return redirect(url_for('login_restaurant'))



def query_restaurants_by_postal_code(postal_code):
   
    with sqlite3.connect('mydatabase.db') as conn:
        cursor = conn.cursor()

        current_time = datetime.now().time()

        
        cursor.execute("SELECT * FROM Restaurants")
        restaurants = cursor.fetchall()

        filtered_restaurants = []

        for restaurant in restaurants:
            
            delivery_radius_str = restaurant[9]
            delivery_radius_list = [code.strip() for code in delivery_radius_str.replace('\r\n', ',').split(',')]


            # opening and closing times
            opening_time_str = restaurant[7]
            closing_time_str = restaurant[8]

            opening_time = datetime.strptime(opening_time_str, '%H:%M').time()
            closing_time = datetime.strptime(closing_time_str, '%H:%M').time()

            # Check if the user's postal code is in the delivery radius
            if postal_code in delivery_radius_list and opening_time <= current_time <= closing_time:
                filtered_restaurants.append(restaurant)
            

    return filtered_restaurants


def query_menu_items_by_restaurant_id(restaurant_id):
    
    with sqlite3.connect('mydatabase.db') as conn:
        cursor = conn.cursor()

        
        cursor.execute("SELECT * FROM MenuItems WHERE restaurant_id=?", (restaurant_id,))
        menu_items = cursor.fetchall()

    return menu_items

# Route to display the details of a specific restaurant
@app.route('/restaurant/<int:restaurant_id>', methods=['GET'])
def restaurant_detail(restaurant_id):
    if 'user_id' in session:
        
        restaurant = query_restaurant_by_id(restaurant_id)
        menu_items = query_menu_items_by_restaurant_id(restaurant_id)
        if restaurant:
            return render_template('restaurant_detail.html', restaurant=restaurant, menu_items=menu_items)
    return redirect(url_for('login_user'))

def get_user_by_id(user_id):
    
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    
    cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    
    conn.close()

    return user

def query_restaurant_by_id(restaurant_id):
    
    with sqlite3.connect('mydatabase.db') as conn:
        cursor = conn.cursor()

        
        cursor.execute("SELECT * FROM Restaurants WHERE id=?", (restaurant_id,))
        restaurant = cursor.fetchone()

    return restaurant    

# Dashboard für angemeldete Benutzer
@app.route('/dashboard/user')
def dashboard_user():
    if 'user_id' in session:
        user_id = session['user_id']
        
        user = get_user_by_id(user_id)

        # Debugging: Print relevant information for the user
        print(f"User ID: {user_id}")
        print(f"User Data: {user}")

        if user:
            user_postal_code = user[5] if user and len(user) > 4 else None

            
            print(f"User's Original Postal Code: {user_postal_code}")

            
            normalized_user_postal_code = ''.join(filter(str.isdigit, str(user_postal_code)))

            
            print(f"User's Normalized Postal Code: {normalized_user_postal_code}")

            
            restaurants = query_restaurants_by_postal_code(normalized_user_postal_code)
            return render_template('dashboard_user.html', user=user, restaurants=restaurants)


    return redirect(url_for('login_user'))


@app.route('/add_to_cart/<int:restaurant_id>/<int:item_id>', methods=['POST'])
def add_to_cart(restaurant_id, item_id):
    if 'user_id' in session:
        user_id = session['user_id']
        quantity = int(request.form.get('quantity', 1))

        
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        
        cursor.execute("SELECT * FROM MenuItems WHERE id=?", (item_id,))
        menu_item = cursor.fetchone()

        if menu_item:
            
            cart_key = f"cart_{user_id}"
            cart = session.get(cart_key, [])
            cart.append({
                'restaurant_id': restaurant_id,
                'item_id': item_id,
                'name': menu_item[2],
                'price': menu_item[4],
                'quantity': quantity,
            })
            session[cart_key] = cart

            flash(f'{quantity} {menu_item[2]} added to your cart.', 'success')

        
        conn.close()

    return redirect(url_for('restaurant_detail', restaurant_id=restaurant_id))


def calculate_total_price(cart_items):
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return total_price


def get_menu_item_details(item_id):
    with sqlite3.connect('mydatabase.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM MenuItems WHERE id=?", (item_id,))
        menu_item = cursor.fetchone()

    return menu_item


def get_ordered_items(order_id):
    with sqlite3.connect('mydatabase.db') as conn:
        
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        
        cursor.execute("SELECT * FROM Orders WHERE id=?", (order_id,))
        order = cursor.fetchone()

    ordered_items = []
    if order:
        # Access tuple elements by index
        item_id = order['item_id']
        quantity = order['quantity']

        
        menu_item = get_menu_item_details(item_id)

        # Create a dictionary with item details and quantity
        ordered_item = {
            'name': menu_item['name'],
            'price': menu_item['price'],
            'quantity': quantity,
        }

        ordered_items.append(ordered_item)

    return ordered_items



def get_user_orders(user_id):
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Orders WHERE user_id=?", (user_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders


def get_restaurant_orders(restaurant_id):
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Orders WHERE restaurant_id=?", (restaurant_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders

def update_order_status_in_db(order_id, new_status):
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    
    cursor.execute("UPDATE Orders SET status = ? WHERE id = ?", (new_status, order_id))

    
    conn.commit()

    
    conn.close()



@app.route('/cart_overview', methods=['GET', 'POST'])
def cart_overview():
    if 'user_id' in session:
        user_id = session['user_id']

        
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Retrieve cart items from the session
        cart_key = f"cart_{user_id}"
        cart = session.get(cart_key, [])

        # Fetch menu item details for items in the cart
        cart_items = []
        total_price = 0
        for item in cart:
            cursor.execute("SELECT * FROM MenuItems WHERE id=?", (item['item_id'],))
            menu_item = cursor.fetchone()
            if menu_item:
                total_price += menu_item[4] * item['quantity']
                cart_items.append({
                    'id': item['item_id'],  
                    'name': menu_item[2],
                    'price': menu_item[4],
                    'quantity': item['quantity'],
                })

        
        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'update':
                item_id = int(request.form.get('item_id'))
                new_quantity = int(request.form.get('quantity'))
                
                
                for item in cart:
                    if item['item_id'] == item_id:
                        item['quantity'] = new_quantity
                        break

                flash('Cart updated successfully!', 'success')

            elif action == 'remove':
                item_id = int(request.form.get('item_id'))
                
                
                cart = [item for item in cart if item['item_id'] != item_id]

                flash('Item removed from the cart!', 'success')

            elif action == 'place_order':
                additional_notes = request.form.get('additional_notes')

                
                if cart:
                    
                    restaurant_id = get_restaurant_id_for_cart(cart)

                    
                    cursor.executemany('''
                        INSERT INTO Orders (user_id, restaurant_id, item_id, quantity, note, total_price, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', [(user_id, restaurant_id, item['item_id'], item['quantity'], additional_notes, total_price, 'In Bearbeitung') for item in cart])

                    
                    conn.commit()

                    
                    order_id = cursor.lastrowid

                    
                    session.pop(cart_key, None)

                    update_order_status_route(order_id, 'In Bearbeitung')

                    flash('Order placed successfully!', 'success')
                else:
                    flash('Your cart is empty. Add items before placing an order.', 'error')

                
                return redirect(url_for('thank_you'))

            
            session[cart_key] = cart

            
            return redirect(url_for('cart_overview'))

        
        conn.close()

        return render_template('cart_overview.html', cart_items=cart_items, total_price=total_price)

    return redirect(url_for('login_user'))


def get_order_status(order_id):
    conn = sqlite3.connect('mydatabase.db')  
    cursor = conn.cursor()

    
    cursor.execute("SELECT status FROM Orders WHERE id = ?", (order_id,))
    result = cursor.fetchone()

    
    conn.close()

    if result:
        return result[8]  
    else:
        return "Order Status Not Found"



@app.route('/customer_orders')
def customer_orders():
    if 'user_id' in session:
        user_id = session['user_id']
        orders = get_user_orders(user_id)
        orders_with_status = []

        for order in orders:
            order_id = order[0]
            status = get_order_status(order_id)  
            ordered_items = get_ordered_items(order_id)
            orders_with_status.append((order, status, ordered_items))

        return render_template('customer_orders.html', orders_with_status=orders_with_status)

    return redirect(url_for('login_user'))


@app.route('/restaurant_orders')
def restaurant_orders():
    if 'restaurant_id' in session:
        restaurant_id = session['restaurant_id']
        orders = get_restaurant_orders(restaurant_id)

        orders_with_items = []

        for order in orders:
            order_id = order[0]
            ordered_items = get_ordered_items(order_id)
            orders_with_items.append({'order_details': order, 'ordered_items': ordered_items})

        return render_template('restaurant_orders.html', orders_with_items=orders_with_items)

    return redirect(url_for('login_user'))



@app.route('/update_order_status_route', methods=['POST'])
def update_order_status_route():
    if 'restaurant_id' in session:
        restaurant_id = session['restaurant_id']

        order_id = request.form.get('order_id')
        if isinstance(order_id, tuple):
            order_id = order_id[0]

        try:
            order_id = int(order_id)
        except ValueError:
            return "Invalid order ID"    
        new_status = request.form.get('new_status')

        update_order_status_in_db(order_id, new_status)
        flash('Order status updated successfully!', 'success')

        return redirect(url_for('restaurant_orders'))

    return redirect(url_for('login_user'))



@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')


def get_restaurant_id_for_cart(cart):
    
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    try:
        
        if cart:
            first_item_id = cart[0]['item_id']

            
            cursor.execute("SELECT restaurant_id FROM MenuItems WHERE id=?", (first_item_id,))
            restaurant_id = cursor.fetchone()[0]

            return restaurant_id
        else:
            return None
    finally:
        
        conn.close()
    

if __name__ == '__main__':
    app.run(debug=True)
    

    