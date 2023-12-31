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
from gfx_perp_sdk.types.market_product_group import MarketProductGroup
from gfx_perp_sdk.types.trader_risk_group import TraderRiskGroup

rpc_client = Client(
    "https://omniscient-frequent-wish.solana-devnet.quiknode.pro/8b6a255ef55a6dbe95332ebe4f6d1545eae4d128/")
keyp = Keypair.from_bytes([])

def on_asks_change(ask_value_changes, ask_added, ask_removed):
    if len(ask_value_changes) > 0 or len(ask_added) > 0 or len(ask_removed) > 0:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path = f'tests/events/{timestamp}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.join(folder_path, 'on_asks_change')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if len(ask_value_changes) > 0:
            utils.write_json(ask_value_changes, f'{folder_path}/ask_value_changes.json')
        if len(ask_added) > 0:
            utils.write_json(ask_added, f'{folder_path}/ask_added.json')
        if len(ask_removed) > 0:
            utils.write_json(ask_removed, f'{folder_path}/ask_removed.json')

def on_bids_change(bid_value_changes, bid_added, bid_removed):
    if len(bid_value_changes) > 0 or len(bid_added) > 0 or len(bid_removed) > 0:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path = f'tests/events/{timestamp}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.join(folder_path, 'on_bids_change')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if len(bid_value_changes) > 0:
            utils.write_json(bid_value_changes, f'{folder_path}/bid_value_changes.json')
        if len(bid_added) > 0:
            utils.write_json(bid_added, f'{folder_path}/bid_added.json')
        if len(bid_removed) > 0:
            utils.write_json(bid_removed, f'{folder_path}/bid_removed.json')

def on_fills_change(fill_value_changes, fill_added, fill_removed):
    if len(fill_value_changes) > 0 or len(fill_added) > 0 or len(fill_removed) > 0:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path = f'tests/events/{timestamp}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.join(folder_path, 'on_fills_change')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if len(fill_value_changes) > 0:
            utils.write_json(fill_value_changes, f'{folder_path}/fill_value_changes.json')
        if len(fill_added) > 0:
            utils.write_json(fill_added, f'{folder_path}/fill_added.json')
        if len(fill_removed) > 0:
            utils.write_json(fill_removed, f'{folder_path}/fill_removed.json')

def on_outs_change(out_value_changes, out_added, out_removed):
    if len(out_value_changes) > 0 or len(out_added) > 0 or len(out_removed) > 0:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path = f'tests/events/{timestamp}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.join(folder_path, 'on_outs_change')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if len(out_value_changes) > 0:
            utils.write_json(out_value_changes, f'{folder_path}/out_value_changes.json')
        if len(out_added) > 0:
            utils.write_json(out_added, f'{folder_path}/out_added.json')
        if len(out_removed) > 0:
            utils.write_json(out_removed, f'{folder_path}/out_removed.json')
    
def on_trader_balance_change(old_token_balance: int, new_token_balance: int):
    print("Old Token Balance:", old_token_balance)
    print("New Token Balance:", new_token_balance)

def on_active_products_change(active_products_changes):
    if active_products_changes != {}:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path = f'tests/events/{timestamp}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.join(folder_path, 'on_active_products_change')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)    
        utils.write_json(active_products_changes, f'{folder_path}/active_products_changes.json')
    else:
        print("active_products_changes is None")

def on_total_deposited_change(total_deposited_changes):
    if total_deposited_changes != {}:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path = f'tests/events/{timestamp}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.join(folder_path, 'on_total_deposited_change')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        utils.write_json(total_deposited_changes, f'{folder_path}/total_deposited_changes.json')
    else:
        print("total_deposited_changes is None")

def on_total_withdrawn_change(total_withdrawn_changes):
    if total_withdrawn_changes != {}:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path = f'tests/events/{timestamp}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.join(folder_path, 'on_total_withdrawn_change')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        utils.write_json(total_withdrawn_changes, f'{folder_path}/total_withdrawn_changes.json')
    else:
        print("total_withdrawn_changes is None")

def on_cash_balance_change(cash_balance_changes):
    if cash_balance_changes != {}:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path = f'tests/events/{timestamp}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.join(folder_path, 'on_cash_balance_change')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        perp = Perp(rpc_client, 'devnet', keyp)
        perp.init()
        product = Product(perp)
        product.init_by_name('SOL-PERP')
        if 'cash_balance' in cash_balance_changes and 'old' in cash_balance_changes['cash_balance'] and 'new' in cash_balance_changes['cash_balance']:
            cash_balance_changes['cash_balance']['old'] /= 10**5
            cash_balance_changes['cash_balance']['new'] /= 10**5
            utils.write_json(cash_balance_changes, f'{folder_path}/cash_balance_changes.json')
    else:
        print("cash_balance_changes is None")

def on_trader_positions_change(trader_position_changes):
    if trader_position_changes != {}:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path = f'tests/events/{timestamp}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.join(folder_path, 'on_trader_positions_change')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        utils.write_json(trader_position_changes, f'{folder_path}/trader_position_changes.json')
    else:
        print("trader_position_changes is None")

def on_open_orders_change(open_orders_changes):
    if open_orders_changes != {}:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path = f'tests/events/{timestamp}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.join(folder_path, 'on_open_orders_change')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        utils.write_json(open_orders_changes, f'{folder_path}/open_orders_changes.json')
        perp = Perp(rpc_client, 'devnet', keyp)
        perp.init()
        product = Product(perp)
        product.init_by_name('SOL-PERP')
        if len(open_orders_changes["open_orders"]["added_orders"]) > 0:
            added_orders_info = []
            for order_id in open_orders_changes["open_orders"]["added_orders"]:
                order_info = product.get_order_details_by_order_id(int(order_id))
                order_info['order_id'] = order_id
                added_orders_info.append(order_info)
            utils.write_json(added_orders_info, f'{folder_path}/added_open_orders_info.json')
        if len(open_orders_changes["open_orders"]["removed_orders"]) > 0:
            removed_orders_info = []
            for order_id in open_orders_changes["open_orders"]["removed_orders"]:
                order_info = product.get_order_details_by_order_id(int(order_id))
                order_info['order_id'] = order_id
                removed_orders_info.append(order_info)
            utils.write_json(removed_orders_info, f'{folder_path}/removed_open_orders_info.json')
    else:
        print("open_orders_changes is None")

async def main():
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
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
    utils.write_json(open_orders, f'{folder_path}/open_orders_of_trader.json')
    prevTrg = t.fetch_trader_risk_group()
    utils.write_json(prevTrg.to_json(), f'{folder_path}/prev_trg.json')
    # utils.write_json(perp.marketProductGroup.to_json(), f'{folder_path}/prev_mpg.json')
    bids_sub = asyncio.create_task(product.subscribe_to_bids(on_bids_change))
    asks_sub = asyncio.create_task(product.subscribe_to_asks(on_asks_change))
    fills_sub = asyncio.create_task(t.subscribe_trader_positions(product, on_fills_change, "fills"))
    outs_sub = asyncio.create_task(t.subscribe_trader_positions(product, on_outs_change, "outs"))
    act_sub = asyncio.create_task(t.subscribe_to_trader_risk_group(on_active_products_change, "active_products"))
    deposit_sub = asyncio.create_task(t.subscribe_to_trader_risk_group(on_total_deposited_change, "total_deposited"))
    withdraw_sub = asyncio.create_task(t.subscribe_to_trader_risk_group(on_total_withdrawn_change, "total_withdrawn"))
    cash_bal_sub = asyncio.create_task(t.subscribe_to_trader_risk_group(on_cash_balance_change, "cash_balance"))
    positions_sub = asyncio.create_task(t.subscribe_to_trader_risk_group(on_trader_positions_change, "trader_positions"))
    open_orders_sub = asyncio.create_task(t.subscribe_to_trader_risk_group(on_open_orders_change, "open_orders"))
    # token_bal_sub = asyncio.create_task(t.subscribe_to_token_balance_change(on_trader_balance_change))
    # orderDetails = product.get_order_details_by_order_id(l3ob['asks'][0].orderId)
    # print("orderDetails:", orderDetails)
    print("starting tasks...")
    await bids_sub
    await asks_sub
    await fills_sub
    await outs_sub
    await act_sub
    await deposit_sub
    await withdraw_sub
    await cash_bal_sub
    await positions_sub
    await open_orders_sub

if __name__ == "__main__":
    print("\nStarting script...")
    asyncio.run(main())
