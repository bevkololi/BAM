# BOOK A MEAL APP

[![Build Status](https://travis-ci.org/bevkololi/Book-A-Meal.svg?branch=challenge2)](https://travis-ci.org/bevkololi/Book-A-Meal)


Book-A-Meal is an application that allows customers to make food orders and helps the food vendor know what the customers want to eat. This tracking helps keep work in order.
Find it on https://bevkololi.github.io or clone the files from https://github.com/bevkololi/Book-A-Meal.git. You can then open index.html file on your browser. Documentation is also here https://bookameal2.docs.apiary.io/#

# TECHNOLOGIES USED
The application is built using the following technologies:
1. Python 3.6
2. Flask Microframework

Dependancies are installed in the requirements.txt tile, as long as one has set up one's own virtual environments.
Process of using it includes customer sign up and loging in to access meals and make orders.
 
# UI
The UI page contains:
1. User sign up and sign in pages
2. A ppage where the caterer can perform CRUD operations i.e Create, Read, Update and modify meals
3. A page where the caterer can add the meals of the day
4. A page where users can see the menu
5. A page where users can order the meal they want.

The following is a preview of the application:

![bookameal](https://user-images.githubusercontent.com/26184534/39295059-17f0958e-4946-11e8-9627-60c7dc1b590f.png)


![screenshot 22](https://user-images.githubusercontent.com/26184534/39295064-1ac17788-4946-11e8-8265-ede8d9dc58bb.png)


![screenshot 23](https://user-images.githubusercontent.com/26184534/39295075-25e9f7ca-4946-11e8-9680-6ad55f7caa18.png)

    
# Unit testing
The following tests have beeen setuo:
1. test_meals.py: To test on the addition, updating or removal of meals
2. test_orders.py: To test how to get the orders given by the customers
3. test_auth.py: To test the sign in and login of applications
Pytest is much prefered in conducting these tests.

# API ENDPOINTS
The following are the API endpoints used in the application:
1. /api/auth/signup: To register a user
2. /api/auth/login: To login an authenticated user
3. /api/v1/meals: To get meals available
4. /api/v1/meals/<int:id>: To get meal using its meal id, and update or delete it
5. /api/v1/orders: To get all the orders
6: /api/v1/orders/<username>: To get orders by a particular customer
    

The endpoints have been tested on postman. Here are the expected outcomes:

![screenshot 26](https://user-images.githubusercontent.com/26184534/39310723-d0b7a332-4973-11e8-82d3-6e39738f1c31.png)

![screenshot 27](https://user-images.githubusercontent.com/26184534/39310724-d11ecf62-4973-11e8-81c6-a5c0d9ba33ce.png)

![screenshot 28](https://user-images.githubusercontent.com/26184534/39310726-d1820c80-4973-11e8-9f4f-fe8b62129ba0.png)


 Feedback is much appreciated.
 
 Enjoy 



