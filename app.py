# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from binance.client import Client

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

BINANCE_API_KEY = 'your_binance_api_key'
BINANCE_API_SECRET = 'your_binance_api_secret'
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    balance = db.Column(db.Float, default=0.0)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'username': user.username, 'email': user.email})
        return jsonify({'access_token': access_token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()
    return jsonify({'balance': user.balance})

@app.route('/deposit', methods=['POST'])
@jwt_required()
def deposit():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()
    data = request.get_json()
    amount = float(data['amount'])
    user.balance += amount
    db.session.commit()
    return jsonify({'message': 'Deposit successful', 'new_balance': user.balance})

@app.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user['email']).first()
    data = request.get_json()
    amount = float(data['amount'])
    if user.balance >= amount:
        user.balance -= amount
        db.session.commit()
        return jsonify({'message': 'Withdrawal successful', 'new_balance': user.balance})
    else:
        return jsonify({'message': 'Insufficient balance'}), 400

@app.route('/buy', methods=['POST'])
@jwt_required()
def buy():
    current_user = get_jwt_identity()
    data = request.get_json()
    symbol = data['symbol']
    quantity = float(data['quantity'])
    try:
        order = client.order_market_buy(symbol=symbol, quantity=quantity)
        return jsonify({'message': f'Bought {quantity} of {symbol}', 'order': order})
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@app.route('/sell', methods=['POST'])
@jwt_required()
def sell():
    current_user = get_jwt_identity()
    data = request.get_json()
    symbol = data['symbol']
    quantity = float(data['quantity'])
    try:
        order = client.order_market_sell(symbol=symbol, quantity=quantity)
        return jsonify({'message': f'Sold {quantity} of {symbol}', 'order': order})
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)