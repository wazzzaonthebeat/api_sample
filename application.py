from flask import Flask,request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
auth = HTTPBasicAuth()
db = SQLAlchemy(app)

USER_DATA= {
    "admin" : "SuperSecretPwd"
}

class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),unique=True, nullable=False)
    description = db.Column(db.String(120))

    def __repr__(self):
        return f"{self.name} - {self.description}"

@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password
@app.route('/')
def index ():
    return 'Hello!'

@app.route('/drinks')
@auth.login_required
def get_drinks():
    drinks = Drink.query.all()
    output = []
    for drink in drinks:
        drink_data = {'name': drink.name, 'description': drink.description}
        output.append((drink_data))
    return {"drinks": output}

@app.route('/drinks/<id>')
@auth.login_required
def get_drink(id):
    drink = Drink.query.get_or_404(id)
    return  {"name": drink.name, "description": drink.description}

@app.route('/drinks', methods=['POST'])
@auth.login_required
def add_drink():
    drink = Drink(name=request.json['name'], description=request.json['description'])
    db.session.add(drink)
    db.session.commit()
    return {'id': drink.id,"name": drink.name, "description": drink.description}#{}


@app.route ('/drinks/<id>', methods=['DELETE'])
@auth.login_required
def delete_drink(id):
    drink = Drink.query.get(id)
    if drink is None:
        return {"error": "not found"}
    db.session.delete(drink)
    db.session.commit()
    return {"message": "drink deleted!"}