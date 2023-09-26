import json
import os
from gfx_perp_sdk import (Perp, Product, Trader)
from solana.rpc.api import Client
from solders.keypair import Keypair
from solana.rpc import types
from solana.transaction import Transaction
from solders.instruction import Instruction as TransactionInstruction
from solders.message import Message as TransactionMessage
from gfx_perp_sdk.types import Fractional

from gfx_perp_sdk.types.market_product_group import MarketProductGroup
from solders.pubkey import Pubkey as PublicKey

rpc_client = Client(
    "https://omniscient-frequent-wish.solana-devnet.quiknode.pro/8b6a255ef55a6dbe95332ebe4f6d1545eae4d128/")
keyp = Keypair.from_bytes([])

import asyncio
import pytest

pytest_plugins = ('pytest_asyncio',)


def market_product_group_to_dict(mpg: MarketProductGroup) -> dict:
    return {
        'tag': int(mpg.tag),  # Assuming U64 can be converted to int
        # Assuming FixedLenArray[U8, 16] can be converted to list of ints
        'name': bytes(mpg.name).rstrip(b'\x00').decode('utf-8'),
        # Assuming Solana_pubkey has a __str__ method
        'authority': str(PublicKey(mpg.authority.bytes)),
        # Assuming Solana_pubkey has a __str__ method
        'successor': str(PublicKey(mpg.successor.bytes)),
        # Assuming Solana_pubkey has a __str__ method
        'vault_mint': str(PublicKey(mpg.vault_mint.bytes)),
        # Assuming Fractional has a __str__ method
        'collected_fees': mpg.collected_fees.value,
        # Assuming Solana_pubkey has a __str__ method
        'fee_collector': str(PublicKey(mpg.fee_collector.bytes)),
        'decimals': int(mpg.decimals),  # Assuming U64 can be converted to int
        # Assuming Solana_pubkey has a __str__ method
        'risk_engine_program_id': str(PublicKey(mpg.risk_engine_program_id.bytes)),
        # Assuming Solana_pubkey has a __str__ method
        'fee_model_program_id': str(PublicKey(mpg.fee_model_program_id.bytes)),
        # Assuming Solana_pubkey has a __str__ method
        'fee_model_configuration_acct': str(PublicKey(mpg.fee_model_configuration_acct.bytes)),
        # Assuming Solana_pubkey has a __str__ method
        'risk_model_configuration_acct': str(PublicKey(mpg.risk_model_configuration_acct.bytes)),
        # Assuming Bitset has a __str__ method
        'active_flags_products': str(mpg.active_flags_products),
        # Assuming FixedLenArray[U64, 4] can be converted to list of ints
        'ewma_windows': [int(x) for x in mpg.ewma_windows],
        # Assuming FixedLenArray[U8, 143360] can be converted to list of ints
        'market_products': [int(x) for x in mpg.market_products],
        # Assuming U16 can be converted to int
        'vault_bump': int(mpg.vault_bump),
        # Assuming U16 can be converted to int
        'risk_and_fee_bump': int(mpg.risk_and_fee_bump),
        # Assuming U16 can be converted to int
        'find_fees_discriminant_len': int(mpg.find_fees_discriminant_len),
        # Assuming U16 can be converted to int
        'validate_account_discriminant_len': int(mpg.validate_account_discriminant_len),
        # Assuming FixedLenArray[U8, 8] can be converted to list of ints
        'find_fees_discriminant': [int(x) for x in mpg.find_fees_discriminant],
        # Assuming FixedLenArray[U8, 8] can be converted to list of ints
        'validate_account_health_discriminant': [int(x) for x in mpg.validate_account_health_discriminant],
        # Assuming FixedLenArray[U8, 8] can be converted to list of ints
        'validate_account_liquidation_discriminant': [int(x) for x in mpg.validate_account_liquidation_discriminant],
        # Assuming FixedLenArray[U8, 8] can be converted to list of ints
        'create_risk_state_account_discriminant': [int(x) for x in mpg.create_risk_state_account_discriminant],
        # Assuming I16 can be converted to int
        'max_maker_fee_bps': int(mpg.max_maker_fee_bps),
        # Assuming I16 can be converted to int
        'min_maker_fee_bps': int(mpg.min_maker_fee_bps),
        # Assuming I16 can be converted to int
        'max_taker_fee_bps': int(mpg.max_taker_fee_bps),
        # Assuming I16 can be converted to int
        'min_taker_fee_bps': int(mpg.min_taker_fee_bps),
        # Assuming Solana_pubkey has a __str__ method
        'fee_output_register': str(PublicKey(mpg.fee_output_register.bytes)),
        # Assuming Solana_pubkey has a __str__ method
        'risk_output_register': str(PublicKey(mpg.risk_output_register.bytes)),
        # Assuming U128 can be converted to str
        'sequence_number': str(mpg.sequence_number),
    }


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)


async def changeFn(self, msg):
    print(f"Change detected: {msg}")


def send_solana_transaction(wallet: Keypair, ixs: [TransactionInstruction], signers):
    blockhash = rpc_client.get_latest_blockhash(commitment="finalized")
    transaction = Transaction(recent_blockhash=blockhash.value.blockhash,
                              fee_payer=wallet.pubkey())
    for ix in ixs:
        transaction.add(ix)
    if len(signers) == 1:
        result = rpc_client.send_transaction(
            transaction, *signers, opts=types.TxOpts(skip_preflight=True))
    elif len(signers) == 3:
        result = rpc_client.send_transaction(
            transaction, *signers, opts=types.TxOpts(skip_preflight=True))

    return result.value


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_perp_init():
    perp = Perp(rpc_client, 'devnet', keyp)
    with open('tests/test_perp_init/perp_before_init.txt', 'w') as f:
        f.write(f"perp: {perp}\n")
        f.write(f"perp.wallet: {perp.wallet}\n")
        f.write(f"perp.connection: {perp.connection}\n")
        f.write(f"perp.networkType: {perp.networkType}\n")
    assert perp.wallet != None
    assert perp.connection != None
    assert perp.networkType != None
    perp.init()
    with open('tests/test_perp_init/perp_after_init.txt', 'w') as f:
        f.write(f"perp: {perp}\n")
        f.write(f"perp.wallet: {perp.wallet}\n")
        f.write(f"perp.connection: {perp.connection}\n")
        f.write(f"perp.networkType: {perp.networkType}\n")
        f.write(f"perp.mpgBytes: {perp.mpgBytes}\n")
        f.write(f"perp.marketProductGroup: {perp.marketProductGroup}\n")
    assert perp.marketProductGroup != None


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_product_init():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    with open('tests/test_product_init/perp_after_init.txt', 'w') as f:
        f.write(f"perp: {perp}\n")
        f.write(f"perp.wallet: {perp.wallet}\n")
        f.write(f"perp.connection: {perp.connection}\n")
        f.write(f"perp.networkType: {perp.networkType}\n")
        f.write(f"perp.mpgBytes: {perp.mpgBytes}\n")
        f.write(f"perp.marketProductGroup: {perp.marketProductGroup}\n")
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    with open('tests/test_product_init/product_after_init.txt', 'w') as f:
        f.write(f"product: {product}\n")
        f.write(f"product.wallet: {product.wallet}\n")
        f.write(f"product.connection: {product.connection}\n")
        f.write(f"product.networkType: {product.networkType}\n")
        # f.write(f"product.mpgBytes: {product.mpgBytes}\n")
        # f.write(f"product.marketProductGroup: {product.marketProductGroup}\n")
        f.write(f"product.name: {product.name}\n")
        f.write(f"product.PRODUCT_ID: {product.PRODUCT_ID}\n")
        f.write(f"product.ORDERBOOK_ID: {product.ORDERBOOK_ID}\n")
        f.write(f"product.BIDS: {product.BIDS}\n")
        f.write(f"product.ASKS: {product.ASKS}\n")
        f.write(f"product.EVENT_QUEUE: {product.EVENT_QUEUE}\n")
        f.write(f"product.marketSigner: {product.marketSigner}\n")
        f.write(f"product.tick_size: {product.tick_size}\n")
        f.write(f"product.decimals: {product.decimals}\n")
    assert product.PRODUCT_ID != None


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_product_orderbooks():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    with open('tests/test_product_orderbooks/product_after_init.txt', 'w') as f:
        f.write(f"product: {product}\n")
        f.write(f"product.wallet: {product.wallet}\n")
        f.write(f"product.connection: {product.connection}\n")
        f.write(f"product.networkType: {product.networkType}\n")
        # f.write(f"product.mpgBytes: {product.mpgBytes}\n")
        # f.write(f"product.marketProductGroup: {product.marketProductGroup}\n")
        f.write(f"product.name: {product.name}\n")
        f.write(f"product.PRODUCT_ID: {product.PRODUCT_ID}\n")
        f.write(f"product.ORDERBOOK_ID: {product.ORDERBOOK_ID}\n")
        f.write(f"product.BIDS: {product.BIDS}\n")
        f.write(f"product.ASKS: {product.ASKS}\n")
        f.write(f"product.EVENT_QUEUE: {product.EVENT_QUEUE}\n")
        f.write(f"product.marketSigner: {product.marketSigner}\n")
        f.write(f"product.tick_size: {product.tick_size}\n")
        f.write(f"product.decimals: {product.decimals}\n")
    mpg_dict = market_product_group_to_dict(product.marketProductGroup)
    write_json(mpg_dict, 'tests/test_product_orderbooks/marketProductGroup.json')
    orderbook = product.get_orderbook_L2()
    write_json(orderbook, 'tests/test_product_orderbooks/orderbook.json')
    assert len(orderbook['bids']) != 0
    assert len(orderbook['asks']) != 0

    orderbookL3 = product.get_orderbook_L3()
    for bid in orderbookL3['bids']:
        bid['user'] = str(bid['user'])
    for ask in orderbookL3['asks']:
        ask['user'] = str(ask['user'])
    write_json(orderbookL3, 'tests/test_product_orderbooks/orderbookL3.json')
    assert len(orderbookL3['bids']) != 0
    assert len(orderbookL3['asks']) != 0


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_product_trades():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    trades = product.get_trades()
    write_json(trades, 'tests/test_product_trades/trades.json')
    print("trades: ", trades)
    assert len(trades) > 0


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_init():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    with open('tests/test_trader_init/perp_after_init.txt', 'w') as f:
        f.write(f"perp: {perp}\n")
        f.write(f"perp.wallet: {perp.wallet}\n")
        f.write(f"perp.connection: {perp.connection}\n")
        f.write(f"perp.networkType: {perp.networkType}\n")

    t = Trader(perp)
    with open('tests/test_trader_init/trader_before_init.txt', 'w') as f:
        f.write(f"t: {t}\n")
        f.write(f"t.wallet: {t.wallet}\n")
        f.write(f"t.connection: {t.connection}\n")
        f.write(f"t.networkType: {t.networkType}\n")
        # f.write(f"t.marketProductGroup: {t.marketProductGroup}\n")
        # f.write(f"t.mpgBytes: {t.mpgBytes}\n")
    t.init()
    with open('tests/test_trader_init/trader_after_init.txt', 'w') as f:
        f.write(f"t: {t}\n")
        f.write(f"t.wallet: {t.wallet}\n")
        f.write(f"t.connection: {t.connection}\n")
        f.write(f"t.networkType: {t.networkType}\n")
        # f.write(f"t.marketProductGroup: {t.marketProductGroup}\n")
        # f.write(f"t.mpgBytes: {t.mpgBytes}\n")
        # f.write(f"t.traderRiskGroup: {t.traderRiskGroup}\n")
        # f.write(f"t.trgBytes: {t.trgBytes}\n")
        f.write(f"t.trgKey: {t.trgKey}\n")
        f.write(f"t.userTokenAccount: {t.userTokenAccount}\n")
        f.write(f"t.marketProductGroupVault: {t.marketProductGroupVault}\n")
        f.write(f"t.totalDeposited: {t.totalDeposited}\n")
        f.write(f"t.totalWithdrawn: {t.totalWithdrawn}\n")
        # f.write(f"t.marginAvailable: {t.marginAvailable}\n")
        f.write(f"t.traderPositions: {t.traderPositions}\n")
        f.write(f"t.totalTradedVolume: {t.totalTradedVolume}\n")
    assert t.traderRiskGroup != None
    assert t.userTokenAccount != None


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_create_trader_risk():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    with open('tests/test_create_trader_risk/perp_after_init.txt', 'w') as f:
        f.write(f"perp: {perp}\n")
        f.write(f"perp.wallet: {perp.wallet}\n")
        f.write(f"perp.connection: {perp.connection}\n")
        f.write(f"perp.networkType: {perp.networkType}\n")
        # f.write(f"t.marketProductGroup: {t.marketProductGroup}\n")
        # f.write(f"t.mpgBytes: {t.mpgBytes}\n")

    t = Trader(perp)
    with open('tests/test_create_trader_risk/trader_before_create_trader_account_ixs.txt', 'w') as f:
        f.write(f"t: {t}\n")
        f.write(f"t.wallet: {t.wallet}\n")
        f.write(f"t.connection: {t.connection}\n")
        f.write(f"t.networkType: {t.networkType}\n")
        f.write(f"t.marketProductGroup: {t.marketProductGroup}\n")
        f.write(f"t.mpgBytes: {t.mpgBytes}\n")
    ix = t.create_trader_account_ixs()
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response != None
    

# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_deposit_funds():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    t = Trader(perp)
    t.init()
    ix = t.deposit_funds_ix(Fractional.to_decimal(100))
    response = send_solana_transaction(keyp, ix[0], ix[1])
    with open('tests/test_trader_deposit_funds/trader_after_deposit_funds.txt', 'w') as f:
        f.write(f"t.wallet: {t.wallet}\n")
        f.write(f"t.connection: {t.connection}\n")
        f.write(f"t.networkType: {t.networkType}\n")
        f.write(f"t.trgKey: {t.trgKey}\n")
        f.write(f"t.userTokenAccount: {t.userTokenAccount}\n")
        f.write(f"t.marketProductGroupVault: {t.marketProductGroupVault}\n")
        f.write(f"t.totalDeposited: {t.totalDeposited}\n")
        f.write(f"t.totalWithdrawn: {t.totalWithdrawn}\n")
        # f.write(f"t.marginAvailable: {t.marginAvailable}\n")
        f.write(f"t.traderPositions: {t.traderPositions}\n")
        f.write(f"t.totalTradedVolume: {t.totalTradedVolume}\n")
        f.write(f"response: {response}\n")
    print(response)
    assert response != None


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_withdraw_funds():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    t = Trader(perp)
    t.init()
    ix = t.withdraw_funds_ix(Fractional.to_decimal(100))
    response = send_solana_transaction(keyp, ix[0], ix[1])
    with open('tests/test_trader_withdraw_funds/trader_after_withdraw_funds.txt', 'w') as f:
        f.write(f"t.wallet: {t.wallet}\n")
        f.write(f"t.connection: {t.connection}\n")
        f.write(f"t.networkType: {t.networkType}\n")
        f.write(f"t.trgKey: {t.trgKey}\n")
        f.write(f"t.userTokenAccount: {t.userTokenAccount}\n")
        f.write(f"t.marketProductGroupVault: {t.marketProductGroupVault}\n")
        f.write(f"t.totalDeposited: {t.totalDeposited}\n")
        f.write(f"t.totalWithdrawn: {t.totalWithdrawn}\n")
        # f.write(f"t.marginAvailable: {t.marginAvailable}\n")
        f.write(f"t.traderPositions: {t.traderPositions}\n")
        f.write(f"t.totalTradedVolume: {t.totalTradedVolume}\n")
        f.write(f"response: {response}\n")
    print(response)
    assert response != None

# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_open_orders():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp)
    t.init()
    orders = t.get_open_orders(product)
    print(orders)
    write_json(orders, 'tests/test_trader_open_orders/trader_open_orders.json')
    assert orders['bids'] != None
    assert orders['asks'] != None


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_new_order_single():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp)
    t.init()
    ix = t.new_order_ix(product, Fractional.to_decimal(
        100000), Fractional.to_decimal(18), 'bid', 'limit')
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response != None

# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_new_order_multiple():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp)
    t.init()
    ix1 = t.new_order_ix(product, Fractional.to_decimal(
        100000), Fractional.to_decimal(18), 'bid', 'limit')
    ix2 = t.new_order_ix(product, Fractional.to_decimal(
        40000), Fractional.to_decimal(32), 'ask', 'limit')
    response = send_solana_transaction(keyp, ix1[0] + ix2[0], ix1[1])
    print(response)
    assert response != None


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_cancel_order_single():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp)
    t.init()
    ix1 = t.cancel_order_ix(product, 269375752548498747818049433352371)
    response = send_solana_transaction(keyp, ix1[0], ix1[1])
    print(response)
    assert response != None

# @pytest.mark.asyncio


@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_cancel_order_multiple():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp)
    t.init()
    ix1 = t.cancel_order_ix(product, 277298568799925181577403828385709)
    ix2 = t.cancel_order_ix(product, 285221385051351615336758223419572)
    response = send_solana_transaction(keyp, ix1[0] + ix2[0], ix1[1])
    print(response)
    assert response != None

@pytest.mark.asyncio
# @pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_subscribe_to_bids():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    t = Trader(perp)
    t.init()
    ix1 = t.new_order_ix(product, Fractional.to_decimal(
        100000), Fractional.to_decimal(42), 'bid', 'limit')
    ix2 = t.new_order_ix(product, Fractional.to_decimal(
        40000), Fractional.to_decimal(0.69), 'ask', 'limit')
    response = send_solana_transaction(keyp, ix1[0] + ix2[0], ix1[1])
    print("response: \n", response)
    print()
    assert response != None
    orderbook = product.get_orderbook_L2()
    write_json(orderbook, 'tests/test_subscribe_to_bids/orderbook.json')
    assert len(orderbook['bids']) != 0
    assert len(orderbook['asks']) != 0

    orderbookL3 = product.get_orderbook_L3()
    for bid in orderbookL3['bids']:
        bid['user'] = str(bid['user'])
    for ask in orderbookL3['asks']:
        ask['user'] = str(ask['user'])
    write_json(orderbookL3, 'tests/test_subscribe_to_bids/orderbookL3.json')
    assert len(orderbookL3['bids']) != 0
    assert len(orderbookL3['asks']) != 0
