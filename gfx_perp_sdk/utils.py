from solders.pubkey import Pubkey as PublicKey
from solders.signature import Signature
from solders.instruction import Instruction as TransactionInstruction
from solders.keypair import Keypair
from solana.transaction import Transaction
from solana.rpc import types
from solana.rpc.api import Client
from solana.rpc.types import MemcmpOpts
from solana.transaction import AccountMeta
from spl.token._layouts import ACCOUNT_LAYOUT
from gfx_perp_sdk.agnostic.EventQueue import FillEventInfo, OutEventInfo
from gfx_perp_sdk.agnostic.Slabs import OrderSide, Slab
from gfx_perp_sdk.constant_instructions.instructions import initialize_trader_acct_ix
import re
import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from podite import U64, Variant
from typing import List, Dict, Tuple, TypeVar, Union, NamedTuple, Optional
from copy import deepcopy
from gfx_perp_sdk.constants.perps_constants import MINT_DECIMALS, TOKEN_PROGRAM_ID
from gfx_perp_sdk.types.fractional import Fractional
from gfx_perp_sdk.types.market_product_group import MarketProductGroup
from gfx_perp_sdk.types.solana_pubkey import Solana_pubkey
from gfx_perp_sdk.types.trader_risk_group import TraderRiskGroup
from deepdiff import DeepDiff 
import time

@dataclass
class L3OrderbookInfo:
    """Class representing Level 3 Order Book Information."""
    size: float
    price: float
    user: str
    orderId: int
    orderSide: str
    callBackId: int

    def to_dict(self):
        return asdict(self)
    
    def to_json(self):
        return {
            'size': self.size,
            'price': self.price,
            'user': self.user,
            'orderId': self.orderId,
            'orderSide': self.orderSide,
            'callBackId': self.callBackId,
        }

@dataclass
class SlabOrderInfo:
    """Class representing Slab info received from Asks and Bids accounts."""
    size: int
    price: int
    user: PublicKey
    orderId: int
    orderSide: str
    callBackId: int

    def to_json(self):
        return {
            'size': self.size,
            'price': self.price,
            'user': self.user.__str__(),
            'orderId': self.orderId,
            'orderSide': self.orderSide,
            'callbackId': self.callBackId
        }

def get_market_signer(product: PublicKey, DEX_ID: PublicKey) -> PublicKey:
    addr = PublicKey.find_program_address([product.__bytes__()], DEX_ID)
    return addr[0]

def processOrderbook(bidsParam, asksParams, tickSize, decimals):
    result = {}
    result["bids"] = []
    if bidsParam is not None:
        for bids in bidsParam:
            result["bids"].append(
                {
                    'size': bids['size'] / (10 ** (decimals + 5)),
                    'price': (bids['price'] >> 32) / tickSize
                }
            )
    result["asks"] = []
    if asksParams is not None:
        for asks in asksParams:
            result["asks"].append(
                {
                    'size': asks['size'] / (10 ** (decimals + 5)),
                    'price': (asks['price'] >> 32) / tickSize
                }
            )
    return result

def processL3Ob(bidsParam: List[SlabOrderInfo], asksParams: List[SlabOrderInfo], tickSize: int, decimals: int):
    result: Dict[str, List[L3OrderbookInfo]] = {}
    result["bids"]: List[L3OrderbookInfo] = []
    if bidsParam is not None:
        for bids in bidsParam:
            result["bids"].append(
                L3OrderbookInfo(
                    size=bids.size / (10 ** (decimals + 5)),
                    price=(bids.price >> 32) / tickSize,
                    user=str(bids.user),
                    orderId=bids.orderId,
                    orderSide=bids.orderSide,
                    callBackId=bids.callBackId
                )
            )
    result["asks"]: List[L3OrderbookInfo] = []
    if asksParams is not None:
        for asks in asksParams:
            result["asks"].append(
                L3OrderbookInfo(
                    size=asks.size / (10 ** (decimals + 5)),
                    price=(asks.price >> 32) / tickSize,
                    user=str(asks.user),
                    orderId=asks.orderId,
                    orderSide=asks.orderSide,
                    callBackId=asks.callBackId
                )
            )
    return result

def process_deserialized_slab_data(bidDeserialized: Slab, askDeserialized: Slab):
    result: Dict[str, List[SlabOrderInfo]] = {}
    result["bids"]: List[SlabOrderInfo] = []
    if bidDeserialized is not None:
        for bids in bidDeserialized.items():
            price = bids[0].getPrice()
            size = bids[0].baseQuantity
            user = bids[1].userAccount
            callBackId = bids[1].callbackId
            orderId = bids[0].key
            result['bids'].append(
                SlabOrderInfo(
                    size=size,
                    price=price,
                    user=user,
                    orderId=orderId,
                    orderSide=OrderSide.BID.value,
                    callBackId=callBackId
                )
            )
    result["asks"]: List[SlabOrderInfo] = []
    if askDeserialized is not None:
        for asks in askDeserialized.items():
            price = asks[0].getPrice()
            size = asks[0].baseQuantity
            user = asks[1].userAccount
            callBackId = asks[1].callbackId
            orderId = asks[0].key
            result['asks'].append(
                SlabOrderInfo(
                    size=size,
                    price=price,
                    user=user,
                    orderId=orderId,
                    orderSide=OrderSide.ASK.value,
                    callBackId=callBackId
                )
            )
    return result
    
def getTraderRiskGroup(wallet: PublicKey, connection: Client, DEX_ID: PublicKey, MPG_ID: PublicKey):
    try:
        m1 = [MemcmpOpts(offset=16, bytes=MPG_ID.__bytes__())]
        m1.append(MemcmpOpts(offset=48, bytes=wallet.__bytes__()))
        res = connection.get_program_accounts(
            DEX_ID, commitment="confirmed", encoding="base64", filters=m1)
        result = res.value
        if len(result) == 0:
            return None
        pubkey_str = result[0].pubkey.__str__()
        return pubkey_str
    except:
        print("error in getting trg")
        return None
def getAllTraderRiskGroup(wallet: PublicKey, connection: Client, DEX_ID: PublicKey, MPG_ID: PublicKey):
    try:
        m1 = [MemcmpOpts(offset=16, bytes=MPG_ID.__bytes__())]
        m1.append(MemcmpOpts(offset=48, bytes=wallet.__bytes__()))
        res = connection.get_program_accounts(
            DEX_ID, commitment="confirmed", encoding="base64", filters=m1)
        result = res.value
        if len(result) == 0:
            return None
        pubkeys = [account.pubkey for account in result]
        return pubkeys
    except:
        print("error in getting trg")
        return None

def getUserAta(wallet: PublicKey, vault_mint: PublicKey):
    return PublicKey.find_program_address([
        wallet.__bytes__(),
        PublicKey.from_string(
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA").__bytes__(),
        vault_mint.__bytes__()],
        PublicKey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
    )[0]

def getMpgVault(
        VAULT_SEED: str,
        MPG_ID: PublicKey,
        DEX_ID: PublicKey):
    return PublicKey.find_program_address([bytes(VAULT_SEED, encoding="utf-8"), MPG_ID.__bytes__()], DEX_ID)[0]

def get_fee_model_configuration_addr(
        market_product_group_key: PublicKey,
        program_id: PublicKey,
) -> PublicKey:
    key, _ = PublicKey.find_program_address(
        seeds=[
            b"fee_model_config_acct",
            market_product_group_key.__bytes__(),
        ],
        program_id=program_id,
    )
    return key

def get_trader_fee_state_acct(
        trader_risk_group: PublicKey,
        market_product_group: PublicKey,
        program_id: PublicKey,
) -> PublicKey:
    key, _ = PublicKey.find_program_address(
        seeds=[
            b"trader_fee_acct",
            trader_risk_group.__bytes__(),
            market_product_group.__bytes__(),
        ],
        program_id=program_id,
    )
    return key

SYSTEM_PROGRAM = PublicKey.from_string("11111111111111111111111111111111")

def initialize_trader_fee_acct(
    payer: PublicKey,
    market_product_group: PublicKey,
    program_id: PublicKey,
    trader_risk_group: PublicKey,
    system_program: PublicKey,
    fee_model_config_acct: PublicKey,
):

    if fee_model_config_acct is None:
        fee_model_config_acct = get_fee_model_configuration_addr(
            market_product_group,
            program_id,
        )

    trader_fee_acct = get_trader_fee_state_acct(
        trader_risk_group,
        market_product_group,
        program_id,
    )

    # return Transaction(fee_payer=payer).add(

    return initialize_trader_acct_ix(
        payer=payer,
        fee_model_config_acct=fee_model_config_acct,
        trader_fee_acct=trader_fee_acct,
        market_product_group=market_product_group,
        trader_risk_group=trader_risk_group,
        system_program=system_program,
        program_id=program_id,
    )

def getRiskSigner(MPG_ID: PublicKey, DEX_ID: PublicKey):
    res = PublicKey.find_program_address([MPG_ID.__bytes__()], DEX_ID)
    return res[0]

def filterOpenOrders(l3ob: dict[str, List[L3OrderbookInfo]], trader: str):
    result: Dict[str, List[L3OrderbookInfo]] = {}
    result["bids"]: List[L3OrderbookInfo] = []
    result['asks']: List[L3OrderbookInfo] = []

    for bids in l3ob['bids']:
        if bids.user == trader:
            result["bids"].append(bids)

    for asks in l3ob['asks']:
        if asks.user == trader:
            result["asks"].append(asks)
    return result

def serialize_l3ob_to_dict(l3ob: dict[str, List[L3OrderbookInfo]]) -> dict:
    serialized_l3ob = {}
    for key, value in l3ob.items():
        serialized_l3ob[key] = [asdict(item) for item in value]
    return serialized_l3ob

def serialize_open_orders_to_dict(open_orders: dict[str, list[dict]]) -> dict:
    serialized_l3ob = {}
    for key, value in open_orders.items():
        serialized_list = []
        for item in value:
            # if isinstance(item, dict):
            serialized_list.append(item)
            # else:
            #     print(f"Skipping item of type {type(item)}, not a dictionary.")
        serialized_l3ob[key] = serialized_list
    return serialized_l3ob

def get_trader_from_trader_risk_group(connection: Client, trgKey: PublicKey):
    response = connection.get_account_info(
        pubkey=trgKey, commitment="processed", encoding="base64")
    if not response.value:
        raise KeyError("No Trader Risk Group account found for this trgKey.")
    r = response.value.data
    decoded = r[8:]
    trg = TraderRiskGroup.from_bytes(decoded)
    return trg.owner

def get_trader_risk_group(connection: Client, trgKey: PublicKey):
    response = connection.get_account_info(
        pubkey=trgKey, commitment="processed", encoding="base64")
    if not response.value:
        raise KeyError("No Trader Risk Group account found for this trgKey.")
    r = response.value.data
    decoded = r[8:]
    trg: TraderRiskGroup = TraderRiskGroup.from_bytes(decoded)
    return trg

def get_user_info_bid_ask(connection: Client, bid_ask: L3OrderbookInfo):
    userWalletPubkey = get_trader_risk_group(connection, PublicKey.from_string(bid_ask.user)).owner
    userWallet = PublicKey(Solana_pubkey.to_bytes(userWalletPubkey))
    userWallet = str(userWallet)
    return {
        'size': bid_ask.size, 
        'price': bid_ask.price, 
        'orderSide': bid_ask.orderSide, 
        'user': bid_ask.user, 
        'userWallet': userWallet
    }
        
def get_user_info_from_trader_risk_group(connection: Client, order_list: Dict[str, List[L3OrderbookInfo]], trgKey: PublicKey):
    orders_list_with_user = {'bids': [], 'asks': []}
    userWalletPubkey = get_trader_risk_group(connection, trgKey).owner
    for bid in order_list["bids"]:
        orders_list_with_user['bids'].append({
            'size': bid.size, 
            'price': bid.price, 
            'orderSide': bid.orderSide, 
            'user': bid.user, 
            'userWallet': userWalletPubkey
        })
    for ask in order_list["asks"]:
        orders_list_with_user['asks'].append({
            'size': ask.size, 
            'price': ask.price, 
            'orderSide': ask.orderSide, 
            'user': ask.user, 
            'userWallet': userWalletPubkey
        })
    return orders_list_with_user

def compare_trader_risk_groups(prevTrg: TraderRiskGroup, newtrg: TraderRiskGroup, change_param: str):
    differences = {}
    prev_trg_json = prevTrg.to_json()
    new_trg_json = newtrg.to_json()
    
    if change_param == 'active_products':
        try:
            old_active_products = set(tuple(sorted(d.items())) for d in prev_trg_json.get('active_products', []))
            new_active_products = set(tuple(sorted(d.items())) for d in new_trg_json.get('active_products', []))
        except Exception as e:
            print("Exception occurred:", e)
            return differences
        added_products = new_active_products - old_active_products
        removed_products = old_active_products - new_active_products
        if added_products or removed_products:
            differences['active_products_changes'] = {
                'added': list(added_products),
                'removed': list(removed_products)
            }
        return differences
    elif change_param == 'total_deposited' or change_param == 'total_withdrawn' or change_param == 'cash_balance':
        old_value = prev_trg_json.get(change_param, 0)
        new_value = new_trg_json.get(change_param, 0)
        if old_value != new_value:
            differences[change_param] = {'old': old_value, 'new': new_value}
        return differences
    elif change_param == 'trader_positions':
        old_positions = {pos['product_key']: pos for pos in prev_trg_json.get('trader_positions', [])}
        new_positions = {pos['product_key']: pos for pos in new_trg_json.get('trader_positions', [])}
        position_changes = {}
        for key, new_pos in new_positions.items():
            if key not in old_positions:
                position_changes[key] = {'added': new_pos}
            elif old_positions[key] != new_pos:
                position_changes[key] = {'changed': {'old': old_positions[key], 'new': new_pos}}
        for key in old_positions:
            if key not in new_positions:
                position_changes[key] = {'removed': old_positions[key]}
        if position_changes:
            differences['trader_positions'] = position_changes
        return differences
    elif change_param == 'open_orders':
        old_orders = set((order['id'] for order in prev_trg_json.get('open_orders', {}).get('orders', [])))
        new_orders = set((order['id'] for order in new_trg_json.get('open_orders', {}).get('orders', [])))
        added_orders = new_orders - old_orders
        if added_orders:
            differences['open_orders'] = {'added_orders': list(added_orders)}

        removed_orders = old_orders - new_orders
        if removed_orders:
            if 'open_orders' not in differences:
                differences['open_orders'] = {}
            differences['open_orders']['removed_orders'] = list(removed_orders)

        return differences
    
    return differences
def process_deepdiff(differences, prev_data, new_data, type: str):
    structured_diff = {
        "values_changed": [],
        # "items_added": [],
        # "items_removed": [],
        "iterable_item_added": [],
        "iterable_item_removed": [],
    }
    for change_type, changes in differences.items():
        for path, change in changes.items():
            if change_type == 'values_changed':
                if type == 'FILL_OUT':
                    path_parts = path.replace('root[', '').replace(']', '').split('[')
                    list_index = int(path_parts[0])
                    affected_field = path_parts[1].strip('\'\"')
                    prev_object = prev_data[list_index]
                    new_object = new_data[list_index]
                    if affected_field in ['makerOrderId', 'baseSizeConverted']:
                        structured_diff['values_changed'].append({
                            "list_index": list_index,
                            "old_value": change['old_value'],
                            "new_value": change['new_value'],
                            "affected_field": affected_field,
                            "prev_object": prev_object,
                            "new_object": new_object
                        })
                elif type == 'BID_ASK':
                    path_parts = path.replace('root[', '').replace(']', '').split('[')
                    list_index = int(path_parts[0])
                    affected_field = path_parts[1].strip('\'\"')
                    prev_object = prev_data[list_index]
                    new_object = new_data[list_index]
                    structured_diff['values_changed'].append({
                        "list_index": list_index,
                        "old_value": change['old_value'],
                        "new_value": change['new_value'],
                        "affected_field": affected_field,
                        "prev_object": prev_object,
                        "new_object": new_object
                    })
            # elif change_type == 'dictionary_item_added':
            #     structured_diff['items_added'].append(f"New item at {path}: {change}")
            # elif change_type == 'dictionary_item_removed':
            #     structured_diff['items_removed'].append(f"Removed item at {path}: {change}")
            elif change_type == 'iterable_item_added':
                path_parts = path.replace('root[', '').replace(']', '').split('[')
                list_index = int(path_parts[0])
                added_object = new_data[list_index]
                structured_diff['iterable_item_added'].append({
                    "list_index": list_index,
                    "added_object": added_object
                })
            elif change_type == 'iterable_item_removed':
                path_parts = path.replace('root[', '').replace(']', '').split('[')
                list_index = int(path_parts[0])
                structured_diff['iterable_item_removed'].append({
                    "list_index": list_index,
                    "removed_object": prev_data[list_index]
                })
    return structured_diff

def camel_to_snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

def snake_to_camel(name):
    def _upper(m):
        return m.group(0)[1].upper()

    return re.sub(r"(?P<start>_[a-z])", _upper, name)

def pascal_to_snake(name):
    return camel_to_snake(name[0].lower() + name[1:])

def snake_to_pascal(name):
    pascal = snake_to_camel(name)
    return pascal[0].upper() + pascal[1:]

def kebab_to_snake(name):
    return re.sub("-", "_", name)

def snake_to_kebab(name):
    return re.sub("_", "-", name)

def sighash(namespace: str, name: str) -> int:
    preimage = f"{namespace}:{name}".encode()
    hash_bytes = sha256(preimage).digest()

    return U64.from_bytes(hash_bytes[:8])

class AccountDiscriminant(Variant):
    def assign_value(self, cls, prev_value):
        self.value = sighash("account", snake_to_pascal(self.name.lower()))

class InstructionDiscriminant(Variant):
    def assign_value(self, cls, prev_value):
        self.value = sighash("global", self.name.lower())

def to_account_meta(
    account: Union[str, PublicKey],
    is_signer: bool,
    is_writable: bool,
) -> AccountMeta:
    if isinstance(account, str):
        account = PublicKey(account)

    return AccountMeta(account, is_signer=is_signer, is_writable=is_writable)

def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

T = TypeVar('T')  # Type variable to handle different event types generically

def convert_userAccount_to_string(events: List[T]) -> List[T]:
    """
    Convert the userAccount in CallbackInfo to its string representation.
    """
    converted_events = deepcopy(events)
    
    for event in converted_events:
        if hasattr(event, 'maker_callback_info'):
            event.maker_callback_info.userAccount = str(event.maker_callback_info.userAccount)
        if hasattr(event, 'taker_callback_info'):
            event.taker_callback_info.userAccount = str(event.taker_callback_info.userAccount)
        if hasattr(event, 'callback_info'):
            event.callback_info.userAccount = str(event.callback_info.userAccount)
    
    return converted_events

def calculate_bid_ask_changes(
    prevBidsAsks: List[L3OrderbookInfo],
    newBidsAsks: List[L3OrderbookInfo]
) -> Tuple[List[L3OrderbookInfo], List[L3OrderbookInfo], List[L3OrderbookInfo], List[L3OrderbookInfo]]:

    prev_bids_asks_json = [bid_ask.to_json() for bid_ask in prevBidsAsks]
    new_bids_asks_json = [bid_ask.to_json() for bid_ask in newBidsAsks]
    deep_differences_bids_asks = DeepDiff(prev_bids_asks_json, new_bids_asks_json, ignore_order=True)
    processed_deep_differences_bids_asks = process_deepdiff(deep_differences_bids_asks, prev_bids_asks_json, new_bids_asks_json, "BID_ASK")
    bid_ask_value_changes = processed_deep_differences_bids_asks["values_changed"]
    bid_ask_added = processed_deep_differences_bids_asks["iterable_item_added"]
    bid_ask_removed = processed_deep_differences_bids_asks["iterable_item_removed"]
    return bid_ask_value_changes, bid_ask_added, bid_ask_removed

def compare_slabs(a: L3OrderbookInfo,b: L3OrderbookInfo) -> bool:
    return (a.size == b.size and
            a.price == b.price and
            a.user == b.user and
            a.orderId == b.orderId and
            a.orderSide == b.orderSide)

def get_slab_changes(
        prev_slab_data: List[L3OrderbookInfo],
        current_slab_data: List[L3OrderbookInfo]
) -> List[L3OrderbookInfo]:
    new_slab_data: List[L3OrderbookInfo] = []

    for current_slab in current_slab_data:
        found = False
        for prev_slab in prev_slab_data:
            is_same = compare_slabs(current_slab, prev_slab)
            if is_same:
                found = True
                break

        if not found:
            new_slab_data.append(current_slab)

    return new_slab_data

def compare_events(a: FillEventInfo, b: FillEventInfo) -> bool:
    return (a.fill_event.baseSize == b.fill_event.baseSize and
            a.fill_event.quoteSize == b.fill_event.quoteSize and
            a.fill_event.makerOrderId == b.fill_event.makerOrderId and
            a.fill_event.takerSide == b.fill_event.takerSide and
            str(a.maker_callback_info) == str(b.maker_callback_info) and
            str(a.taker_callback_info) == str(b.taker_callback_info))

def calculate_fill_changes(
    prev_fill_events: List[FillEventInfo],
    current_fill_events: List[FillEventInfo],
) -> List[FillEventInfo]:
    new_fill_events: List[FillEventInfo] = []

    for current_fill_event in current_fill_events:
        found = False
        for prev_fill_event in prev_fill_events:
            is_same = compare_events(current_fill_event, prev_fill_event)
            if is_same:
                found = True
                break

        if not found:
            new_fill_events.append(current_fill_event)

    return new_fill_events 

def calculate_out_changes(
    prev_out_events: List[OutEventInfo],
    new_out_events: List[OutEventInfo],
    decimals: int,
    tick_size: int,
):
    prev_out_events_json = [event.to_json() for event in prev_out_events]
    new_out_events_json = [event.to_json() for event in new_out_events]

    for event in prev_out_events_json:
        event['price'] = ((event['orderId'] >> 64) >> 32) / tick_size
        event['baseSizeConverted'] = event['baseSize'] / (10 ** (decimals + 5))

    for event in new_out_events_json:
        event['price'] = ((event['orderId'] >> 64) >> 32) / tick_size
        event['baseSizeConverted'] = event['baseSize'] / (10 ** (decimals + 5))

    deep_differences_out = DeepDiff(prev_out_events_json, new_out_events_json, ignore_order=True)
    processed_deep_differences_out = process_deepdiff(deep_differences_out, prev_out_events_json, new_out_events_json, "FILL_OUT")
    out_value_changes = processed_deep_differences_out["values_changed"]
    out_added = processed_deep_differences_out["iterable_item_added"]
    out_removed = processed_deep_differences_out["iterable_item_removed"]

    return out_value_changes, out_added, out_removed

def trader_position_status(orders_list, current_market_price):
    net_position = 0.0
    avg_bid_price = 0.0
    avg_ask_price = 0.0

    total_bid_size = sum(order['size'] for order in orders_list.get('bids', []) if order['orderSide'].upper() == 'BID')
    total_ask_size = sum(order['size'] for order in orders_list.get('asks', []) if order['orderSide'].upper() == 'ASK')

    if total_bid_size > 0:
        avg_bid_price = sum(order['size'] * order['price'] for order in orders_list.get('bids', []) if order['orderSide'].upper() == 'BID') / total_bid_size

    if total_ask_size > 0:
        avg_ask_price = sum(order['size'] * order['price'] for order in orders_list.get('asks', []) if order['orderSide'].upper() == 'ASK') / total_ask_size

    net_position = total_bid_size - total_ask_size

    status = {
        'net_position': net_position,
        'avg_bid_price': avg_bid_price,
        'avg_ask_price': avg_ask_price,
        'current_market_price': current_market_price,
    }

    if net_position > 0:
        status['position_status'] = 'Net Long'
        if current_market_price < avg_bid_price:
            status['profit_status'] = 'Losing'
        else:
            status['profit_status'] = 'Winning'
    elif net_position < 0:
        status['position_status'] = 'Net Short'
        if current_market_price > avg_ask_price:
            status['profit_status'] = 'Losing'
        else:
            status['profit_status'] = 'Winning'
    else:
        status['position_status'] = 'Neutral'
        status['profit_status'] = 'Neutral'

    return status

class TokenAccountInfo(NamedTuple):
    """Information about an account."""

    mint: PublicKey
    """The mint associated with this account."""
    owner: PublicKey
    """Owner of this account."""
    amount: int
    """Amount of tokens this account holds."""
    delegate: Optional[PublicKey]
    """The delegate for this account."""
    delegated_amount: int
    """The amount of tokens the delegate authorized to the delegate."""
    is_initialized: bool
    """ Is this account initialized."""
    is_frozen: bool
    """Is this account frozen."""
    is_native: bool
    """Is this a native token account."""
    rent_exempt_reserve: Optional[int]
    """If this account is a native token, it must be rent-exempt.

    This value logs the rent-exempt reserve which must remain in the balance
    until the account is closed.
    """
    close_authority: Optional[PublicKey]
    """Optional authority to close the account."""

def create_token_account_info(bytes_data):
    if len(bytes_data) != ACCOUNT_LAYOUT.sizeof():
        raise ValueError("Invalid account size")

    decoded_data = ACCOUNT_LAYOUT.parse(bytes_data)

    mint = PublicKey(decoded_data.mint)
    owner = PublicKey(decoded_data.owner)
    amount = decoded_data.amount

    if decoded_data.delegate_option == 0:
        delegate = None
        delegated_amount = 0
    else:
        delegate = PublicKey(decoded_data.delegate)
        delegated_amount = decoded_data.delegated_amount

    is_initialized = decoded_data.state != 0
    is_frozen = decoded_data.state == 2

    if decoded_data.is_native_option == 1:
        rent_exempt_reserve = decoded_data.is_native
        is_native = True
    else:
        rent_exempt_reserve = None
        is_native = False

    close_authority = None if decoded_data.close_authority_option == 0 else PublicKey(decoded_data.owner)

    return TokenAccountInfo(
        mint,
        owner,
        amount,
        delegate,
        delegated_amount,
        is_initialized,
        is_frozen,
        is_native,
        rent_exempt_reserve,
        close_authority,
    )

def send_solana_transaction(rpc_client: Client, wallet: Keypair, ixs: [TransactionInstruction], signers):
    blockhash = rpc_client.get_latest_blockhash(commitment="finalized")
    transaction = Transaction(recent_blockhash=blockhash.value.blockhash,
                              fee_payer=wallet.pubkey())
    for ix in ixs:
        transaction.add(ix)
    # result = rpc_client.send_transaction(
    #     transaction, *signers, opts=types.TxOpts(skip_preflight=True))
    result = rpc_client.send_transaction(transaction, *signers, opts=types.TxOpts(
        skip_preflight=False, preflight_commitment="confirmed"))
    return result.value

def get_transaction_status(connection: Client, raw_sigs: List[Signature]):
    sig_status_mapping = {}
    for raw_sig in raw_sigs:
        raw_sig: str = raw_sig.__str__()
    time.sleep(2)
    sig_status = connection.get_signature_statuses(signatures=raw_sigs, search_transaction_history=False)

    for i, transaction_status in enumerate(sig_status.value):
        sig = raw_sigs[i]
        if transaction_status is None:
            error_message = "Unable to Get Signature Status"
            sig_status_mapping[sig.__str__()] = error_message
        elif transaction_status.err is not None:
            # Process error scenario
            error_message = f"Error: {transaction_status.err}"
            sig_status_mapping[sig.__str__()] = error_message
        else:
            # Process success scenario
            sig_status_mapping[sig.__str__()] = "Success"

    return sig_status_mapping