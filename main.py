from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

packages = [
    {
        "name": "Maharashtra",
        "description": "Explore the beauty of Maharashtra with our exclusive package.",
        "price": 15000,
        "image": "img-1.jpg",
        "link": "https://example.com/maharashtra"
    },
    {
        "name": "Himachal",
        "description": "Experience the serene landscapes of Himachal Pradesh.",
        "price": 20000,
        "image": "img-2.jpg",
        "link": "https://example.com/himachal"
    },
    {
        "name": "London",
        "description": "Discover the charm of London, the capital city of England.",
        "price": 25000,
        "image": "img-3.jpg",
        "link": "https://example.com/london"
    },
    {
        "name": "Paris",
        "description": "Fall in love with the romantic atmosphere of Paris, the city of love.",
        "price": 30000,
        "image": "img-4.jpg",
        "link": "https://example.com/paris"
    },
    {
        "name": "Prague",
        "description": "Experience the rich history and stunning architecture of Prague.",
        "price": 28000,
        "image": "img-5.jpg",
        "link": "https://example.com/prague"
    },
    {
        "name": "Jammu",
        "description": "Explore the scenic beauty and spirituality of Jammu.",
        "price": 22000,
        "image": "img-6.jpg",
        "link": "https://example.com/jammu"
    },
    {
        "name": "Kerala",
        "description": "Relax and rejuvenate amidst the lush greenery of Kerala.",
        "price": 27000,
        "image": "img-7.jpg",
        "link": "https://example.com/kerala"
    },
    {
        "name": "Goa",
        "description": "Experience the vibrant nightlife and sandy beaches of Goa.",
        "price": 32000,
        "image": "img-8.jpg",
        "link": "https://example.com/goa"
    }
]


# Function to create the users table in the database
def create_users_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        );
    ''')
    # Check if there are any admin users
    cursor.execute("SELECT * FROM users WHERE is_admin = 1")
    admin_exists = cursor.fetchone()
    # If no admin users exist, create one
    if not admin_exists:
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                       ('admin', 'admin', 1))
        conn.commit()
    conn.close()

create_users_table()

def create_user_details_table():
    conn = sqlite3.connect('database_details.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cust_id TEXT UNIQUE,
            username TEXT NOT NULL,
            name TEXT,
            home_city TEXT,
            email TEXT,
            contact_number TEXT,
            gender TEXT,
            age INTEGER,
            address TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        );
    ''')
    conn.commit()
    conn.close()

create_user_details_table()
# Route for the home page

def create_reservations_table():
    conn = sqlite3.connect('database-1.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            guests INTEGER NOT NULL,
            place TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

create_reservations_table()

@app.route('/')
def home():
    return render_template('home.html', packages=packages)


# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if is_valid(username, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

# Function to check if the username and password are valid
def is_valid(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return True
    return False

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not is_existing_user(username):
            add_user(username, password)
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Username already exists.')
    return render_template('register.html')

# Function to check if the username already exists in the database
def is_existing_user(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return True
    return False

# Function to add a new user to the database
def add_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

# Route for the dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        username = session['username']
        is_admin = check_admin(username)
        
        # Check if user details already exist
        user_details = get_user_details(username)
        if not user_details:
            if request.method == 'POST':
                name = request.form['name']
                home_city = request.form['home_city']
                email = request.form['email']
                contact_number = request.form['contact_number']
                gender = request.form['gender']
                age = request.form['age']
                address = request.form['address']
                cust_id = generate_cust_id()
                add_user_details(username, cust_id, name, home_city, email, contact_number, gender, age, address)
                return redirect(url_for('home')) 
            return render_template('details_form.html')  
        else:
            return redirect(url_for('home')) 
    return redirect(url_for('login'))

# Function to generate a unique cust_id
def generate_cust_id():
    return str(uuid.uuid4())

# Function to add user details to the database
def add_user_details(username, cust_id, name, home_city, email, contact_number, gender, age, address):
    conn = sqlite3.connect('database_details.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_details (cust_id, username, name, home_city, email, contact_number, gender, age, address) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (cust_id, username, name, home_city, email, contact_number, gender, age, address))
    conn.commit()
    conn.close()

# Route for the admin page
@app.route('/admin')
def admin():
    if 'username' in session:
        username = session['username']
        is_admin = check_admin(username)
        if is_admin:
            return render_template('admin.html')
        else:
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Function to check if the user is an admin
def check_admin(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT is_admin FROM users WHERE username=?', (username,))
    is_admin = cursor.fetchone()[0]
    conn.close()
    return bool(is_admin)

@app.route('/show_users')
def show_users():
    if 'username' in session:
        username = session['username']
        is_admin = check_admin(username)
        if is_admin:
            conn = sqlite3.connect('database_details.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM user_details
            ''')
            users_details = cursor.fetchall()
            conn.close()
            return render_template('all_users.html', users_details=users_details)
        else:
            return "You are not authorized to view this page."
    else:
        return redirect(url_for('login'))

@app.route('/add_customer', methods=['POST'])
def add_customer():
    if request.method == 'POST':
        username = request.form['username']
        cust_id = generate_cust_id()  
        name = request.form['name']
        home_city = request.form['home_city']
        email = request.form['email']
        contact_number = request.form['contact_number']
        gender = request.form['gender']
        age = request.form['age']
        address = request.form['address']

        add_user_details(username, cust_id, name, home_city, email, contact_number, gender, age, address)

        return redirect(url_for('admin'), error="Error in Adding customer")
    
# Route for deleting a user
@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    if 'username' in session:
        username = session['username']
        is_admin = check_admin(username)
        if is_admin:
            user_to_delete = request.form['username']
            conn = sqlite3.connect('database_details.db')
            cursor = conn.cursor()
            
            # Check if the user exists before attempting to delete
            cursor.execute("SELECT username FROM user_details WHERE username=?", (user_to_delete,))
            existing_user = cursor.fetchone()
            if existing_user:
                #cursor.execute("DELETE FROM users WHERE username=?", (user_to_delete,))
                cursor.execute("DELETE FROM user_details WHERE username=?", (user_to_delete,))
                conn.commit()
                conn.close()
                return redirect(url_for('all_users'))
            else:
                print('User does not exist', 'error')
                conn.close()
                return redirect(url_for('all_users'))  # or any other appropriate action
    return redirect(url_for('login'))


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        # Assuming the form has fields for name, description, price, image, and link
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.form['image']
        link = request.form['link']

        # Now you can do something with this data, like add it to a database

    return render_template('add_post.html')

@app.route('/update_post')
def update_post():
    return render_template('update_post.html')

@app.route('/make_reservation', methods=['GET', 'POST'])
def make_reservation():
    if request.method == 'POST':
        # Get the form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        date = request.form['date']
        time = request.form['time']
        guests = request.form['guests']
        place = request.form['place']

        # Insert the reservation into the database
        add_reservation(name, email, phone, date, time, guests, place)
        
        return redirect(url_for('view_reservation'))

    return render_template('make_reservation.html', packages=packages)

# Function to add reservation to the database
def add_reservation(name, email, phone, date, time, guests, place):
    conn = sqlite3.connect('database-1.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reservations (name, email, phone, date, time, guests, place)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, email, phone, date, time, guests, place))
    conn.commit()
    conn.close()


@app.route('/view_reservation')
def view_reservation():
    conn = sqlite3.connect('database-1.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservations')
    reservations = cursor.fetchall()
    conn.close()
    return render_template('view_reservation.html', reservations=reservations)

# Route for the profile page
@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        is_admin = check_admin(username)
        
        # Check if user details already exist
        user_details = get_user_details(username)
        edit_mode = session.get('edit_mode', False)
        
        return render_template('profile.html', username=username, is_admin=is_admin, user_details=user_details, edit_mode=edit_mode)
    return redirect(url_for('login'))

# Route for editing user details
@app.route('/profile_edit', methods=['POST'])
def profile_edit():
    if 'username' in session:
        session['edit_mode'] = True
    return redirect(url_for('profile'))


# Route for updating user profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' in session and 'edit_mode' in session:
        username = session['username']
        name = request.form['name']
        home_city = request.form['home_city']
        email = request.form['email']
        contact_number = request.form['contact_number']
        gender = request.form['gender']
        age = request.form['age']
        address = request.form['address']
        update_user_details(username, name, home_city, email, contact_number, gender, age, address)
        session.pop('edit_mode', None)
    return redirect(url_for('profile'))

# Function to update user details in the database
def update_user_details(username, name, home_city, email, contact_number, gender, age, address):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE user_details
        SET name=?, home_city=?, email=?, contact_number=?, gender=?, age=?, address=?
        WHERE username=?
    ''', (name, home_city, email, contact_number, gender, age, address, username))
    conn.commit()
    conn.close()


# Function to get user details from the database
def get_user_details(username):
    conn = sqlite3.connect('database_details.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_details WHERE username=?', (username,))
    user_details = cursor.fetchone()
    conn.close()
    return user_details


# Route for the logout page
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/all_users')
def all_users():
    if 'username' in session:
        username = session['username']
        is_admin = check_admin(username)
        if is_admin:
            conn = sqlite3.connect('database_details.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM user_details
            ''')
            users_details = cursor.fetchall()
            conn.close()
            return render_template('all_users.html', users_details=users_details)
        else:
            return "You are not authorized to view this page."
    else:
        return redirect(url_for('login'))
    

if __name__ == '__main__':
    app.run(debug=True)
