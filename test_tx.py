from web3 import Web3

AMOY_RPC_URL = "https://rpc-amoy.polygon.technology"
PRIVATE_KEY = "0xa6ebde4a0429a4b248d888043fdbe1450a8fb7796fd5f44f5f4cab8d5125d76a"
ADDRESS = "0x6E0b2b024c976e3d27F0d40be458646207506843"

w3 = Web3(Web3.HTTPProvider(AMOY_RPC_URL))

print(f"Conectado: {w3.is_connected()}")

# Balance
balance = w3.eth.get_balance(ADDRESS)
print(f"Balance: {w3.from_wei(balance, 'ether')} MATIC")

if balance == 0:
    print("\nNo tienes MATIC para enviar tx de prueba.")
    print("Consigue MATIC en: https://faucet.polygon.technology/")
else:
    # Enviar tx a ti mismo
    nonce = w3.eth.get_transaction_count(ADDRESS)

    tx = {
        'from': ADDRESS,
        'to': ADDRESS,
        'value': w3.to_wei(0.001, 'ether'),  # 0.001 MATIC
        'gas': 21000,
        'gasPrice': w3.to_wei(30, 'gwei'),
        'nonce': nonce,
        'chainId': 80002
    }

    signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    print(f"\nTX enviada: {tx_hash.hex()}")
    print(f"Ver: https://amoy.polygonscan.com/tx/{tx_hash.hex()}")
    print("\nEspera unos segundos y revisa la consola del servidor Flask...")
