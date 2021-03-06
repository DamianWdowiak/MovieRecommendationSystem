from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

ONE_DAY = 24 * 60 * 60

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datasets/users_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'

db = SQLAlchemy(app)

import views, models, resources

db.create_all()
db.session.commit()


app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'

jwt = JWTManager(app)

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(ONE_DAY)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.CollaborativeFilterRecommender, '/recommender/collaborative')
api.add_resource(resources.ContentFilterRecommender, '/recommender/content')
api.add_resource(resources.Film, '/films', '/films/<filmId>')
api.add_resource(resources.User, '/user', '/user/<filmId>')
api.add_resource(resources.PopularityFilterRecommender, '/recommender/popularity')

if __name__ == '__main__':
    app.run()
