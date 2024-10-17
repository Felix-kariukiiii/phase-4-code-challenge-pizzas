#!/usr/bin/env python3
from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db, Restaurant, RestaurantPizza, Pizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
CORS(app)

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return '<h1>Pizza Code Challenge</h1>'

class Restaurants(Resource):
    def get(self):
        all_res = Restaurant.query.all()
        restaurants = [restaurant.to_dict(include_pizzas=False) for restaurant in all_res]
        return make_response(jsonify(restaurants), 200)

api.add_resource(Restaurants, '/restaurants')

class RestaurantsByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            resp = {"error": "Restaurant not found"}
            return make_response(jsonify(resp), 404)  # Return 404 for not found
        restaurant_dict = restaurant.to_dict(include_pizzas=True)
        return make_response(jsonify(restaurant_dict), 200)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            resp = {"error": "Restaurant not found"}
            return make_response(jsonify(resp), 404)  # Return 404 for not found
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)  # Return 204 for successful deletion

api.add_resource(RestaurantsByID, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
        return make_response(jsonify(pizzas), 200)

api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def get(self):
        restaurantPizza = [pizzarest.to_dict() for pizzarest in RestaurantPizza.query.all()]
        return make_response(jsonify(restaurantPizza), 200)

    def post(self):
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            
            # Fetch the related pizza and restaurant
            pizza = Pizza.query.get(data['pizza_id'])
            restaurant = Restaurant.query.get(data['restaurant_id'])

            return make_response(jsonify({
                'id': new_restaurant_pizza.id,
                'price': new_restaurant_pizza.price,
                'pizza_id': new_restaurant_pizza.pizza_id,
                'restaurant_id': new_restaurant_pizza.restaurant_id,
                'pizza': pizza.to_dict(),  # Include pizza details
                'restaurant': restaurant.to_dict()  # Include restaurant details
            }), 201)  # Return created object with price
        except ValueError as e:
            return make_response({"errors": [str(e)]}, 400)
    
    def delete(self, id):
        restaurant_pizza = RestaurantPizza.query.filter_by(id=id).first()
        if not restaurant_pizza:
            resp = {"error": "RestaurantPizza not found"}
            return make_response(jsonify(resp), 404)  # Return 404 for not found
        db.session.delete(restaurant_pizza)
        db.session.commit()
        return make_response('', 204)  # Return 204 for successful deletion

api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555)
