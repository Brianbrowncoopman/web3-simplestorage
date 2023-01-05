from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()


# compilar
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)


with open("compliled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# abi
abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]

w3 = Web3(Web3.HTTPProvider("http://172.19.0.1:7545"))
chain_id = 1337
my_address = "0x246F9eC6FBE3279DAba2440bA8374212d37a4B2d"
private_key = os.getenv("PRIVATE_KEY")


SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)


# nonce
nonce = w3.eth.getTransactionCount(my_address)

# 1.construir la transaccion
# 2.firmar la transaccion
# 3.enviar la transaccion

transaction = SimpleStorage.constructor().build_transaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)

singed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)


tx_hash = w3.eth.send_raw_transaction(singed_txn.rawTransaction)
print("Waiting for transaction to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(tx_receipt.contractAddress)
