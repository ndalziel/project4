from flask import json
import requests as req
# sudo netstat -tulnp | grep :5002

import eth_account
import algosdk
import random

eth_account.Account.enable_unaudited_hdwallet_features()
acct, mnemonic = eth_account.Account.create_with_mnemonic()

eth_pk = acct.address
eth_sk = acct.key

algo_sk, algo_pk = algosdk.account.generate_account()

def create_order(platform,pk):
    platforms = ["Algorand", "Ethereum"]       
    other_platform = platforms[1-platforms.index(platform)]
    order = {}
    order['sender_pk'] = pk 
    order['receiver_pk'] = hex(random.randint(0,2**256))[2:] 
    order['buy_currency'] = platform
    order['sell_currency'] = other_platform
    order['buy_amount'] = random.randint(1,10)
    order['sell_amount'] = random.randint(1,10)
    order['platform'] = platform 

    return order

payload_eth = {'buy_amount':random.randint(1,10),
    'buy_currency': "Ethereum",
    'platform': "Ethereum",
    'receiver_pk': hex(random.randint(0,2**256))[2:], 
    'sell_amount': random.randint(1,10),
    'sell_currency':"Algorand",
    'sender_pk': eth_pk, }

   
payload_algo = {'buy_amount':random.randint(1,10),
    'buy_currency': "Algorand",
    'platform': "Algorand",
    'receiver_pk': hex(random.randint(0,2**256))[2:], 
    'sell_amount': random.randint(1,10),
    'sell_currency':"Ehereum",
    'sender_pk': algo_pk}


#payload_eth = create_order("Ethereum",eth_pk)
#payload_algo = create_order("Algorand",algo_pk)

encoded_payload = eth_account.messages.encode_defunct(text=json.dumps(payload_eth))
eth_sig_obj = eth_account.Account.sign_message(encoded_payload,eth_sk)
eth_sig = eth_sig_obj.signature.hex()
algo_sig = algosdk.util.sign_bytes(json.dumps(payload_algo).encode('utf-8'),algo_sk)

eth_data = {'sig': eth_sig, 'payload': payload_eth}
algo_data = {'sig': algo_sig, 'payload':payload_algo}

print("before:")
response = req.get("http://127.0.0.1:5002/order_book")
print(response.text)


print("Ethereum trade:")
response = req.post("http://127.0.0.1:5002/trade", json = eth_data)
print(response.text)

print("Algorand trade:")
response = req.post("http://127.0.0.1:5002/trade", json = algo_data)
print(response.text)

print("after:")
response = req.get("http://127.0.0.1:5002/order_book")
print(response.text)

print("logs:")
response = req.get("http://127.0.0.1:5002/log")
print(response.text)