from solana.publickey import PublicKey
from typing import List
from .perp import Perp
from .product import Product
from .types import TraderRiskGroup
import utils
from dataclasses import dataclass, field
import base64


class TraderPosition:
    quantity: str
    averagePrice: str
    index: str

class Trader(Perp):
    traderRiskGroup: TraderRiskGroup
    trgBytes: bytes
    trgKey: PublicKey
    userTokenAccount: PublicKey
    marketProductGroupVault: PublicKey
    totalDeposited: str
    totalWithdrawn: str
    marginAvailable: str
    traderPositions: any
    totalTradedVolume: str

    def __init__(self, perp: Perp):
        super(Trader,self).__init__(
            perp.connection,
            perp.networkType,
            perp.wallet,
            perp.marketProductGroup,
            perp.mpgBytes
        )

    def create_trader_account_ixs():
        print('create_trader_account_ixs')

    def get_open_orders(product: Product):
        print('get_open_orders')
    
    def init(self):
        trgAddress = utils.getTraderRiskGroup(self.wallet.public_key, self.connection, self.ADDRESSES["DEX_ID"], self.ADDRESSES["MPG_ID"])
        if trgAddress == None:
            raise KeyError("No Trader Risk Group account for this wallet. Please create a new one first.")
        response = self.connection.get_account_info(PublicKey(trgAddress))
        try:
            r = response['result']['value']['data'][0]
            decoded = base64.b64decode(r)[8:]
            trg = TraderRiskGroup.from_bytes(decoded)
            self.traderRiskGroup = trg
            self.trgBytes = decoded
            self.userTokenAccount = utils.getUserAta(self.wallet.public_key, self.ADDRESSES['VAULT_MINT'])
            self.marketProductGroupVault = utils.getMpgVault(self.ADDRESSES['VAULT_SEED'], self.ADDRESSES['MPG_ID'], self.ADDRESSES['DEX_ID'])
        except:
            raise KeyError("No Trader Risk Group account for this wallet. Please create a new one first.") 
        
    def deposit_funds_ix():
        print('deposit_funds_ix')

    def withdraw_funds_ix():
        print('withdraw_funds_ix')

    def new_order_ix():
        print('new_order_ix')
    
    def cancel_order_ix():
        print('cancel_order_ix')

    def refresh_data():
        print('refresh_data')