from web3 import Web3

AMOY_RPC_URL = "https://polygon-amoy.g.alchemy.com/v2/oJcNgzEeK1PumjP8PZi5I"
ADDRESS = "0x6E0b2b024c976e3d27F0d40be458646207506843"

w3 = Web3(Web3.HTTPProvider(AMOY_RPC_URL))

print(f"Conectado: {w3.is_connected()}")

confirmed = w3.eth.get_transaction_count(ADDRESS, "latest")
pending = w3.eth.get_transaction_count(ADDRESS, "pending")

print(f"Nonce confirmado: {confirmed}")
print(f"Nonce pendiente: {pending}")

if pending > confirmed:
    print(f"\n⚠️ Tienes {pending - confirmed} tx pendiente(s)")
    print(f"Nonce atascado mas bajo: {confirmed}")
else:
    print("\n✅ No hay transacciones pendientes")

# Balance
balance = w3.eth.get_balance(ADDRESS)
print(f"\nBalance: {w3.from_wei(balance, 'ether')} MATIC")
