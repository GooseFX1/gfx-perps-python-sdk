  <div align="center">
  <img height="142" src="https://media.goosefx.io/logos/GooseFX-light.png" />
  <h2>GooseFX Perpetual Futures SDK</h2>

  <h4>
    <a href="https://goosefx.io">Website</a>
    <span> | </span>
    <a href="https://docs.goosefx.io">Docs</a>
    <span> | </span>
    <a href="https://discord.com/channels/833693973687173121/833742620371058688">Discord</a>
    <span> | </span>
    <a href="https://www.t.me/goosefx">Telegram</a>
    <span> | </span>
    <a href="https://medium.com/goosefx">Medium</a>
  </h4>
  <br />
  <br />
</div>

# GooseFX Perpetual Futures SDK

This SDK contains 3 classes to interact with the GooseFX on-chain perpetual futures.

- `Perp`
- `Product`
- `Trader`

The `Perp` class is required to initialise the connection and wallet that is going to be used for subsequent interaction.
Initialising the `Perp` class should be the first step irrespective of the type of operation in the following manner:

```python
perp = Perp(rpc_client, 'devnet', wallet)
perp.init()
```

### Product

An instance of the `product` class signfies one of the perp product we offer to trade. Initialization of the `product` class can be done in one of two ways:

1. By index:

```python
perp = Perp(rpc_client, 'devnet', wallet)
perp.init()
product = Product(perp)
product.initByIndex(0)
```

2. By name:

```python
perp = Perp(rpc_client, 'devnet', wallet)
perp.init()
product = Product(perp)
product.initByName('SOL-PERP')
```

This `product` instance will be useful for the following functions:

- `GET L2 Orderbook`: Get the latest layer 2 orderbook

```python
orderbook = product.get_orderbook_L2()
```

- `GET L3 Orderbook`: Get the latest layer 3 orderbook. (Orders mapped to users)

```python
orderbook = product.get_orderbook_L3()
```

### Trader

The `Trader` class is required to get instructions to send transactions to the program. Each wallet must have a unique trader account initialized to be able to place orders and deposit funds. This account needs to be created once using the `create_trader_account_ixs` instruction. After it has been created once, for all subsequent interactions by the wallet, the `Trader` class needs to be initialized using the `init` function.

- To create a new `Trader` account on-chain:

```python
  perp = Perp(rpc_client, 'devnet', wallet)
  perp.init()
  trader = Trader(perp)
  [ixs, signers] = trader.create_trader_account_ixs()
```

where `ixs` is an array of required instructions and `signers` is an array of required walletairs for signature. The wallet must also sign the transaction along with the walletairs in the `signers` array

- Once the account is created successfully, the `Trader` instance must be initialised in the following way:

```python
  perp = Perp(rpc_client, 'devnet', wallet)
  perp.init()
  trader = Trader(perp)
  trader.init()
```

## Fractional Datatype

The Fractional data type uses a simple formula to represent a fractional number based on its mantissa (m) and exponent (exp):
`number = mantissa / (10 ^ exponent)`

## Trader Instructions

### Deposit Funds

To start placing new orders, traders need to deposit some collateral. This instruction will transfer the required USDC from the wallet to the trader account which will be used as collateral to place new orders.

The only parameter to this function is the amount of USDC to be depositted.

```python
  perp = Perp(rpc_client, 'devnet', wallet)
  perp.init()
  trader = Trader(perp)
  trader.init()
  [ix, signers] = trader.deposit_funds_ix(Fractional.to_decimal(100))
```

### Withdraw Funds

Similar to deposit funds, this function takes the amount of USDC to be withdrawn as the only parameter. This instruction will transfer funds from the trader account to the wallet address.

```python
  perp = Perp(rpc_client, 'devnet', wallet)
  perp.init()
  trader = Trader(perp)
  trader.init()
  [ix, signers] = await trader.withdraw_funds_ix(Fractional.to_decimal(100))
```

NOTE: The above two instructions do not need a `product` instance as a parameter since the market is cross collateralized and the amount of USDC deposited can be used across products. The following two instructions to place a new order and cancel an order are specific to products and hence need a `product` instance as one of the parameters.

### Trader's open orders for a prouct

To get all open orders for a `Trader` for a `product`:

```python
  perp = Perp(rpc_client, 'devnet', wallet)
  perp.init()
  product = Product(perp)
  product.initByIndex(0)
  trader = Trader(perp)
  trader.init()
  orderbookData = trader.getOpenOrders(product)
```

### New Order

The New order instruction needs the following as parameters

- Quantity (Fractional)
  **Please note: 1 unit of the product is denoted by 1 \* 100000 units. So to buy 1 unit, the parameter to pass as quantity should be**

```python
  Fractional.to_decimal(100000)
```

- Price (Fractional)
- Order side ('buy' or 'sell')
- Order Type ('limit', 'market', 'immediateOrCancel', 'postOnly')
- Product instance

```python
  perp = Perp(rpc_client, 'devnet',wallet)
  perp.init()
  product = Product(perp)
  product.initByIndex(0)
  trader = Trader(perp)
  trader.init()
  [ix, signers] = trader.new_order_ix(product, Fractional.to_decimal(50000), Fractional.to_decimal(35), Side.ASK, OrderType.Limit)
```

### Cancel Order

The cancel order instruction needs the orderId in string format to cancel the order. Use `getOpenOrders()` to get open orders and its id's to pass as a parameter to cancel the order

```python
  perp = Perp(rpc_client, 'devnet',wallet)
  perp.init()
  product = Product(perp)
  product.initByIndex(0)
  trader = Trader(perp)
  trader.init()
  [ix, signers] = trader.cancel_order_ix(product, 269375752548498747818049433352371) # Get this order id from t.get_open_orders()
```

Checkout https://github.com/GooseFX1/gfx-perps-python-sdk/blob/dev/test_perp.py for examples on the above functionalities!

### Subscribe to asks

The subscribe to asks feature needs a callback function which can process added_asks which tracks the new asks at new prices and size changes which tracks if the size of ask is changed

```python
  def on_ask_change(updated_asks):
    print("Updated Asks:", updated_asks)

  perp = Perp(rpc_client, 'devnet', keyp)
  perp.init()
  product = Product(perp)
  product.init_by_name('SOL-PERP')
  orderbook = product.get_orderbook_L2()
  await product.subscribe_to_asks(on_ask_change)

```

### Subscribe to bids

The subscribe to bids feature needs a callback function which can process added_bids which tracks the new bids at new prices and size changes which tracks if the size of bid is changed

```python
  def on_bid_change(updated_bids):
    print("Updated Bids:", updated_bids)

  perp = Perp(rpc_client, 'devnet', keyp)
  perp.init()
  product = Product(perp)
  product.init_by_name('SOL-PERP')
  orderbook = product.get_orderbook_L2()
  await product.subscribe_to_bids(on_bid_change)

```

Checkout https://github.com/GooseFX1/gfx-perps-python-sdk/test_subscribe_accounts.py for examples on the subscription functionalities!

Happy trading!
