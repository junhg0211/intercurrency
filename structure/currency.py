from dataclasses import dataclass, asdict
from copy import copy
from math import exp, log

LOG_2 = log(2)


@dataclass
class Currency:
    unit: str
    code: str
    total_value: int
    multiplier: int
    total_currency: int
    frozen: int

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
