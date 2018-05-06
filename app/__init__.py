from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response
from datetime import datetime, timedelta

# local import
from instance.config import app_config

NOT_FOUND = 'Not found'
BAD_REQUEST = 'Bad request'


db = SQLAlchemy()

def create_app(config_name):
    from app.models import Meal, User, Order, Menu
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.url_map.strict_slashes = False
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': NOT_FOUND}), 404)


    @app.errorhandler(400)
    def bad_request(error):
        return make_response(jsonify({'error': BAD_REQUEST}), 400)




    @app.route('/api/v1/meals/', methods=['POST', 'GET'])
    def meals():
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                if request.method == "POST":
                    current_user = User.query.filter_by(id=user_id).first()
                    if current_user.caterer:
                        name = str(request.data.get('name', ''))
                        description = str(request.data.get('description', ''))
                        price = str(request.data.get('price', ''))
                        if price:
                            int(price)
                        else:
                            return {"message": "Price should be a number"}
                        if name:
                            meal = Meal(name=name, description=description, price=price)
                            meal.save()
                            response = jsonify({
                                'message': 'Meal created successfully',
                                'id': meal.id,
                                'name': meal.name,
                                'description': meal.description,
                                'price': meal.price
                            })
                            response.status_code = 201
                            return response

                        else:
                            return jsonify({'message': 'Please input the name of the meal'})
                    
                    else:
                        response = jsonify({"message": "You are unauthorized to access this"})
                        response.status_code = 401
                        return response

                else:
                    current_user = User.query.filter_by(id=user_id).first()
                    if current_user.caterer:
                        meals = Meal.get_all()
                        results = []

                        for meal in meals:
                            obj = {
                                'id': meal.id,
                                'name': meal.name,
                                'description': meal.description,
                                'price': meal.price
                            }
                            results.append(obj)

                        return make_response(jsonify(results)), 200
                    else:
                        return jsonify({'message': 'You are not authorized to access this'})

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401


        else:
            response = {
                'message': 'Please input access token'
            }
            return make_response(jsonify(response)), 401

    

    @app.route('/api/v1/meals/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def meals_manipulation(id, **kwargs):

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                current_user = User.query.filter_by(id=user_id).first()
                if current_user.caterer:
                    meal = Meal.query.filter_by(id=id).first()
                    if not meal:
                        abort(404)

                    if request.method == "DELETE":
                        meal.delete()
                        return {
                            "message": "meal {} deleted".format(meal.id)
                        }, 200
                    elif request.method == 'PUT':
                        name = str(request.data.get('name', ''))
                        description = str(request.data.get('description', ''))
                        price = str(request.data.get('price', ''))
                        if price:
                            int(price)
                        else:
                            {"message": "Price should be a number" 
                     }, 200
                        meal.name = name
                        meal.description = description
                        meal.price = price
                        meal.save()
                        response = {
                            'id': meal.id,
                            'name': meal.name,
                            'description': meal.description,
                            'price': meal.price
                        }
                        return make_response(jsonify(response)), 200
                    else:
                        response = jsonify({
                            'id': meal.id,
                            'name': meal.name,
                            'description': meal.description,
                            'price': meal.price
                        })
                        return make_response(response), 200
                else:
                                  
                    response = {
                        'message': 'You are not authorized to perform these functions'
                    }
                    return make_response(jsonify(response)), 401

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

        else:
            response = {
                'message': 'Please input access token'
            }
            return make_response(jsonify(response)), 401

    
    @app.route('/api/v1/myorders/', methods=['POST', 'GET'])
    def myorders():
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                if request.method == "POST":
                    meal = str(request.data.get('meal', ''))
                    quantity = str(request.data.get('quantity', ''))
                    ordered_by = Order.ordered_by
                    if quantity:
                            int(quantity)
                    else:
                        return {"message": "Quantity should be a number" 
                 }, 200
                    if meal:
                        order = Order(meal=meal, quantity=quantity, ordered_by=user_id)
                        order.save()
                        response = jsonify({
                            'id': order.id,
                            'meal': order.meal,
                            'time_ordered': order.time_ordered,
                            'quantity': order.quantity,
                            'ordered_by': user_id
                        })

                        return make_response(response), 201
                    else:
                        return jsonify({'message': 'Please input the meal name and quantity'})

                else:
                    orders = Order.get_all(user_id)
                    results = []

                    for order in orders:
                        obj = {
                            'id': order.id,
                            'meal': order.meal,
                            'time_ordered': order.time_ordered,
                            'quantity': order.quantity,
                            'ordered_by': order.ordered_by
                        }
                        results.append(obj)

                    return make_response(jsonify(results)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

        else:
            response = {
                'message': 'Please input access token'
            }
            return make_response(jsonify(response)), 401


    @app.route('/api/v1/orders/', methods=['POST', 'GET'])
    def orders():
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                if request.method == "POST":
                    current_user = User.query.filter_by(id=user_id).first()
                    if current_user.caterer:
                        meal = str(request.data.get('meal', ''))
                        quantity = str(request.data.get('quantity', ''))
                        ordered_by = Order.ordered_by
                        if quantity:
                                int(quantity)
                        else:
                            return {"message": "Quantity should be a number" 
                     }, 200
                        if meal:
                            order = Order(meal=meal, quantity=quantity, ordered_by=user_id)
                            order.save()
                            response = jsonify({
                                'id': order.id,
                                'meal': order.meal,
                                'time_ordered': order.time_ordered,
                                'quantity': order.quantity,
                                'ordered_by': user_id
                            })

                            return make_response(response), 201
                        else:
                            return jsonify({'message': 'Please input the meal name and quantity'})
                        
                    else:
                        response = jsonify({"message": "You are unauthorized to access this"})
                        response.status_code = 401
                        return response

                else:
                    current_user = User.query.filter_by(id=user_id).first()
                    if current_user.caterer:
                        orders = Order.get_all(user_id)
                        results = []

                        for order in orders:
                            obj = {
                                'id': order.id,
                                'meal': order.meal,
                                'time_ordered': order.time_ordered,
                                'quantity': order.quantity,
                                'ordered_by': order.ordered_by
                            }
                            results.append(obj)

                        return make_response(jsonify(results)), 200
                    else:
                        return jsonify({'message': 'You are not authorized to access this'})

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401


        else:
            response = {
                'message': 'Please input access token'
            }
            return make_response(jsonify(response)), 401



    @app.route('/api/v1/orders/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def order_manipulation(id, **kwargs):

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                current_user = User.query.filter_by(id=user_id).first()
                if current_user.caterer:
                    order = Order.query.filter_by(id=id).first()
                    if not order:
                        abort(404)

                    if request.method == "DELETE":
                        order.delete()
                        return {
                            "message": "order {} deleted".format(order.id)
                        }, 200
                    elif request.method == 'PUT':
                        meal = str(request.data.get('meal', ''))
                        quantity = str(request.data.get('quantity', ''))
                        order.meal = meal
                        order.quantity = quantity
                        order.save()
                        response = {
                            'id': order.id,
                            'meal': order.meal,
                            'time_ordered': order.time_ordered,
                            'quantity': order.quantity,
                            'ordered_by': user_id
                        }
                        return make_response(jsonify(response)), 200
                    else:
                        # GET
                        response = jsonify({
                            'id': order.id,
                            'meal': order.meal,
                            'time_ordered': order.time_ordered,
                            'quantity': order.quantity,
                            'ordered_by': user_id
                    })
                        return make_response(response), 200
                else:
                                  
                    response = {
                        'message': 'You are not authorized to perform these functions'
                    }
                    return make_response(jsonify(response)), 401
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

        else:
            response = {
                'message': 'Please input access token'
            }
            return make_response(jsonify(response)), 401


    
    

    @app.route('/api/v1/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def users_manipulation(id, **kwargs):

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                current_user = User.query.filter_by(id=user_id).first()
                if current_user.caterer:
                    user = User.query.filter_by(id=id).first()
                    if not user:
                        abort(404)

                    if request.method == "DELETE":
                        user.delete()
                        return {
                            "message": "user {} has been deleted".format(user.id)
                        }, 200
                    elif request.method == 'PUT':
                        username = str(request.data.get('user', ''))
                        email = str(request.data.get('email', ''))
                        password = str(request.data.get('password', ''))
                        
                        user.username = username
                        user.email = email
                        user.password = password
                        user.save()
                        response = {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'password': user.password,
                            'caterer': user.caterer
                        }
                        return make_response(jsonify(response)), 200
                    else:
                        response = jsonify({
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'password': user.password,
                            'caterer': user.caterer
                        })
                        return make_response(response), 200
                else:
                                  
                    response = {
                        'message': 'You are not authorized to perform these functions'
                    }
                    return make_response(jsonify(response)), 401

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

        else:
            response = {
                'message': 'Please input access token'
            }
            return make_response(jsonify(response)), 401

    
    @app.route('/api/v1/promote/user/<int:id>', methods=['PUT'])
    def promote_user(id, **kwargs):
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                current_user = User.query.filter_by(id=user_id).first()
                if current_user.caterer:
                    user = User.query.filter_by(id=id).first()
                    if not user:
                            return jsonify({'message' : 'No user found!'})                 
                    
                    if request.method == "PUT":
                        user.caterer = True
                        user.save()              

                                          
                        
                        return jsonify({'message' : 'The user has been promoted to caterer!'})
                else:
                                  
                    response = {
                        'message': 'You are not authorized to perform these functions'
                    }
                    return make_response(jsonify(response)), 401
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

        else:
            response = {
                'message': 'Please input access token'
            }
            return make_response(jsonify(response)), 401


    @app.route('/api/v1/menu/', methods=['POST', 'GET'])
    def menu():
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                current_user = User.query.filter_by(id=user_id).first()
                if request.method == "POST":
                    if current_user.caterer:
                        menu_meals = request.data.get('meal_list', '')
                        date = request.data.get('date', '')
                        # date = json_data.get('date')
                        if date == '':
                            date = datetime.utcnow().date()
                        if menu_meals:
                            meals = [Meal.get(id=id) for id in menu_meals]
                            menu = Menu(date=date)
                            menu.add_meal_to_menu(meals) 
                            return {'message': 'Todays menu has been updated'}, 201
                        return {'message': 'Please add meals to menu'}, 202
                        
                    else:
                              
                        response = {
                            'message': 'You are unauthorized to access this'
                        }
                        return make_response(jsonify(response)), 401

                else:
                
                    menu = Menu.query.order_by('menu.date').all()[-1]
                    menu_meals = [item.make_dict() for item in menu.meals]
                    return {
                        'message': 'Here is the menu for today',
                        'menu': menu_meals
                    }, 200
                     
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401 

        else:
            response = {
                'message': 'Please input access token'
            }
            return make_response(jsonify(response)), 401    



    
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)
    

    return app