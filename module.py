from json import dumps

from requests import get, post

from util import get_secret

API_URL = 'http://localhost:5000/api'


class Currency:
    def __init__(self, code: str, token: str):
        self.code = code
        self.token = token

        self.total_value = 0
        self.multiplier = 0
        self.total_currency = 0
        self.frozen = 0
        self.unit = ''
        self.syncronise()

    def __str__(self):
        return f'{self.code.upper()}' \
               f'({self.get_unit_value()}[e/{self.unit}])'

    def __repr__(self):
        return f"<Currency {self}: " \
               f"{self.total_value}, " \
               f"{self.total_currency / self.multiplier}, " \
               f"{self.frozen / self.multiplier}>"

    def get_total_currency(self) -> float:
        return self.total_currency / self.multiplier

    def get_frozen(self) -> float:
        return self.frozen / self.multiplier

    def get_rotating(self) -> float:
        return (self.total_currency - self.frozen) / self.multiplier

    def get_unit_value(self) -> float:
        return self.total_value / self.frozen * self.multiplier

    def apply(self, json: dict):
        self.total_value = json.get('total_value')
        self.multiplier = json.get('multiplier')
        self.total_currency = json.get('total_currency')
        self.frozen = json.get('frozen')
        self.unit = json.get('unit')

    def syncronise(self):
        """ sends GET request to the API server and gets data syncronised. """

        # send GET request to the API server
        request = get(f'{API_URL}/currency/{self.code}')

        # check if data successfully looked up
        data = request.json()
        if request.status_code != 200:
            raise ValueError(data.get('message'))

        # close connection
        request.close()

        # apply data
        result = data.get('result')
        self.apply(result)

    def rotate(self, value: int) -> int:
        # send POST request to the API server
        headers = {'Content-Type': 'application/json'}
        data = {'token': self.token, 'elit': value}
        request = post(
            f'{API_URL}/currency/{self.code}/rotate',
            headers=headers, data=dumps(data))

        # check if data successfully looked up
        data = request.json()
        if request.status_code != 200:
            raise ValueError(data.get('message'))

        # close connection
        request.close()

        # apply data
        result = data.get('result')
        after = result.get('after')
        self.apply(after)

        # return data
        return result.get('delta')

    def freeze(self, amount: int) -> int:
        # preprocess amount to be suitable for database
        amount = round(amount * self.multiplier)

        # send POST request to the API server
        headers = {'Content-Type': 'application/json'}
        data = {'token': self.token, 'amount': amount}
        request = post(
            f'{API_URL}/currency/{self.code}/freeze',
            headers=headers, data=dumps(data))

        # check if data successfully looked up
        data = request.json()
        if request.status_code != 200:
            raise ValueError(data.get('message'))

        # close connection
        request.close()

        # apply data
        result = data.get('result')
        after = result.get('after')
        self.apply(after)

        # retutn data
        return result.get('elit')

    def refresh(self, rotating: float):
        # preprocess rotating to be suitable for database
        rotating = round(rotating * self.multiplier)

        # send POST request to the API server
        headers = {'Content-Type': 'application/json'}
        data = {'token': self.token, 'rotating': rotating}
        request = post(
            f'{API_URL}/currency/{self.code}/refresh',
            headers=headers, data=dumps(data))

        # check if data successfully looked up
        data = request.json()
        if request.status_code != 200:
            raise ValueError(data.get('message'))

        # close connection
        request.close()

        # apply data
        result = data.get('result')
        after = result.get('after')
        self.apply(after)


if __name__ == '__main__':
    TOKEN = get_secret('tokens.zst')
    currency = Currency('zst', TOKEN)

    currency.refresh(20)
    print(repr(currency))

    # amount = currency.rotate(20)
    # print(amount)
    # print(repr(currency))
