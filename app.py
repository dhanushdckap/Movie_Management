import hashlib
import json
import datetime
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_jwt_extended import create_access_token, JWTManager
from bson.objectid import ObjectId

class MovieDatabaseApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_database()
        self.setup_jwt()
        self.setup_routes()

    def setup_database(self):
        self.client = MongoClient('mongodb://localhost:27017')
        self.database = self.client['movie_database']
        self.user_collection = self.database['users']

    def setup_jwt(self):
        self.JWT_manager = JWTManager(self.app)
        self.app.config["JWT_SECRET_KEY"] = "143"
        self.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)

    def setup_routes(self):
        self.app.route('/create_user_data', methods=['POST'])(self.create_user_data)
        self.app.route('/show_users_data', methods=['GET'])(self.show_users_data)
        self.app.route('/edit_user_data', methods=['PUT'])(self.edit_user_data)
        self.app.route('/delete_user_data', methods=['DELETE'])(self.delete_user_data)
        self.app.route('/login_info', methods=['GET', 'POST'])(self.login_info)

    def create_user_data(self):
        email = request.json['email']
        password = request.json['password']
        password_byte = password.encode('utf-8')
        encryt_password = hashlib.sha256(password_byte).hexdigest()

        user_data = {
            'email': email,
            'password': encryt_password
        }

        self.user_collection.insert_one(user_data)

        return "Successfully inserted"

    def show_users_data(self):
        database_users_data = self.user_collection.find()
        user_data = []
        for user in database_users_data:
            user.pop('_id', None)
            user_data.append(user)

        return jsonify(user_data)


    def edit_user_data(self):
        get_id = request.json['id']
        update_email = request.json['update_email']
        password = request.json['update_password']
        password_byte = password.encode('utf-8')
        encryt_password = hashlib.sha256(password_byte).hexdigest()

        update_user_id = {'_id': ObjectId(get_id)}
        update_user = {
            '$set': {
                'email': update_email,
                'password': encryt_password
            }
        }
        self.user_collection.update_one(update_user_id, update_user)

        return "Profile has been updated"

    def delete_user_data(self):
        get_id = request.json['id']
        self.user_collection.delete_one({"_id":ObjectId(get_id)})
        return "profile has succesfully deleted"




    def login_info(self):
        email = request.json['email']
        password = request.json['password']
        password_byte = password.encode('utf-8')
        encryt_password = hashlib.sha256(password_byte).hexdigest()

        user_database_password = self.user_collection.find_one({"email": email}, {"_id": 0})

        if user_database_password:
            if encryt_password == user_database_password["password"]:
                token = create_access_token(identity={'email': email, 'password': encryt_password})
                return token
            return "Password doesn't match"
        return str(user_database_password)

    def run(self):
        self.app.run(debug=True)

if __name__ == "__main__":
    movie_app = MovieDatabaseApp()
    movie_app.run()
