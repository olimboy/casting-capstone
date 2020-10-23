import os
from functools import wraps
from flask import Flask, request, jsonify, abort, redirect
from flask_cors import CORS
from datetime import datetime

from models import setup_db, Movie, Actor, Association
from auth import AuthError, requires_auth
from authlib.integrations.flask_client import OAuth


# Decorator for check in request have json;
# Check keys in json;
def valid_json(keys=None, func=any):
    if keys is None:
        keys = []

    def valid_json_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                abort(415)
            data = request.get_json()
            if not func([item in data for item in keys]):
                abort(422)
            return f(data, *args, **kwargs)

        return wrapper

    return valid_json_decorator


app = Flask(__name__)
app.secret_key = 'asdasdadadasdadasdasdadasdasdadasdsadasdadasd'
setup_db(app)
CORS(app)

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    api_base_url='https://{}'.format(os.environ['AUTH0_DOMAIN']),
    access_token_url='https://{}/oauth/token'.format(os.environ['AUTH0_DOMAIN']),
    authorize_url='https://{}/authorize'.format(os.environ['AUTH0_DOMAIN'])
)

# ROUTES
# Movies


@app.route('/')
def login():
    login_url = 'https://{}/authorize?audience={}&response_type=token&client_id={}&redirect_uri={}'.format(
        os.environ['AUTH0_DOMAIN'],
        os.environ['API_AUDIENCE'],
        os.environ['CLIENT_ID'],
        os.environ['LOGIN_RESULTS']
    )
    return redirect(login_url)


@app.route('/login-results')
def results():
    print(request.url)
    print(request.__dict__)
    return jsonify({})
    # token = auth0.authorize_access_token()
    # userinfo = auth0.parse_id_token(token)
    # print(token)
    # print(userinfo)
    # return jsonify({
    #     'success': True,
    #     'token': auth0.token
    # })


@app.route('/movies')
@requires_auth(permission='get:movies')
def get_movies():
    return jsonify({
        'success': True,
        'movies': [movie.format() for movie in Movie.query.all()]
    })


@app.route('/movies', methods=['POST'])
@requires_auth(permission='post:movies')
@valid_json(keys=['title', 'release_date'], func=all)
def create_movie(data):
    try:
        date = datetime.strptime(data['release_date'], '%d.%m.%Y')
    except:
        abort(422)
    movie = Movie(title=data['title'], release_date=date)
    movie.insert()
    return jsonify({
        'success': True,
        'movie': movie.format()
    })


@app.route('/movies/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:movies')
@valid_json(keys=['title', 'release_date'], func=any)
def update_movie(data, id):
    movie = Movie.query.filter_by(id=id).one_or_none()
    if movie is None:
        abort(404)
    if 'title' in data:
        movie.title = data['title']
    if 'release_date' in data:
        movie.release_date = data['release_date']
    movie.update()
    return jsonify({
        'success': True,
        'movie': movie.format()
    })


@app.route('/movies/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:movies')
def delete_movie(id):
    movie = Movie.query.filter_by(id=id).one_or_none()
    if movie is None:
        abort(404)
    movie.delete()
    return jsonify({
        'success': True,
        'delete': id
    })


# Actors
@app.route('/actors')
@requires_auth(permission='get:actors')
def get_actors():
    return jsonify({
        'success': True,
        'actors': [actor.format() for actor in Actor.query.all()]
    })


@app.route('/actors', methods=['POST'])
@requires_auth(permission='post:actors')
@valid_json(keys=['name', 'age', 'gender'], func=all)
def create_actor(data):
    actor = Actor(name=data['name'], age=data['age'], gender=data['gender'])
    actor.insert()
    return jsonify({
        'success': True,
        'actor': actor.format()
    })


@app.route('/actors/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:actors')
@valid_json(keys=['name', 'age', 'gender'], func=any)
def update_actor(data, id):
    actor = Actor.query.filter_by(id=id).one_or_none()
    if actor is None:
        abort(404)
    if 'name' in data:
        actor.name = data['name']
    if 'age' in data:
        actor.age = data['age']
    if 'gender' in data:
        actor.gender = data['gender']
    actor.update()
    return jsonify({
        'success': True,
        'actor': actor.format()
    })


@app.route('/actors/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:actors')
def delete_actor(id):
    actor = Actor.query.filter_by(id=id).one_or_none()
    if actor is None:
        abort(404)
    actor.delete()
    return jsonify({
        'success': True,
        'delete': id
    })


# Many To Many {Movie - Actor}

@app.route('/movies/<int:id>/actors', methods=['POST'])
@requires_auth(permission='post:movies_actors')
@valid_json(keys=['ids'], func=all)
def create_movies_actors(data, id):
    movie = Movie.query.filter_by(id=id).one_or_none()
    if movie is None:
        abort(404)
    actors = Actor.query.filter(Actor.id.in_(data['ids'])).all()
    associations = []
    for actor in actors:
        association = Association.query.filter_by(actor_id=actor.id, movie_id=movie.id).one_or_none()
        if association is None:
            association = Association(actor=actor, movie=movie)
        associations.append(association)
    movie.actors.extend(associations)
    movie.update()
    return jsonify({
        'success': True,
        'movie': movie.format()
    })


@app.route('/movies/<int:id>/actors', methods=['DELETE'])
@requires_auth(permission='delete:movies_actors')
@valid_json(keys=['ids'], func=all)
def delete_movies_actors(data, id):
    movie = Movie.query.filter_by(id=id).one_or_none()
    if movie is None:
        abort(404)
    movie_actors = Association.query.filter(Association.movie_id == movie.id,
                                            Association.actor_id.in_(data['ids'])).all()
    for actor in movie_actors:
        actor.delete()
    return jsonify({
        'success': True,
        'movie': movie.format()
    })


@app.route('/actors/<int:id>/movies', methods=['POST'])
@requires_auth(permission='post:actors_movies')
@valid_json(keys=['ids'], func=all)
def create_actors_movies(data, id):
    actor = Actor.query.filter_by(id=id).one_or_none()
    if actor is None:
        abort(404)
    movies = Movie.query.filter(Movie.id.in_(data['ids'])).all()
    associations = []
    for movie in movies:
        association = Association.query.filter_by(actor_id=actor.id, movie_id=movie.id).one_or_none()
        if association is None:
            association = Association(actor=actor, movie=movie)
        associations.append(association)
    actor.movies.extend(associations)
    actor.update()
    return jsonify({
        'success': True,
        'actor': actor.format()
    })


@app.route('/actors/<int:id>/movies', methods=['DELETE'])
@requires_auth(permission='delete:actors_movies')
@valid_json(keys=['ids'], func=all)
def delete_actors_movies(data, id):
    actor = Actor.query.filter_by(id=id).one_or_none()
    if actor is None:
        abort(404)
    actors_movies = Association.query.filter(Association.actor_id == actor.id,
                                            Association.movie_id.in_(data['ids'])).all()
    for movie in actors_movies:
        movie.delete()
    return jsonify({
        'success': True,
        'actor': actor.format()
    })


@app.errorhandler(401)
def unathorized(error):
    return jsonify({
        "success": False,
        "error": error.description
    }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": {
            "code": 404,
            "message": "Resource not found"
        }
    }), 404


@app.errorhandler(409)
def conflict(error):
    return jsonify({
        "success": False,
        "error": {
            "code": 409,
            "message": "Data already have in db"
        }
    }), 409


@app.errorhandler(415)
def unsupported_media(error):
    return jsonify({
        "success": False,
        "error": {
            "code": 415,
            "message": "Unsupported media type"
        }
    }), 415


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": {
            "code": 422,
            "message": "Data is not fully"
        }
    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": {
            "code": 500,
            "message": "Internal server error"
        }
    }), 500


@app.errorhandler(AuthError)
def auth_error(exp):
    return jsonify({
        "success": False,
        "error": exp.error
    }), exp.status_code
