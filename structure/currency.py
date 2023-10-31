from dataclasses import dataclass, asdict
from copy import copy
from math import exp, log

from util import encrypt

LOG_2 = log(2)


@dataclass
class Currency:
    unit: str
    code: str
    total_value: int
    multiplier: int
    total_currency: int
    frozen: int
    __token: str

    @staticmethod
    def from_row(row):
        if row is None:
            return None

        unit = row[0]
        code = row[1]
        total_value = row[2]
        multiplier = row[3]
        total_currency = row[4]
        frozen = row[5]
        __token = row[6]
        return Currency(
            unit, code, total_value, multiplier, total_currency, frozen, __token)

    def get_unit_value(self) -> float:
        return self.total_value / self.frozen

    def get_rotating(self) -> int:
        return self.total_currency - self.frozen

    def get_extra(self) -> dict:
        return {
            'unit_value': self.get_unit_value(),
            'rotating': self.get_rotating(),
            'rotate_limit': self.get_rotate_limit(),
        }

    def jsonify(self) -> dict:
        result = asdict(self)
        for key in list(result.keys()):
            if '__' not in key:
                continue
            result.pop(key)

        extra = self.get_extra()
        result['extra'] = extra

        return result

    def get_rotate_limit(self) -> float:
        return self.total_value * LOG_2

    def can_rotate(self, value: int) -> bool:
        return self.frozen > self.rotate(value)

    def rotate(self, value: int) -> int:
        delta = round(self.frozen * (exp(value / self.total_value) - 1))
        return delta

    def freeze(self, amount: int) -> int:
        value = round(self.total_value * log(amount / self.frozen + 1))
        return value

    def add_frozen(self, amount: int) -> 'Currency':
        result = copy(self)
        result.frozen += amount
        return result

    def set_rotating(self, rotating: int) -> 'Currency':
        result = copy(self)
        result.frozen = result.total_currency - rotating
        return result

    def check(self, token: str) -> bool:
        return encrypt(token) == self.__token
