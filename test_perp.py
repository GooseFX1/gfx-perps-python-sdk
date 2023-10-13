import pytest
from gfx_perp_sdk import (Perp, Product, Trader)
from gfx_perp_sdk.types import Fractional
from solana.rpc.api import Client
from solana.rpc import types
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.instruction import Instruction as TransactionInstruction

rpc_client = Client(
    "https://omniscient-frequent-wish.solana-devnet.quiknode.pro/8b6a255ef55a6dbe95332ebe4f6d1545eae4d128/")
# Insert your Keypair to test it locally
keyp = Keypair.from_bytes([])

pytest_plugins = ('pytest_asyncio',)


def send_solana_transaction(wallet: Keypair, ixs: [TransactionInstruction], signers):
    blockhash = rpc_client.get_latest_blockhash(commitment="finalized")
    transaction = Transaction(recent_blockhash=blockhash.value.blockhash,
                              fee_payer=wallet.pubkey())
    for ix in ixs:
        transaction.add(ix)
    result = rpc_client.send_transaction(
        transaction, *signers, opts=types.TxOpts(skip_preflight=True))
    return result.value


@pytest.mark.asyncio
async def test_perp_init():
    perp = Perp(rpc_client, 'devnet', keyp)
    assert perp.wallet != None
    assert perp.connection != None
    assert perp.networkType != None

    perp.init()
    assert perp.marketProductGroup != None

@pytest.mark.asyncio
async def test_product_init():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    assert product.PRODUCT_ID != None

@pytest.mark.asyncio
async def test_product_orderbooks():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    orderbook = product.get_orderbook_L2()
    assert len(orderbook['bids']) != 0
    assert len(orderbook['asks']) != 0

    orderbookL3 = product.get_orderbook_L3()
    assert len(orderbookL3['bids']) != 0
    assert len(orderbookL3['asks']) != 0

@pytest.mark.asyncio
async def test_product_trades():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    trades = product.get_trades()
    assert len(trades) > 0


@pytest.mark.asyncio
async def test_trader_init():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    t = Trader(perp)
    t.init()
    assert t.traderRiskGroup != None
    assert t.userTokenAccount != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_create_trader_risk():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    t = Trader(perp)
    ix = t.create_trader_account_ixs()
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response != None


@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_deposit_funds():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    t = Trader(perp) 
    t.init()
    ix = t.deposit_funds_ix(Fractional.to_decimal(100))
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response['result'] != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_withdraw_funds():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    t = Trader(perp) 
    t.init()
    ix = t.withdraw_funds_ix(Fractional.to_decimal(100))
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response['result'] != None

@pytest.mark.asyncio
async def test_trader_open_orders():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    orders = t.get_open_orders(product)
    print(orders)
    assert orders['bids'] != None
    assert orders['asks'] != None


@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_new_order_single():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix = t.new_order_ix(product, Fractional.to_decimal(50000), Fractional.to_decimal(35), 'ask', 'limit')
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response['result'] != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_new_order_multiple():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix1 = t.new_order_ix(product, Fractional.to_decimal(50000), Fractional.to_decimal(34), 'ask', 'limit')
    ix2 = t.new_order_ix(product, Fractional.to_decimal(50000), Fractional.to_decimal(36), 'ask', 'limit')
    response = send_solana_transaction(keyp, ix1[0] + ix2[0], ix1[1])
    print(response)
    assert response['result'] != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_cancel_order_single():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix1 = t.cancel_order_ix(product, 269375752548498747818049433352371) # Get this order id from t.get_open_orders()
    response = send_solana_transaction(keyp, ix1[0], ix1[1])
    print(response)
    assert response != None


@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_cancel_order_multiple():
    perp = Perp(rpc_client, 'devnet',keyp)
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


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_subscribe_to_bids():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    t = Trader(perp)
    t.init()
    ix1 = t.new_order_ix(product, Fractional.to_decimal(
        100000), Fractional.to_decimal(21.6), 'bid', 'limit')
    ix2 = t.new_order_ix(product, Fractional.to_decimal(
        10000), Fractional.to_decimal(0.34), 'ask', 'limit')
    response = send_solana_transaction(keyp, ix1[0] + ix2[0], ix1[1])
    print("response: \n", response)
    assert response != None
    orderbook = product.get_orderbook_L2()
    assert len(orderbook['bids']) != 0
    assert len(orderbook['asks']) != 0

    orderbookL3 = product.get_orderbook_L3()
    assert len(orderbookL3['bids']) != 0
    assert len(orderbookL3['asks']) != 0
