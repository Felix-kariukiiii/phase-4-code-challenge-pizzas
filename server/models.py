from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'
    serialize_rules = ('-restaurants.restaurant',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    restaurantpizzas = db.relationship('RestaurantPizza', backref='restaurant')

    def to_dict(self, include_pizzas=False):
        restaurant_dict = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
        }

        if include_pizzas:
            pizzas = Pizza.query.join(RestaurantPizza).filter_by(restaurant_id=self.id).all()
            restaurant_dict['restaurant_pizzas'] = [pizza.to_dict() for pizza in pizzas]

        return restaurant_dict

    def __repr__(self):
        return f'{self.name} at {self.address}'


class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)
    restaurantpizzas = db.relationship('RestaurantPizza', backref='pizza')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
        }

    def __repr__(self):
        return f'For {self.name} the ingredients are {self.ingredients}'


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurantpizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)

    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    def to_dict(self):
        pizza = Pizza.query.get(self.pizza_id)
        return {
            "id": self.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        }

    @validates('price')
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError('Price must be between 1 and 30')
        return price

    def __repr__(self):
        return f'Price is {self.price}'
