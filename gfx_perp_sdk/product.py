from solders.pubkey import Pubkey as PublicKey
from solana.rpc.websocket_api import (connect, SolanaWsClientProtocol)
from .constants import perps_constants
from .perp import Perp
from .agnostic import Slab
import gfx_perp_sdk.utils as utils
import base64
import requests
import json

class Product(Perp):
    name: str
    PRODUCT_ID: PublicKey
    ORDERBOOK_ID: PublicKey
    BIDS: PublicKey
    ASKS: PublicKey
    EVENT_QUEUE: PublicKey
    marketSigner: PublicKey
    tick_size: int
    decimals: int

    def __init__(self, perp: Perp):
        super(Product, self).__init__(perp.connection, 
        perp.networkType, 
        perp.wallet, 
        perp.marketProductGroup, 
        perp.mpgBytes)

    def init_by_index(self, index: int):
        products = None
        products = self.ADDRESSES
        if index > len(products['PRODUCTS']) - 1:
            raise IndexError('Index out of bounds')
        selectedProduct = products['PRODUCTS'][index]
        self.name = selectedProduct['name']
        self.PRODUCT_ID = selectedProduct['PRODUCT_ID']
        self.ORDERBOOK_ID = selectedProduct['ORDERBOOK_ID']
        self.BIDS = selectedProduct['BIDS']
        self.ASKS = selectedProduct['ASKS']
        self.EVENT_QUEUE = selectedProduct['EVENT_QUEUE']
        self.tick_size = selectedProduct['tick_size']
        self.decimals = selectedProduct['decimals']
        self.marketSigner = utils.get_market_signer(
            self.PRODUCT_ID,
            self.ADDRESSES['DEX_ID']
        )

    def init_by_name(self, name: str):
        selectedProduct = None
        products = self.ADDRESSES
        for index in range(0, len(products['PRODUCTS'])):
            if products['PRODUCTS'][index]['name'] == name:
                selectedProduct = products['PRODUCTS'][index]
        if selectedProduct == None:
            raise IndexError('Index out of bounds')
        
        self.name = selectedProduct['name']
        self.PRODUCT_ID = selectedProduct['PRODUCT_ID']
        self.ORDERBOOK_ID = selectedProduct['ORDERBOOK_ID']
        self.BIDS = selectedProduct['BIDS']
        self.ASKS = selectedProduct['ASKS']
        self.EVENT_QUEUE = selectedProduct['EVENT_QUEUE']
        self.tick_size = selectedProduct['tick_size']
        self.decimals = selectedProduct['decimals']
        self.marketSigner = utils.get_market_signer(
            self.PRODUCT_ID,
            self.ADDRESSES['DEX_ID']
        )

    def get_orderbook_L2(self):
        try:
            if len(self.name) < 1:
                raise ModuleNotFoundError(
                    "Please initialize with the right Product first...")
        except:
            raise ModuleNotFoundError(
                "Please initialize with the right Product first...")
        bidKey = self.BIDS
        askKey = self.ASKS
        bidsData = self.connection.get_account_info(
            pubkey=bidKey, commitment="processed", encoding="base64")
        r1 = bidsData.value.data
        bidDeserialized = Slab.deserialize(r1, 40)
        obBids = bidDeserialized.getL2DepthJS(40, True)
        asksData = self.connection.get_account_info(
            pubkey=askKey, commitment="processed", encoding="base64")
        r2 = asksData.value.data
        askDeserialized = Slab.deserialize(r2, 40)
        obAsks = askDeserialized.getL2DepthJS(40, True)
        processedData = utils.processOrderbook(
            obBids, obAsks, self.tick_size, self.decimals)
        return processedData

    def get_orderbook_L3(self):
        try:
            if len(self.name) < 1:
                raise ModuleNotFoundError(
                    "Please initialize with the right Product first...")
        except:
            raise ModuleNotFoundError(
                "Please initialize with the right Product first...")
        bidKey = self.BIDS
        askKey = self.ASKS
        bidsData = self.connection.get_account_info(
            pubkey=bidKey, commitment="processed", encoding="base64")
        r1 = bidsData.value.data
        bidDeserialized = Slab.deserialize(r1, 40)
        asksData = self.connection.get_account_info(
            pubkey=askKey, commitment="processed", encoding="base64")
        r2 = asksData.value.data
        askDeserialized = Slab.deserialize(r2, 40)
        result = {"bids": [], "asks": []}
        for bids in bidDeserialized.items():
            price = bids[0].getPrice()
            size = bids[0].baseQuantity
            user = PublicKey(bids[1][0:32])
            orderId = bids[0].key
            result['bids'].append({
                "price": price,
                "size": size,
                "user": user,
                "orderId": orderId
            })

        for asks in askDeserialized.items():
            price = asks[0].getPrice()
            size = asks[0].baseQuantity
            user = PublicKey(asks[1][0:32])
            orderId = asks[0].key
            result['asks'].append({
                "price": price,
                "size": size,
                "user": user,
                "orderId": orderId
            })

        result = utils.processL3Ob(
            result['bids'], result['asks'], self.tick_size, self.decimals)
        return result

    def get_trades(self):
        req_param = {
            'isDevnet': True if self.networkType == 'devnet' else False,
            'pairName': self.name
        }
        res = requests.post(perps_constants.API_BASE +
                            perps_constants.TRADE_HISTORY, json=req_param)
        return json.loads(res.text)

    async def subscribe_to_orderbook(self, changeFn):
        wss = self.connection._provider.endpoint_uri.replace("https", "wss")
        # cl = await connect(wss)
        # await cl.account_subscribe(self.EVENT_QUEUE)
        # i = 0
        # while True:
        #    res = await cl.recv()
        #    print(i)
        #    print(res)
        #    i = i + 1
        # async with connect(wss) as solana_webscoket:
        #  await solana_webscoket.account_subscribe(self.EVENT_QUEUE)
        #  first_resp = await solana_webscoket.recv()
        #  print("result 1: ", first_resp)
        #  #subscription_id = first_resp[0].result
        #  async for idx, msg in enumerate(solana_webscoket):
        #      if idx == 3:
        #          break
        #      print("i is: ", idx)
        #      print(msg)
        # await solana_webscoket.account_unsubscribe(subscription_id)

    # async def changeFn(self, msg):
    #     print(f"Change detected: {msg}")

    async def subscribe_to_bids(self, changeFn):
        wss = self.connection._provider.endpoint_uri.replace("https", "wss")
        async with connect(wss) as solana_webscoket:
            solana_webscoket: SolanaWsClientProtocol
            await solana_webscoket.account_subscribe(self.BIDS)
            # await solana_webscoket.account_subscribe(PublicKey.from_string("G6U4K1T9wBdRxVpPNjcyHJFZtPR8yP4xEaKHZ36cDEV1"))
            first_resp = await solana_webscoket.recv()
            print("first_resp: ", first_resp)

            subscription_id = first_resp[0].result if first_resp and hasattr(
                first_resp[0], 'result') else None

            print("subscription_id: ", subscription_id)
            idx = 0
            while True:  # Replace with your own termination condition
                try:
                    msg = await solana_webscoket.recv()
                    if msg:
                        await changeFn(msg)
                    else:
                        print(f"No message received: {msg}")
                except Exception as e:
                    print(f"An error occurred: {e}")
                # if idx == 30:  # Stop after 30 messages, for example
                #     break
            # await solana_webscoket.account_unsubscribe(subscription_id)