#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):

    def post(self):

        request_json = request.get_json()

        try:
            user= User(
            username = request_json.get('username'),
            image_url = request_json.get('image_url'),
            bio = request_json.get('bio')
            ) 


            user.password_hash = request_json.get('password')


            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return make_response(user.to_dict()), 201

        except (IntegrityError, ValueError) as err:
            return {'errors': [str(err)]}, 422

class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return make_response(user.to_dict(), 200)
        else:        
            return {'error': '401 Unauthorized'}, 401 

class Login(Resource):
    def post(self):

        request_json = request.get_json()

        user = User.query.filter(User.username ==request_json.get('username')).first()

        if user:
            if user and user.authenticate(request_json.get('password')):

                session['user_id'] = user.id
                return make_response(user.to_dict()), 200

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

        recipes = Recipe.query.all()
        return [recipe.to_dict() for recipe in recipes], 200

        
    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'errors': ['Unauthorized']}, 401

        request_json = request.get_json()
        user = User.query.get(user_id)

        try:
            recipe = Recipe(
                title=request_json.get('title'),
                instructions=request_json.get('instructions'),
                minutes_to_complete=request_json.get('minutes_to_complete'),
                user=user
            )

            db.session.add(recipe)
            db.session.commit()
            return make_response(recipe.to_dict(), 201)
        except (IntegrityError, ValueError) as err:
            return {'errors': [str(err)]}, 422
        

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)