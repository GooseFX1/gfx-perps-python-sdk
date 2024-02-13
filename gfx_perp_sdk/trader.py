from typing import Optional, List
from solders.pubkey import Pubkey as PublicKey
from solders.keypair import Keypair
from solders.rpc.responses import GetAccountInfoResp
from solana.rpc.websocket_api import (connect, SolanaWsClientProtocol)
from solders.system_program import (ID as SYS_PROGRAM_ID, create_account, CreateAccountParams)
from gfx_perp_sdk.constants.perps_constants import MINT_DECIMALS, TOKEN_PROGRAM_ID
import gfx_perp_sdk.utils as utils

from .perp import Perp
from .product import Product
from .types import (TraderRiskGroup, Fractional, Solana_pubkey, base, Side, OrderType)
from .instructions.initialize_trader_risk_group import initialize_trader_risk_group
from .instructions.deposit_funds import (deposit_funds, DepositFundsParams)
from .instructions.withdraw_funds import (withdraw_funds, WithdrawFundsParams)
from .instructions.new_order import (new_order, NewOrderParams)
from .instructions.cancel_order import (cancel_order, CancelOrderParams)
from .instructions.close_trader_risk_group import close_trader_risk_group
from podite import U32
from dataclasses import dataclass

@dataclass
class TraderPositionVer:
    quantity: str
    averagePrice: str
    index: int
    def __init__(self, quantity: Fractional, averagePrice: Fractional, index: int):
        self.quantity = quantity
        self.averagePrice = averagePrice
        self.index = index
    def to_json(self):
        return {
            "quantity": self.quantity,
            "averagePrice": self.averagePrice,
            "index": self.index
        }
    def __str__(self):
        return f"TraderPositionVer(quantity={self.quantity}, averagePrice={self.averagePrice}, index={self.index})"

    def __repr__(self):
        return f"TraderPositionVer(quantity={self.quantity}, averagePrice={self.averagePrice}, index={self.index})"

class Trader(Perp):
    traderRiskGroup: TraderRiskGroup
    trgBytes: bytes
    trgKey: PublicKey
    userTokenAccount: PublicKey
    marketProductGroupVault: PublicKey
    totalDeposited: str
    totalWithdrawn: str
    marginAvailable: str
    traderPositions: List[TraderPositionVer]
    totalTradedVolume: str

    def __init__(self, perp: Perp):
        super(Trader, self).__init__(
            perp.connection,
            perp.networkType,
            perp.wallet,
            perp.marketProductGroup,
            perp.mpgBytes
        )

    def get_all_trg_accounts(self):
        accounts = utils.getAllTraderRiskGroup(
            self.wallet.pubkey(), self.connection, self.ADDRESSES["DEX_ID"], self.ADDRESSES["MPG_ID"])
        return accounts

    def create_trader_account_ixs(self):
        trgAddress = utils.getTraderRiskGroup(
            self.wallet.pubkey(), self.connection, self.ADDRESSES["DEX_ID"], self.ADDRESSES["MPG_ID"])
        if trgAddress != None:
            raise KeyError("Trader Risk Group already exists for this wallet")

        trg = Keypair()
        trader_risk_state_acct = Keypair()
        ix1 = utils.initialize_trader_fee_acct(
            self.wallet.pubkey(),
            self.ADDRESSES["MPG_ID"],
            self.ADDRESSES["FEES_ID"],
            trg.pubkey(),
            SYS_PROGRAM_ID,
            None
        )
        crParams = CreateAccountParams(from_pubkey=self.wallet.pubkey(),
                                       to_pubkey=trg.pubkey(),
                                       lamports=96600000,
                                       space=13744,
                                       owner=self.ADDRESSES["DEX_ID"])
        ix2 = create_account(crParams)
        ix3 = initialize_trader_risk_group(
            owner=self.wallet.pubkey(),
            trader_risk_group=trg.pubkey(),
            market_product_group=self.ADDRESSES["MPG_ID"],
            risk_signer=utils.getRiskSigner(
                self.ADDRESSES["MPG_ID"], self.ADDRESSES["DEX_ID"]),
            trader_risk_state_acct=trader_risk_state_acct.pubkey(),
            trader_fee_state_acct=utils.get_trader_fee_state_acct(
                trg.pubkey(), self.ADDRESSES["MPG_ID"], self.ADDRESSES["FEES_ID"]),
            risk_engine_program=self.ADDRESSES["RISK_ID"],
            referral_key=PublicKey.from_string(
                "11111111111111111111111111111111"),
            system_program=SYS_PROGRAM_ID,
            program_id=self.ADDRESSES["DEX_ID"]
        )
        # signers = list(trader_risk_state_acct )
        # signers.append(trg)
        # signers.append(self.wallet)
        return [[ix1, ix2, ix3], [trader_risk_state_acct, trg, self.wallet]]

    def get_open_orders(self, product: Product):
        l3ob = product.get_orderbook_L3()
        open_orders = utils.filterOpenOrders(l3ob, str(self.trgKey))
        open_orders_json = {key: [order_info.to_json() for order_info in value] for key, value in open_orders.items()}
        return open_orders_json

    def fetch_trader_risk_group(self):
        response = self.connection.get_account_info(
            pubkey=self.trgKey, commitment="processed", encoding="base64")
        if not response.value:
            raise KeyError("No Trader Risk Group account found for this trgKey.")
        r = response.value.data
        decoded = r[8:]
        trg: TraderRiskGroup = TraderRiskGroup.from_bytes(decoded)
        self.trgBytes = decoded
        return trg
    
    def init(self):
        trgAddress = utils.getTraderRiskGroup(
            self.wallet.pubkey(), self.connection, self.ADDRESSES["DEX_ID"], self.ADDRESSES["MPG_ID"])
        if trgAddress == None:
            raise KeyError(
                "No Trader Risk Group account for this wallet. Please create a new one first.")
        self.trgKey = PublicKey.from_string(trgAddress)
        self.traderRiskGroup = self.fetch_trader_risk_group()
        self.userTokenAccount = utils.getUserAta(self.wallet.pubkey(), self.ADDRESSES['VAULT_MINT'])
        self.marketProductGroupVault = utils.getMpgVault(self.ADDRESSES['VAULT_SEED'], self.ADDRESSES['MPG_ID'], self.ADDRESSES['DEX_ID'])
        self.totalDeposited = self.traderRiskGroup.total_deposited.value / 100000
        self.totalWithdrawn = self.traderRiskGroup.total_withdrawn.value / 100000
        positions: List[TraderPositionVer] = []
        idx = 0
        for trader_position in self.traderRiskGroup.trader_positions:
            if trader_position.product_key != SYS_PROGRAM_ID:
                positions.append(
                    TraderPositionVer(trader_position.position.value / 100000,
                                    self.traderRiskGroup.avg_position[idx].price.value / 100, idx)
                )
            idx = idx + 1

        self.traderPositions = positions
        self.totalTradedVolume = self.traderRiskGroup.total_traded_volume.value
    
    def deposit_funds_ix(self, amount: Fractional):
        param = DepositFundsParams(amount)
        ix1 = deposit_funds(
            user=self.wallet.pubkey(),
            user_token_account=self.userTokenAccount,
            trader_risk_group=self.trgKey,
            market_product_group=self.ADDRESSES["MPG_ID"],
            market_product_group_vault=self.marketProductGroupVault,
            params=param,
            program_id=self.ADDRESSES["DEX_ID"]
        )
        return [[ix1], [self.wallet]]

    def withdraw_funds_ix(self, amount: Fractional):
        param = WithdrawFundsParams(amount)
        ix1 = withdraw_funds(self.wallet.pubkey(),
                             self.ADDRESSES["BUDDY_LINK_PROGRAM"],
                             self.userTokenAccount,
                             self.trgKey,
                             self.ADDRESSES["MPG_ID"],
                             self.marketProductGroupVault,
                             self.ADDRESSES["RISK_ID"],
                             PublicKey(Solana_pubkey.to_bytes(
                                 self.marketProductGroup.risk_model_configuration_acct)),
                             PublicKey(Solana_pubkey.to_bytes(
                                 self.marketProductGroup.risk_output_register)),
                             PublicKey(Solana_pubkey.to_bytes(
                                 self.traderRiskGroup.risk_state_account)),
                             utils.getRiskSigner(
                                 self.ADDRESSES["MPG_ID"], self.ADDRESSES["DEX_ID"]),
                             param,
                             self.ADDRESSES["DEX_ID"],
                             [SYS_PROGRAM_ID, SYS_PROGRAM_ID, SYS_PROGRAM_ID, SYS_PROGRAM_ID, SYS_PROGRAM_ID,
                                 self.ADDRESSES["BUDDY_LINK_PROGRAM"], self.ADDRESSES["BUDDY_LINK_PROGRAM"], self.ADDRESSES["BUDDY_LINK_PROGRAM"]]
                             )
        return [[ix1], [self.wallet]]

    def withdraw_funds_ix_for_trg(self, amount: Fractional, trgKey: PublicKey):
        param = WithdrawFundsParams(amount)
        trader_risk_group = utils.get_trader_risk_group(self.connection, trgKey)
        ix1 = withdraw_funds(self.wallet.pubkey(),
                             self.ADDRESSES["BUDDY_LINK_PROGRAM"],
                             self.userTokenAccount,
                             trgKey,
                             self.ADDRESSES["MPG_ID"],
                             self.marketProductGroupVault,
                             self.ADDRESSES["RISK_ID"],
                             PublicKey(Solana_pubkey.to_bytes(
                                 self.marketProductGroup.risk_model_configuration_acct)),
                             PublicKey(Solana_pubkey.to_bytes(
                                 self.marketProductGroup.risk_output_register)),
                             PublicKey(Solana_pubkey.to_bytes(
                                trader_risk_group.risk_state_account)),
                             utils.getRiskSigner(
                                 self.ADDRESSES["MPG_ID"], self.ADDRESSES["DEX_ID"]),
                             param,
                             self.ADDRESSES["DEX_ID"],
                             [SYS_PROGRAM_ID, SYS_PROGRAM_ID, SYS_PROGRAM_ID, SYS_PROGRAM_ID, SYS_PROGRAM_ID,
                                 self.ADDRESSES["BUDDY_LINK_PROGRAM"], self.ADDRESSES["BUDDY_LINK_PROGRAM"], self.ADDRESSES["BUDDY_LINK_PROGRAM"]]
                             )
        return [[ix1], [self.wallet]]

    def new_order_ix(self, product: Product, size: Fractional,
                     price: Fractional, 
                     side: Side, 
                     order_type: OrderType, 
                     self_trade_behaviour: Optional[base.SelfTradeBehavior] = base.SelfTradeBehavior.DECREMENT_TAKE,  
                     callback_id: Optional[U32] = 0):
        # if side == 'bid':
        #     sideParam = base.Side.BID
        # elif side == 'ask':
        #     sideParam = base.Side.ASK
        # else:
        #     raise KeyError("Side can only be bid or ask")
        if side not in  {Side.BID, Side.ASK}:
            raise KeyError("Side can only be bid or ask")
        if order_type not in {OrderType.LIMIT, OrderType.MARKET, OrderType.FILL_OR_KILL, OrderType.IMMEDIATE_OR_CANCEL, OrderType.POST_ONLY}:
            raise KeyError(
                    "Order type can onle be limit, market, fill_or_kill, immediate_or_cancel or post_only")


        match_limit = 1000
        # if order_type == "limit":
        #     order_type_param = OrderType.LIMIT
        # elif order_type == "market":
        #     order_type_param = OrderType.MARKET
        # elif order_type == "fill_or_kill":
        #     order_type_param = OrderType.FILL_OR_KILL
        # elif order_type == "immediate_or_cancel":
        #     order_type_param = OrderType.IMMEDIATE_OR_CANCEL
        # elif order_type == "post_only":
        #     order_type_param = OrderType.POST_ONLY
        # else:
        #     raise KeyError(
        #         "Order type can onle be limit, market, fill_or_kill, immediate_or_cancel or post_only")
        

        newParams = NewOrderParams(side,
                                   size,
                                   order_type,
                                   self_trade_behaviour,
                                   match_limit,
                                   price,
                                   callback_id
                                   )
        ix1 = new_order(
            self.wallet.pubkey(),
            self.trgKey,
            self.ADDRESSES["MPG_ID"],
            product.PRODUCT_ID,
            self.ADDRESSES["ORDERBOOK_P_ID"],
            product.ORDERBOOK_ID,
            utils.get_market_signer(
                product.PRODUCT_ID, self.ADDRESSES["DEX_ID"]),
            product.EVENT_QUEUE,
            product.BIDS,
            product.ASKS,
            self.ADDRESSES["FEES_ID"],
            PublicKey(Solana_pubkey.to_bytes(
                self.marketProductGroup.fee_model_configuration_acct)),
            PublicKey(Solana_pubkey.to_bytes(
                self.traderRiskGroup.fee_state_account)),
            PublicKey(Solana_pubkey.to_bytes(
                self.marketProductGroup.fee_output_register)),
            self.ADDRESSES["RISK_ID"],
            PublicKey(Solana_pubkey.to_bytes(
                self.marketProductGroup.risk_model_configuration_acct)),
            PublicKey(Solana_pubkey.to_bytes(
                self.marketProductGroup.risk_output_register)),
            PublicKey(Solana_pubkey.to_bytes(
                self.traderRiskGroup.risk_state_account)),
            utils.getRiskSigner(
                self.ADDRESSES["MPG_ID"], self.ADDRESSES["DEX_ID"]),
            newParams,
            self.ADDRESSES["DEX_ID"],
            SYS_PROGRAM_ID)

        return [[ix1], [self.wallet]]

    def cancel_order_ix(self, product: Product, orderId):
        param = CancelOrderParams(orderId)
        ix1 = cancel_order(
            self.wallet.pubkey(),
            self.trgKey,
            self.ADDRESSES["MPG_ID"],
            product.PRODUCT_ID,
            self.ADDRESSES["ORDERBOOK_P_ID"],
            product.ORDERBOOK_ID,
            utils.get_market_signer(
                product.PRODUCT_ID, self.ADDRESSES["DEX_ID"]),
            product.EVENT_QUEUE,
            product.BIDS,
            product.ASKS,
            self.ADDRESSES["RISK_ID"],
            PublicKey(Solana_pubkey.to_bytes(
                self.marketProductGroup.risk_model_configuration_acct)),
            PublicKey(Solana_pubkey.to_bytes(
                self.marketProductGroup.risk_output_register)),
            PublicKey(Solana_pubkey.to_bytes(
                self.traderRiskGroup.risk_state_account)),
            utils.getRiskSigner(
                self.ADDRESSES["MPG_ID"], self.ADDRESSES["DEX_ID"]),
            param,
            self.ADDRESSES["DEX_ID"],
            SYS_PROGRAM_ID)

        return [[ix1], [self.wallet]]

    def close_trader_risk_group_ix_for_trg(self, trgKey: PublicKey):
        ix =  close_trader_risk_group(
            owner=self.wallet.pubkey(),
            trader_risk_group=trgKey,
            market_product_group=self.ADDRESSES["MPG_ID"],
            system_program=SYS_PROGRAM_ID,
            program_id=self.ADDRESSES["DEX_ID"]
        )
        
        return [[ix], [self.wallet]]

    def refresh_data(self):
        self.init()
        
    async def subscribe_trader_positions(self, product: Product, on_fill_out_change):
        await product.subscribe_to_trades(self.trgKey, on_fill_out_change)
    
    async def subscribe_to_trader_risk_group(self, on_trader_state_change, change_param: str):
        wss = self.connection._provider.endpoint_uri.replace("http", "ws")
        async with connect(wss) as solana_websocket:
            solana_websocket: SolanaWsClientProtocol
            await solana_websocket.account_subscribe(pubkey=self.trgKey, commitment="processed", encoding="base64")
            first_resp = await solana_websocket.recv()
            subscription_id = first_resp[0].result if first_resp and hasattr(
                first_resp[0], 'result') else None
            prevTrg = self.fetch_trader_risk_group()
            while True:
                try:
                    msg = await solana_websocket.recv()
                    if msg:
                        r1 = msg[0].result.value.data
                        decoded = r1[8:]
                        currTrg: TraderRiskGroup = TraderRiskGroup.from_bytes(decoded)
                        trg_diffs = utils.compare_trader_risk_groups(prevTrg, currTrg, change_param)
                        if trg_diffs != {}:
                            on_trader_state_change(trg_diffs)
                        prevTrg = currTrg
                except Exception:
                    raise ModuleNotFoundError(
                        "unable to process the Trader Risk Group")

    async def get_position_update(self, current_market_price):
        open_orders = self.get_open_orders(self.product)
        position_status = utils.trader_position_status(open_orders, current_market_price)
        return position_status
    
    def get_cash_balance(self):
        trg = utils.get_trader_risk_group(self.connection, self.trgKey)
        return trg.cash_balance.value / 10 ** 5
    
    def get_cash_balance_for_trg(self, trgKey: PublicKey):
        trg = utils.get_trader_risk_group(self.connection, trgKey)
        return trg.cash_balance.value / 10 ** 5
    
    def get_deposited_amount(self):
        trg = utils.get_trader_risk_group(self.connection, self.trgKey)
        return trg.total_deposited.value / 10 ** 5

    def get_withdrawn_amount(self):
        trg = utils.get_trader_risk_group(self.connection, self.trgKey)
        return trg.total_withdrawn.value / 10 ** 5
    
    def get_trader_positions_by_product_index(self, index: int) -> List[TraderPositionVer] :
        self.refresh_data()
        # check product_key of traderPosition to be equal to product.PRODUCT_ID
        products = None
        products = self.ADDRESSES
        if index > len(products['PRODUCTS']) - 1:
            raise IndexError('Index out of bounds')
        positions: List[TraderPositionVer] = []
        for traderPosition in self.traderPositions:
            if traderPosition.index == index:
                positions.append(traderPosition)
        return positions
    
    def get_trader_positions_by_product_name(self, product_name: str) -> List[TraderPositionVer] :
        self.refresh_data()
        selectedProductIndex = None
        products = self.ADDRESSES
        for index in range(0, len(products['PRODUCTS'])):
            if products['PRODUCTS'][index]['name'] == product_name:
                selectedProductIndex = index
        if selectedProductIndex == None:
            raise IndexError('Index out of bounds')
        positions: List[TraderPositionVer] = []
        for traderPosition in self.traderPositions:
            if traderPosition.index == selectedProductIndex:
                positions.append(traderPosition)
        return positions
    
    def get_trader_positions_for_all_products(self) -> List[TraderPositionVer] :
        self.refresh_data()
        trader_positions: List[TraderPositionVer] = []
        for trader_position in self.traderPositions:
            if trader_position.quantity != 0:
                trader_positions.append(trader_position)
        return trader_positions

    def get_trader_positions_for_trg(self, trgkey: PublicKey) -> List[TraderPositionVer] :
        trg = utils.get_trader_risk_group(self.connection, trgkey)
        positions: List[TraderPositionVer] = []
        idx = 0
        for trader_position in trg.trader_positions:
            if trader_position.product_key != SYS_PROGRAM_ID:
                positions.append(
                    TraderPositionVer(trader_position.position.value / 100000,
                                    trg.avg_position[idx].price.value / 100, idx)
                )
            idx = idx + 1
        return positions
    
    async def subscribe_to_token_balance_change(self, callback_func):
        wss = self.connection._provider.endpoint_uri.replace("http", "ws")
        async with connect(wss) as solana_websocket:
            solana_websocket: SolanaWsClientProtocol
            await solana_websocket.account_subscribe(pubkey=self.userTokenAccount, commitment="processed", encoding="base64")
            first_resp = await solana_websocket.recv()
            subscription_id = first_resp[0].result if first_resp and hasattr(
                first_resp[0], 'result') else None
            tokenAccountData: GetAccountInfoResp = self.connection.get_account_info(
                pubkey=self.userTokenAccount, commitment="processed", encoding="base64")
            value = tokenAccountData.value
            if value is None:
                raise ValueError("Invalid account owner")
            if value.owner != TOKEN_PROGRAM_ID:
                raise AttributeError("Invalid account owner")

            oldTokenAccountInfo = utils.create_token_account_info(tokenAccountData.value.data)
            while True:
                try:
                    msg = await solana_websocket.recv()
                    if msg:
                        r1 = msg[0].result.value.data
                        newTokenAccountInfo = utils.create_token_account_info(r1)
                        if oldTokenAccountInfo.amount != newTokenAccountInfo.amount:
                            callback_func(
                                oldTokenAccountInfo.amount/10 ** MINT_DECIMALS, 
                                newTokenAccountInfo.amount/10 ** MINT_DECIMALS
                            )
                            oldTokenAccountInfo = newTokenAccountInfo
                except Exception:
                    raise ModuleNotFoundError(
                        "unable to process the Token Account")       