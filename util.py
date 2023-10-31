from random import choice, random
from json import load
from hashlib import sha256

with open('res/secret.json', 'r') as file:
    secret = load(file)


def get(result: dict, path: str):
    paths = path.split('.')
    while paths:
        result = result[paths.pop(0)]

        if result is None:
            return None

    return result


def get_secret(path: str):
    return get(secret, path)


def encrypt(token: str) -> str:
    for _ in range(len(token) * 37):
        sala = sha256(token.encode()).hexdigest()
        token = token + sala
        token = sha256(token.encode()).hexdigest()

    return token


def random_token() -> str:
    result = list()

    for _ in range(64):
        letter = chr(choice(list(range(ord('A'), ord('Z')+1))))
        if random() > 0.5:
            letter = letter.lower()

        result.append(letter)

    return ''.join(result)


if __name__ == '__main__':
    token = random_token()
    print(token)
    print(encrypt(token))
