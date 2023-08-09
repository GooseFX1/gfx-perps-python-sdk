from gfx_perps_sdk import (Perp, Product, Trader)
from solana.rpc.api import Client
from solana.keypair import Keypair
rpc_client = Client("https://explorer-api.devnet.solana.com/")
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
    r = await Prod.get_orderbook_L3()
    t = Trader(Perps) 
    t.init() 
    assert 1 == 0
