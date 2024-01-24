from solders.pubkey import Pubkey as PublicKey
from solana.rpc.websocket_api import (connect, SolanaWsClientProtocol)
from solders.rpc.responses import GetAccountInfoResp
import gfx_perp_sdk.utils as utils
from solana.rpc.api import Client
import asyncio

client = Client("https://api.mainnet-beta.solana.com")
async def subscribe_to_token_balance_change_sol(client, callback_func):
        wss = client._provider.endpoint_uri.replace("http", "ws")
        
        wallet_pubkey = PublicKey.from_string("4sM2fguyTymZUtRLBY9qUARigmUGzkLfsQ1S3rGbbBM5")
        
        async with connect(wss) as solana_websocket:
            solana_websocket: SolanaWsClientProtocol
            await solana_websocket.account_subscribe(pubkey=wallet_pubkey, commitment="processed", encoding="base64")
            first_resp = await solana_websocket.recv()
            subscription_id = first_resp[0].result if first_resp and hasattr(
                first_resp[0], 'result') else None
            print("subscription_id:", subscription_id)
            balanceResponse = client.get_balance(wallet_pubkey)
            oldLamports = balanceResponse.value
            print("oldLamports:", oldLamports)

            while True:
                try:
                    msg = await solana_websocket.recv()
                    if msg:
                        newLamports = msg[0].result.value.lamports
                        print("newLamports:", newLamports)
                        
                        if oldLamports != newLamports:
                            callback_func(oldLamports, newLamports)
                            oldLamports = newLamports
                except Exception:
                    raise ModuleNotFoundError(
                        "unable to process the Token Account") 

def on_trader_balance_change(old_balance, new_balance):
    print("old_balance:", old_balance)
    print("new_balance:", new_balance)

async def main():
    url = 'https://api.mainnet-beta.solana.com'
    rpc_client = Client(url)
    
    token_sol_sub = asyncio.create_task(subscribe_to_token_balance_change_sol(rpc_client, on_trader_balance_change))
    await token_sol_sub

if __name__ == '__main__':
    asyncio.run(main())