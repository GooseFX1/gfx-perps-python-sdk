import asyncio
import pytest
from gfx_perp_sdk import (Perp, Product, Trader, utils)
from gfx_perp_sdk.types import Fractional, base
from solana.rpc.api import Client
from solana.rpc import types
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
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

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
async def test_perp_init():
    perp = Perp(rpc_client, 'devnet', keyp)
    assert perp.wallet != None
    assert perp.connection != None
    assert perp.networkType != None

    perp.init()
    assert perp.marketProductGroup != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
async def test_product_init():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    assert product.PRODUCT_ID != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
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

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
async def test_product_trades():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    trades = product.get_trades()
    assert len(trades) > 0

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
async def test_trader_init():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    t = Trader(perp)
    t.init()
    assert t.traderRiskGroup != None
    assert t.userTokenAccount != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
async def test_create_trader_risk():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    t = Trader(perp)
    ix = t.create_trader_account_ixs()
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print("\n response:", response)
    status = utils.get_transaction_status([response])
    
    assert response != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
async def test_trader_deposit_funds():
    perp = Perp(rpc_client, 'mainnet',keyp)
    perp.init()
    t = Trader(perp) 
    t.init()
    ix = t.deposit_funds_ix(Fractional.to_decimal(100))
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print("\n response:", response)
    status = utils.get_transaction_status(connection=rpc_client, raw_sigs=[response])
    print("\n status:", status)
    assert response != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
async def test_trader_withdraw_funds():
    perp = Perp(rpc_client, 'mainnet',keyp)
    perp.init()
    t = Trader(perp) 
    t.init()
    ix = t.withdraw_funds_ix(Fractional.to_decimal(100))
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print(response)
    assert response != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
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
# @pytest.mark.asyncio
async def test_trader_new_order_single():
    perp = Perp(rpc_client, 'mainnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix = t.new_order_ix(
        product, 
        Fractional.to_decimal(1000), 
        Fractional.to_decimal(35),
        'ask', 
        'limit'
        )
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print()
    status = utils.get_transaction_status(connection=rpc_client, raw_sigs=[response])
    print("\n status:", status)
    assert response != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
async def test_trader_new_order_single_with_callback_id():
    perp = Perp(rpc_client, 'mainnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix = t.new_order_ix(
        product, 
        Fractional.to_decimal(1000), 
        Fractional.to_decimal(35), 
        'bid', 
        'limit',
        base.SelfTradeBehavior.ABORT_TRANSACTION,
        324567
        )
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print()
    status = utils.get_transaction_status(connection=rpc_client, raw_sigs=[response])
    print("\n status:", status)
    assert response != None

@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
# @pytest.mark.asyncio
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
    assert response != None

# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_cancel_order_single():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix1 = t.cancel_order_ix(product, 213123757163389514870706933277370) # Get this order id from t.get_open_orders()
    response = send_solana_transaction(keyp, ix1[0], ix1[1])
    print(response)
    assert response != None


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_trader_cancel_order_multiple():
    perp = Perp(rpc_client, 'devnet',keyp)
    perp.init()
    product = Product(perp)
    product.init_by_index(0)
    t = Trader(perp) 
    t.init()
    ix1 = t.cancel_order_ix(product, 213123757163389514870706933277368)
    ix2 = t.cancel_order_ix(product, 213123757163389514870706933277369)
    response = send_solana_transaction(keyp, ix1[0] + ix2[0], ix1[1])
    print(response)
    assert response != None


# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_multi_new_orders():
    perp = Perp(rpc_client, 'mainnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    t = Trader(perp)
    t.init()
    ix1 = t.new_order_ix(product, Fractional.to_decimal(
        13000), Fractional.to_decimal(140), 'bid', 'limit')
    ix3 = t.new_order_ix(product, Fractional.to_decimal(
        11000), Fractional.to_decimal(32.41), 'ask', 'limit')
    ix2 = t.new_order_ix(product, Fractional.to_decimal(
        12000), Fractional.to_decimal(32.46), 'ask', 'limit')
    # ix1 = t.new_order_ix(product, Fractional.to_decimal(
    #     10000), Fractional.to_decimal(32.4), 'ask', 'limit')
    # ix2 = t.new_order_ix(product, Fractional.to_decimal(
    #     210000), Fractional.to_decimal(32.44), 'ask', 'limit')
    response = send_solana_transaction(keyp, ix1[0] + ix2[0] + ix3[0], ix1[1])
    # response = send_solana_transaction(keyp,ix3[0], ix3[1])
    # response = send_solana_transaction(keyp, ix1[0], ix1[1])
    # response = send_solana_transaction(keyp, ix2[0], ix2[1])
    print("\n response: \n", response)
    assert response != None
    orderbook = product.get_orderbook_L2()
    assert len(orderbook['bids']) != 0
    # assert len(orderbook['asks']) != 0

    orderbookL3 = product.get_orderbook_L3()
    assert len(orderbookL3['bids']) != 0
    # assert len(orderbookL3['asks']) != 0

# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_get_order_details_():
    perp = Perp(rpc_client, 'devnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    result = product.get_order_details_by_order_id(297897891053633909351725255941436)
    print("\n result: \n", result)
    assert result != None

# @pytest.mark.asyncio
@pytest.mark.skip(reason="This test will send transactions to the Solana network.")
async def test_get_all_trg_accounts():
    perp = Perp(rpc_client, 'mainnet', keyp)
    perp.init()
    product = Product(perp)
    product.init_by_name('SOL-PERP')
    t = Trader(perp)
    t.init()
    print("t.trgKey: ", t.trgKey)
    # cash_balance = t.get_cash_balance()
    # print()
    # print(f"cash_balance of trgKey: {t.trgKey} is {cash_balance}")
    result = t.get_all_trg_accounts()
    # do a for loop for result
    print("result.len: ", len(result))
    for trgkey in result:
        cash_balance = t.get_cash_balance_for_trg(trgkey)
        # print cash balance along with the trg key
        print(f"cash_balance of trgKey: {trgkey} is {cash_balance}")
        trader_positions = t.get_trader_positions_for_trg(trgkey)
        for trader_position in trader_positions:
            if trader_position['quantity'] != 0:
                print(f"trader_positions of trgKey: {trgkey} is {trader_position}")
         
    print("pubkey: ", keyp.pubkey())
    # ix = t.close_trader_risk_group_ix_for_trg(Pubkey.from_string("G7faixeJJzy8gMtkjLYShvNHftG6ZouvHLRNXPqPy6Vs"))
    # ix = t.withdraw_funds_ix(Fractional.to_decimal(0.01))
    ix = t.withdraw_funds_ix_for_trg(Fractional.to_decimal(0.01), Pubkey.from_string("A8zk4qVLG5fyjGL3vovtcJXMwGwRb1JTP4f8LpPfy3ur"))
    response = send_solana_transaction(keyp, ix[0], ix[1])
    print()
    status = utils.get_transaction_status(connection=rpc_client, raw_sigs=[response])
    print("\n status:", status)
    
    assert result != None