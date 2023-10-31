from dataclasses import asdict

from flask import Flask, request

from structure import Currency, Response

app = Flask(__name__)

currencies: dict[Currency] = dict()
currencies['zst'] = Currency('T', 'zst', 1000, 100, 10000, 10000)
currencies['ken'] = Currency('K', 'ken', 12302, 1000, 21903, 21903)


@app.route('/api/currency', methods=['GET'])
def get_api_currency():
    result = list(map(Currency.jsonify, currencies.values()))
    response = Response(200, 'OK', result)
    return asdict(response), 200


@app.route('/api/currency/<currency_id>', methods=['GET'])
def get_api_currency_id(currency_id: str):
    if currency_id not in currencies:
        response = Response(404, 'currency with that id was not found.', dict())
        return asdict(response), 404

    result = currencies[currency_id].jsonify()
    response = Response.ok(result)
    return asdict(response), 200


@app.route('/api/currency/<currency_id>/rotate', methods=['POST'])
def post_api_currency_id_rotate(currency_id: str):
    if currency_id not in currencies:
        response = Response(404, 'currency with that id was not found.', dict())
        return asdict(response), 404

    data = request.get_json()
    elit = data.get('elit')
    if elit is None:
        response = Response(
            400, '`elit` was not found in request data.', dict())
        return asdict(response), 400

    before = currencies[currency_id]
    if not before.can_rotate(elit):
        response = Response(400, '`elit` limit exceeded.', dict())
        return asdict(response), 400

    delta = before.rotate(elit)
    after = before.add_frozen(-delta)
    currencies[currency_id] = after

    result = {
        'after': after.jsonify(),
        'before': before.jsonify(),
        'delta': delta,
    }
    response = Response.ok(result)
    return asdict(response), 200


@app.route('/api/currency/<currency_id>/freeze', methods=['POST'])
def post_api_currency_id_freeze(currency_id: str):
    if currency_id not in currencies:
        response = Response(404, 'currency with that id was not found.', dict())
        return asdict(response), 404

    data = request.get_json()
    amount = data.get('amount')
    if amount is None:
        response = Response(
            400, '`amount` was not found in request data.', dict())
        return asdict(response), 400

    before = currencies[currency_id]
    if amount > before.get_rotating():
        response = Response(400, '`amount` limit exceeded.', dict())
        return asdict(response), 400

    elit = before.freeze(amount)
    after = before.add_frozen(amount)
    currencies[currency_id] = after

    result = {
        'before': before.jsonify(),
        'after': after.jsonify(),
        'elit': elit
    }
    response = Response.ok(result)
    return asdict(response), 200


@app.route('/api/currency/<currency_id>/refresh', methods=['POST'])
def post_api_currency_id_refresh(currency_id: str):
    if currency_id not in currencies:
        response = Response(404, 'currency with that id was not found.', dict())
        return asdict(response), 404

    data = request.get_json()
    rotating = data.get('rotating')
    if rotating is None:
        response = Response(
            400, '`rotating` was not found in request data.', dict())
        return asdict(response), 400

    before = currencies[currency_id]
    after = before.set_rotating(rotating)
    currencies[currency_id] = after

    result = {
        'before': before.jsonify(),
        'after': after.jsonify(),
    }
    response = Response.ok(result)
    return asdict(response), 200


if __name__ == '__main__':
    app.run(debug=True)
