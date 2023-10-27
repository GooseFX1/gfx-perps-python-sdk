from solders.pubkey import Pubkey as PublicKey
from solana.rpc.api import Client
from solana.rpc.types import MemcmpOpts
from solana.transaction import AccountMeta
from spl.token._layouts import ACCOUNT_LAYOUT
from gfx_perp_sdk.agnostic.EventQueue import CallbackInfo, FillEventInfo, OutEvent, OutEventInfo
from gfx_perp_sdk.agnostic.Slabs import OrderSide, Slab
from gfx_perp_sdk.constant_instructions.instructions import initialize_trader_acct_ix
import podite
import re
import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from podite import U64
from typing import List, Dict, Tuple, TypeVar, Union, NamedTuple, Optional
from copy import deepcopy
from gfx_perp_sdk.constants.perps_constants import MINT_DECIMALS, TOKEN_PROGRAM_ID
from gfx_perp_sdk.types.fractional import Fractional
from gfx_perp_sdk.types.solana_pubkey import Solana_pubkey

from gfx_perp_sdk.types.trader_risk_group import TraderRiskGroup

@dataclass
class L3OrderbookInfo:
    """Class representing Level 3 Order Book Information."""
    size: float
    price: float
    user: str
    orderId: int
    orderSide: str

    def to_dict(self):
        return asdict(self)
@dataclass
class SlabOrderInfo:
    """Class representing Slab info received from Asks and Bids accounts."""
    price: int
    size: int
    user: PublicKey
    orderId: int
    OrderSide: str

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
                    size=bids['size'] / (10 ** (decimals + 5)),
                    price=(bids['price'] >> 32) / tickSize,
                    user=str(bids['user']),
                    orderId=bids['orderId'],
                    orderSide=bids['orderSide']
                )
            )
    result["asks"]: List[L3OrderbookInfo] = []
    if asksParams is not None:
        for asks in asksParams:
            result["asks"].append(
                L3OrderbookInfo(
                    size=asks['size'] / (10 ** (decimals + 5)),
                    price=(asks['price'] >> 32) / tickSize,
                    user=str(asks['user']),
                    orderId=asks['orderId'],
                    orderSide=asks['orderSide']
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
            user = PublicKey(bids[1][0:32])
            orderId = bids[0].key
            result['bids'].append({
                "price": price,
                "size": size,
                "user": user,
                "orderId": orderId,
                "orderSide": OrderSide.BID.value
            })
    result["asks"]: List[SlabOrderInfo] = []
    if askDeserialized is not None:
        for asks in askDeserialized.items():
            price = asks[0].getPrice()
            size = asks[0].baseQuantity
            user = PublicKey(asks[1][0:32])
            orderId = asks[0].key
            result['asks'].append({
                "price": price,
                "size": size,
                "user": user,
                "orderId": orderId,
                "orderSide": OrderSide.ASK.value
            })
    return result
    
def getTraderRiskGroup(wallet: PublicKey, connection: Client, DEX_ID: PublicKey, MPG_ID: PublicKey):
    try:
        m1 = [MemcmpOpts(offset=48, bytes=wallet.__str__())]
        m1.append(MemcmpOpts(offset=16, bytes=MPG_ID.__str__()))
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

def get_user_info_bid_ask(connection: Client, bid_ask: L3OrderbookInfo):
    userWalletPubkey = get_trader_from_trader_risk_group(connection, PublicKey.from_string(bid_ask.user)) 
    userWallet = PublicKey(Solana_pubkey.to_bytes(userWalletPubkey))
    userWallet = str(userWallet)
    return {
        'size': bid_ask.size, 
        'price': bid_ask.price, 
        'orderSide': bid_ask.orderSide, 
        'user': bid_ask.user, 
        'userWallet': userWallet
    }
        
def get_user_info_from_trader_risk_group(connection: Client, order_list: Dict[str, List[L3OrderbookInfo]]):
    orders_list_with_user = {'bids': [], 'asks': []}
    for bid in order_list["bids"]:
        bid_with_user_info = get_user_info_bid_ask(connection, bid)
        orders_list_with_user['bids'].append(bid_with_user_info)
    for ask in order_list["asks"]:
        ask_with_user_info = get_user_info_bid_ask(connection, ask)
        orders_list_with_user['asks'].append(ask_with_user_info)
    return orders_list_with_user

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

class AccountDiscriminant(podite.Variant):
    def assign_value(self, cls, prev_value):
        self.value = sighash("account", snake_to_pascal(self.name.lower()))

class InstructionDiscriminant(podite.Variant):
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
    prevBidAsks: List[L3OrderbookInfo],
    newBidAsks: List[L3OrderbookInfo]
) -> Tuple[List[L3OrderbookInfo], List[L3OrderbookInfo], List[L3OrderbookInfo], List[L3OrderbookInfo]]:

    added_bid_asks = []
    size_changes_at_price = []
    added_users = []
    removed_bid_asks = []

    prev_bid_ask_dict = {(d.price, d.user): d for d in prevBidAsks}
    new_bid_ask_dict = {(d.price, d.user): d for d in newBidAsks}

    # Identify added bid_asks (new prices and users)
    for (price, user), new_order in new_bid_ask_dict.items():
        prev_order = prev_bid_ask_dict.get((price, user))
        
        if prev_order is None:
            added_bid_asks.append(new_order)
            
            # Check if the user is entirely new
            if not any(user == prev.user for prev in prevBidAsks):
                added_users.append(new_order)
        
        else:
            # Check for size changes
            size_change = new_order.size - prev_order.size
            if size_change != 0:
                size_changes_at_price.append(L3OrderbookInfo(
                    size=size_change,
                    price=price,
                    user=new_order.user,
                    orderId=new_order.orderId,
                    orderSide=new_order.orderSide
                ))
    
    # Identify removed bid_asks
    for (price, user), prev_order in prev_bid_ask_dict.items():
        if (price, user) not in new_bid_ask_dict:
            removed_bid_asks.append(prev_order)
            
    return added_bid_asks, size_changes_at_price, added_users, removed_bid_asks

def calculate_fill_changes(prev_fill_events: List[FillEventInfo], new_fill_events: List[FillEventInfo], decimals: int) -> Tuple[List[Dict], List[Dict]]:
     # Convert each FillEventInfo to a tuple of its FillEvent attributes for comparison
    prev_event_dicts = {tuple(asdict(event.fill_event).values()): event for event in prev_fill_events}
    new_event_dicts = {tuple(asdict(event.fill_event).values()): event for event in new_fill_events}

    # Determine added and removed fills based on changes in FillEvent variables
    added_fills = [event for key, event in new_event_dicts.items() if key not in prev_event_dicts]
    removed_fills = [event for key, event in prev_event_dicts.items() if key not in new_event_dicts]
    
    added_fills_total_baseSize = sum([event.fill_event.baseSize for event in added_fills])
    removed_fills_total_baseSize = sum([event.fill_event.baseSize for event in removed_fills])
    
    added_fills = [
        {
            'makerOrderId': event.fill_event.makerOrderId,
            'quoteSize': event.fill_event.quoteSize,
            'baseSize': event.fill_event.baseSize,
            'makerUserAccount': str(event.maker_callback_info.userAccount),
            'takerUserAccount': str(event.taker_callback_info.userAccount)
        }
        for event in added_fills
    ]
    removed_fills = [
        {
            'makerOrderId': event.fill_event.makerOrderId,
            'quoteSize': event.fill_event.quoteSize,
            'baseSize': event.fill_event.baseSize,
            'makerUserAccount': str(event.maker_callback_info.userAccount),
            'takerUserAccount': str(event.taker_callback_info.userAccount)
        }
        for event in removed_fills
    ]
    return added_fills, removed_fills, added_fills_total_baseSize, removed_fills_total_baseSize

def calculate_out_changes(prev_out_events: List[OutEventInfo], new_out_events: List[OutEventInfo], decimals: int) -> Tuple[List[Dict], List[Dict]]:
    # Convert each OutEventInfo to a tuple of its OutEvent attributes for comparison
    prev_event_dicts = {tuple(asdict(event.out_event).values()): event for event in prev_out_events}
    new_event_dicts = {tuple(asdict(event.out_event).values()): event for event in new_out_events}
    
    # Determine added and removed outs based on changes in OutEvent variables
    added_outs = [event for key, event in new_event_dicts.items() if key not in prev_event_dicts]
    removed_outs = [event for key, event in prev_event_dicts.items() if key not in new_event_dicts]
    
    added_outs = [
        {
            'orderId': event.out_event.orderId,
            'baseSize': event.out_event.baseSize,
            'makerUserAccount': str(event.callback_info.userAccount)
        }
        for event in added_outs
    ]

    removed_outs = [
        {
            'orderId': event.out_event.orderId,
            'baseSize': event.out_event.baseSize,
            'makerUserAccount': str(event.callback_info.userAccount)
        }
        for event in removed_outs
    ]
    return added_outs, removed_outs
 
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