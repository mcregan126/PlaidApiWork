from flask import Flask, jsonify, request, session, redirect, url_for, render_template
from flask_login import LoginManager
import sqlite3
import os

from users.users import users_bp, User
from transactions.transactions import transactions_bp
from plaid_routes import plaid_bp

app = Flask(__name__)
app.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(transactions_bp, url_prefix='/transactions')
app.register_blueprint(plaid_bp)

#user loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return User(id=user_data[0], username=user_data[1], password=user_data[2])
    return None

@app.route('/')
def home():
    return redirect(url_for('users.login'))

if __name__ == '__main__':
    app.run(debug=True)

