from flask import Flask,request,jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017')
database = client['movie_database']
user_collection = database['users']

@app.route('/create_user_data',methods=['POST'])
def create_user_data():
    email = request.args.get('email')
    password = request.args.get('password')

    user_data = {
        'email':email,
        'password':password
    }
    print(email)
    user_collection.insert_one(user_data)
    return "Succesfully inserted"


@app.route('/show_users_data', methods=['GET'])
def show_users_data():
    # Fetch data from MongoDB and convert it to a list of dictionaries
    database_users_data = database.users.find()
    user_data = []
    for user in database_users_data:
        # Remove the '_id' field if you don't need it
        user.pop('_id', None)
        user_data.append(user)

    # Return the data as a JSON response
    return jsonify(user_data)

@app.route('/edit_user_data',methods=['PUT'])
def edit_user_data():
    email = request.args.get('email')
    updateEmail = request.args.get('updateEmail')
    updatePassword = request.args.get('updatePassword')

    update_user_email = {'email':email}
    update_user = {'$set':{
        'email':updateEmail,
        'password':updatePassword
    }}
    user_collection.update_one(update_user_email,update_user)

    return "profile has update"

@app.route('/delete_user_data',methods=['DELETE'])
def delete_user_data():
    email = request.args.get('email')
    delete_email_id = {'email':email}
    user_collection.delete_one(delete_email_id)

    return "profile has succesfully deleted"



app.run(debug=True)