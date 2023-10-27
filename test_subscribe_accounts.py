from dataclasses import asdict
from typing import Dict, List
from solana.rpc.api import Client
from solders.keypair import Keypair
from gfx_perp_sdk.agnostic.EventQueue import FillEventInfo, OutEventInfo
from gfx_perp_sdk.product import Product
from gfx_perp_sdk.perp import Perp
from gfx_perp_sdk import utils
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import os
from datetime import datetime

from gfx_perp_sdk.trader import Trader

def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)


rpc_client = Client(
    "https://omniscient-frequent-wish.solana-devnet.quiknode.pro/8b6a255ef55a6dbe95332ebe4f6d1545eae4d128/")
keyp = Keypair.from_bytes(bytes([]))

def on_ask_change(added_asks, size_changes_at_price, added_users, removed_asks):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    folder_path = f'tests/events/{timestamp}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    folder_path = os.path.join(folder_path, 'on_ask_change')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    serializable_added_asks = [asdict(item) for item in added_asks]
    utils.write_json(serializable_added_asks,  f'{folder_path}/added_asks.json')
    serializable_size_changes_at_price = [asdict(item) for item in size_changes_at_price]
    utils.write_json(serializable_size_changes_at_price,  f'{folder_path}/ask_size_changes_at_price.json')
    serializable_added_users = [asdict(item) for item in added_users]
    utils.write_json(serializable_added_users,  f'{folder_path}/added_users.json')
    serializable_removed_asks = [asdict(item) for item in removed_asks]
    utils.write_json(serializable_removed_asks,  f'{folder_path}/removed_asks.json')

def on_bid_change(added_bids, size_changes_at_price, added_users, removed_bids):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    folder_path = f'tests/events/{timestamp}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    folder_path = os.path.join(folder_path, 'on_bid_change')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    serializable_added_bids = [asdict(item) for item in added_bids]
    utils.write_json(serializable_added_bids,  f'{folder_path}/added_bids.json')
    serializable_size_changes_at_price = [asdict(item) for item in size_changes_at_price]
    utils.write_json(serializable_size_changes_at_price,  f'{folder_path}/bid_size_changes_at_price.json')
    serializable_added_users = [asdict(item) for item in added_users]
    utils.write_json(serializable_added_users,  f'{folder_path}/added_users.json')
    serializable_removed_bids = [asdict(item) for item in removed_bids]
    utils.write_json(serializable_removed_bids,  f'{folder_path}/removed_bids.json')

def on_fills_change(added_fills: List[Dict], removed_fills: List[Dict], added_fills_total_baseSize, removed_fills_total_baseSize):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    folder_path = f'tests/events/{timestamp}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    folder_path = os.path.join(folder_path, 'on_fills_change')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    print("added_fills_total_baseSize:", added_fills_total_baseSize)
    print("removed_fills_total_baseSize:", removed_fills_total_baseSize)
    write_json(added_fills, f'{folder_path}/added_fills.json')
    write_json(added_fills, f'{folder_path}/removed_fills.json') 
    
def on_outs_change(added_outs: List[Dict], removed_outs: List[Dict] ):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    folder_path = f'tests/events/{timestamp}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    folder_path = os.path.join(folder_path, 'on_outs_change')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    write_json(added_outs, f'{folder_path}/added_outs.json')
    write_json(removed_outs, f'{folder_path}/removed_outs.json')
  
def on_trader_balance_change(old_token_balance: int, new_token_balance: int):
    print("Old Token Balance:", old_token_balance)
    print("New Token Balance:", new_token_balance)
    
executor = ThreadPoolExecutor()

async def main():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    folder_path = f'tests/events/{timestamp}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    orderbook = product.get_orderbook_L2()
    utils.write_json(orderbook, f'{folder_path}/orderbook.json')
    l3ob = product.get_orderbook_L3()
    serialized_l3ob = utils.serialize_l3ob_to_dict(l3ob) 
    utils.write_json(serialized_l3ob, f'{folder_path}/l3ob.json')
    t = Trader(perp)
    t.init()
    print("wallet address:", keyp.pubkey())
    
    open_orders = t.get_open_orders(product)
    serialize_open_orders = utils.serialize_open_orders_to_dict(open_orders)
    utils.write_json(serialize_open_orders, f'{folder_path}/open_orders_of_trader.json')
    
    task1 = asyncio.create_task(product.subscribe_to_bids(on_bid_change))
    task2 = asyncio.create_task(product.subscribe_to_asks(on_ask_change))
    task3 = asyncio.create_task(t.subscribe_trader_positions(product, on_fills_change, on_outs_change))
    task4 = asyncio.create_task(t.subscribe_to_token_balance_change(on_trader_balance_change))
    orderDetails = product.get_order_details_by_order_id(l3ob['asks'][0].orderId)
    print("orderDetails:", orderDetails)
    await task1
    await task2
    await task3
    await task4

if __name__ == "__main__":
    print("\nStarting script...")
    asyncio.run(main())
