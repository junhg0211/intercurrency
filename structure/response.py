from dataclasses import dataclass
from typing import Union


ResultType = Union[dict, list]

@dataclass
class Response:
    code: int
    message: str
    result: dict

    @staticmethod
    def ok(result: ResultType) -> 'Response':
        return Response(200, 'OK', result)

    @staticmethod
    def unauthorised() -> 'Response':
        return Response(401, 'unauthorised', dict())
