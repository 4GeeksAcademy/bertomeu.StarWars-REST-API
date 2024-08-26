from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    planets_favorites = db.relationship('FavoritePlanets', back_populates='user_relationship')
    characters_favorites = db.relationship('FavoriteCharacters', back_populates='user_relationship')
    vehicles_favorites = db.relationship('FavoriteVehicles', back_populates='user_relationship')

    def __repr__(self):
        return f'Created user with username {self.user_name} and id {self.id}'

    def serialize(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }
class Planet(db.Model):
    __tablename__ = 'planet' 
    planet_id = db.Column(db.Integer, primary_key=True)
    planet_name = db.Column(db.String(25), unique=True, nullable=False)   
    diameter = db.Column(db.Integer, unique=False, nullable=False)
    rotation_period = db.Column(db.Integer, unique=False, nullable=False)
    orbital_period = db.Column(db.Integer, unique=False, nullable=False)
    climate = db.Column(db.String(25), unique=False, nullable=False)
    favorite_by = db.relationship('FavoritePlanets', back_populates='planet_relationship')
    

    def __repr__(self):
        return f'Planet created with name {self.planet_name}'
    def serialize(self):
        return {
            "planet_id": self.planet_id,
            "planet_name": self.planet_name,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "climate": self.climate
        }
class Character(db.Model):
    __tablename__ = 'character'
    character_id = db.Column(db.Integer, primary_key=True)
    character_name = db.Column(db.String(25), unique=True, nullable=False)
    skin_color = db.Column(db.String(25), unique=False, nullable=False)
    hair_color = db.Column(db.String(25), unique=False, nullable=False)
    gender = db.Column(db.String(25), unique=False, nullable=False)
    age = db.Column(db.Integer, unique=False, nullable=False)
    favorite_by = db.relationship('FavoriteCharacters', back_populates='character_relationship')    
    
    def __repr__(self):
        return f'Character created with name {self.character_name}'
    def serialize(self):
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "skin_color": self.skin_color,
            "hair_color": self.hair_color,
            "gender": self.gender,
            "age": self.age,                               
        }     
class Vehicle(db.Model):
    __tablename__ = 'vehicle'  
    vehicle_id = db.Column(db.Integer, primary_key=True)
    vehicle_name = db.Column(db.String(25), unique=True, nullable=False)
    passengers = db.Column(db.Integer, unique=False, nullable=False)
    load_capacity = db.Column(db.Integer, unique=False, nullable=False)
    armament = db.Column(db.String(50), unique=False, nullable=False)
    length = db.Column(db.Integer, unique=False, nullable=False)  
    favorite_by = db.relationship('FavoriteVehicles', back_populates='vehicle_relationship') 

    def __repr__(self):
        return f'Vehicle created with name {self.vehicle_name}'
    def serialize(self):
        return {
            "vehicle_id": self.vehicle_id,
            "vehicle_name": self.vehicle_name,
            "passengers": self.passengers,
            "load_capacity": self.load_capacity,
            "armament": self.armament,
            "length": self.length
        }
class FavoritePlanets(db.Model):
    __tablename__ = 'favorite_planets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_relationship = db.relationship('User', back_populates='planets_favorites')
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.planet_id'))
    planet_relationship = db.relationship('Planet', back_populates='favorite_by') 

    def __repr__(self):
        return f'(User {self.user_id} likes planet {self.planet_id})'
    def serialize(self):
        return {
            'id': self.id,    
            'planet': self.planet_relationship.serialize()
        }      
class FavoriteCharacters(db.Model):
    __tablename__ = 'favorite_characters'  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_relationship = db.relationship('User', back_populates='characters_favorites') 
    character_id = db.Column(db.Integer, db.ForeignKey('character.character_id')) 
    character_relationship = db.relationship('Character', back_populates='favorite_by')

    def __repr__(self):
        return f'(User {self.user_id} likes character {self.character_id})'
    def serialize(self):
        return {
            'id': self.id,
            'character': self.character_relationship.serialize()

        }
class FavoriteVehicles(db.Model):
    __tablename__ = 'favorite_vehicles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_relationship = db.relationship('User', back_populates='vehicles_favorites') 
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id')) 
    vehicle_relationship = db.relationship('Vehicle', back_populates='favorite_by')  

    def __repr__(self):
        return f'(User {self.user_id} likes vehicle {self.vehicle_id})'  
    def serialize(self):
        return {
            'id': self.id,
            'vehicle': self.vehicle_relationship.serialize()

        }
