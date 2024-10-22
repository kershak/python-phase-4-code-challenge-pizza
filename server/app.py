#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

class RestaurantsByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        return make_response(jsonify(restaurant.to_dict(include_pizzas=True)),200)
    
    def delete(self,id):
        restaurant = Restaurant.query.filter_by(id =id).first()
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)
api.add_resource(RestaurantsByID, "/restaurants/<int:id>")

# @app.route('/restaurants/<int:id>', methods=['GET'])
# def get_restaurant(id):
#     restaurant = Restaurant.query.filter_by(id=id).first()
#     if restaurant is None:
#         return make_response({"error": "Restaurant not found"}, 404)
#     return make_response(jsonify(restaurant.to_dict()), 200)

# @app.route('/restaurants/<int:id>', methods=['DELETE'])
# def delete_restaurant(id):
#     restaurant = Restaurant.query.filter_by(id=id).first()
#     if restaurant is None:
#         return make_response({"error": "Restaurant not found"}), 404
#     db.session.delete(restaurant)
#     db.session.commit()
#     return make_response("", 204)

@app.route('/pizzas', methods = ['GET'])
def get_pizza():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

@app.route('/restaurant_pizzas', methods = ['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    if not all(i in data for i in ("restaurant_id", "pizza_id", "price")):
            return make_response({"error": "Missing data"}, 400)
    try: 
        restaurant_pizza = RestaurantPizza(
            price = data['price'],
            pizza_id = data ['pizza_id'],
            restaurant_id = data ['restaurant_id']
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
    except ValueError as e:
        return make_response({"errors": ["validation errors"]}, 400)
    
    return jsonify(restaurant_pizza.to_dict()), 201

if __name__ == "__main__":

    app.run(port=5555, debug=True)
