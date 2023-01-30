from requests import HTTPError


class MockResponse:
    def __init__(self, status_code, data: dict, url: str = ""):
        self.status_code = status_code
        self.data = data
        self.url = url

    def json(self):
        return self.data

    def raise_for_status(self):
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = f"{self.status_code} Client Error"

        elif 500 <= self.status_code < 600:
            http_error_msg = f"{self.status_code} Server Error"

        if http_error_msg:
            raise HTTPError(http_error_msg, response=self)
