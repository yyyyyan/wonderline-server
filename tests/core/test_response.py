from wonderline_app.core.api_responses.response import Response


# TODO: test other Response class functions
def test_response_json():
    res = Response(payload={"input": "tutu"})
    res.timestamp = 1597094178958585
    assert res.to_dict() == {
        "payload": {"input": "tutu"},
        "errors": [],
        "feedbacks": [],
        "timestamp": 1597094178958585
    }
