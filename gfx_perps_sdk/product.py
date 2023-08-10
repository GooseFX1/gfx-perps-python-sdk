from solana.publickey import PublicKey
from .perp import Perp
from .agnostic import Slab
import utils
import base64

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
        for index in range(0,len(products['PRODUCTS'])):
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
              raise ModuleNotFoundError("Please initialize with the right Product first...")
        except:
              raise ModuleNotFoundError("Please initialize with the right Product first...")
        bidKey = self.BIDS
        askKey = self.ASKS
        bidsData = self.connection.get_account_info(PublicKey(bidKey), commitment="processed", encoding="base64")
        r1 = bidsData['result']['value']['data'][0]
        decodedBids = base64.b64decode(r1)
        bidDeserialized = Slab.deserialize(decodedBids, 40)
        obBids = bidDeserialized.getL2DepthJS(40, True)
        asksData = self.connection.get_account_info(PublicKey(askKey), commitment="processed", encoding="base64")
        r2 = asksData['result']['value']['data'][0]
        decodedAsks = base64.b64decode(r2)
        askDeserialized = Slab.deserialize(decodedAsks, 40)
        obAsks = askDeserialized.getL2DepthJS(40, True)
        processedData = utils.processOrderbook(obBids, obAsks, self.tick_size, self.decimals)
        return processedData

    def get_orderbook_L3(self):
        try:
            if len(self.name) < 1:
              raise ModuleNotFoundError("Please initialize with the right Product first...")
        except:
              raise ModuleNotFoundError("Please initialize with the right Product first...")
        bidKey = self.BIDS
        askKey = self.ASKS
        bidsData = self.connection.get_account_info(PublicKey(bidKey), commitment="processed", encoding="base64")
        r1 = bidsData['result']['value']['data'][0]
        decodedBids = base64.b64decode(r1)
        bidDeserialized = Slab.deserialize(decodedBids, 40)
        asksData = self.connection.get_account_info(PublicKey(askKey), commitment="processed", encoding="base64")
        r2 = asksData['result']['value']['data'][0]
        decodedAsks = base64.b64decode(r2)
        askDeserialized = Slab.deserialize(decodedAsks, 40)
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
      
        result = utils.processL3Ob(result['bids'], result['asks'], self.tick_size, self.decimals)
        return result    
    def get_trades(self):
        print('get_trades')

    def subscribe_to_orderbook(self):
        print('subscribe_to_orderbook')