from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_migrate import Migrate
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anonymous.db'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    data_used = db.Column(db.Float, default=0.0)  # in MB
    paid = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=True)

# Create database tables within the application context
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(username=data['username']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return jsonify({'message': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    remaining_data = max(50.0 - user.data_used, 0.0)
    buy_more_message = "You need to buy more data" if remaining_data == 0 else "You have enough data"
    
    return render_template('dashboard.html', user=user, remaining_data=remaining_data, buy_more_message=buy_more_message)

@app.route('/update_details', methods=['POST'])
def update_details():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user.name = request.form['name']
    user.email = request.form['email']
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/use_data', methods=['POST'])
def use_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    data_amount = float(request.form['data_amount'])
    if user.data_used + data_amount > 50.0:
        return redirect(url_for('dashboard'))  # Redirect to dashboard with message
   
    user.data_used += data_amount
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/pay', methods=['POST'])
def pay():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user.data_used < 50.0:
        return redirect(url_for('dashboard'))  # Redirect to dashboard with message
    
    # Simulate M-Pesa payment
    payment_success = random.choice([True, False])  # Randomly choose if the payment is successful
    
    if payment_success:
        user.data_used = 0.0
        user.paid = True
        db.session.commit()
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))  # Redirect to dashboard with message

if __name__ == '__main__':
    app.run(debug=True)
