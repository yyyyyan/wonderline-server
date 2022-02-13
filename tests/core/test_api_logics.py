import os
import unittest

from wonderline_app import APP
from wonderline_app.db.cassandra.models import create_and_return_new_trip, delete_all_about_given_trip, \
    delete_reply_given_reply_id
from wonderline_app.db.postgres.init import db_session
from wonderline_app.db.postgres.models import User
from wonderline_app.utils import encode_image

HOST = "http://localhost:80"


class ApiTEST(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        pass

    def _get_req_from_jon(self, endpoint, set_valid_token=True, **kwargs):
        """HTTP GET request with Jon Snow user token"""
        with APP.test_client() as c:
            with c.session_transaction() as sess:
                sess['_user_id'] = 'user_001'
                sess['_fresh'] = True
            sign_in_req = c.post(
                "http://localhost:80/users/signIn",
                json=dict(email='jon@gmail.com', password='password')
            )
            jon_user_token = sign_in_req.json['payload']['userToken']
            default_headers = {"Content-Type": "application/json"}
            default_headers.update(kwargs.pop('headers', {}))
            if set_valid_token:
                kwargs['params']['userToken'] = jon_user_token
            url = HOST + endpoint
            return c.get(url, headers=default_headers, query_string=kwargs['params'])

    def _post_req_from_jon(self, endpoint, method='post', set_valid_token=True, **kwargs):
        """HTTP GET request with Jon Snow user token"""
        with APP.test_client() as c:
            with c.session_transaction() as sess:
                sess['_user_id'] = 'user_001'
                sess['_fresh'] = True
            sign_in_req = c.post(
                "http://localhost:80/users/signIn",
                json=dict(email='jon@gmail.com', password='password')
            )
            jon_user_token = sign_in_req.json['payload']['userToken']
            default_headers = {"Content-Type": "application/json"}
            default_headers.update(kwargs.pop('headers', {}))
            if set_valid_token:
                kwargs['params']['userToken'] = jon_user_token
            url = HOST + endpoint
            if method == 'post':
                req_method = c.post
            elif method == 'patch':
                req_method = c.patch
            elif method == 'delete':
                req_method = c.delete
            return req_method(url, headers=default_headers, query_string=kwargs['params'],
                              json=kwargs['payload'])

    def _assert_equal_json(self, j1: dict, j2: dict):
        for key, value in j1.items():
            if key not in j2:
                return False

    def _assert_response(self, expected_code, expected_res, response, excludes=None):
        def _pop_exclude_key(exclude_keys, item):
            if isinstance(item, list):
                for ele in item:
                    _pop_exclude_key(exclude_keys, ele)
            elif isinstance(item, dict):
                items_keys = list(item.keys())
                for k in items_keys:
                    if k in exclude_keys:
                        assert item[k] is not None
                        item.pop(k)
                    elif isinstance(item[k], dict):
                        _pop_exclude_key(exclude_keys, item[k])
                    elif isinstance(item[k], list):
                        for ele in item[k]:
                            _pop_exclude_key(exclude_keys, ele)
            else:
                return

        response_json = response.json
        if excludes is None:
            excludes = ['timestamp']
        excludes = set(excludes)
        _pop_exclude_key(exclude_keys=excludes, item=response_json)
        _pop_exclude_key(exclude_keys=excludes, item=expected_res)

        try:
            self.assertEqual(expected_code, response.status_code)
            self.assertEqual(expected_res, response_json)
        except AssertionError as e:
            print(f"Assert Error, got response: {response_json}")
            print(f"expected response without timestamp: {expected_res}")
            raise e

    def test_get_user_with_success(self):
        response = self._get_req_from_jon(
            endpoint='/users/user_001',
            params={
                "userToken": 'test',
                "followersSortType": "createTime",
                "followerNb": 2
            })
        expected_res = {
            "payload": {
                "reducedUser": {
                    "id": "user_001",
                    "accessLevel": "everyone",
                    "nickName": "Jon Snow",
                    "uniqueName": "jon_snow",
                    "avatarSrc": "avatar.png"
                },
                "createTime": 1596134528,
                "signature": "The king of the North, Danny is my QUEEN!",
                "profileLqSrc": "bkg.png",
                "profileSrc": "bkg.png",
                "followerNb": 6,
                "followers": [
                    {
                        "id": "user_007",
                        "accessLevel": "everyone",
                        "nickName": "Night King",
                        "uniqueName": "night_king",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_006",
                        "accessLevel": "everyone",
                        "nickName": "Cersei Lannister",
                        "uniqueName": "cersei_lannister",
                        "avatarSrc": "avatar.png"
                    }
                ],
                "isFollowedByLoginUser": False
            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1601155452818
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_user_with_default_parameters_expect_success(self):
        response = self._get_req_from_jon(
            endpoint='/users/user_001',
            params={
                "userToken": 'test',
            })
        expected_res = {
            "payload": {
                "reducedUser": {
                    "id": "user_001",
                    "accessLevel": "everyone",
                    "nickName": "Jon Snow",
                    "uniqueName": "jon_snow",
                    "avatarSrc": "avatar.png"
                },
                "createTime": 1596134528,
                "signature": "The king of the North, Danny is my QUEEN!",
                "profileLqSrc": "bkg.png",
                "profileSrc": "bkg.png",
                "followerNb": 6,
                "followers": [
                    {
                        "id": "user_007",
                        "accessLevel": "everyone",
                        "nickName": "Night King",
                        "uniqueName": "night_king",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_006",
                        "accessLevel": "everyone",
                        "nickName": "Cersei Lannister",
                        "uniqueName": "cersei_lannister",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_005",
                        "accessLevel": "everyone",
                        "nickName": "Samwell Tarly",
                        "uniqueName": "samwell_tarly",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_004",
                        "accessLevel": "everyone",
                        "nickName": "Blue Dragon",
                        "uniqueName": "blue_dragon",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_003",
                        "accessLevel": "everyone",
                        "nickName": "Red Dragon",
                        "uniqueName": "red_dragon",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_002",
                        "accessLevel": "everyone",
                        "nickName": "Daenerys Targaryen",
                        "uniqueName": "daenerys_targaryen",
                        "avatarSrc": "avatar.png"
                    }
                ],
                "isFollowedByLoginUser": False
            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598562624846
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_user_with_404_error(self):  # when a resource is not found
        response = self._get_req_from_jon(
            endpoint='/users/user_009',
            params={
                "userToken": 'test',
                "followersSortType": "createTime",
                "followerNb": 2
            })
        expected_res = {
            "payload": {
                "reducedUser": None,
                "createTime": None,
                "signature": None,
                "profileLqSrc": None,
                "profileSrc": None,
                "followerNb": None,
                "followers": None,
                "isFollowedByLoginUser": None

            },
            "feedbacks": [],
            "errors": [
                {
                    "code": 404,
                    "message": "User user_009 is not found"
                }
            ],
            "timestamp": 1598221098773
        }
        self._assert_response(
            expected_code=404,
            expected_res=expected_res,
            response=response
        )

    def test_get_user_with_401_error(self):  # when user is unauthorized
        response = self._get_req_from_jon(
            endpoint='/users/user_009',
            set_valid_token=False,
            params={
                "userToken": None,
                "followersSortType": "createTime",
                "followerNb": 2
            })
        expected_res = {
            "payload": {
                "reducedUser": None,
                "createTime": None,
                "signature": None,
                "profileLqSrc": None,
                "profileSrc": None,
                "followerNb": None,
                "followers": None,
                "isFollowedByLoginUser": None
            },
            "feedbacks": [],
            "errors": [
                {
                    "code": 401,
                    "message": "Unauthorized: user token is None"
                }
            ],
            "timestamp": 1598221228649
        }
        self._assert_response(
            expected_code=401,
            expected_res=expected_res,
            response=response
        )

    def test_get_user_with_isFollowedByLoginUser_True(self):
        response = self._get_req_from_jon(
            endpoint='/users/user_002',
            set_valid_token=True,
            params={
                "userToken": 'test',
                "followersSortType": "createTime",
                "followerNb": 0
            })
        expected_res = {
            "payload": {
                "reducedUser": {
                    "id": "user_002",
                    "accessLevel": "everyone",
                    "nickName": "Daenerys Targaryen",
                    "uniqueName": "daenerys_targaryen",
                    "avatarSrc": "avatar.png"
                },
                "createTime": 1596134628,
                "signature": "How many times must I say no before you understand?",
                "profileLqSrc": "bkg.png",
                "profileSrc": "bkg.png",
                "followerNb": 3,
                "followers": [],
                "isFollowedByLoginUser": True
            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1601215707809
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_followers_expect_success(self):
        response = self._get_req_from_jon(
            endpoint='/users/user_001/followers',
            params={
                "userToken": 'test',
                "sortType": "createTime",
                "nb": 2,
                "startIndex": 1
            })

        expected_res = {'payload': [
            {'id': 'user_006', 'accessLevel': 'everyone', 'nickName': 'Cersei Lannister',
             'uniqueName': 'cersei_lannister', 'avatarSrc': 'avatar.png'},
            {'id': 'user_005', 'accessLevel': 'everyone', 'nickName': 'Samwell Tarly', "uniqueName": "samwell_tarly",
             'avatarSrc': 'avatar.png'}],
            'feedbacks': [], 'errors': [], 'timestamp': 1598128569991}
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_user_trips_expect_success(self):
        response = self._get_req_from_jon(
            endpoint='/users/user_001/trips',
            params={
                "userToken": 'test',
                "sortType": "createTime",
                "nb": 1,
                "startIndex": 0,
                "accessLevel": "everyone"
            })
        expected_res = {'payload':
            [{
                'id': 'trip_01',
                'ownerId': 'user_001',
                'accessLevel': 'everyone',
                'name': 'The Winds of Winter',
                'description': 'Winter is the time when things die, and cold and ice and darkness fill the world, so this is not going to be the happy feel-good that people may be hoping for. Things get worse before they get better, so things are getting worse for a lot of people.',
                'status': 'confirmed',
                'users': [
                    {
                        'id': 'user_004',
                        'accessLevel': 'everyone',
                        'nickName': 'Blue Dragon',
                        "uniqueName": "blue_dragon",
                        'avatarSrc': 'avatar.png'
                    },
                    {
                        'id': 'user_002',
                        'accessLevel': 'everyone',
                        'nickName': 'Daenerys Targaryen',
                        'uniqueName': 'daenerys_targaryen',
                        'avatarSrc': 'avatar.png'
                    },
                    {
                        'id': 'user_001',
                        'accessLevel': 'everyone',
                        'nickName': 'Jon Snow',
                        'uniqueName': 'jon_snow',
                        'avatarSrc': 'avatar.png'
                    },
                    {
                        'id': 'user_007',
                        'accessLevel': 'everyone',
                        'nickName': 'Night King',
                        'uniqueName': 'night_king',
                        'avatarSrc': 'avatar.png'
                    },
                    {
                        'id': 'user_003',
                        'accessLevel': 'everyone',
                        'nickName': 'Red Dragon',
                        'uniqueName': 'red_dragon',
                        'avatarSrc': 'avatar.png'
                    },
                    {
                        'id': 'user_005',
                        'accessLevel': 'everyone',
                        'nickName': 'Samwell Tarly',
                        "uniqueName": "samwell_tarly",
                        'avatarSrc': 'avatar.png'
                    }],
                'createTime': 1596142528,
                'beginTime': 1596142628,
                'endTime': 1596143628,
                'photoNb': 9,
                'coverPhoto': {
                    'id': 'photo_01_2', 'accessLevel': 'everyone', 'tripId': 'trip_01',
                    'status': 'confirmed',
                    'user': {
                        'id': 'user_001',
                        'accessLevel': 'everyone',
                        'nickName': 'Jon Snow',
                        'uniqueName': 'jon_snow',
                        'avatarSrc': 'avatar.png'
                    },
                    'location': 'Westeros', 'country': 'Westeros',
                    'createTime': 1596142638, 'uploadTime': 1596142638,
                    'width': 374, 'height': 280, 'lqSrc': 'photo_2.jpg',
                    'src': 'photo_2.jpg', 'likedNb': 0}}], 'feedbacks': [],
            'errors': [], 'timestamp': 1598132005855}
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    # TODO: implement the test for get highlights
    # def test_get_highlights_expect_success(self):
    #     response = self._get_req(
    #         endpoint='/users/user_001/highlights',
    #         params={
    #             "userToken": 'test',
    #             "sortType": "createTime",
    #             "nb": 2,
    #             "startIndex": 1,
    #             "accessLevel": "everyone"
    #         })
    #     expected_res = {'payload': [
    #         {'id': 'user_006', 'accessLevel': 'everyone', 'name': 'Cersei Lannister', 'avatarSrc': 'avatar.png'},
    #         {'id': 'user_005', 'accessLevel': 'everyone', 'name': 'Samwell Tarly',  "uniqueName": "samwell_tarly", 'avatarSrc': 'avatar.png'}],
    #         'feedbacks': [], 'errors': [], 'timestamp': 1598128569991}
    #     self._assert_response(
    #         expected_code=200,
    #         expected_res_json_without_timestamp=expected_res,
    #         response=response
    #     )

    def test_get_albums_expect_success(self):
        response = self._get_req_from_jon(
            endpoint='/users/user_001/albums',
            params={
                "userToken": 'test',
                "sortType": "createTime",
                "nb": 2,
                "startIndex": 1,
                "accessLevel": "everyone"
            })
        expected_res = {
            "payload": [
                {
                    "id": "album_001_4",
                    "accessLevel": "everyone",
                    "coverPhotos": [
                        {
                            "photo": {
                                "id": "photo_01_7",
                                "accessLevel": "everyone",
                                "tripId": "trip_01",
                                "status": "confirmed",
                                "user": {
                                    "id": "user_002",
                                    "accessLevel": "everyone",
                                    "nickName": "Daenerys Targaryen",
                                    "uniqueName": "daenerys_targaryen",
                                    "avatarSrc": "avatar.png"
                                },
                                "location": "Westeros",
                                "country": "Westeros",
                                "createTime": 1596142688,
                                "uploadTime": 1596142688,
                                "width": 1920,
                                "height": 2716,
                                "lqSrc": "photo_7.jpg",
                                "src": "photo_7.jpg",
                                "likedNb": 0
                            },
                            "ratioType": "vertical"
                        }
                    ],
                    "createTime": 1596142628
                },
                {
                    "id": "album_001_3",
                    "accessLevel": "everyone",
                    "coverPhotos": [
                        {
                            "photo": {
                                "id": "photo_01_4",
                                "accessLevel": "everyone",
                                "tripId": "trip_01",
                                "status": "confirmed",
                                "user": {
                                    "id": "user_001",
                                    "accessLevel": "everyone",
                                    "nickName": "Jon Snow",
                                    "uniqueName": "jon_snow",
                                    "avatarSrc": "avatar.png"
                                },
                                "location": "Westeros",
                                "country": "Westeros",
                                "createTime": 1596142658,
                                "uploadTime": 1596142658,
                                "width": 640,
                                "height": 1136,
                                "lqSrc": "photo_4.jpg",
                                "src": "photo_4.jpg",
                                "likedNb": 0
                            },
                            "ratioType": "vertical"
                        },
                        {
                            "photo": {
                                "id": "photo_01_6",
                                "accessLevel": "everyone",
                                "tripId": "trip_01",
                                "status": "confirmed",
                                "user": {
                                    "id": "user_001",
                                    "accessLevel": "everyone",
                                    "nickName": "Jon Snow",
                                    "uniqueName": "jon_snow",
                                    "avatarSrc": "avatar.png"
                                },
                                "location": "Westeros",
                                "country": "Westeros",
                                "createTime": 1596142678,
                                "uploadTime": 1596142678,
                                "width": 2560,
                                "height": 1565,
                                "lqSrc": "photo_6.jpg",
                                "src": "photo_6.jpg",
                                "likedNb": 0
                            },
                            "ratioType": "vertical"
                        }
                    ],
                    "createTime": 1596142738
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598136936429
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_mentions_expect_success(self):
        response = self._get_req_from_jon(
            endpoint='/users/user_001/mentions',
            params={
                "userToken": 'test',
                "sortType": "createTime",
                "nb": 2,
                "startIndex": 1,
                "accessLevel": "everyone"
            })
        expected_res = {
            "payload": [
                {
                    "id": "mention_001_2",
                    "photo": {
                        "id": "photo_01_2",
                        "accessLevel": "everyone",
                        "tripId": "trip_01",
                        "status": "confirmed",
                        "user": {
                            "id": "user_001",
                            "accessLevel": "everyone",
                            "nickName": "Jon Snow",
                            "uniqueName": "jon_snow",
                            "avatarSrc": "avatar.png"
                        },
                        "location": "Westeros",
                        "country": "Westeros",
                        "createTime": 1596142638,
                        "uploadTime": 1596142638,
                        "width": 374,
                        "height": 280,
                        "lqSrc": "photo_2.jpg",
                        "src": "photo_2.jpg",
                        "likedNb": 0
                    },
                    "accessLevel": "everyone"
                },
                {
                    "id": "mention_001_4",
                    "photo": {
                        "id": "photo_01_4",
                        "accessLevel": "everyone",
                        "tripId": "trip_01",
                        "status": "confirmed",
                        "user": {
                            "id": "user_001",
                            "accessLevel": "everyone",
                            "nickName": "Jon Snow",
                            "uniqueName": "jon_snow",
                            "avatarSrc": "avatar.png"
                        },
                        "location": "Westeros",
                        "country": "Westeros",
                        "createTime": 1596142658,
                        "uploadTime": 1596142658,
                        "width": 640,
                        "height": 1136,
                        "lqSrc": "photo_4.jpg",
                        "src": "photo_4.jpg",
                        "likedNb": 0
                    },
                    "accessLevel": "everyone"
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598137014805
        }

        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_trip_expect_success(self):
        response = self._get_req_from_jon(
            endpoint='/trips/trip_01',
            params={
                "userToken": 'test',
                "usersSortType": "createTime",
            })
        expected_res = {
            "payload": {
                "reducedTrip": {
                    "id": "trip_01",
                    "ownerId": "user_001",
                    "accessLevel": "everyone",
                    "name": "The Winds of Winter",
                    "description": "Winter is the time when things die, and cold and ice and darkness fill the world, so this is not going to be the happy feel-good that people may be hoping for. Things get worse before they get better, so things are getting worse for a lot of people.",
                    'status': 'confirmed',
                    "users": [
                        {
                            "id": "user_001",
                            "accessLevel": "everyone",
                            "nickName": "Jon Snow",
                            "uniqueName": "jon_snow",
                            "avatarSrc": "avatar.png"
                        },
                        {
                            "id": "user_002",
                            "accessLevel": "everyone",
                            "nickName": "Daenerys Targaryen",
                            "uniqueName": "daenerys_targaryen",
                            "avatarSrc": "avatar.png"
                        },
                        {
                            "id": "user_003",
                            "accessLevel": "everyone",
                            "nickName": "Red Dragon",
                            "uniqueName": "red_dragon",
                            "avatarSrc": "avatar.png"
                        },
                        {
                            "id": "user_004",
                            "accessLevel": "everyone",
                            "nickName": "Blue Dragon",
                            "uniqueName": "blue_dragon",
                            "avatarSrc": "avatar.png"
                        },
                        {
                            "id": "user_005",
                            "accessLevel": "everyone",
                            "nickName": "Samwell Tarly",
                            "uniqueName": "samwell_tarly",
                            "avatarSrc": "avatar.png"
                        },
                        {
                            "id": "user_007",
                            "accessLevel": "everyone",
                            "nickName": "Night King",
                            "uniqueName": "night_king",
                            "avatarSrc": "avatar.png"
                        }
                    ],
                    "createTime": 1596142528,
                    "beginTime": 1596142628,
                    "endTime": 1596143628,
                    "photoNb": 9,
                    "coverPhoto": {
                        "id": "photo_01_2",
                        "accessLevel": "everyone",
                        "tripId": "trip_01",
                        "status": "confirmed",
                        "user": {
                            "id": "user_001",
                            "accessLevel": "everyone",
                            "nickName": "Jon Snow",
                            "uniqueName": "jon_snow",
                            "avatarSrc": "avatar.png"
                        },
                        "location": "Westeros",
                        "country": "Westeros",
                        "createTime": 1596142638,
                        "uploadTime": 1596142638,
                        "width": 374,
                        "height": 280,
                        "lqSrc": "photo_2.jpg",
                        "src": "photo_2.jpg",
                        "likedNb": 0
                    }
                },
                "likedNb": 23892,
                "sharedNb": 1656,
                "savedNb": 4222,

            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598134263573
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_trip_users(self):
        response = self._get_req_from_jon(
            endpoint='/trips/trip_01/users',
            params={
                "userToken": 'test',
                "sortType": "createTime",
                "nb": 4,
                "startIndex": 2
            })
        expected_res = {
            "payload": [
                {
                    "id": "user_003",
                    "accessLevel": "everyone",
                    "nickName": "Red Dragon",
                    "uniqueName": "red_dragon",
                    "avatarSrc": "avatar.png"
                },
                {
                    "id": "user_004",
                    "accessLevel": "everyone",
                    "nickName": "Blue Dragon",
                    "uniqueName": "blue_dragon",
                    "avatarSrc": "avatar.png"
                },
                {
                    "id": "user_005",
                    "accessLevel": "everyone",
                    "nickName": "Samwell Tarly",
                    "uniqueName": "samwell_tarly",
                    "avatarSrc": "avatar.png"
                },
                {
                    "id": "user_007",
                    "accessLevel": "everyone",
                    "nickName": "Night King",
                    "uniqueName": "night_king",
                    "avatarSrc": "avatar.png"
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598177267994
        }

        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_trip_photos(self):
        response = self._get_req_from_jon(
            endpoint='/trips/trip_01/photos',
            params={
                "userToken": 'test',
                "sortType": "createTime",
                "nb": 2,
                "startIndex": 2,
                "accessLevel": "everyone"
            })
        expected_res = {
            "payload": [
                {
                    "id": "photo_01_3",
                    "accessLevel": "everyone",
                    "tripId": "trip_01",
                    "status": "confirmed",
                    "user": {
                        "id": "user_002",
                        "accessLevel": "everyone",
                        "nickName": "Daenerys Targaryen",
                        "uniqueName": "daenerys_targaryen",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "Westeros",
                    "country": "Westeros",
                    "createTime": 1596142648,
                    "uploadTime": 1596142648,
                    "width": 640,
                    "height": 1136,
                    "lqSrc": "photo_3.jpg",
                    "src": "photo_3.jpg",
                    "likedNb": 0
                },
                {
                    "id": "photo_01_4",
                    "accessLevel": "everyone",
                    "tripId": "trip_01",
                    "status": "confirmed",
                    "user": {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "Westeros",
                    "country": "Westeros",
                    "createTime": 1596142658,
                    "uploadTime": 1596142658,
                    "width": 1920,
                    "height": 1080,
                    "lqSrc": "photo_4.jpg",
                    "src": "photo_4.jpg",
                    "likedNb": 0
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598174563320
        }

        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_trip_photo_expect_success(self):
        response = self._get_req_from_jon(
            endpoint='/trips/trip_01/photos/photo_01_1',
            params={
                "userToken": 'test',
                "likedUsersSortType": "createTime",
                "likedUserNb": 2,
                "commentsSortType": "createTime",
                "commentNb": 2,
            })
        expected_res = {
            "payload": {
                "reducedPhoto": {
                    "id": "photo_01_1",
                    "accessLevel": "everyone",
                    "tripId": "trip_01",
                    "status": "confirmed",
                    "user": {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "Westeros",
                    "country": "Westeros",
                    "createTime": 1596142628,
                    "uploadTime": 1596142628,
                    "width": 768,
                    "height": 1365,
                    "lqSrc": "photo_1.jpg",
                    "src": "photo_1.jpg",
                    "likedNb": 7
                },
                "hqSrc": "",
                "likedUsers": [
                    {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_002",
                        "accessLevel": "everyone",
                        "nickName": "Daenerys Targaryen",
                        "uniqueName": "daenerys_targaryen",
                        "avatarSrc": "avatar.png"
                    }
                ],
                "mentionedUsers": [
                    {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    }
                ],
                "commentNb": 0,
                "comments": [
                    {
                        "replyNb": 3,
                        "replies": [
                            {
                                "id": "reply_03",
                                "user": {
                                    "id": "user_005",
                                    "accessLevel": "everyone",
                                    "nickName": "Samwell Tarly",
                                    "uniqueName": "samwell_tarly",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596146639,
                                "content": "yes",
                                "likedNb": 1,
                                "mentions": [],
                                "hashtags": [],
                                "hasLiked": False
                            },
                            {
                                "id": "reply_02",
                                "user": {
                                    "id": "user_004",
                                    "accessLevel": "everyone",
                                    "nickName": "Blue Dragon",
                                    "uniqueName": "blue_dragon",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142639,
                                "content": "good",
                                "likedNb": 3,
                                "mentions": [],
                                "hashtags": [],
                                "hasLiked": False
                            }
                        ],
                        "id": "comment_02",
                        "user": {
                            "id": "user_002",
                            "accessLevel": "everyone",
                            "nickName": "Daenerys Targaryen",
                            "uniqueName": "daenerys_targaryen",
                            "avatarSrc": "avatar.png"
                        },
                        "createTime": 1596142639,
                        "content": "hello #wonderline @jon_snow awesome",
                        "likedNb": 7,
                        "mentions": [
                            {
                                "uniqueName": "jon_snow",
                                "userId": "user_001",
                                "startIndex": 18,
                                "endIndex": 27
                            }
                        ],
                        "hashtags": [
                            {
                                "name": "wonderline",
                                "startIndex": 6,
                                "endIndex": 17
                            }
                        ],
                        "hasLiked": False
                    },
                    {
                        "replyNb": 2,
                        "replies": [
                            {
                                "id": "reply_02",
                                "user": {
                                    "id": "user_006",
                                    "accessLevel": "everyone",
                                    "nickName": "Cersei Lannister",
                                    "uniqueName": "cersei_lannister",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142639,
                                "content": "good",
                                "likedNb": 4,
                                "mentions": [],
                                "hashtags": [],
                                "hasLiked": False
                            },
                            {
                                "id": "reply_01",
                                "user": {
                                    "id": "user_002",
                                    "accessLevel": "everyone",
                                    "nickName": "Daenerys Targaryen",
                                    "uniqueName": "daenerys_targaryen",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142629,
                                "content": "what?",
                                "likedNb": 3,
                                "mentions": [],
                                "hashtags": [],
                                "hasLiked": False
                            }
                        ],
                        "id": "comment_01",
                        "user": {
                            "id": "user_001",
                            "accessLevel": "everyone",
                            "nickName": "Jon Snow",
                            "uniqueName": "jon_snow",
                            "avatarSrc": "avatar.png"
                        },
                        "createTime": 1596142629,
                        "content": "hi",
                        "likedNb": 6,
                        "mentions": [],
                        "hashtags": [],
                        "hasLiked": False
                    }
                ],
            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598177205794
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_trip_photo_comments_expect_success(self):
        response = self._get_req_from_jon(
            endpoint='/trips/trip_01/photos/photo_01_1/comments',
            params={
                "userToken": 'test',
                "repliesSortType": "createTime",
                "replyNb": 2,
            })
        expected_res = {
            "payload": [
                {
                    "replyNb": 3,
                    "replies": [
                        {
                            "id": "reply_03",
                            "user": {
                                "id": "user_005",
                                "accessLevel": "everyone",
                                "nickName": "Samwell Tarly",
                                "uniqueName": "samwell_tarly",
                                "avatarSrc": "avatar.png"
                            },
                            "createTime": 1596146639,
                            "content": "yes",
                            "likedNb": 1,
                            "mentions": [],
                            "hashtags": [],
                            "hasLiked": False
                        },
                        {
                            "id": "reply_02",
                            "user": {
                                "id": "user_004",
                                "accessLevel": "everyone",
                                "nickName": "Blue Dragon",
                                "uniqueName": "blue_dragon",
                                "avatarSrc": "avatar.png"
                            },
                            "createTime": 1596142639,
                            "content": "good",
                            "likedNb": 3,
                            "mentions": [],
                            "hashtags": [],
                            "hasLiked": False
                        }
                    ],
                    "id": "comment_02",
                    "user": {
                        "id": "user_002",
                        "accessLevel": "everyone",
                        "nickName": "Daenerys Targaryen",
                        "uniqueName": "daenerys_targaryen",
                        "avatarSrc": "avatar.png"
                    },
                    "createTime": 1596142639,
                    "content": "hello #wonderline @jon_snow awesome",
                    "likedNb": 7,
                    "mentions": [
                        {
                            "uniqueName": "jon_snow",
                            "userId": "user_001",
                            "startIndex": 18,
                            "endIndex": 27
                        }
                    ],
                    "hashtags": [
                        {
                            "name": "wonderline",
                            "startIndex": 6,
                            "endIndex": 17
                        }
                    ],
                    "hasLiked": True
                },
                {
                    "replyNb": 2,
                    "replies": [
                        {
                            "id": "reply_02",
                            "user": {
                                "id": "user_006",
                                "accessLevel": "everyone",
                                "nickName": "Cersei Lannister",
                                "uniqueName": "cersei_lannister",
                                "avatarSrc": "avatar.png"
                            },
                            "createTime": 1596142639,
                            "content": "good",
                            "likedNb": 4,
                            "mentions": [],
                            "hashtags": [],
                            "hasLiked": False
                        },
                        {
                            "id": "reply_01",
                            "user": {
                                "id": "user_002",
                                "accessLevel": "everyone",
                                "nickName": "Daenerys Targaryen",
                                "uniqueName": "daenerys_targaryen",
                                "avatarSrc": "avatar.png"
                            },
                            "createTime": 1596142629,
                            "content": "what?",
                            "likedNb": 3,
                            "mentions": [],
                            "hashtags": [],
                            "hasLiked": False
                        }
                    ],
                    "id": "comment_01",
                    "user": {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    "createTime": 1596142629,
                    "content": "hi",
                    "likedNb": 6,
                    "mentions": [],
                    "hashtags": [],
                    "hasLiked": False
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1644016844
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_get_comment_replies_expect_success(self):
        response = self._get_req_from_jon(
            endpoint='/trips/trip_01/photos/photo_01_1/comments/comment_02/replies',
            params={
                "userToken": 'test',
                "sortType": "createTime",
                "startIndex": 1,
                "nb": 2
            })
        expected_res = {
            "payload": [
                {
                    "id": "reply_02",
                    "user": {
                        "id": "user_004",
                        "accessLevel": "everyone",
                        "nickName": "Blue Dragon",
                        "uniqueName": "blue_dragon",
                        "avatarSrc": "avatar.png"
                    },
                    "createTime": 1596142639,
                    "content": "good",
                    "likedNb": 3,
                    "mentions": [],
                    "hashtags": [],
                    "hasLiked": False
                },
                {
                    "id": "reply_01",
                    "user": {
                        "id": "user_003",
                        "accessLevel": "everyone",
                        "nickName": "Red Dragon",
                        "uniqueName": "red_dragon",
                        "avatarSrc": "avatar.png"
                    },
                    "createTime": 1596142629,
                    "content": "what?",
                    "likedNb": 3,
                    "mentions": [],
                    "hashtags": [],
                    "hasLiked": False
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1644016765
        }

        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response,
            excludes=['timestamp'],
        )

    def test_sign_up(self):
        try:
            res = APP.test_client().post(
                "http://localhost:80/users/signUp",
                json=dict(email="test@gmail.com", password="password", uniqueName="test"))
            payload = res.json['payload']
            assert 'userToken' in payload and isinstance(payload['userToken'], str)
            assert payload['user']['reducedUser']['nickName'] is None
            assert payload['user']['reducedUser']['uniqueName'] == 'test'
            assert payload['user']['reducedUser']['accessLevel'] == 'everyone'
            assert payload['user']['reducedUser'][
                       'avatarSrc'] == 'http://localhost/photos/default_avatar.png'
            assert payload['user']['isFollowedByLoginUser'] is False
            assert res.status_code == 201
        except Exception as e:
            raise e
        finally:
            test_user = User.query.filter_by(email="test@gmail.com").first()
            if test_user is not None:
                db_session.delete(test_user)
                db_session.commit()

    def test_sign_in(self):
        res = APP.test_client().post(
            "http://localhost:80/users/signIn",
            json=dict(email="jon@gmail.com", password="password"))
        payload = res.json['payload']
        assert 'userToken' in payload and isinstance(payload['userToken'], str)
        assert payload['user']['reducedUser']['nickName'] == 'Jon Snow'
        assert payload['user']['reducedUser']['uniqueName'] == 'jon_snow'
        assert payload['user']['isFollowedByLoginUser'] is False
        assert res.status_code == 200

    def test_sign_out(self):
        with APP.test_client() as c:
            with c.session_transaction() as sess:
                sess['_user_id'] = 'user_001'
                sess['_fresh'] = True
            sign_in_req = c.post(
                "http://localhost:80/users/signIn",
                json=dict(email='jon@gmail.com', password='password')
            )
            jon_user_token = sign_in_req.json['payload']['userToken']
            default_headers = {"Content-Type": "application/json"}
            res = c.post("http://localhost:80/users/signOut", headers=default_headers,
                         query_string=dict(userToken=jon_user_token))
            self._assert_response(
                response=res,
                expected_code=200,
                expected_res={'errors': [], 'feedbacks': [], 'timestamp': 1601155452818}
            )

    def test_post_a_new_trip(self):
        response = self._post_req_from_jon(
            endpoint='/trips/',
            params={
                "userToken": 'test',
            },
            payload={
                "ownerId": "user_001",
                "tripName": "New Trip Name",
                "userIds": [
                    "user_001",
                    "user_002"
                ],
                "usersSortType": "createTime"
            }
        )
        expected_res = {
            "payload": {
                "reducedTrip": {
                    "id": "5ee749f8-1250-11eb-8417-0242ac160005",
                    "ownerId": "user_001",
                    "accessLevel": "everyone",
                    "status": "editing",
                    "name": "New Trip Name",
                    "description": "",
                    "users": [
                        {
                            "id": "user_001",
                            "accessLevel": "everyone",
                            "nickName": "Jon Snow",
                            "uniqueName": "jon_snow",
                            "avatarSrc": "avatar.png"
                        },
                        {
                            "id": "user_002",
                            "accessLevel": "everyone",
                            "nickName": "Daenerys Targaryen",
                            "uniqueName": "daenerys_targaryen",
                            "avatarSrc": "avatar.png"
                        }
                    ],
                    "createTime": 1603142196,
                    "beginTime": None,
                    "endTime": None,
                    "photoNb": 0,
                    "coverPhoto": None
                },
                "likedNb": 0,
                "sharedNb": 0,
                "savedNb": 0
            },
            "feedbacks": [
                {
                    "code": 201,
                    "message": "Trip 'New Trip Name' successfully created"
                }
            ],
            "errors": [],
            "timestamp": 1601155452818
        }
        # delete the test trip from cassandra
        delete_all_about_given_trip(trip_id=response.json['payload']['reducedTrip']['id'])
        self._assert_response(
            expected_code=201,
            expected_res=expected_res,
            response=response,
            excludes=[
                'timestamp',
                'id',
                'createTime'
            ]
        )

    def test_update_trip(self):
        new_trip = create_and_return_new_trip(owner_id='user_001', trip_name='test trip',
                                              user_ids=['user_001', 'user_002'])
        response = self._post_req_from_jon(
            endpoint=f'/trips/{new_trip.trip_id}',
            method='patch',
            params={
                "userToken": 'test',
            },
            payload={
                "name": "new trip name",
                "description": "new test trip",
                "userIds": [
                    "user_001",
                    "user_003"
                ],
            }
        )
        expected_res = {
            "payload": {
                "reducedTrip": {
                    "id": "fd8557e0-1641-11eb-ab40-0242ac160004",
                    "ownerId": "user_001",
                    "accessLevel": "everyone",
                    "status": "editing",
                    "name": "new trip name",
                    "description": "new test trip",
                    "users": [
                        {
                            "id": "user_001",
                            "accessLevel": "everyone",
                            "nickName": "Jon Snow",
                            "uniqueName": "jon_snow",
                            "avatarSrc": "avatar.png"
                        },
                        {
                            "id": "user_003",
                            "accessLevel": "everyone",
                            "nickName": "Red Dragon",
                            "uniqueName": "red_dragon",
                            "avatarSrc": "avatar.png"
                        }
                    ],
                    "createTime": 1603575824,
                    "beginTime": None,
                    "endTime": None,
                    "photoNb": 0,
                    "coverPhoto": None
                },
                "likedNb": 0,
                "sharedNb": 0,
                "savedNb": 0
            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1603575872
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response,
            excludes=[
                'timestamp',
                'id',
                'createTime'
            ]
        )
        # delete the test trip from cassandra
        delete_all_about_given_trip(trip_id=new_trip.trip_id)

    def test_search_users(self):
        response = self._get_req_from_jon(
            endpoint='/search/users',
            params={
                "userToken": 'test',
                "query": 'jon',
                "sortType": "bestMatch",
                "startIndex": 0,
                "nb": 1
            })
        expected_res = {
            "payload": [
                {
                    "id": "user_001",
                    "accessLevel": "everyone",
                    "nickName": "Jon Snow",
                    "uniqueName": "jon_snow",
                    "avatarSrc": "avatar.png"
                }
            ],

            "feedbacks": [],
            "errors": [],
            "timestamp": 1598176302710
        }

        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response
        )

    def test_post_trip_photos_without_location_field(self):
        new_trip = create_and_return_new_trip(owner_id='user_001', trip_name='test', user_ids=['user_001'])
        trip_id = new_trip.trip_id
        response = self._post_req_from_jon(
            endpoint=f'/trips/{trip_id}/photos',
            params={
                "userToken": 'test',
            },
            payload={
                "originalPhotos": [
                    {
                        "data": encode_image(os.environ['TEST_PHOTO_PATH']),
                        "latitude": "64.752895",
                        "latitudeRef": "N",
                        "longitude": "14.53861166666667",
                        "longitudeRef": "W",
                        "time": 1605306885,
                        "width": 400,
                        "height": 600,
                        "mentionedUserIds": [
                            "user_001"
                        ],
                        "accessLevel": "everyone"
                    }
                ]
            }
        )
        expected_res = {
            "payload": [
                {
                    "id": "ea8c6af8-30f8-11eb-8474-0242ac160005",
                    "accessLevel": "everyone",
                    "tripId": "0866515c-30f8-11eb-8474-0242ac160005",
                    "status": "editing",
                    "user": {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "14.53861166666667 W, 64.752895 N",
                    "country": "Royrvik, NO",
                    "createTime": 1605306885,
                    "uploadTime": 1606520321,
                    "width": 400,
                    "height": 600,
                    "lqSrc": "http://localhost/photos/ea8a259a-30f8-11eb-8474-0242ac160005.png",
                    "src": "http://localhost/photos/ea8651ea-30f8-11eb-8474-0242ac160005.png",
                    "likedNb": 0
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1601155452818
        }
        photo_id = response.json['payload'][0]['id']
        self._assert_response(
            expected_code=201,
            expected_res=expected_res,
            response=response,
            excludes=[
                'timestamp',
                'id',
                'uploadTime',
                'lqSrc',
                'src',
                'tripId',
                'feedbacks'
            ]
        )
        # delete the test trip and photo from cassandra
        delete_all_about_given_trip(trip_id=new_trip.trip_id, photo_ids=[photo_id])

    def test_post_trip_photos_with_location_field(self):
        new_trip = create_and_return_new_trip(owner_id='user_001', trip_name='test', user_ids=['user_001'])
        trip_id = new_trip.trip_id
        response = self._post_req_from_jon(
            endpoint=f'/trips/{trip_id}/photos',
            params={
                "userToken": 'test',
            },
            payload={
                "originalPhotos": [
                    {
                        "data": encode_image(os.environ['TEST_PHOTO_PATH']),
                        "latitude": "64.752895",
                        "latitudeRef": "N",
                        "longitude": "14.53861166666667",
                        "longitudeRef": "W",
                        "location": "Shanghai",
                        "time": 1605306885,
                        "width": 400,
                        "height": 600,
                        "mentionedUserIds": [
                            "user_001"
                        ],
                        "accessLevel": "everyone"
                    }
                ]
            }
        )
        expected_res = {
            "payload": [
                {
                    "id": "ea8c6af8-30f8-11eb-8474-0242ac160005",
                    "accessLevel": "everyone",
                    "tripId": "0866515c-30f8-11eb-8474-0242ac160005",
                    "status": "editing",
                    "user": {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "Shanghai",
                    "country": "Royrvik, NO",
                    "createTime": 1605306885,
                    "uploadTime": 1606520321,
                    "width": 400,
                    "height": 600,
                    "lqSrc": "http://localhost/photos/ea8a259a-30f8-11eb-8474-0242ac160005.png",
                    "src": "http://localhost/photos/ea8651ea-30f8-11eb-8474-0242ac160005.png",
                    "likedNb": 0
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1601155452818
        }
        photo_id = response.json['payload'][0]['id']
        self._assert_response(
            expected_code=201,
            expected_res=expected_res,
            response=response,
            excludes=[
                'timestamp',
                'id',
                'uploadTime',
                'lqSrc',
                'src',
                'tripId',
                'feedbacks'
            ]
        )
        # delete the test trip and photo from cassandra
        delete_all_about_given_trip(trip_id=new_trip.trip_id, photo_ids=[photo_id])

    def test_patch_trip_photo_expect_success(self):
        response = self._post_req_from_jon(
            endpoint=f'/trips/trip_01/photos/photo_01_1',
            method='patch',
            params={
                "userToken": 'test',
            },
            payload={
                "accessLevel": "everyone",
                "mentionedUserIds": ["user_001", "user_002"],
                "location": "Shanghai"

            }
        )
        expected_res = {
            "payload": {
                "reducedPhoto": {
                    "id": "photo_01_1",
                    "accessLevel": "everyone",
                    "tripId": "trip_01",
                    "status": "confirmed",
                    "user": {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "Shanghai",
                    "country": "Westeros",
                    "createTime": 1596142628,
                    "uploadTime": 1596142628,
                    "width": 768,
                    "height": 1365,
                    "lqSrc": "photo_1.jpg",
                    "src": "photo_1.jpg",
                    "likedNb": 7
                },
                "hqSrc": "",
                "likedUsers": [
                    {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_002",
                        "accessLevel": "everyone",
                        "nickName": "Daenerys Targaryen",
                        "uniqueName": "daenerys_targaryen",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_003",
                        "accessLevel": "everyone",
                        "nickName": "Red Dragon",
                        "uniqueName": "red_dragon",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_004",
                        "accessLevel": "everyone",
                        "nickName": "Blue Dragon",
                        "uniqueName": "blue_dragon",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_005",
                        "accessLevel": "everyone",
                        "nickName": "Samwell Tarly",
                        "uniqueName": "samwell_tarly",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_006",
                        "accessLevel": "everyone",
                        "nickName": "Cersei Lannister",
                        "uniqueName": "cersei_lannister",
                        "avatarSrc": "avatar.png"
                    }
                ],
                "mentionedUsers": [
                    {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_002",
                        "accessLevel": "everyone",
                        "nickName": "Daenerys Targaryen",
                        "uniqueName": "daenerys_targaryen",
                        "avatarSrc": "avatar.png"
                    }
                ],
                "commentNb": 0,
                "comments": [
                    {
                        "replyNb": 3,
                        "replies": [
                            {
                                "id": "reply_03",
                                "user": {
                                    "id": "user_005",
                                    "accessLevel": "everyone",
                                    "nickName": "Samwell Tarly",
                                    "uniqueName": "samwell_tarly",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596146639,
                                "content": "yes",
                                "likedNb": 1,
                                "mentions": [],
                                "hashtags": [],
                                "hasLiked": False
                            },
                            {
                                "id": "reply_02",
                                "user": {
                                    "id": "user_004",
                                    "accessLevel": "everyone",
                                    "nickName": "Blue Dragon",
                                    "uniqueName": "blue_dragon",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142639,
                                "content": "good",
                                "likedNb": 3,
                                "mentions": [],
                                "hashtags": [],
                                "hasLiked": False
                            },
                            {
                                "id": "reply_01",
                                "user": {
                                    "id": "user_003",
                                    "accessLevel": "everyone",
                                    "nickName": "Red Dragon",
                                    "uniqueName": "red_dragon",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142629,
                                "content": "what?",
                                "likedNb": 3,
                                "mentions": [],
                                "hashtags": [],
                                "hasLiked": False
                            }
                        ],
                        "id": "comment_02",
                        "user": {
                            "id": "user_002",
                            "accessLevel": "everyone",
                            "nickName": "Daenerys Targaryen",
                            "uniqueName": "daenerys_targaryen",
                            "avatarSrc": "avatar.png"
                        },
                        "createTime": 1596142639,
                        "content": "hello #wonderline @jon_snow awesome",
                        "likedNb": 7,
                        "mentions": [
                            {
                                "uniqueName": "jon_snow",
                                "userId": "user_001",
                                "startIndex": 18,
                                "endIndex": 27
                            }
                        ],
                        "hashtags": [
                            {
                                "name": "wonderline",
                                "startIndex": 6,
                                "endIndex": 17
                            }
                        ],
                        "hasLiked": False
                    },
                    {
                        "replyNb": 2,
                        "replies": [
                            {
                                "id": "reply_02",
                                "user": {
                                    "id": "user_006",
                                    "accessLevel": "everyone",
                                    "nickName": "Cersei Lannister",
                                    "uniqueName": "cersei_lannister",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142639,
                                "content": "good",
                                "likedNb": 4,
                                "mentions": [],
                                "hashtags": [],
                                "hasLiked": False
                            },
                            {
                                "id": "reply_01",
                                "user": {
                                    "id": "user_002",
                                    "accessLevel": "everyone",
                                    "nickName": "Daenerys Targaryen",
                                    "uniqueName": "daenerys_targaryen",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142629,
                                "content": "what?",
                                "likedNb": 3,
                                "mentions": [],
                                "hashtags": [],
                                "hasLiked": False
                            }
                        ],
                        "id": "comment_01",
                        "user": {
                            "id": "user_001",
                            "accessLevel": "everyone",
                            "nickName": "Jon Snow",
                            "uniqueName": "jon_snow",
                            "avatarSrc": "avatar.png"
                        },
                        "createTime": 1596142629,
                        "content": "hi",
                        "likedNb": 6,
                        "mentions": [],
                        "hashtags": [],
                        "hasLiked": False
                    }
                ]
            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1608221288
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response,
            excludes=[
                'timestamp',
            ]
        )
        # change back
        self._post_req_from_jon(
            endpoint=f'/trips/trip_01/photos/photo_01_1',
            method='patch',
            params={
                "userToken": 'test',
            },
            payload={
                "accessLevel": "everyone",
                "mentionedUserIds": ["user_001"],
                "location": "Westeros",
            }
        )

    def test_delete_trip_photos(self):
        new_trip = create_and_return_new_trip(owner_id='user_001', trip_name='test', user_ids=['user_001'])
        new_trip_id = new_trip.trip_id
        new_photos_response = self._post_req_from_jon(
            endpoint=f'/trips/{new_trip_id}/photos',
            params={
                "userToken": 'test',
            },
            payload={
                "originalPhotos": [
                    {
                        "data": encode_image(os.environ['TEST_PHOTO_PATH']),
                        "latitude": "64.752895",
                        "latitudeRef": "N",
                        "longitude": "14.53861166666667",
                        "longitudeRef": "W",
                        "time": 1605306885,
                        "width": 400,
                        "height": 600,
                        "mentionedUserIds": [
                            "user_001"
                        ],
                        "accessLevel": "everyone"
                    }
                ]
            }
        )
        response = self._post_req_from_jon(
            endpoint=f'/trips/{new_trip.trip_id}/photos',
            method='delete',
            params={
                "userToken": 'test',
            },
            payload={
                "photoIds": [new_photos_response.json['payload'][0]['id']]
            }
        )
        expected_res = {
            "feedbacks": [],
            "errors": [],
            "timestamp": 1608224337
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response,
            excludes=[
                'timestamp',
            ]
        )
        delete_all_about_given_trip(trip_id=new_trip_id)

    def test_patch_trip_photos(self):
        response = self._post_req_from_jon(
            endpoint=f'/trips/trip_01/photos',
            method='patch',
            params={
                "userToken": 'test',
            },
            payload={
                "photoIds": [
                    "photo_01_1",
                    "photo_01_2"
                ],
                "accessLevel": "mockAccessLevel"
            }
        )
        expected_res = {
            "payload": [
                {
                    "id": "photo_01_1",
                    "accessLevel": "mockAccessLevel",
                    "tripId": "trip_01",
                    "status": "confirmed",
                    "user": {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "Westeros",
                    "country": "Westeros",
                    "createTime": 1596142628,
                    "uploadTime": 1596142628,
                    "width": 768,
                    "height": 1365,
                    "lqSrc": "photo_1.jpg",
                    "src": "photo_1.jpg",
                    "likedNb": 7
                },
                {
                    "id": "photo_01_2",
                    "accessLevel": "mockAccessLevel",
                    "tripId": "trip_01",
                    "status": "confirmed",
                    "user": {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "nickName": "Jon Snow",
                        "uniqueName": "jon_snow",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "Westeros",
                    "country": "Westeros",
                    "createTime": 1596142638,
                    "uploadTime": 1596142638,
                    "width": 374,
                    "height": 280,
                    "lqSrc": "photo_2.jpg",
                    "src": "photo_2.jpg",
                    "likedNb": 0
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1622584999
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response,
            excludes=[
                'timestamp',
            ]
        )
        # change back
        self._post_req_from_jon(
            endpoint=f'/trips/trip_01/photos',
            method='patch',
            params={
                "userToken": 'test',
            },
            payload={
                "photoIds": [
                    "photo_01_1",
                    "photo_01_2"
                ],
                "accessLevel": "everyone"
            }
        )

    def test_search_users_in_trip(self):
        # create a new trip
        new_trip = create_and_return_new_trip(owner_id='user_001', trip_name='test trip',
                                              user_ids=['user_001', 'user_002'])
        # add users into the trip
        # user_001: Jon, user_003: Red Dragon
        self._post_req_from_jon(
            endpoint=f'/trips/{new_trip.trip_id}',
            method='patch',
            params={
                "userToken": 'test',
            },
            payload={
                "name": "new trip name",
                "description": "new test trip",
                "userIds": [
                    "user_001",
                    "user_003"
                ],
            }
        )
        # search user in the trip using letter 'n', it is expected to return Jon and Red Dragon only
        response = self._get_req_from_jon(
            endpoint=f'/search/trip/{new_trip.trip_id}/users',
            params={
                "userToken": 'test',
                "query": 'n',
                "sortType": "bestMatch",
                "startIndex": 0,
                "nb": 2
            })
        expected_res = {
            "payload": [
                {
                    "id": "user_001",
                    "accessLevel": "everyone",
                    "nickName": "Jon Snow",
                    "uniqueName": "jon_snow",
                    "avatarSrc": "avatar.png"
                },
                {
                    "id": "user_003",
                    "accessLevel": "everyone",
                    "nickName": "Red Dragon",
                    "uniqueName": "red_dragon",
                    "avatarSrc": "avatar.png"
                },

            ],

            "feedbacks": [],
            "errors": [],
            "timestamp": 1598176302710
        }
        self._assert_response(
            expected_code=200,
            expected_res=expected_res,
            response=response,
            excludes=['timestamp']
        )
        delete_all_about_given_trip(trip_id=new_trip.trip_id)

    def test_post_comment_reply(self):
        response = self._post_req_from_jon(
            endpoint='/trips/trip_01/photos/photo_01_1/comments/comment_01/replies',
            method='post',
            params={
                "userToken": 'test',
                "sortType": "createTime",
                "startIndex": 0,
                "nb": 3
            },
            payload={
                "comment": {
                    "content": "hello #wonderline @jon_snow awesome",
                    "mentions": [
                        {
                            "uniqueName": "job_snow",
                            "userId": "user_001",
                            "startIndex": 18,
                            "endIndex": 27
                        }
                    ],
                    "hashtags": [
                        {
                            "name": "wonderline",
                            "startIndex": 6,
                            "endIndex": 17
                        }
                    ]
                }
            }
        )
        reply_id_to_remove = [r["id"] for r in response.json["payload"] if not r["id"].startswith("reply")][0]
        self._assert_response(
            expected_code=201,
            expected_res={
                "payload": [
                    {
                        "id": "2006bf62-663e-44b7-89f0-6ceb359aa473",
                        "user": {
                            "id": "user_001",
                            "accessLevel": "everyone",
                            "nickName": "Jon Snow",
                            "uniqueName": "jon_snow",
                            "avatarSrc": "avatar.png"
                        },
                        "createTime": 1644708233,
                        "content": "hello #wonderline @jon_snow awesome",
                        "likedNb": 0,
                        "mentions": [
                            {
                                "uniqueName": "job_snow",
                                "userId": "user_001",
                                "startIndex": 18,
                                "endIndex": 27
                            }
                        ],
                        "hashtags": [
                            {
                                "name": "wonderline",
                                "startIndex": 6,
                                "endIndex": 17
                            }
                        ],
                        "hasLiked": False
                    },
                    {
                        "id": "reply_02",
                        "user": {
                            "id": "user_006",
                            "accessLevel": "everyone",
                            "nickName": "Cersei Lannister",
                            "uniqueName": "cersei_lannister",
                            "avatarSrc": "avatar.png"
                        },
                        "createTime": 1596142639,
                        "content": "good",
                        "likedNb": 4,
                        "mentions": [],
                        "hashtags": [],
                        "hasLiked": False
                    },
                    {
                        "id": "reply_01",
                        "user": {
                            "id": "user_002",
                            "accessLevel": "everyone",
                            "nickName": "Daenerys Targaryen",
                            "uniqueName": "daenerys_targaryen",
                            "avatarSrc": "avatar.png"
                        },
                        "createTime": 1596142629,
                        "content": "what?",
                        "likedNb": 3,
                        "mentions": [],
                        "hashtags": [],
                        "hasLiked": False
                    }
                ],
                "feedbacks": [
                    {
                        "code": 201,
                        "message": "Reply 2006bf62-663e-44b7-89f0-6ceb359aa473 has been successfully created"
                    }
                ],
                "errors": [],
                "timestamp": 1644708233
            },
            response=response,
            excludes=[
                'timestamp',
                'createTime',
                'id',
                'message'
            ]
        )
        delete_reply_given_reply_id(
            photo_id="photo_01_1",
            comment_id="comment_01",
            reply_id=reply_id_to_remove,
        )
