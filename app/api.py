from flask import Flask, jsonify, request
from app.models.items import get_all_items
from app.models.parties import get_party_by_id
from app.shop import buy_item, sell_item, deposit_gold, withdraw_gold, haggle

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to Grozzlebeard's Emporium API!"})

# List Shop Items
@app.route('/items', methods=['GET'])
def list_items():
    items = get_all_items()
    return jsonify([dict(item) for item in items])

# View Party Info
@app.route('/party/<party_id>', methods=['GET'])
def party_info(party_id):
    party = get_party_by_id(party_id)
    if not party:
        return jsonify({"error": "Party not found"}), 404
    return jsonify(dict(party))

# Buy Item
@app.route('/buy', methods=['POST'])
def api_buy_item():
    data = request.json
    result = buy_item(data['party_id'], data['player_id'], data['item_name'])
    return jsonify(result)

# Sell Item
@app.route('/sell', methods=['POST'])
def api_sell_item():
    data = request.json
    result = sell_item(data['party_id'], data['player_id'], data['item_name'], data['amount'])
    return jsonify(result)

# Deposit Gold
@app.route('/deposit', methods=['POST'])
def api_deposit_gold():
    data = request.json
    result = deposit_gold(data['party_id'], data['player_id'], data['amount'])
    return jsonify(result)

# Withdraw Gold
@app.route('/withdraw', methods=['POST'])
def api_withdraw_gold():
    data = request.json
    result = withdraw_gold(data['party_id'], data['player_id'], data['amount'])
    return jsonify(result)

# Haggle
@app.route('/haggle', methods=['POST'])
def api_haggle():
    data = request.json
    result = haggle(data['party_id'], data['item_name'])
    return jsonify(result)
