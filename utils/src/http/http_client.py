import logging
from typing import Optional

import requests
from requests import HTTPError

logger = logging.getLogger(__name__)


class HttpClient:
    @staticmethod
    def request(
        method: str,
        url: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None,
        raise_error: Optional[bool] = True,
    ):
        try:
            response = requests.request(
                method=method, url=url, json=json, params=params, headers=headers, timeout=timeout
            )

            if raise_error:
                response.raise_for_status()

            return response
        except HTTPError as error:
            if error.response.status_code <= 500:
                logger.debug(f"HTTP 4xx or 500 Error for {url}: {error}")
            else:
                logger.error(f"HTTP Error for {url}: {error}", exc_info=True)
            raise
