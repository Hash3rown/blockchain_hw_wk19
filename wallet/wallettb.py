
from constants import *
import os
from dotenv import load_dotenv
import subprocess
import json
from web3 import Web3
from eth_account import Account
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI




load_dotenv()
mnemonic = os.getenv("MNEMONIC", 'deposit quote question hidden brave raw tiny fragile vehicle foil they fabric')

#set eth testnet address
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.isConnected()


def derive_wallets (mnemonic, coin, number):
    
    command = f"./derive -g --mnemonic='{mnemonic}' --coin='{coin}' --numderive='{number}' --format=json"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = process.communicate()
    process_status = process.wait()
    keys = json.loads(output)
    
    return keys


def coins ():
    coin_dict = {
    'btc-test': derive_wallets(mnemonic, BTCTEST, 3),
    'eth': derive_wallets(mnemonic, ETH, 3)
    }
    return coin_dict



#create account object that can be consumed by web3 or bit
def priv_key_to_account(coin, priv_key):

    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    else:
        return 'err: unsupported key'





#set eth sender account
eth_sender = priv_key_to_account(ETH, coins()[ETH][0]['privkey'])

#set ETH recipient address
eth_rec = priv_key_to_account(ETH, coins()[ETH][0]['privkey'])

#set btc_testnet sender
btc_sender = priv_key_to_account(BTCTEST, coins()[BTCTEST][0]['privkey'])

#set btc_testnet recipient
btc_rec = priv_key_to_account(BTCTEST, coins()[BTCTEST][1]['privkey'])
print(btc_rec.address)

def create_tx(coin, account, to, amount):
    
    if coin == ETH:
        gasEstimate = w3.eth.estimate_gas({
            'from': account.address, 
            'to': to, 
            'value': w3.toWei(amount,'ether') 
            })
        return {
            'to': to, 
            'from': account.address, 
            'value': w3.toWei(amount,'ether'), 
            'gas': gasEstimate, 
            'gasPrice': w3.eth.gas_price, 
            'nonce':w3.eth.get_transaction_count(account.address),
        }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account, [(to, amount, BTC)])


# create function to sign and send tx's
def send_tx (coin, account, to, amount):
    raw_tx = create_tx(coin, account, to, amount)
    signed_tx = account.sign_transaction(raw_tx)
    
    if coin == ETH:
        return w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    elif coin == BTCTEST:
        return NetworkAPI.broadcast_tx_testnet(signed_tx)


