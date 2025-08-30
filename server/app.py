#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):

    def post(self):

        request_json = request.get_json()

        username = request_json.get('username')
        password = request_json.get('password')
    
        if not username:
            return {'errors': ['Username is required']}, 422
        if not password:
            return {'errors': ['Password is required']}, 422

        try:
            user = User(
                username=username, 
                image_url=request_json.get('image_url'),
                bio=request_json.get('bio')
            )

            user.password_hash = password  # Use the validated password variable

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return user.to_dict(), 201  # Remove make_response wrapper

        except (IntegrityError, ValueError) as err:
            db.session.rollback()
            return {'errors': [str(err)]}, 422


class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return user.to_dict(), 200  # Remove make_response wrapper
        else:        
            return {'error': '401 Unauthorized'}, 401 

class Login(Resource):
    def post(self):

        request_json = request.get_json()

        username = request_json.get('username')
        password = request_json.get('password')

        if not username or not password:
            return {'error': '401 Unauthorized'}, 401
    
        user = User.query.filter(User.username == username).first()
    
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200  # Remove make_response wrapper

        return {'error': '401 Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None 
            return {}, 204
        else:
            return {'error': '401 Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'errors': ['Unauthorized']}, 401

        recipes = Recipe.query.filter_by(user_id=user_id).all()
        return [recipe.to_dict() for recipe in recipes], 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'errors': ['Unauthorized']}, 401

        request_json = request.get_json()

        try:
            recipe = Recipe(
                title=request_json.get('title'),
                instructions=request_json.get('instructions'),
                minutes_to_complete=request_json.get('minutes_to_complete'),
                user_id=user_id
            )

            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201  # Remove make_response wrapper
        except (IntegrityError, ValueError) as err:
            db.session.rollback()
            return {'errors': [str(err)]}, 422

        

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)