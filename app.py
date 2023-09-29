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
        user_email = request.json['email']
        updateEmail = request.json['updateEmail']
        updatePassword = request.json['updatePassword']

        update_user_email = {'email': user_email}
        update_user = {
            '$set': {
                'email': updateEmail,
                'password': updatePassword
            }
        }
        self.user_collection.update_one(update_user_email, update_user)

        return "Profile has been updated"

    def delete_user_data(self):
        user_given_id = request.json['id']
        database_users_data = self.user_collection.find()
        user_data = []
        for user in database_users_data:

            # converting the id into string.
            user_id = user['_id']
            user_id_str = str(user_id)
            user_data.append(user_id_str)

        # if user_given_id in user_data:
        #     return 


        # return "Profile has been successfully deleted"

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
