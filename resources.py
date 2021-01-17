import pickle
import joblib
import pandas
from flask import jsonify
from flask import request
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from flask_restful import Resource, reqparse, abort

from filters.collaborative_based_filter import collaborative_filter
from filters.content_based_filter import content_filter
from models import RevokedTokenModel
from models import UserModel

parser = reqparse.RequestParser()
parser.add_argument('username', help='This field cannot be blank', required=True)
parser.add_argument('password', help='This field cannot be blank', required=True)

users_data = pandas.read_csv(open("datasets/user_db.csv", "rb"))
titles_data = pickle.load(open("datasets/title.merged.sav", "rb"))

count_matrix = joblib.load('datasets/count_matrix.joblib')

from filters.popularity_based_filter import getTopN


class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}, 422

        new_user = UserModel(
            username=data['username'],
            password=UserModel.generate_hash(data['password'])
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}, 422

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token,
            }
        else:
            return {'message': 'Wrong credentials'}, 422


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return UserModel.return_all()

    def delete(self):
        return UserModel.delete_all()


class CollaborativeFilterRecommender(Resource):
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)
        userId = current_user.id
        recommendations = collaborative_filter(users_data, userId, n_recommendations=30)
        return {
            'data': recommendations
        }


class ContentFilterRecommender(Resource):
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)
        userId = current_user.id
        recommendations = content_filter(titles_data, users_data, count_matrix, userId, n_recommendations=30)
        return {
            'data': recommendations
        }


class PopularityFilterRecommender(Resource):
    @jwt_required
    def get(self):
        recommendations = getTopN(30)
        return jsonify(recommendations.values.tolist())


class Film(Resource):
    def get(self, filmId=None):
        if filmId is not None:
            return jsonify(titles_data[titles_data['tconst'] == filmId].values.tolist())
        else:
            size = 10
            page = getPage(self)

            start_index = (page - 1) * size
            end_index = (page * size)

            if request.args.get('title') is not None:
                return jsonify(titles_data[titles_data['primaryTitle'].str.contains(request.args.get('title'))][
                               start_index:end_index].values.tolist())
            else:
                return jsonify(titles_data[start_index:end_index].values.tolist())


class User(Resource):
    @jwt_required
    def get(self, filmId=None):
        username = get_jwt_identity()
        current_user = UserModel.find_by_username(username)
        userId = current_user.id
        data = users_data[users_data['userId'] == userId]

        if filmId is not None:
            return jsonify(data[data['tconst'] == filmId].values.tolist())

        size = 10
        page = getPage(self)

        start_index = (page - 1) * size
        end_index = (page * size)
        data = pandas.merge(data, titles_data[['tconst', 'primaryTitle']], on="tconst")
        return jsonify(data[start_index:end_index].values.tolist())

    @jwt_required
    def post(self, filmId=None):
        if filmId is not None and request.args.get('rating') is not None:
            username = get_jwt_identity()
            current_user = UserModel.find_by_username(username)
            userId = current_user.id

            global users_data

            if not ((users_data['userId'] == userId) & (users_data['tconst'] == filmId)).any():
                users_data = users_data.append(
                    {'userId': userId, 'tconst': filmId, 'rating': request.args.get('rating')},
                    ignore_index=True)

                return {'tconst': filmId, 'rating': request.args.get('rating')}
        abort(422)

    @jwt_required
    def put(self, filmId=None):
        if request.args.get('rating') is not None and filmId is not None:
            username = get_jwt_identity()
            current_user = UserModel.find_by_username(username)
            userId = current_user.id
            users_data.loc[(users_data['userId'] == userId) & (users_data['tconst'] == filmId), 'rating'] = float(
                request.args.get('rating'))
            return jsonify(
                users_data.loc[(users_data['userId'] == userId) & (users_data['tconst'] == filmId)].values.tolist())
        abort(422)


def getPage(self):
    page = 1
    if request.args.get('page') is not None:
        try:
            page = int(request.args.get('page'))
        except:
            page = 1

        if page <= 0:
            page = 1
    return page
