#!/usr/bin/env python3

import os
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code Challenge</h1>'

#  Restaurants Routes 

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  
    
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    
    return jsonify({
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address,
        'restaurant_pizzas': [pizza.to_dict() for pizza in restaurant.restaurant_pizzas]
    }), 200

@app.route('/restaurants/<int:id>', methods=['PATCH'])
def update_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    
    data = request.get_json()
    if 'name' in data:
        restaurant.name = data['name']
    if 'address' in data:
        restaurant.address = data['address']
    
    db.session.commit()
    return make_response(restaurant.to_dict(), 200)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    
    db.session.delete(restaurant)
    db.session.commit()
    return jsonify({"message": "Restaurant deleted."}), 204

#  Pizzas Routes 

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{
        'id': pizza.id,
        'name': pizza.name,
        'ingredients': pizza.ingredients
    } for pizza in pizzas]), 200

@app.route('/pizzas/<int:id>', methods=['GET'])
def get_pizza(id):
    pizza = db.session.get(Pizza, id) 
    if not pizza:
        return make_response({"error": "Pizza not found"}, 404)
    
    return make_response(pizza.to_dict(), 200)

@app.route('/pizzas', methods=['POST'])
def create_pizza():
    data = request.get_json()
    name = data.get('name')
    ingredients = data.get('ingredients')

    if not (name and ingredients):
        return make_response({"error": "Missing required fields"}, 400)
    
    pizza = Pizza(name=name, ingredients=ingredients)
    db.session.add(pizza)
    db.session.commit()

    return make_response(pizza.to_dict(), 201)

@app.route('/pizzas/<int:id>', methods=['PATCH'])
def update_pizza(id):
    pizza = db.session.get(Pizza, id) 
    if not pizza:
        return make_response({"error": "Pizza not found"}, 404)
    
    data = request.get_json()
    if 'name' in data:
        pizza.name = data['name']
    if 'ingredients' in data:
        pizza.ingredients = data['ingredients']
    
    db.session.commit()
    return make_response(pizza.to_dict(), 200)

@app.route('/pizzas/<int:id>', methods=['DELETE'])
def delete_pizza(id):
    pizza = db.session.get(Pizza, id)  
    if not pizza:
        return make_response({"error": "Pizza not found"}, 404)
    
    db.session.delete(pizza)
    db.session.commit()
    return make_response({"message": "Pizza deleted"}, 200)

#  RestaurantPizza Routes 

@app.route('/restaurant_pizzas', methods=['GET'])
def get_restaurant_pizzas():
    all_restaurant_pizzas = [restaurant_pizza.to_dict() for restaurant_pizza in RestaurantPizza.query.all()]
    return make_response(all_restaurant_pizzas, 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    restaurant_id = data.get('restaurant_id')
    pizza_id = data.get('pizza_id')
    price = data.get('price')

    # Check if all required fields are provided
    if not (restaurant_id and pizza_id and price is not None):
        return make_response({"errors": ["Missing required fields"]}, 400)

    # Validate that the price is between 1 and 30
    if not (1 <= price <= 30):
        return make_response({"errors": ['Price must be between 1 and 30',]}, 400)

    restaurant = db.session.get(Restaurant, restaurant_id)
    pizza = db.session.get(Pizza, pizza_id)

    if not (restaurant and pizza):
        return make_response({"errors": ["Pizza or Restaurant not found"]}, 404)

    restaurant_pizza = RestaurantPizza(restaurant=restaurant, pizza=pizza, price=price)
    db.session.add(restaurant_pizza)
    db.session.commit()

    return make_response(restaurant_pizza.to_dict(), 201)


if __name__ == "__main__":
    app.run(debug=True)

