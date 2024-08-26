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
from models import db, User, Planet, Character, Vehicle, FavoritePlanets, FavoriteCharacters, FavoriteVehicles
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

@app.route('/user', methods=['GET'])
def get_all_users():
    all_users = User.query.all()

    return jsonify({
        'msg': 'GET all users ',
        'data': list(map(User.serialize, all_users))
    }), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    single_user = User.query.get(user_id)
    if single_user is None:
        return jsonify({'msg': f'User with id {user_id} does not exist'}), 404    

    return jsonify({
        'msg': 'GET single user ',
        'data': single_user.serialize()
    }), 200

@app.route('/user', methods=['POST'])
def add_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'You must send information in the body'}), 400
    
    required_fields = ['user_name', 'email', 'password', 'is_active'] 
       
    if not all(field in body for field in required_fields):
            return jsonify({'msg': 'The fields user_name, email, password and is_active are required'}), 400
    for field in body:
        if field not in required_fields:
            return jsonify({'msg': 'allowed fields user_name, email, password and is_active'}), 400
    
    if User.query.filter_by(user_name=body['user_name']).first() or User.query.filter_by(email=body['email']).first():
        return jsonify({'msg': 'User with this username or email already exists'}), 400    
    
    new_user = User(**body)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'msg': 'New user created',
        'data': new_user.serialize()
    }), 201

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg':f'User with id {user_id} not found'}), 404
    
    if not user.is_active:
        return jsonify({'msg': f'User with id {user_id} is already deactivated'}), 400
    
    user.is_active = False   
    db.session.commit()

    return jsonify({'msg':f'User with id {user_id} deactivated'}), 200
    
@app.route('/user/<int:user_id>', methods=['PUT'])
def modified_user(user_id):

    user = User.query.get(user_id)     
    if user is None:
        return jsonify({'msg':f'User with id {user_id} not found'}), 404
    
    body = request.get_json(silent=True)
    if not body:
        return jsonify({'msg':'You must send information in the body'}), 400
    
    allowed_fields = ['user_name', 'email', 'password', 'is_active']
    for field in body:
        if field not in allowed_fields:
            return jsonify({'msg': 'allowed fields user_name, email, password and is_active'}), 400
    
    if 'user_name' in body:
        if User.query.filter_by(user_name=body['user_name']).first():
            return jsonify({'msg': 'This username already exists'}), 400
        
    if 'email' in body:            
        if User.query.filter_by(email=body['email']).first():
            return jsonify({'msg': 'This email already exists'}), 400
    
    if 'user_name' in body:
        user.user_name = body['user_name']
    if 'email' in body:
        user.email = body['email']    
    if 'password' in body:
        user.password = body['password']
    if 'is_active' in body:
        user.is_active = body['is_active'] 
    db.session.commit()

    return jsonify({'msg':f'User with id {user_id} modified successfully'}), 200

@app.route('/planet', methods=['GET'])
def get_all_planets():
    all_planets = Planet.query.all()
    
    return jsonify({
        'msg': 'GET all PLanets',
        'data': list(map(Planet.serialize, all_planets))
    })

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    single_planet = Planet.query.get(planet_id)
    if single_planet is None:
        return jsonify({'msg': f'Planet with id {planet_id} does not exist'}), 404
    return jsonify({
        'msg': 'GET single planet',
        'data': single_planet.serialize()
    })

@app.route('/planet', methods=['POST'])
def add_planet():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'You must send information in the body'}), 400
    
    required_fields = ['planet_name', 'diameter', 'rotation_period', 'orbital_period', 'climate']
    if not all(field in body for field in required_fields):
        return jsonify({'msg': 'The fields planet_name, diameter, rotation_period, orbital_period and climate are required'}), 400
    for field in body:
        if field not in required_fields:
            return jsonify({'msg': 'Allowed fields planet_name, diameter, rotation_period, orbital_period and climate'}), 400
    
    if Planet.query.filter_by(planet_name=body['planet_name']).first():
        return jsonify({'msg': 'Planet name already exists'}), 400
    
    new_planet = Planet(**body)
    db.session.add(new_planet)
    db.session.commit()

    return jsonify ({
        'msg': 'New planet created',
        'data': new_planet.serialize()
    }), 201

@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': f'Planet with id {planet_id} not found'}), 404
    db.session.delete(planet)
    db.session.commit()

    return jsonify({'msg': f'Planet with id {planet_id} delete'}), 200

@app.route('/planet/<int:planet_id>', methods=['PUT'])
def modified_planet(planet_id):

    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'msg':f'Planet with id {planet_id} not found'}), 404
    
    body = request.get_json(silent=True)
    if not body:
        return jsonify({'msg':'You must send information in the body'}), 400
    
    allowed_fields = ['planet_name', 'diameter', 'rotation_period', 'orbital_period', 'climate']
    for field in body:
        if field not in allowed_fields:
            return jsonify({'msg': 'allowed fields planet_name, diameter, rotation_period, orbital_period and climate'}), 400

    if 'planet_name' in body:
        if Planet.query.filter_by(planet_name=body['planet_name']).first():
            return jsonify({'msg': 'Planet name already exists'}), 400

    if 'planet_name' in body:
        planet.planet_name = body['planet_name']
    if 'diameter' in body:
        planet.diameter = body['diameter']
    if 'rotation_period' in body:
        planet.rotation_period = body['rotation_period']
    if 'orbital_period' in body:
        planet.orbital_period = body['orbital_period']
    if 'climate' in body:
        planet.climate = body['climate'] 
    db.session.commit()

    return jsonify({'msg':f'Planet with id {planet_id} modified successfully'}), 200       
                   
@app.route('/character', methods=['GET'])
def get_all_characters():
    all_characters = Character.query.all()
    
    return jsonify({
        'msg': 'GET all Characters',
        'data': list(map(Character.serialize, all_characters))
    })

@app.route('/character/<int:character_id>', methods=['GET'])
def get_single_character(character_id):
    single_character = Character.query.get(character_id)
    if single_character is None:
        return jsonify({'msg': f'Character with id {character_id} does not exist'}), 404
    return jsonify({
        'msg': 'GET single character',
        'data': single_character.serialize()
    })

@app.route('/character', methods=['POST'])
def add_character():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'You must send information in the body'}), 400
    
    required_fields = ['character_name', 'skin_color', 'hair_color', 'gender', 'age']
    if not all(field in body for field in required_fields):
        return jsonify({'msg': 'The fields character_name, skin_color, hair_color, gender and age are required'}), 400
    for field in body:
        if field not in required_fields:
            return jsonify({'msg': 'allowed fields character_name, skin_color, hair_color, gender and age'}), 400
    
    if Character.query.filter_by(character_name=body['character_name']).first():
        return jsonify({'msg': 'Character name already exists'}), 400
    
    new_character = Character(**body)
    db.session.add(new_character)
    db.session.commit()

    return jsonify ({
        'msg': 'New character created',
        'data': new_character.serialize()
    }), 201

@app.route('/character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({'msg': f'Character with id {character_id} not found'}), 404
    db.session.delete(character)
    db.session.commit()

    return jsonify({'msg': f'Character with id {character_id} delete'}), 200

@app.route('/character/<int:character_id>', methods=['PUT'])
def modified_character(character_id):

    character = Character.query.get(character_id)
    if character is None:
        return jsonify({'msg':f'Character with id {character_id} not found'}), 404
    
    body = request.get_json(silent=True)
    if not body:
        return jsonify({'msg':'You must send information in the body'}), 400
    
    allowed_fields = ['character_name', 'skin_color', 'hair_color', 'gender', 'age']
    for field in body:
        if field not in allowed_fields:
            return jsonify({'msg': 'allowed fields character_name, skin_color, hair_color, gender and age'}), 400

    if 'character_name' in body:
        if Character.query.filter_by(character_name=body['character_name']).first():
            return jsonify({'msg': 'Character name already exists'}), 400

    if 'character_name' in body:
        character.character_name = body['character_name']
    if 'skin_color' in body:
        character.skin_color = body['skin_color']
    if 'hair_color' in body:
        character.hair_color = body['hair_color']
    if 'gender' in body:
        character.gender = body['gender']
    if 'age' in body:
        character.age = body['age'] 
    db.session.commit()

    return jsonify({'msg':f'Character with id {character_id} modified successfully'}), 200  

@app.route('/vehicle', methods=['GET'])
def get_all_vehicles():
    all_vehicle = Vehicle.query.all()
    
    return jsonify({
        'msg': 'GET all Vehicle',
        'data': list(map(Vehicle.serialize, all_vehicle))
    })

@app.route('/vehicle/<int:vehicle_id>', methods=['GET'])
def get_single_vehicle(vehicle_id):
    single_vehicle = Vehicle.query.get(vehicle_id)
    if single_vehicle is None:
        return jsonify({'msg': f'vehicle with id {vehicle_id} does not exist'}), 404
    return jsonify({
        'msg': 'GET single vehicle',
        'data': single_vehicle.serialize()
    })

@app.route('/vehicle', methods=['POST'])
def add_vehicle():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'You must send information in the body'}), 400
    
    required_fields = ['vehicle_name', 'passengers', 'load_capacity', 'armament', 'length']
    if not all(field in body for field in required_fields):
        return jsonify({'msg': 'The fields vehicle_name, passengers, load_capacity, armament and length are required'}), 400
    for field in body:
        if field not in required_fields:
            return jsonify({'msg': 'allowed fields vehicle_name, passengers, load_capacity, armament and length'}), 400
    
    if Vehicle.query.filter_by(vehicle_name=body['vehicle_name']).first():
        return jsonify({'msg': 'vehicle name already exists'}), 400
    
    new_vehicle = Vehicle(**body)
    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify ({
        'msg': 'New vehicle created',
        'data': new_vehicle.serialize()
    }), 201

@app.route('/vehicle/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle is None:
        return jsonify({'msg': f'Vehicle with id {vehicle_id} not found'}), 404
    db.session.delete(vehicle)
    db.session.commit()

    return jsonify({'msg': f'Vehicle with id {vehicle_id} delete'}), 200

@app.route('/vehicle/<int:vehicle_id>', methods=['PUT'])
def modified_vehicle(vehicle_id):

    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle is None:
        return jsonify({'msg':f'Vehicle with id {vehicle_id} not found'}), 404
    
    body = request.get_json(silent=True)
    if not body:
        return jsonify({'msg':'You must send information in the body'}), 400
    
    allowed_fields = ['vehicle_name', 'passengers', 'load_capacity', 'armament', 'length']
    for field in body:
        if field not in allowed_fields:
            return jsonify({'msg': 'allowed fields vehicle_name, passengers, load_capacity, armament and length'}), 400

    if 'vehicle_name' in body:
        if Vehicle.query.filter_by(vehicle_name=body['vehicle_name']).first():
            return jsonify({'msg': 'vehicle name already exists'}), 400

    if 'vehicle_name' in body:
        vehicle.vehicle_name = body['vehicle_name']
    if 'passengers' in body:
        vehicle.passengers = body['passengers']
    if 'load_capacity' in body:
        vehicle.load_capacity = body['load_capacity']
    if 'armament' in body:
        vehicle.armament = body['armament']
    if 'length' in body:
        vehicle.length = body['length'] 
    db.session.commit()

    return jsonify({'msg':f'Vehicle with id {vehicle_id} modified successfully'}), 200  

@app.route('/user/<int:id_user>/favorites', methods=['GET'])
def get_favorites(id_user):
    favorite_planets = FavoritePlanets.query.filter_by(user_id = id_user).all()
    favorite_characters = FavoriteCharacters.query.filter_by(user_id = id_user).all()
    favorite_vehicles = FavoriteVehicles.query.filter_by(user_id = id_user).all()
    return jsonify ({
        'msg': f'GET all favorites of user with id {id_user}',
        'data': {
            'favorite_planets': list(map(FavoritePlanets.serialize, favorite_planets)),
            'favorite_characters': list(map(FavoriteCharacters.serialize, favorite_characters)),
            'favorite_vehicles': list(map(FavoriteVehicles.serialize, favorite_vehicles)),
            'user_data': favorite_planets[0].user_relationship.serialize()
        }
    }), 200

@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['POST'])
def add_favorite_planet(planet_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'The user does not exist'}), 404    
    
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': 'The planet does not exist'}), 404    
    
    if FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first():
        return jsonify({'msg': 'Planet is already a favorite'}), 400
    
    new_favorite_planet = FavoritePlanets()
    new_favorite_planet.user_id = user_id
    new_favorite_planet.planet_id = planet_id

    db.session.add(new_favorite_planet)
    db.session.commit()
    
    return jsonify({'msg': 'Planet added to favorites'}), 201

@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id, user_id):
    
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'User not found'}), 404    
    
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404    
    
    favorite_planet = FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite_planet is None:
        return jsonify({'msg': 'Favorite planet not found'}), 404    
    
    db.session.delete(favorite_planet)
    db.session.commit()
    
    return jsonify({'msg': 'Favorite planet deleted'}), 200

@app.route('/favorite/character/<int:character_id>/<int:user_id>', methods=['POST'])
def add_favorite_character(character_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'The user does not exist'}), 404    
    
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({'msg': 'The character does not exist'}), 404    
    
    if FavoriteCharacters.query.filter_by(user_id=user_id, character_id=character_id).first():
        return jsonify({'msg': 'character is already a favorite'}), 400
    
    new_favorite_character = FavoriteCharacters()
    new_favorite_character.user_id = user_id
    new_favorite_character.character_id = character_id

    db.session.add(new_favorite_character)
    db.session.commit()
    
    return jsonify({'msg': 'character added to favorites'}), 201

@app.route('/favorite/character/<int:character_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_character(character_id, user_id):
    
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'User not found'}), 404    
    
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({'msg': 'Character not found'}), 404    
    
    favorite_character = FavoriteCharacters.query.filter_by(user_id=user_id, character_id=character_id).first()
    if favorite_character is None:
        return jsonify({'msg': 'Favorite character not found'}), 404    
    
    db.session.delete(favorite_character)
    db.session.commit()
    
    return jsonify({'msg': 'Favorite character deleted'}), 200

@app.route('/favorite/vehicle/<int:vehicle_id>/<int:user_id>', methods=['POST'])
def add_favorite_vehicle(vehicle_id, user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'The user does not exist'}), 404    
    
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle is None:
        return jsonify({'msg': 'The vehicle does not exist'}), 404    
    
    if FavoriteVehicles.query.filter_by(user_id=user_id, vehicle_id=vehicle_id).first():
        return jsonify({'msg': 'Vehicle is already a favorite'}), 400
    
    new_favorite_vehicle = FavoriteVehicles()
    new_favorite_vehicle.user_id = user_id
    new_favorite_vehicle.vehicle_id = vehicle_id

    db.session.add(new_favorite_vehicle)
    db.session.commit()
    
    return jsonify({'msg': 'Vehicle added to favorites'}), 201

@app.route('/favorite/vehicle/<int:vehicle_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_vehicle(vehicle_id, user_id):
    
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': 'User not found'}), 404    
    
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle is None:
        return jsonify({'msg': 'Vehicle not found'}), 404    
    
    favorite_vehicle = FavoriteVehicles.query.filter_by(user_id=user_id, vehicle_id=vehicle_id).first()
    if favorite_vehicle is None:
        return jsonify({'msg': 'Favorite vehicle not found'}), 404    
    
    db.session.delete(favorite_vehicle)
    db.session.commit()
    
    return jsonify({'msg': 'Favorite vehicle deleted'}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
