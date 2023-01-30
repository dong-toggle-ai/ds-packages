from unittest import mock

import pytest
import requests
from requests import HTTPError

from src.http_client.http_client import HttpClient
from tests.test_http_client.conftest import MockResponse


@mock.patch.object(requests, "request")
def test_request(mock_request):
    # Given
    expected = {"status": "OK"}
    mock_request.return_value = MockResponse(200, expected)

    # When
    actual = HttpClient.request("GET", "/some-url").json()

    # Then
    assert actual == expected


@mock.patch.object(requests, "request")
def test_request_fail(mock_request):
    # Given
    mock_request.return_value = MockResponse(500, {})

    # When
    # Then
    with pytest.raises(HTTPError):
        HttpClient.request("GET", "/some-url")


@pytest.mark.parametrize(
    "log_level, status_code, expected",
    [
        ("DEBUG", 400, "HTTP 4xx or 500 Error"),
        ("DEBUG", 404, "HTTP 4xx or 500 Error"),
        ("DEBUG", 500, "HTTP 4xx or 500 Error"),
    ],
)
@mock.patch.object(requests, "request")
def test_request_warn_log(mock_request, log_level, status_code, expected, caplog):
    # Given
    caplog.set_level(log_level)
    mock_request.return_value = MockResponse(status_code, {})

    # When
    # Then
    with pytest.raises(HTTPError):
        HttpClient.request("GET", "/some-url")
        assert expected in caplog.text


@pytest.mark.parametrize(
    "log_level, status_code, expected",
    [
        ("ERROR", 400, "HTTP 4xx or 500 Error"),
        ("ERROR", 404, "HTTP 4xx or 500 Error"),
        ("ERROR", 500, "HTTP 4xx or 500 Error"),
        ("ERROR", 502, "HTTP Error"),
    ],
)
@mock.patch.object(requests, "request")
def test_request_error_log(mock_request, log_level, status_code, expected, caplog):
    # Given
    caplog.set_level(log_level)
    mock_request.return_value = MockResponse(status_code, {})

    # When
    # Then
    with pytest.raises(HTTPError):
        HttpClient.request("GET", "/some-url")
        if status_code <= 500:
            assert expected not in caplog.text
        else:
            assert expected in caplog.text
