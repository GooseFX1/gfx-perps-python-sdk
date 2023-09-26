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


def initialize_perp_product():
    perp = Perp(rpc_client, 'devnet', keyp)
    try:
        perp.init()
    except:
        print("Perp Already initialized")
    product = Product(perp)
    try:
        product.init_by_name('SOL-PERP')
    except:
        print("Product Already initialized")
    return perp, product


async def change_function(msg):
    print(f"Change detected: {msg}")


async def main():
    perp, product = initialize_perp_product()
    orderbook = product.get_orderbook_L2()
    print(orderbook)
    orderbookL3 = product.get_orderbook_L3()
    await product.subscribe_to_bids(change_function)

if __name__ == "__main__":
    print("Starting script...")
    asyncio.run(main())
