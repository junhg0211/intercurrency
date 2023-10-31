from json import load

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
