"""
Definition of common API request parsers.
"""
from flask_restplus import reqparse

common_parser = reqparse.RequestParser()
common_parser.add_argument(
    "userToken",
    location='args',
    type=str,
    help="Logged-in user token for request authentication.\n "
         "To simplify the test it only contains unencrypted logged-in user id in the current version."
)