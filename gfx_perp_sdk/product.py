from typing import List
from solders.pubkey import Pubkey as PublicKey
from solana.rpc.websocket_api import (connect, SolanaWsClientProtocol)

from gfx_perp_sdk.types.solana_pubkey import Solana_pubkey
import gfx_perp_sdk.utils as utils

from .constants import perps_constants
from .perp import Perp
from .agnostic import Slab, EventQueue
from gfx_perp_sdk.agnostic.EventQueue import FillEventInfo


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
    events: [FillEventInfo]

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
        self.events = []

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
        self.events = []

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
        result = utils.process_deserialized_slab_data(bidDeserialized, askDeserialized)
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

    def get_order_details_by_order_id(self, order_id: int):
        l3ob = self.get_orderbook_L3()
        for bid in l3ob['bids']:
            if bid.orderId == order_id:
                return utils.get_user_info_bid_ask(self.connection, bid)
        for ask in l3ob['asks']:
            if ask.orderId == order_id:
                return utils.get_user_info_bid_ask(self.connection, ask)
        return None
    
    def get_order_details_for_multiple_order_ids(self, order_ids: List[int]):
        l3ob = self.get_orderbook_L3()
        order_details = {}
        for order_id in order_ids:
            order_details[order_id] = None
            for bid in l3ob['bids']:
                if bid.orderId == order_id:
                    bid_details = utils.get_user_info_bid_ask(self.connection, bid)
                    bid_details['orderId'] = bid.orderId
                    order_details[order_id] = bid_details
                    break 
            if order_details[order_id] is None:
                for ask in l3ob['asks']:
                    if ask.orderId == order_id:
                        ask_details = utils.get_user_info_bid_ask(self.connection, ask)
                        ask_details['orderId'] = ask.orderId
                        order_details[order_id] = bid_details
                        break 
        return order_details
    
    async def subscribe_to_bids(self, on_bids_change):
        wss = self.connection._provider.endpoint_uri.replace("https", "wss")
        async with connect(wss) as solana_webscoket:
            solana_webscoket: SolanaWsClientProtocol
            await solana_webscoket.account_subscribe(pubkey=self.BIDS, encoding="base64+zstd")
            first_resp = await solana_webscoket.recv()

            subscription_id = first_resp[0].result if first_resp and hasattr(
                first_resp[0], 'result') else None
            bidsData = self.connection.get_account_info(
                pubkey=self.BIDS, commitment="processed", encoding="base64")
            r1 = bidsData.value.data
            bidDeserialized = Slab.deserialize(r1, 40)
            prevBids = utils.process_deserialized_slab_data(bidDeserialized, None)
            prevBidsProcessed = utils.processL3Ob(prevBids["bids"], None, self.tick_size, self.decimals)["bids"]
            while True:
                try:
                    msg = await solana_webscoket.recv()
                    if msg:
                        r1 = msg[0].result.value.data
                        bidDeserialized = Slab.deserialize(r1, 40)
                        currentBids = utils.process_deserialized_slab_data(bidDeserialized, None)
                        currentBidsProcessed = utils.processL3Ob(currentBids["bids"], None, self.tick_size, self.decimals)["bids"]
                        new_bids = utils.get_slab_changes(prevBidsProcessed, currentBidsProcessed)
                        on_bids_change(currentBidsProcessed, new_bids)
                        # bid_ask_value_changes, bid_ask_added, bid_ask_removed = utils.calculate_bid_ask_changes(prevBidsProcessed, currentBidsProcessed)
                        prevBidsProcessed = currentBidsProcessed
                        # prevBids = currentBids
                        # on_bids_change(bid_ask_value_changes, bid_ask_added, bid_ask_removed)
                except Exception:
                    raise ModuleNotFoundError(
                        "unable to process the bids")

    async def subscribe_to_asks(self, on_asks_change):
        wss = self.connection._provider.endpoint_uri.replace("https", "wss")
        async with connect(wss) as solana_webscoket:
            solana_webscoket: SolanaWsClientProtocol
            await solana_webscoket.account_subscribe(pubkey=self.ASKS, encoding="base64+zstd")
            first_resp = await solana_webscoket.recv()

            subscription_id = first_resp[0].result if first_resp and hasattr(
                first_resp[0], 'result') else None
            asksData = self.connection.get_account_info(
                pubkey=self.ASKS, commitment="processed", encoding="base64")
            r1 = asksData.value.data
            askDeserialized = Slab.deserialize(r1, 40)
            prevAsks = utils.process_deserialized_slab_data(None, askDeserialized)
            prevAsksProcessed = utils.processL3Ob(None, prevAsks["asks"], self.tick_size, self.decimals)["asks"]
            while True:
                try:
                    msg = await solana_webscoket.recv()
                    if msg:
                        r1 = msg[0].result.value.data
                        askDeserialized = Slab.deserialize(r1, 40)
                        currentAsks = utils.process_deserialized_slab_data(None, askDeserialized)
                        currentAsksProcessed = utils.processL3Ob(None, currentAsks["asks"], self.tick_size, self.decimals)["asks"]
                        new_asks = utils.get_slab_changes(prevAsksProcessed, currentAsksProcessed)
                        on_asks_change(currentAsksProcessed, new_asks)
                        # bid_ask_value_changes, bid_ask_added, bid_ask_removed = utils.calculate_bid_ask_changes(prevAsksProcessed, currentAsksProcessed)
                        prevAsksProcessed = currentAsksProcessed
                        # prevAsks = currentAsks
                        # on_asks_change(bid_ask_value_changes, bid_ask_added, bid_ask_removed)
                except Exception:
                    raise ModuleNotFoundError(
                        "unable to process the asks")

    # async def subscribe_to_trades(self, trgKey:PublicKey, on_fill_out_change, event_type: str):
    async def subscribe_to_trades(self, trgKey:PublicKey, on_positions_change):
        wss = self.connection._provider.endpoint_uri.replace("https", "wss")
        async with connect(wss) as solana_webscoket:
            solana_webscoket: SolanaWsClientProtocol
            await solana_webscoket.account_subscribe(pubkey=self.EVENT_QUEUE, encoding="base64+zstd")
            first_resp = await solana_webscoket.recv()

            subscription_id = first_resp[0].result if first_resp and hasattr(
                first_resp[0], 'result') else None
            eventData = self.connection.get_account_info(
                pubkey=self.EVENT_QUEUE, commitment="processed", encoding="base64")
            r1 = eventData.value.data
            eventQueueDeserialized = EventQueue.deserialize(r1)
            # (prevFillEvents, prevOutEvents) = eventQueueDeserialized.get_fill_out_events()
            # prevL3ob = self.get_orderbook_L3()
            while True:
                try:
                    msg = await solana_webscoket.recv()
                    if msg:
                        r1 = msg[0].result.value.data
                        eventQueueDeserialized = EventQueue.deserialize(r1)
                        (newFillEvents, newOutEvents) = eventQueueDeserialized.get_fill_out_events()
                        
                        # newL3ob = self.get_orderbook_L3()
                        # if event_type == "fills":
                        new_fill_events_json = []
                        for new_fill_event in newFillEvents:
                            new_fill_events_json.append(new_fill_event.to_json())

                        new_fill_events = utils.calculate_fill_changes(self.events, newFillEvents)
                        self.events.extend(new_fill_events)
                        if len(new_fill_events):
                            print(new_fill_events)
                        on_positions_change(new_fill_events)
                        
                        # elif event_type == "outs":
                        #     out_value_changes, out_added, out_removed = utils.calculate_out_changes(prevOutEvents, newOutEvents, self.decimals, self.tick_size)
                        #     on_fill_out_change(out_value_changes, out_added, out_removed)
                        #     prevOutEvents = newOutEvents
                        # bid_value_changes, bid_added, bid_removed = utils.calculate_bid_ask_changes(prevL3ob['bids'], newL3ob['bids'])
                        # ask_value_changes, ask_added, ask_removed = utils.calculate_bid_ask_changes(prevL3ob['asks'], newL3ob['asks'])
                        # prevL3ob = newL3ob
                except Exception:
                    raise ModuleNotFoundError(
                        "unable to process the eventqueue")