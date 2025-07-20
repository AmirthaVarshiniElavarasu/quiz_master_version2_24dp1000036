from flask import Blueprint,jsonify,request,make_response
from flask_security import auth_required,roles_required,current_user,utils,auth_token_required
from .database import db
from .userdb import datastore
from datetime import datetime
from flask_restful import Resource

main_routes=Blueprint('main_routes',__name__)

class AdminHome(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        return make_response(jsonify({"message":"This is admin page"}),200)

class UserHome(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self):
        user = current_user
        return make_response(jsonify({
            "username":user.username,
            "email":user.email,
            "password":user.password
        }),200)


class Registration(Resource):
    def post(self):
        details_of_user=request.get_json()

        if 'email' not in details_of_user or 'password' not in details_of_user:
            return make_response(jsonify({
                'message': 'email and passwrod are required'
            }),400)
        
        email= details_of_user.get('email')
        password=utils.hash_password(details_of_user.get('password'))
        username=details_of_user.get('username')
        qualification=details_of_user.get('qualification')
        gender=details_of_user.get('gender')
        dob_str=details_of_user.get('dob')
        dob=datetime.strptime(dob_str,'%Y-%m-%d').date()

        user=datastore.find_user(email=email)
        if user:
            return make_response(jsonify({
                'message': 'User already exists'
            }),400)
        
        user_role=datastore.find_role('user')
        user=datastore.create_user(email=email,
                                password=password,
                                username=username,
                                qualification=qualification,
                                gender=gender,
                                dob=dob,
                                roles=[user_role])
        
        db.session.commit()

        return make_response(jsonify({
            'message': 'User created successfully',
            'user':{
                'email': user.email,
                'roles': [role.name for role in user.roles]
            }
        }), 201)


class Login(Resource):
    def post(self):
        login_credentials = request.get_json()

        if 'email' not in login_credentials or 'password' not in login_credentials:
            return make_response(jsonify({
                'message': 'email and password are required'
            }),400)
        
        email= login_credentials.get('email')
        password= login_credentials.get('password')

        user = datastore.find_user(email=email)
        if not user:
            return make_response(jsonify({
                'message':'User does not exist'
            }),404)
        
        if not utils.verify_password(password,user.password):
            return make_response(jsonify({
                'message': 'Invalid password'
            }),401)
        utils.login_user(user)

        auth_token=user.get_auth_token()

        return make_response(jsonify({
            'message':'Login Successfully',
            'user':{
                'email': user.email,
                'roles':[role.name for role in user.roles] 
            },
            'auth_token':auth_token
        }),200)

class Logout(Resource):
    @auth_token_required
    def post(self):
        utils.logout_user()
        return make_response(jsonify({
            'message':'Logout successful'
        }),200)


def register_routes(api):
    api.add_resource(AdminHome,'/api/admin')
    api.add_resource(UserHome,'/api/user')
    api.add_resource(Registration,'/api/registration')
    api.add_resource(Login,'/api/login')
    api.add_resource(Logout, '/api/logout')
