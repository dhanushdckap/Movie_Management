import hashlib, json, datetime
from flask import Flask,request,jsonify
from pymongo import MongoClient
from flask_jwt_extended import create_access_token,JWTManager

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017')
database = client['movie_database']
user_collection = database['users']

JWT_manager = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "143"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)

@app.route('/create_user_data',methods=['POST'])
def create_user_data():
    email = request.args.get('email')
    password = request.args.get('password')
    password_byte = password.encode('utf-8')
    encryt_password = hashlib.sha256(password_byte).hexdigest()


    user_data = {
        'email': email,
        'password': encryt_password
    }

    user_collection.insert_one(user_data)

    return "Succesfully inserted"

@app.route('/show_users_data', methods=['GET'])
def show_users_data():
    show_users_id = request.args.get("id")
    # Fetch data from MongoDB and convert it to a list of dictionaries
    database_users_data = database.users.find()
    user_data = []
    for user in database_users_data:
        # Remove the '_id' field if you don't need it
        # user.pop('_id', None)

        #converting the id into string.
        user_id = user['_id']
        user_id_str = str(user_id)
        user_data.append(user_id_str)

    # Return the data as a JSON response
    return jsonify(user_data)

@app.route('/edit_user_data',methods=['PUT'])
def edit_user_data():
    user_email = request.args.get('email')
    updateEmail = request.args.get('updateEmail')
    updatePassword = request.args.get('updatePassword')

    update_user_email = {'email':user_email}
    update_user = {'$set':{
        'email':updateEmail,
        'password':updatePassword
    }}
    user_collection.update_one(update_user_email,update_user)

    return "profile has update"
@app.route('/delete_user_data',methods=['DELETE'])
def delete_user_data():
    id = int(request.args.get('id'))
    delete_id = {'id':id}
    user_collection.delete_one(delete_id)

    return "profile has succesfully deleted"


@app.route('/login_info',methods=['GET','POST'])
def login_info():

    email = request.json['email']
    password = request.json['password']
    password_byte = password.encode('utf-8')
    encryt_password = hashlib.sha256(password_byte).hexdigest()

    user_database_password = database.users.find_one({"email":email},{"_id":0})

    if user_database_password:
        if encryt_password == user_database_password["password"]:
            token = create_access_token(identity={'email':email,'password':encryt_password})
            return token
        return "password doesn't match"
    return (user_database_password)


app.run(debug=True)