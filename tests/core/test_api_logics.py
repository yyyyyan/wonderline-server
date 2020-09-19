import unittest

import requests

HOST = "http://localhost:80"


class ApiTEST(unittest.TestCase):
    def setUp(self) -> None:
        pass
        # requests.get(HOST + "/hello_world")

    def _get_req(self, endpoint, **kwargs):
        default_headers = {"Content-Type": "application/json"}
        default_headers.update(kwargs.pop('headers', {}))
        url = HOST + endpoint
        return requests.get(url=url, headers=default_headers, **kwargs)

    def _assert_equal_json(self, j1: dict, j2: dict):
        for key, value in j1.items():
            if key not in j2:
                return False

    def _assert_response(self, expected_code, expected_res_json_without_timestamp, response):
        response_json = response.json()

        self.assertIsNotNone(response_json['timestamp'])
        response_json.pop('timestamp')
        expected_res_json_without_timestamp.pop('timestamp')
        self.assertEqual(expected_code, response.status_code)
        self.assertEqual(expected_res_json_without_timestamp, response_json)

    def test_get_user_with_success(self):
        response = self._get_req(
            endpoint='/users/user_001',
            params={
                "userToken": 'test',
                "followersSortType": "createTime",
                "followerNb": 2
            })
        expected_res = {
            "payload": {
                "createTime": 1596134528628,
                "signature": "The king of the North, Danny is my QUEEN!",
                "profileLqSrc": "bkg.png",
                "profileSrc": "bkg.png",
                "followerNb": 6,
                "followers": [
                    {
                        "id": "user_007",
                        "accessLevel": "everyone",
                        "name": "Night King",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_006",
                        "accessLevel": "everyone",
                        "name": "Cersei Lannister",
                        "avatarSrc": "avatar.png"
                    }
                ],
                "id": "user_001",
                "accessLevel": "everyone",
                "name": "Jon Snow",
                "avatarSrc": "avatar.png"
            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598134804271
        }
        self._assert_response(
            expected_code=200,
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_user_with_default_parameters_expect_success(self):
        response = self._get_req(
            endpoint='/users/user_001',
            params={
                "userToken": 'test',
            })
        expected_res = {
            "payload": {
                "createTime": 1596134528628,
                "signature": "The king of the North, Danny is my QUEEN!",
                "profileLqSrc": "bkg.png",
                "profileSrc": "bkg.png",
                "followerNb": 6,
                "followers": [
                    {
                        "id": "user_007",
                        "accessLevel": "everyone",
                        "name": "Night King",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_006",
                        "accessLevel": "everyone",
                        "name": "Cersei Lannister",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_005",
                        "accessLevel": "everyone",
                        "name": "Samwell Tarly",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_004",
                        "accessLevel": "everyone",
                        "name": "Blue Dragon",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_003",
                        "accessLevel": "everyone",
                        "name": "Red Dragon",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_002",
                        "accessLevel": "everyone",
                        "name": "Daenerys Targaryen",
                        "avatarSrc": "avatar.png"
                    }
                ],
                "id": "user_001",
                "accessLevel": "everyone",
                "name": "Jon Snow",
                "avatarSrc": "avatar.png"
            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598562624846
        }
        self._assert_response(
            expected_code=200,
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_user_with_404_error(self):  # when a resource is not found
        response = self._get_req(
            endpoint='/users/user_009',
            params={
                "userToken": 'test',
                "followersSortType": "createTime",
                "followerNb": 2
            })
        expected_res = {
            "payload": {
                "createTime": None,
                "signature": None,
                "profileLqSrc": None,
                "profileSrc": None,
                "followerNb": None,
                "followers": None,
                "id": None,
                "accessLevel": None,
                "name": None,
                "avatarSrc": None
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
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_user_with_401_error(self):  # when user is unauthorized
        response = self._get_req(
            endpoint='/users/user_009',
            params={
                "userToken": None,
                "followersSortType": "createTime",
                "followerNb": 2
            })
        expected_res = {
            "payload": {
                "createTime": None,
                "signature": None,
                "profileLqSrc": None,
                "profileSrc": None,
                "followerNb": None,
                "followers": None,
                "id": None,
                "accessLevel": None,
                "name": None,
                "avatarSrc": None
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
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_followers_expect_success(self):
        response = self._get_req(
            endpoint='/users/user_001/followers',
            params={
                "userToken": 'test',
                "sortType": "createTime",
                "nb": 2,
                "startIndex": 1
            })

        expected_res = {'payload': [
            {'id': 'user_006', 'accessLevel': 'everyone', 'name': 'Cersei Lannister', 'avatarSrc': 'avatar.png'},
            {'id': 'user_005', 'accessLevel': 'everyone', 'name': 'Samwell Tarly', 'avatarSrc': 'avatar.png'}],
            'feedbacks': [], 'errors': [], 'timestamp': 1598128569991}
        self._assert_response(
            expected_code=200,
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_user_trips_expect_success(self):
        response = self._get_req(
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
                'id': 'user_001', 'accessLevel': 'everyone', 'name': 'The Winds of Winter',
                'description': 'Winter is the time when things die, and cold and ice and darkness fill the world, so this is not going to be the happy feel-good that people may be hoping for. Things get worse before they get better, so things are getting worse for a lot of people.',
                'users': [{
                    'id': 'user_004', 'accessLevel': 'everyone', 'name': 'Blue Dragon',
                    'avatarSrc': 'avatar.png'},
                    {'id': 'user_002', 'accessLevel': 'everyone',
                     'name': 'Daenerys Targaryen', 'avatarSrc': 'avatar.png'},
                    {'id': 'user_001', 'accessLevel': 'everyone', 'name': 'Jon Snow',
                     'avatarSrc': 'avatar.png'},
                    {'id': 'user_007', 'accessLevel': 'everyone', 'name': 'Night King',
                     'avatarSrc': 'avatar.png'},
                    {'id': 'user_003', 'accessLevel': 'everyone', 'name': 'Red Dragon',
                     'avatarSrc': 'avatar.png'},
                    {'id': 'user_005', 'accessLevel': 'everyone', 'name': 'Samwell Tarly',
                     'avatarSrc': 'avatar.png'}],
                'createTime': 1596142528628,
                'beginTime': 1596142628628,
                'endTime': 1596143628628,
                'photoNb': 9,
                'coverPhoto': {
                    'id': 'photo_01_2', 'accessLevel': 'everyone', 'tripId': 'trip_01',
                    'status': 'confirmed',
                    'user': {'id': 'user_001', 'accessLevel': 'everyone',
                             'name': 'Jon Snow', 'avatarSrc': 'avatar.png'},
                    'location': 'Westeros', 'country': 'Westeros',
                    'createTime': 1596142638628, 'uploadTime': 1596142638728,
                    'width': 374, 'height': 280, 'lqSrc': 'photo_2.jpg',
                    'src': 'photo_2.jpg', 'likedNb': 0}}], 'feedbacks': [],
            'errors': [], 'timestamp': 1598132005855}
        self._assert_response(
            expected_code=200,
            expected_res_json_without_timestamp=expected_res,
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
    #         {'id': 'user_005', 'accessLevel': 'everyone', 'name': 'Samwell Tarly', 'avatarSrc': 'avatar.png'}],
    #         'feedbacks': [], 'errors': [], 'timestamp': 1598128569991}
    #     self._assert_response(
    #         expected_code=200,
    #         expected_res_json_without_timestamp=expected_res,
    #         response=response
    #     )

    def test_get_albums_expect_success(self):
        response = self._get_req(
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
                                    "name": "Daenerys Targaryen",
                                    "avatarSrc": "avatar.png"
                                },
                                "location": "Westeros",
                                "country": "Westeros",
                                "createTime": 1596142688628,
                                "uploadTime": 1596142688728,
                                "width": 1920,
                                "height": 2716,
                                "lqSrc": "photo_7.jpg",
                                "src": "photo_7.jpg",
                                "likedNb": 0
                            },
                            "ratioType": "vertical"
                        }
                    ],
                    "createTime": 1596142628628
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
                                    "name": "Jon Snow",
                                    "avatarSrc": "avatar.png"
                                },
                                "location": "Westeros",
                                "country": "Westeros",
                                "createTime": 1596142658628,
                                "uploadTime": 1596142658728,
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
                                    "name": "Jon Snow",
                                    "avatarSrc": "avatar.png"
                                },
                                "location": "Westeros",
                                "country": "Westeros",
                                "createTime": 1596142678628,
                                "uploadTime": 1596142678728,
                                "width": 2560,
                                "height": 1565,
                                "lqSrc": "photo_6.jpg",
                                "src": "photo_6.jpg",
                                "likedNb": 0
                            },
                            "ratioType": "vertical"
                        }
                    ],
                    "createTime": 1596142738628
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598136936429
        }
        self._assert_response(
            expected_code=200,
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_mentions_expect_success(self):
        response = self._get_req(
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
                            "name": "Jon Snow",
                            "avatarSrc": "avatar.png"
                        },
                        "location": "Westeros",
                        "country": "Westeros",
                        "createTime": 1596142638628,
                        "uploadTime": 1596142638728,
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
                            "name": "Jon Snow",
                            "avatarSrc": "avatar.png"
                        },
                        "location": "Westeros",
                        "country": "Westeros",
                        "createTime": 1596142658628,
                        "uploadTime": 1596142658728,
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
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_trip_expect_success(self):
        response = self._get_req(
            endpoint='/trips/trip_01',
            params={
                "userToken": 'test',
                "usersSortType": "createTime",
                "userNb": 1
            })
        expected_res = {
            "payload": {
                "likedNb": 23892,
                "sharedNb": 1656,
                "savedNb": 4222,
                "id": "trip_01",
                "accessLevel": "everyone",
                "name": "The Winds of Winter",
                "description": "Winter is the time when things die, and cold and ice and darkness fill the world, so this is not going to be the happy feel-good that people may be hoping for. Things get worse before they get better, so things are getting worse for a lot of people.",
                "users": [
                    {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "name": "Jon Snow",
                        "avatarSrc": "avatar.png"
                    }
                ],
                "createTime": 1596142528628,
                "beginTime": 1596142628628,
                "endTime": 1596143628628,
                "photoNb": 9,
                "coverPhoto": {
                    "id": "photo_01_2",
                    "accessLevel": "everyone",
                    "tripId": "trip_01",
                    "status": "confirmed",
                    "user": {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "name": "Jon Snow",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "Westeros",
                    "country": "Westeros",
                    "createTime": 1596142638628,
                    "uploadTime": 1596142638728,
                    "width": 374,
                    "height": 280,
                    "lqSrc": "photo_2.jpg",
                    "src": "photo_2.jpg",
                    "likedNb": 0
                }
            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598134263573
        }
        self._assert_response(
            expected_code=200,
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_trip_users(self):
        response = self._get_req(
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
                    "name": "Red Dragon",
                    "avatarSrc": "avatar.png"
                },
                {
                    "id": "user_004",
                    "accessLevel": "everyone",
                    "name": "Blue Dragon",
                    "avatarSrc": "avatar.png"
                },
                {
                    "id": "user_005",
                    "accessLevel": "everyone",
                    "name": "Samwell Tarly",
                    "avatarSrc": "avatar.png"
                },
                {
                    "id": "user_007",
                    "accessLevel": "everyone",
                    "name": "Night King",
                    "avatarSrc": "avatar.png"
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598177267994
        }

        self._assert_response(
            expected_code=200,
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_trip_photos(self):
        response = self._get_req(
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
                        "name": "Daenerys Targaryen",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "Westeros",
                    "country": "Westeros",
                    "createTime": 1596142648628,
                    "uploadTime": 1596142648728,
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
                        "name": "Jon Snow",
                        "avatarSrc": "avatar.png"
                    },
                    "location": "Westeros",
                    "country": "Westeros",
                    "createTime": 1596142658628,
                    "uploadTime": 1596142658728,
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
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_trip_photo_expect_success(self):
        response = self._get_req(
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
                "hqSrc": "",
                "likedUsers": [
                    {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "name": "Jon Snow",
                        "avatarSrc": "avatar.png"
                    },
                    {
                        "id": "user_002",
                        "accessLevel": "everyone",
                        "name": "Daenerys Targaryen",
                        "avatarSrc": "avatar.png"
                    }
                ],
                "mentionedUsers": [],
                "commentNb": 0,
                "comments": [
                    {
                        "replyNb": 3,
                        "replies": [
                            {
                                "id": "reply_01",
                                "user": {
                                    "id": "user_003",
                                    "accessLevel": "everyone",
                                    "name": "Red Dragon",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142629728,
                                "content": "what?",
                                "likedNb": 3
                            },
                            {
                                "id": "reply_02",
                                "user": {
                                    "id": "user_004",
                                    "accessLevel": "everyone",
                                    "name": "Blue Dragon",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142639728,
                                "content": "good",
                                "likedNb": 3
                            }
                        ],
                        "id": "comment_02",
                        "user": {
                            "id": "user_002",
                            "accessLevel": "everyone",
                            "name": "Daenerys Targaryen",
                            "avatarSrc": "avatar.png"
                        },
                        "createTime": 1596142639628,
                        "content": "hello",
                        "likedNb": 7
                    },
                    {
                        "replyNb": 2,
                        "replies": [
                            {
                                "id": "reply_01",
                                "user": {
                                    "id": "user_002",
                                    "accessLevel": "everyone",
                                    "name": "Daenerys Targaryen",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142629728,
                                "content": "what?",
                                "likedNb": 3
                            },
                            {
                                "id": "reply_02",
                                "user": {
                                    "id": "user_006",
                                    "accessLevel": "everyone",
                                    "name": "Cersei Lannister",
                                    "avatarSrc": "avatar.png"
                                },
                                "createTime": 1596142639728,
                                "content": "good",
                                "likedNb": 4
                            }
                        ],
                        "id": "comment_01",
                        "user": {
                            "id": "user_001",
                            "accessLevel": "everyone",
                            "name": "Jon Snow",
                            "avatarSrc": "avatar.png"
                        },
                        "createTime": 1596142629628,
                        "content": "hi",
                        "likedNb": 7
                    }
                ],
                "id": "photo_01_1",
                "accessLevel": "everyone",
                "tripId": "trip_01",
                "status": "confirmed",
                "user": {
                    "id": "user_001",
                    "accessLevel": "everyone",
                    "name": "Jon Snow",
                    "avatarSrc": "avatar.png"
                },
                "location": "Westeros",
                "country": "Westeros",
                "createTime": 1596142628628,
                "uploadTime": 1596142628728,
                "width": 768,
                "height": 1365,
                "lqSrc": "photo_1.jpg",
                "src": "photo_1.jpg",
                "likedNb": 7
            },
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598177205794
        }

        self._assert_response(
            expected_code=200,
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_trip_photo_comments_expect_success(self):
        response = self._get_req(
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
                            "id": "reply_01",
                            "user": {
                                "id": "user_003",
                                "accessLevel": "everyone",
                                "name": "Red Dragon",
                                "avatarSrc": "avatar.png"
                            },
                            "createTime": 1596142629728,
                            "content": "what?",
                            "likedNb": 3
                        },
                        {
                            "id": "reply_02",
                            "user": {
                                "id": "user_004",
                                "accessLevel": "everyone",
                                "name": "Blue Dragon",
                                "avatarSrc": "avatar.png"
                            },
                            "createTime": 1596142639728,
                            "content": "good",
                            "likedNb": 3
                        }
                    ],
                    "id": "comment_02",
                    "user": {
                        "id": "user_002",
                        "accessLevel": "everyone",
                        "name": "Daenerys Targaryen",
                        "avatarSrc": "avatar.png"
                    },
                    "createTime": 1596142639628,
                    "content": "hello",
                    "likedNb": 7
                },
                {
                    "replyNb": 2,
                    "replies": [
                        {
                            "id": "reply_01",
                            "user": {
                                "id": "user_002",
                                "accessLevel": "everyone",
                                "name": "Daenerys Targaryen",
                                "avatarSrc": "avatar.png"
                            },
                            "createTime": 1596142629728,
                            "content": "what?",
                            "likedNb": 3
                        },
                        {
                            "id": "reply_02",
                            "user": {
                                "id": "user_006",
                                "accessLevel": "everyone",
                                "name": "Cersei Lannister",
                                "avatarSrc": "avatar.png"
                            },
                            "createTime": 1596142639728,
                            "content": "good",
                            "likedNb": 4
                        }
                    ],
                    "id": "comment_01",
                    "user": {
                        "id": "user_001",
                        "accessLevel": "everyone",
                        "name": "Jon Snow",
                        "avatarSrc": "avatar.png"
                    },
                    "createTime": 1596142629628,
                    "content": "hi",
                    "likedNb": 7
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598174942804
        }
        self._assert_response(
            expected_code=200,
            expected_res_json_without_timestamp=expected_res,
            response=response
        )

    def test_get_comment_replies_expect_success(self):
        response = self._get_req(
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
                        "name": "Blue Dragon",
                        "avatarSrc": "avatar.png"
                    },
                    "createTime": 1596142639728,
                    "content": "good",
                    "likedNb": 3
                },
                {
                    "id": "reply_03",
                    "user": {
                        "id": "user_005",
                        "accessLevel": "everyone",
                        "name": "Samwell Tarly",
                        "avatarSrc": "avatar.png"
                    },
                    "createTime": 1596146639728,
                    "content": "yes",
                    "likedNb": 1
                }
            ],
            "feedbacks": [],
            "errors": [],
            "timestamp": 1598176302710
        }

        self._assert_response(
            expected_code=200,
            expected_res_json_without_timestamp=expected_res,
            response=response
        )
