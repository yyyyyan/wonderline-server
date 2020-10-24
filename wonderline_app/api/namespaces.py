from flask_restplus import Namespace

common_namespace = Namespace('common', description='Common API Fields')
users_namespace = Namespace('users', description='User API')
trips_namespace = Namespace('trips', description='Trip API')
search_namespace = Namespace('search', description='Search API')
