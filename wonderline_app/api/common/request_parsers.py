"""
Definition of common API request parsers.
"""
from flask_restplus import reqparse

common_parser = reqparse.RequestParser()
common_parser.add_argument(
    "userToken",
    location='args',
    type=str,
    help="Logged-in user token for request authentication."
)
