"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, People, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def list_users():

    users_query=User.query.all()
    users_list=list(map(lambda user:user.serialize(),users_query))
    return jsonify(users_list)
    

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    email = data.get('email')
    password = data.get('password')
    is_active = data.get('is_active', True) 
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
     
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"error": "User already exists"}), 400
    
    new_user = User(email=email, password=password, is_active=is_active, first_name=first_name , last_name=last_name)
    db.session.add(new_user)
    db.session.commit()

    response_body = new_user.serialize()
    return jsonify(response_body), 201
    
@app.route('/planets', methods=['GET'])
def list_planets():
    planets_query=Planets.query.all()
    planets_list=list(map(lambda planet:planet.serialize(),planets_query))
    return jsonify(planets_list)

@app.route('/planets/<int:planet_id>', methods=['GET'])
def list_planet(planet_id):
    planet_query=Planets.query.filter_by(id=planet_id).first()
    if planet_query:
        response_body={
            "msg": "Planeta encontrado" , 
            "result": planet_query.serialize()
        }
        return jsonify(response_body), 200
    else:
        response_body={
           "msg": "Planeta no existe" 
        }
        return jsonify(response_body), 404
    
@app.route('/people', methods=['GET'])
def list_people():
    people_query=People.query.all()
    people_list=list(map(lambda person:person.serialize(),people_query))
    return jsonify(people_list)

@app.route('/people/<int:people_id>', methods=['GET'])
def list_person(people_id):
    people_query=People.query.filter_by(people_id=people_id).first()
    if people_query:
        response_body={
            "msg": "Resultado exitoso" , 
            "result": people_query.serialize()
        }
        return jsonify(response_body), 200
    else:
        response_body={
           "msg": "No existe" 
        }
        return jsonify(response_body), 404

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def user_favorites(user_id):
    user_favorites_query= Favorites.query.filter_by(user_fk=user_id).all()
    if not user_favorites_query:
        response_body={
            "msg": "usuario sin favoritos"
        }
        return jsonify(response_body), 404
    user_favorites=list(map(lambda item:item.serialize(),user_favorites_query))
    response_body={
            "msg": "favoritos encontrados" , 
            "result": user_favorites
        }
    return jsonify(response_body), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def create_planet_favorites(planet_id):
    request_body=request.json
    planet_favorite= Favorites(user_fk= request_body["user_id"],planet_fk=planet_id)
    db.session.add(planet_favorite)
    db.session.commit()
    response_body={
        "msg": "Favorito añadido con exito"
    }
    return(response_body),200

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def create_people_favorites(people_id):
    request_body=request.json
    people_favorite= Favorites(user_fk= request_body["user_id"],people_fk=people_id)
    db.session.add(people_favorite)
    db.session.commit()
    response_body={
        "msg": "Favorito añadido con exito"
    }
    return(response_body),200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorites(planet_id):
    request_body=request.json
    user_id = request_body.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID necesario"}), 400
    favorite = Favorites.query.filter_by(user_fk=user_id, planet_fk=planet_id).first()
    if not favorite:
        return jsonify({"error": "Favorito no encontrado"}), 404
    db.session.delete(favorite)
    db.session.commit()

    response_body={
        "msg": "Favorito eliminado con exito"
    }
    return(response_body),200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_favorites(people_id):
    request_body=request.json
    user_id = request_body.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID necesario"}), 400
    favorite = Favorites.query.filter_by(user_fk=user_id, people_fk=people_id).first()
    if not favorite:
        return jsonify({"error": "Favorito no encontrado"}), 404
    db.session.delete(favorite)
    db.session.commit()
    
    response_body={
        "msg": "Favorito eliminado con exito"
    }
    return(response_body),200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
