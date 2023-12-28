from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

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
        address TEXT NOT NULL,
        description TEXT,
        image_path TEXT,
        password_hash TEXT NOT NULL,
        opening_time TEXT NOT NULL,
        closing_time TEXT NOT NULL,
        delivery_radius TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        address TEXT NOT NULL,
        postal_code TEXT NOT NULL,
        password_hash TEXT NOT NULL
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
        cursor.execute("SELECT * FROM Users WHERE address=?", (username,))
        user = cursor.fetchone()

        # Überprüfen, ob der Benutzer existiert und das Passwort korrekt ist
        if user and check_password_hash(user[5], password):
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
        cursor.execute("SELECT * FROM Restaurants WHERE address=?", (username,))
        restaurant = cursor.fetchone()

        # Überprüfen, ob das Restaurant existiert und das Passwort korrekt ist
        if restaurant and check_password_hash(restaurant[5], password):
            session['restaurant_id'] = restaurant[0]

            return redirect(url_for('dashboard_restaurant'))

    return render_template('login_restaurant.html')

# Route für die Registrierung von Benutzern
@app.route('/register/user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        postal_code = request.form['postal_code']
        password = request.form['password']

        # Passwort hashen
        password_hash = generate_password_hash(password, method='sha256')


        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Benutzer in die Datenbank einfügen
        cursor.execute("INSERT INTO Users (first_name, last_name, address, postal_code, password_hash) VALUES (?, ?, ?, ?, ?)",
                       (first_name, last_name, address, postal_code, password_hash))

        # Änderungen speichern und Verbindung schließen
        conn.commit()
        conn.close()
        flash('Registration successful. You can now log in.', 'success')

        return redirect(url_for('login_user'))

    return render_template('register_user.html')

# Route für die Registrierung von Restaurants
@app.route('/register/restaurant', methods=['GET', 'POST'])
def register_restaurant():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        description = request.form['description']
        image_path = request.form['image_path']
        password = request.form['password']
        opening_time = request.form['opening_time']
        closing_time = request.form['closing_time']
        delivery_radius = request.form['delivery_radius']

        # Passwort hashen
        password_hash = generate_password_hash(password, method='sha256')

        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # Restaurant in die Datenbank einfügen
        cursor.execute("INSERT INTO Restaurants (name, address, description, image_path, password_hash, opening_time, closing_time, delivery_radius) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (name, address, description, image_path, password_hash, opening_time, closing_time, delivery_radius))

        # Änderungen speichern und Verbindung schließen
        conn.commit()
        conn.close()

        flash('Registration successful. You can now log in.', 'success')

        return redirect(url_for('login_restaurant'))

    return render_template('register_restaurant.html')

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
        return f'Welcome, Restaurant! Your restaurant ID is {session["restaurant_id"]}'
    return redirect(url_for('login_restaurant'))

# Weitere Routen und Funktionen hier definieren...

if __name__ == '__main__':
    app.run(debug=True)
