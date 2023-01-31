import atexit
import logging
import sys
import uuid
from enum import Enum
from typing import Optional

import grpc
from google.protobuf.json_format import MessageToDict

from calculator.v1.calculator_api_pb2 import GetSnakeDataRequest
from calculator.v1.calculator_api_pb2 import GetSnakeDataUnaryResponse
from calculator.v1.calculator_api_pb2_grpc import CalculatorAPIStub

from http_client.http_client import HttpClient

logger = logging.getLogger(__name__)

_calculator_channel_singleton: grpc.Channel = None
_calculator_stub_singleton = None


class CalculatorSource(Enum):
    http = "http"
    grpc = "grpc"


class Calculator():
    def __init__(
            self,
            http_host: str = "",
            grpc_host: str = "",
            calculator_source: CalculatorSource = CalculatorSource.http,
    ):
        self.http_host = http_host
        self.grpc_host = grpc_host
        self.calculator_source = calculator_source
        self._validate_config()

        if self.calculator_source == CalculatorSource.grpc:
            self._initialize_grpc()

    def _validate_config(self):
        if (
                (not self.http_host and not self.grpc_host)
                or (self.calculator_source == CalculatorSource.grpc and not self.grpc_host)
                or (self.calculator_source == CalculatorSource.http and not self.http_host)
        ):
            logger.error(f"wrong configuration!")
            sys.exit(1)

    @staticmethod
    def _shutdown_channel():
        logger.info("shutting down calculator process.")
        if _calculator_channel_singleton is not None:
            _calculator_channel_singleton.close()

    def _initialize_grpc(self) -> None:
        global _calculator_channel_singleton
        global _calculator_stub_singleton
        _calculator_channel_singleton = grpc.insecure_channel(target=self.grpc_host)
        _calculator_stub_singleton = CalculatorAPIStub(_calculator_channel_singleton)
        atexit.register(self._shutdown_channel)

    def calculate(self, snake: str, trace_id: Optional[str] = None):
        logger.debug(f"{self.calculator_source.value}: Getting calculator data for snake: {snake}")
        self.trace_id = trace_id if trace_id else str(uuid.uuid4())

        if self.calculator_source == CalculatorSource.grpc:
            return self.grpc_query(snake)
        elif self.calculator_source == CalculatorSource.http:
            return self.http_query(snake)

    def http_query(self, snake: str):
        headers = {"X-Request-Id": str(self.trace_id)}
        query = {"snake_expression": snake}
        try:
            r = HttpClient.request(method="POST", url=self.http_host, json=query, headers=headers, timeout=5)
            if r.status_code != 200:
                logger.warning(f"calculation error: {r.status_code} {snake}")
                return
            return r.json().get("result", {}).get("data")
        except Exception as e:
            logger.warning(f"connection went wrong: {snake} - {e}")
            return

    def grpc_query(self, snake: str):
        try:
            response = self.grpc_request(snake)
            return self.deserialize(response)
        except grpc.RpcError as error:
            if isinstance(error, grpc.Call):
                pass
            raise

    def grpc_request(self, snake):
        request = GetSnakeDataRequest(snake_expression=snake)
        response: GetSnakeDataUnaryResponse = _calculator_stub_singleton.GetSnakeDataUnary(request, timeout=5)
        return response

    def deserialize(self, response):
        return [MessageToDict(message, including_default_value_fields=True) for message in response.data]
