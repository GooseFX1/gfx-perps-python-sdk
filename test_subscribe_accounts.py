from solana.rpc.api import Client
from solders.keypair import Keypair
from gfx_perp_sdk.product import Product
from gfx_perp_sdk.perp import Perp
import asyncio
import json
import os


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)


rpc_client = Client(
    "https://omniscient-frequent-wish.solana-devnet.quiknode.pro/8b6a255ef55a6dbe95332ebe4f6d1545eae4d128/")
keyp = Keypair.from_bytes(bytes([]))

def on_ask_change(added_asks, size_changes):
    print("Added Asks:", added_asks)
    print("Size Changesin Asks:", size_changes)

def on_bid_change(added_bids, size_changes):
    print("Added Bids:", added_bids)
    print("Size Changes in Bids:", size_changes)

async def main():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    orderbook = product.get_orderbook_L2()
    print("\norderbook:", orderbook)
    await product.subscribe_to_bids(on_bid_change)
    
    # task1 = asyncio.create_task(product.subscribe_to_bids(on_bid_change))
    # task2 = asyncio.create_task(product.subscribe_to_asks(on_ask_change))

    # await task1
    # await task2

if __name__ == "__main__":
    print("\nStarting script...")
    asyncio.run(main())
