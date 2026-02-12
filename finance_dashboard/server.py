import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
CORS(app) # Allow frontend to talk to this server

# Plaid configuration
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

host = plaid.Environment.Sandbox
if PLAID_ENV == 'development':
    host = plaid.Environment.Development
elif PLAID_ENV == 'production':
    host = plaid.Environment.Production

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# In-memory store for access tokens (In production, use a database)
ACCESS_TOKENS = []

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    try:
        request_obj = LinkTokenCreateRequest(
            products=[Products('transactions')],
            client_name="Jules Finance Dashboard",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(client_user_id='unique-user-id')
        )
        response = client.link_token_create(request_obj)
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        return jsonify(json.loads(e.body)), 500

@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_public_token():
    public_token = request.json.get('public_token')
    if not public_token:
        return jsonify({'error': 'Missing public token'}), 400

    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']

        # Store token (simple list for demo)
        if access_token not in ACCESS_TOKENS:
            ACCESS_TOKENS.append(access_token)

        return jsonify({'status': 'success'})
    except plaid.ApiException as e:
        return jsonify(json.loads(e.body)), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    if not ACCESS_TOKENS:
        return jsonify({'accounts': [], 'transactions': []})

    all_accounts = []
    all_transactions = []

    for token in ACCESS_TOKENS:
        try:
            # Get Accounts
            accounts_request = AccountsGetRequest(access_token=token)
            accounts_response = client.accounts_get(accounts_request)
            for acc in accounts_response['accounts']:
                all_accounts.append({
                    'name': acc['name'],
                    'type': str(acc['subtype'] or acc['type']),
                    'balance': float(acc['balances']['current'])
                })

            # Get Transactions (last 30 days)
            start_date = (datetime.now() - timedelta(days=30)).date()
            end_date = datetime.now().date()
            transactions_request = TransactionsGetRequest(
                access_token=token,
                start_date=start_date,
                end_date=end_date
            )
            transactions_response = client.transactions_get(transactions_request)
            for tx in transactions_response['transactions']:
                all_transactions.append({
                    'id': tx['transaction_id'],
                    'date': str(tx['date']),
                    'description': tx['name'],
                    'category': tx['category'][0] if tx['category'] else 'Others',
                    'amount': -float(tx['amount']) # Plaid uses positive for spending
                })
        except plaid.ApiException as e:
            print(f"Error fetching data for token: {e}")
            continue

    return jsonify({
        'accounts': all_accounts,
        'transactions': all_transactions
    })

if __name__ == '__main__':
    print("Starting Jules Finance Backend on http://localhost:5000")
    app.run(port=5000, debug=True)
