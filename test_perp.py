from gfx_perps_sdk import (Perp, Product, Trader)
from solana.rpc.api import Client
from solana.keypair import Keypair
from gfx_perps_sdk.types import Fractional

rpc_client = Client("https://omniscient-frequent-wish.solana-devnet.quiknode.pro/8b6a255ef55a6dbe95332ebe4f6d1545eae4d128/")
keyp = Keypair.from_secret_key(bytes([]))

import asyncio
import pytest

pytest_plugins = ('pytest_asyncio',)

@pytest.mark.asyncio
async def test_init():
    Perps = Perp(rpc_client, 'devnet',keyp)
    res = await Perps.init()
    Prod = Product(Perps)
    Prod.init_by_name('SOL-PERP')
    #r = Prod.get_orderbook_L3()
    t = Trader(Perps) 
    t.init()
    #t.create_trader_account_ixs()
    #t.deposit_funds_ix(Fractional.to_decimal(100))
    #t.withdraw_funds_ix(Fractional.to_decimal(100))
    #t.new_order_ix(Prod,Fractional.to_decimal(50000), Fractional.to_decimal(1.5), "bid", "limit")
    op = t.get_open_orders(Prod)
    print(op)
    t.cancel_order_ix(Prod, op['bids'][0]['orderId'])
    assert 1 == 0
