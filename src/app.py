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
from models import db, User
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



   
# Traer lista planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    results = [planet.serialize() for planet in planets]

    return jsonify(results), 200

# Traer un solo planeta
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    # Buscar el planeta por su ID
    planet = Planet.query.get(planet_id)
    
    # Codigo de errores
    if planet:
        return jsonify(planet.serialize()), 200
    else:
        return jsonify({"msg":"planeta no encontrado"})
    
#añadir planeta favoritos
@app.route('/favorites', methods=['POST'])
def add_to_favorites():
    # Obtener los datos de la solicitud
    data = request.get_json()
    planet_id = data.get('planet_id')
   
    # Verificar que se recibieron los datos necesarios
    if not planet_id:
        return jsonify({"error": "Missing planet_id or email"}), 400

    # Buscar el planeta en la base de datos
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    # Verificar si el favorito ya existe
    existing_favorite = Favoritos.query.filter_by(name=planet.name).first()
    if existing_favorite:
        return jsonify({"message": "Planeta existe en favoritos"}), 200

    # Crear un nuevo registro de favorito
    new_favorite = Favoritos(name=planet.name, email=user_email)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Planeta añadido a favoritos"}), 201

#Eliminar planeta de favoritos
@app.route('/favorites', methods=['DELETE'])
def remove_from_favorites():
    # Obtener los datos de la solicitud
    data = request.get_json()
    planet_id = data.get('planet_id')

    # Verificar que se recibieron los datos necesarios
    if not planet_id:
        return jsonify({"error": "Missing planet_id or email"}), 400

    # Buscar el planeta en la base de datos
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    # Buscar el registro de favorito en la base de datos
    favorite = Favoritos.query.filter_by(name=planet.name,).first()
    if favorite is None:
        return jsonify({"error": "Planeta no encontrado en favoritos"}), 404

    # Eliminar el registro de favorito
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Planeta eliminado de favoritos"}), 200





    
    

   















# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
