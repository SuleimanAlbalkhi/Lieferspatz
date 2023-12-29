from flask import Flask, render_template, request, redirect, url_for, session,flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os


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
        postal_code INTEGER NOT NULL,
        description TEXT,
        image_path TEXT,
        password_hash TEXT NOT NULL,
        opening_time TIME  NOT NULL,
        closing_time TIME  NOT NULL,
        delivery_radius TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        username TEXT NOT NULL,
        address TEXT NOT NULL,
        postal_code INTEGER NOT NULL,
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

# Änderungen speichern und Verbindung schließen
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

        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Benutzerdaten abrufen
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

        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Restaurantdaten abrufen
        cursor.execute("SELECT * FROM Restaurants WHERE username=?", (username,))
        restaurant = cursor.fetchone()

        # Überprüfen, ob das Restaurant existiert und das Passwort korrekt ist
        if restaurant and check_password_hash(restaurant[7], password):
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


        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Benutzer in die Datenbank einfügen
        cursor.execute("INSERT INTO Users (first_name, last_name, username, address, postal_code, password_hash) VALUES (?, ?, ?, ?, ?, ?)",
               (first_name, last_name, username, address, postal_code, password_hash))


        # Änderungen speichern und Verbindung schließen
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
        postal_code = request.form['postal_code']
        description = request.form['description']
        image_path = request.form['image_path']
        password = request.form['password']
        opening_time = request.form['opening_time']
        closing_time = request.form['closing_time']
        delivery_radius = request.form['delivery_radius']

        # Passwort hashen
        password_hash = generate_password_hash(password)

        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Restaurant in die Datenbank einfügen
        cursor.execute("INSERT INTO Restaurants (name, address, username, description, image_path, password_hash, opening_time, closing_time, delivery_radius, postal_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (name, address, username, description, image_path, password_hash, opening_time, closing_time, delivery_radius, postal_code))


        # Änderungen speichern und Verbindung schließen
        conn.commit()
        conn.close()


        return redirect(url_for('login_restaurant'))

    return render_template('register_restaurant.html')


# In app.py
@app.route('/menu', methods=['GET'])
def view_menu():
    if session.get('restaurant_id'):
        restaurant_id = session['restaurant_id']

        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Speisekarte des Restaurants abrufen
        cursor.execute("SELECT * FROM MenuItems WHERE restaurant_id=?", (restaurant_id,))
        menu_items = cursor.fetchall()

        # Debugging: Print the retrieved menu items
        print(f"Retrieved menu items: {menu_items}")

        # Verbindung schließen
        conn.close()

        return render_template('view_menu.html', menu_items=menu_items)

    return redirect(url_for('login_restaurant'))
               
UPLOAD_FOLDER = 'D:/Suleiman/DB/Lieferspatz/.venv/static/Uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_item', methods=['GET', 'POST'])
def add_menu_item():
    if 'restaurant_id' in session:
        file_path = None  # Initialize file_path
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']

            # Bild-Upload verarbeiten
            if 'image' in request.files:
                file = request.files['image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                else:
                    flash('Ungültiges Dateiformat für Bild. Nur PNG, JPG, JPEG oder GIF sind erlaubt.', 'error')

            # Weitere Informationen zur Datenbank hinzufügen
            restaurant_id = session['restaurant_id']

            # Verbindung zur Datenbank herstellen
            conn = sqlite3.connect('mydatabase.db')
            cursor = conn.cursor()

            cursor.execute("INSERT INTO MenuItems (name, description, price, image_path, restaurant_id) VALUES (?, ?, ?, ?, ?)",
                           (name, description, price, file_path, restaurant_id))

            # Änderungen speichern und Verbindung schließen
            conn.commit()
            conn.close()

            flash('Item wurde zur Speisekarte hinzugefügt.', 'success')

        return render_template('add_menu_item.html')

    return redirect(url_for('login_restaurant'))

@app.route('/remove_item/<int:item_id>', methods=['GET'])
def remove_menu_item(item_id):
    if 'restaurant_id' in session:
        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Item aus der Speisekarte entfernen
        cursor.execute("DELETE FROM MenuItems WHERE id=?", (item_id,))

        # Änderungen speichern und Verbindung schließen
        conn.commit()
        conn.close()

        flash('Item wurde von der Speisekarte entfernt.', 'success')

        return redirect(url_for('view_menu'))

    return redirect(url_for('login_restaurant'))

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    if 'restaurant_id' in session:
        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Initialize file_path with None
        file_path = None

        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']

            # Bild-Upload verarbeiten
            if 'image' in request.files:
                file = request.files['image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                else:
                    flash('Ungültiges Dateiformat für Bild. Nur PNG, JPG, JPEG oder GIF sind erlaubt.', 'error')

            # Item in der Datenbank aktualisieren
            cursor.execute("UPDATE MenuItems SET name=?, description=?, price=?, image_path=? WHERE id=?",
                           (name, description, price, file_path, item_id))

            # Änderungen speichern und Verbindung schließen
            conn.commit()
            conn.close()

            flash('Item wurde aktualisiert.', 'success')
            return redirect(url_for('view_menu'))

        # Informationen zum Item abrufen und im Formular anzeigen
        cursor.execute("SELECT * FROM MenuItems WHERE id=?", (item_id,))
        menu_item = cursor.fetchone()

        # Verbindung schließen
        conn.close()

        return render_template('edit_menu_item.html', menu_item=menu_item)

    return redirect(url_for('login_restaurant'))


# Dashboard für angemeldete Benutzer
@app.route('/dashboard/user')
def dashboard_user():
    if 'user_id' in session:
        return f'Welcome, User! Your user ID is {session["user_id"]}'
    return redirect(url_for('login_user'))

# Dashboard für angemeldete Restaurants
@app.route('/dashboard/restaurant')
def dashboard_restaurant():
    if 'restaurant_id' in session:
        restaurant_id = session['restaurant_id']

        conn= sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM Restaurants WHERE id=?", (restaurant_id,))
        restaurant = cursor.fetchone()
        

        conn.close()

        if restaurant:
            restaurant_name = restaurant[0]
            session['restaurant_name'] = restaurant_name
        return render_template('dashboard_restaurant.html', restaurant_name=restaurant_name)
  
    return redirect(url_for('login_restaurant'))



if __name__ == '__main__':
    app.run(debug=True)
