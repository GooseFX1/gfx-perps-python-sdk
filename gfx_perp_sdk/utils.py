from dataclasses import asdict
import json
from solders.pubkey import Pubkey as PublicKey
from solana.rpc.api import Client
from solana.rpc.types import MemcmpOpts
from gfx_perp_sdk.agnostic.EventQueue import CallbackInfo, FillEvent, OutEvent
from gfx_perp_sdk.constant_instructions.instructions import initialize_trader_acct_ix
import podite
import re
from hashlib import sha256
from podite import U64
from typing import Union
from solana.transaction import AccountMeta
from typing import List, Dict, Tuple


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


def processL3Ob(bidsParam, asksParams, tickSize, decimals):
    result = {}
    result["bids"] = []
    if bidsParam is not None:
        for bids in bidsParam:
            result["bids"].append(
                {
                    'size': bids['size'] / (10 ** (decimals + 5)),
                    'price': (bids['price'] >> 32) / tickSize,
                    "user": bids['user'],
                    "orderId": bids['orderId']
                }
            )
    result["asks"] = []
    if asksParams is not None:
        for asks in asksParams:
            result["asks"].append(
                {
                    'size': asks['size'] / (10 ** (decimals + 5)),
                    'price': (asks['price'] >> 32) / tickSize,
                    "user": asks['user'],
                    "orderId": asks['orderId']
                }
            )
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


def filterOpenOrders(l3ob, trader: str):
    result = {}
    result["bids"] = []
    result['asks'] = []

    for bids in l3ob['bids']:
        if bids["user"] == trader:
            result["bids"].append({
                "price": bids["price"],
                "size": bids["size"],
                "orderId": bids["orderId"]
            })

    for asks in l3ob['asks']:
        if asks["user"] == trader:
            result["asks"].append({
                "price": asks["price"],
                "size": asks["size"],
                "orderId": asks["orderId"]
            })
    return result


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


def calculate_bid_ask_changes(
    prevBids: List[Dict[str, int]],
    newBids: List[Dict[str, int]]
) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]:

    added_bid_asks = []
    size_changes = []

    # Create dictionaries for easier lookup
    prev_bid_ask_dict = {d['price']: d['size'] for d in prevBids}
    new_bid_ask_dict = {d['price']: d['size'] for d in newBids}

    # Identify added bid_asks (new prices only)
    for price, size in new_bid_ask_dict.items():
        if price not in prev_bid_ask_dict:
            added_bid_asks.append({'price': price, 'size': size})

    # Identify size changes for existing prices
    for price, new_size in new_bid_ask_dict.items():
        prev_size = prev_bid_ask_dict.get(price)
        if prev_size is not None:
            size_change = new_size - prev_size
            if size_change != 0:
                size_changes.append(
                    {'price': price, 'size_change': size_change})

    return added_bid_asks, size_changes


def calculate_fill_changes(prev_fill_events: List[Tuple[FillEvent, CallbackInfo, CallbackInfo]],
                           new_fill_events: List[Tuple[FillEvent, CallbackInfo, CallbackInfo]]) -> Tuple[List[Tuple[FillEvent, CallbackInfo, CallbackInfo]], List[Tuple[FillEvent, CallbackInfo, CallbackInfo]]]:

    # Convert each FillEvent to a tuple of its attributes for easy comparison
    prev_event_dicts = {tuple(asdict(event_tuple[0]).values(
    )): event_tuple for event_tuple in prev_fill_events}
    new_event_dicts = {tuple(asdict(event_tuple[0]).values(
    )): event_tuple for event_tuple in new_fill_events}

    # Determine added fills based on any change in FillEvent variables
    added_fills = [event_tuple for event_key, event_tuple in new_event_dicts.items(
    ) if event_key not in prev_event_dicts]

    # Determine removed fills based on any change in FillEvent variables
    removed_fills = [event_tuple for event_key, event_tuple in prev_event_dicts.items(
    ) if event_key not in new_event_dicts]

    return added_fills, removed_fills


def calculate_out_changes(prev_out_events: List[OutEvent], new_out_events: List[OutEvent]) -> Tuple[List[OutEvent], List[OutEvent]]:

    prev_event_ids = {event.orderId for event in prev_out_events}
    new_event_ids = {event.orderId for event in new_out_events}

    added_outs = [
        event for event in new_out_events if event.orderId not in prev_event_ids]
    removed_outs = [
        event for event in prev_out_events if event.orderId not in new_event_ids]

    return added_outs, removed_outs
