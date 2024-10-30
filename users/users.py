from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import sqlite3

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ensure you set a secret key for session management


# Blueprint for user routes
users_bp = Blueprint('users', __name__)


# Database initialization function
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

# Populate database with fake users
def populate_db():
    fake_users = [
        {'username': 'testuser1', 'password': 'password1'},
        {'username': 'testuser2', 'password': 'password2'},
        {'username': 'testuser3', 'password': 'password3'}
    ]

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    for user in fake_users:
        try:
            hashed_password = generate_password_hash(user['password'], method='pbkdf2:sha256')
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user['username'], hashed_password))
        except sqlite3.IntegrityError:
            pass  # Ignore if the user already exists

    conn.commit()
    conn.close()

# Call the init_db and populate_db functions
init_db()
populate_db()

# User class
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Register route
@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')

        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('users.login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')

    return render_template('register.html')

# Login route
@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('frontend.html')  # Redirect if the user is already logged in

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = c.fetchone()
        conn.close()

        if user_data and check_password_hash(user_data[2], password):
            user = User(id=user_data[0], username=user_data[1], password=user_data[2])
            login_user(user)  # Login the user
            session['username'] = username
            flash('Login successful!', 'success')  # Flash success message
            return render_template('frontend.html')  # Redirect to a different page after successful login
        else:
            flash('Invalid username or password.', 'danger')  # Flash error message for failed login

    return render_template('login.html')  # Render login page if GET or unsuccessful login

if __name__ == '__main__':
    app.run(debug=True)
