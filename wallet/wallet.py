from constants import *
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI

import os
import subprocess
import json



load_dotenv()
mnemonic = os.environ.get('MNEMONIC')
print(mnemonic)
#print(os.environ)

def derive_wallets (P_mnemonic, P_coin, P_numderive):
    command = f"""./derive -g --mnemonic="{P_mnemonic}" --cols=address,index,path,privkey,pubkey,xprv,xpub --numderive={P_numderive} --coin={P_coin} --format=json"""
    # Create the subprocess to run the command
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    # Communicate with the subprocess to capture the output
    (output,err) = p.communicate()

    # Wait the output
    p_status = p.wait()
    
    #(output)
    return json.loads(output)

coins={'btc-test':derive_wallets (mnemonic, BTCTEST, 3),'eth':derive_wallets (mnemonic, ETH, 3)}
print(json.dumps(coins, indent=2, sort_keys=True))

#print(coins[ETH][2]['privkey'])
#===================================================================================================

def priv_key_to_account (coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    

def create_tx (coin, account, to, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        return {
            "to": recipient,
            "from": account.address,
            "value": amount,
            "gas": gasEstimate,
            "gasPrice": w3.eth.gasPrice,
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainID": w3.eth.chainId
        }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

def send_tx (coin, account, to, amount):
    raw_tx = create_tx(coin, account, to, amount)
    signed_tx = account.sign_transaction(raw_tx)
    
    if coin == ETH:
        return w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    elif coin == BTCTEST:
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
