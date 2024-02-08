
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc import types
from gfx_perp_sdk import Perp, Product, Trader, utils
from gfx_perp_sdk.types.fractional import Fractional
from solders.instruction import Instruction as TransactionInstruction
from solana.transaction import Transaction

#recommend using dedicated RPC
url = 'https://api.mainnet-beta.solana.com'
rpc_client = Client(url)

key_pair = [] # 64 int values
wallet = Keypair.from_bytes(key_pair)

# perp
perp = Perp(rpc_client, 'mainnet', wallet)
perp.init()

# trader create account
t = Trader(perp)
# ix = t.create_trader_account_ixs()
# response = send_solana_transaction(rpc_client, wallet, ix[0], ix[1])
# print(response)  # ezyH47nEGfjGt9BJ91XyXfqo4QNhpFfxgTWyo2vpsJ2ouSZULvpf4jBA7knH81sXZEG4SwQupS9nC76ZzWsanmS

print()
print("address:", str(wallet.pubkey()))
t.init()
ix = t.deposit_funds_ix(Fractional.to_decimal(1000))
response = utils.send_solana_transaction(rpc_client, wallet, ix[0], ix[1])
print("response:", response)
    