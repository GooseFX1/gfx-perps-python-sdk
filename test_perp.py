from gfx_perps_sdk import (Perp, Product, Trader)
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.rpc import types
from solana.transaction import Transaction, TransactionInstruction
from gfx_perps_sdk.types import Fractional

rpc_client = Client("https://omniscient-frequent-wish.solana-devnet.quiknode.pro/8b6a255ef55a6dbe95332ebe4f6d1545eae4d128/")
keyp = Keypair.from_secret_key(bytes([]))

import asyncio
import pytest

pytest_plugins = ('pytest_asyncio',)

def send_solana_transaction(wallet,ixs: [TransactionInstruction],signers:[Keypair] ):
    blockhash = rpc_client.get_recent_blockhash(commitment="finalized")
    transaction = Transaction(recent_blockhash=blockhash['result']['value']['blockhash'], 
                                  fee_payer=wallet.public_key)
    for ix in ixs:
         transaction.add(ix)
    for signer in signers:
         transaction.add_signer(signer)
    if len(signers) == 1:
        result = rpc_client.send_transaction(transaction, wallet, opts=types.TxOpts(skip_preflight=True))
    elif len(signers) == 3:
        result = rpc_client.send_transaction(transaction, wallet, signers[0], signers[1], opts=types.TxOpts(skip_preflight=True))
       
    return result
   

@pytest.mark.asyncio
async def test_perp_init():
    perp = Perp(rpc_client, 'devnet', keyp)
    assert perp.wallet != None
    assert perp.connection != None
    assert perp.networkType != None

    perp.init()

    assert perp.marketProductGroup != None

@pytest.mark.asyncio
async def test_product_init():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    assert product.PRODUCT_ID != None

@pytest.mark.asyncio
async def test_product_orderbooks():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    orderbook = product.get_orderbook_L2()
    assert len(orderbook['bids']) != 0
    assert len(orderbook['asks']) != 0

    orderbookL3 = product.get_orderbook_L3()
    assert len(orderbookL3['bids']) != 0
    assert len(orderbookL3['asks']) != 0

@pytest.mark.asyncio
async def test_product_trades():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    trades = product.get_trades()
    print("trades: ", trades )
    assert len(trades) > 0

@pytest.mark.asyncio
async def test_trader_init():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    t = Trader(perp) 
    t.init()
    assert t.traderRiskGroup != None
    assert t.userTokenAccount != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_create_trader_risk():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    t = Trader(perp) 
    ix = t.create_trader_account_ixs()
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response['result'] != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_deposit_funds():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    t = Trader(perp) 
    t.init()
    ix = t.deposit_funds_ix(Fractional.to_decimal(100))
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response['result'] != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_withdraw_funds():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    t = Trader(perp) 
    t.init()
    ix = t.withdraw_funds_ix(Fractional.to_decimal(100))
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response['result'] != None

@pytest.mark.asyncio
async def test_trader_open_orders():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    orders = t.get_open_orders(product)
    print(orders)
    assert orders['bids'] != None
    assert orders['asks'] != None
    
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_new_order_single():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix = t.new_order_ix(product, Fractional.to_decimal(50000), Fractional.to_decimal(35), 'ask', 'limit')
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response['result'] != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_new_order_multiple():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix1 = t.new_order_ix(product, Fractional.to_decimal(50000), Fractional.to_decimal(34), 'ask', 'limit')
    ix2 = t.new_order_ix(product, Fractional.to_decimal(50000), Fractional.to_decimal(36), 'ask', 'limit')
    response = send_solana_transaction(keyp, ix1[0] + ix2[0], ix1[1])
    print(response)
    assert response['result'] != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_cancel_order_single():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix1 = t.cancel_order_ix(product, 269375752548498747818049433352371) # Get this order id from t.get_open_orders()
    response = send_solana_transaction(keyp, ix1[0], ix1[1])
    print(response)
    assert response['result'] != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_cancel_order_multiple():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix1 = t.cancel_order_ix(product, 277298568799925181577403828385709)
    ix2 = t.cancel_order_ix(product, 285221385051351615336758223419572)
    response = send_solana_transaction(keyp, ix1[0] + ix2[0], ix1[1])
    print(response)
    assert response['result'] != None
