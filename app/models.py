from app import db
from flask_bcrypt import Bcrypt
from flask import current_app
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship, backref

menu_meals = db.Table(
    'menu_meals',
    db.Column('menu_id', db.Integer(), db.ForeignKey('menu.id')),
    db.Column('meal_id', db.Integer(), db.ForeignKey('meals.id')))


class User(db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    caterer = db.Column(db.Boolean, default=False)
    orders = db.relationship(
        'Order', order_by='Order.id', cascade="all, delete-orphan")

    

    def __init__(self, username, email, password):
        """Initialize the user with an email and a password."""
        self.username = username
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()
        

    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database.
        This includes creating a new user and editing one.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            return {        'message': 'an error occured',
                            'Error': str(error)
                }, 400 

    @staticmethod
    def get_all():
        return User.query.all()

    def delete(self):
        """Deletes a given bucketlist."""
        db.session.delete(self)
        db.session.commit()


    def generate_token(self, user_id):
        """Generates the access token to be used as the Authorization header"""

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=3600),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                current_app.config.get('SECRET'),
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decode the access token from the Authorization header."""
        try:
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return "Expired token. Please log in to get a new token"
        except jwt.InvalidTokenError:
            return "Invalid token. Please register or login"


class Meal(db.Model):
    """This class defines te meal table."""

    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    price = db.Column(db.Integer())
    # orders = db.relationship(
    #     'Order' ,order_by='Order.id', cascade="all, delete-orphan")
    

    def __init__(self, name, price, description):
        """Initialize the meal with a name and its creator."""
        self.name = name
        self.description = description
        self.price = price
        


    def save(self):
        """Save a meal.
        This applies for both creating a new meal
        and updating an existing meal
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            return {        'message': 'an error occured',
                            'Error': str(error)
                }, 400 

    @staticmethod
    def get_all():
        return Meal.query.all()

    
    def delete(self):
        """Deletes a given meal."""
        db.session.delete(self)
        db.session.commit()

    def add_to_menu(self):
        '''method to add meal to todays menu'''
        Menu.add_meal(self)

    def __repr__(self):
        """Return a representation of a meal instance."""
        return "<Meal: {}>".format(self.meal)

    @classmethod
    def has(cls,**kwargs):
        obj = cls.query.filter_by(**kwargs).first()
        if obj:
            return True
        return False

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    def make_dict(self):
        '''serialize class'''
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}



class Order(db.Model):
    """This class defines the orders table."""

    __tablename__ = 'orders'

    # define the columns of the table, starting with its primary key
    id = db.Column(db.Integer, primary_key=True)
    meal = db.Column(db.String(255))
    quantity = db.Column(db.Integer())
    time_ordered = db.Column(db.DateTime, default=db.func.current_timestamp())
    ordered_by = db.Column(db.Integer, db.ForeignKey(User.id))
    

    def __init__(self, meal, quantity, ordered_by):
        """Initialize the order with a name and its creator."""
        self.meal = meal
        self.ordered_by = ordered_by
        self.quantity = quantity

    def add_meal_to_order(self, meal, quantity=1):
        assoc = MealAssoc(quantity=quantity)
        assoc.meal = meal
        self.meal.append(assoc)

    def save(self):
        """Save an order.
        This applies for both creating a new order
        and updating an existing update
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            return {        'message': 'an error occured',
                            'Error': str(error)
                }, 400 

    @staticmethod
    def get_all(user_id):
        """This method gets all the orders for a given user."""
        return Order.query.filter_by(ordered_by=user_id)

    
    def delete(self):
        """Deletes a given order."""
        db.session.delete(self)
        db.session.commit()

    
    def __repr__(self):
        """Return a representation of a order instance."""
        return "<Order: {}>".format(self.meal)



class Menu(db.Model):
    '''model for Menus'''
    __tablename__ = 'menu'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow().date(), unique=True)
    meals = relationship(
        'Meal', secondary='menu_meals', backref=backref('menu_meals', lazy=True, uselist=True))

        
    def add(self, key, value):
        if isinstance(value, list):
            old_value = getattr(self, key)
            old_value.extend(value)
            self.save()
        else:
            setattr(self, key, value)
            self.save()

    def add_meal_to_menu(self, meal, date=None):
        '''Add meal to menu'''
        if not date:
            date = datetime.utcnow().date()
        menu = Menu.query.filter_by(date=date).first()
        if not menu:
            menu = Menu()
        if isinstance(meal, Meal):
            meal = [meal]
        self.meals.extend(meal)
        self.save()
    

    def save(self):
        """Save a menu.
        This applies for both creating a new menu
        and updating an existing menu
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            return {        'message': 'an error occured',
                            'Error': str(error)
                }, 400 

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    def __repr__(self):
        '''class instance rep'''
        return '<Menu {}>'.format(self.meals)