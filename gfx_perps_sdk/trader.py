from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import (SYS_PROGRAM_ID, create_account, CreateAccountParams)
from typing import List
from .perp import Perp
from .product import Product
from .types import TraderRiskGroup
import utils
from dataclasses import dataclass, field
import base64
from solana.rpc import types
from .instructions.initialize_trader_risk_group import initialize_trader_risk_group

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

    def create_trader_account_ixs(self):
        trg = Keypair.generate()
        trader_risk_state_acct=Keypair.generate()
        ix1 = utils.initialize_trader_fee_acct(
            self.wallet.public_key, 
            self.ADDRESSES["MPG_ID"],
            self.ADDRESSES["FEES_ID"],
            trg.public_key,
            SYS_PROGRAM_ID,
            None
        )
        crParams = CreateAccountParams(from_pubkey=self.wallet.public_key, 
                                       new_account_pubkey=trg.public_key,
                                       lamports=96600000, space=13744,
                                        program_id=self.ADDRESSES["DEX_ID"] )
        ix2 = create_account(crParams)
        ix3 = initialize_trader_risk_group(
            owner=self.wallet.public_key,
            trader_risk_group=trg.public_key,
            market_product_group=self.ADDRESSES["MPG_ID"],
            risk_signer=utils.getRiskSigner(self.ADDRESSES["MPG_ID"], self.ADDRESSES["DEX_ID"]),
            trader_risk_state_acct=trader_risk_state_acct.public_key,
            trader_fee_state_acct=utils.get_trader_fee_state_acct(trg.public_key,self.ADDRESSES["MPG_ID"],self.ADDRESSES["FEES_ID"]),
            risk_engine_program=self.ADDRESSES["MPG_ID"],
            system_program=SYS_PROGRAM_ID
        )
        # signers = list(trader_risk_state_acct )
        # signers.append(trg)
        # signers.append(self.wallet)
        blockhash = self.connection.get_recent_blockhash(commitment="finalized")
        transaction = Transaction(recent_blockhash=blockhash['result']['value']['blockhash'], 
                                  fee_payer=self.wallet.public_key).add(ix1)
        transaction.add(ix2)
        transaction.add(ix3)
        transaction.add_signer(trader_risk_state_acct)
        transaction.add_signer(trg)
        transaction.add_signer(self.wallet)
        result = transaction.verify_signatures()
        result = self.connection.simulate_transaction(transaction)
        #result = self.connection.send_transaction(transaction, self.wallet, trg, trader_risk_state_acct, opts=types.TxOpts(skip_preflight=True))
        print("Transaction response: ", result)



    def get_open_orders(product: Product):
        print('get_open_orders')
    
    def init(self):
        trgAddress = utils.getTraderRiskGroup(self.wallet.public_key, self.connection, self.ADDRESSES["DEX_ID"], self.ADDRESSES["MPG_ID"])
        if trgAddress == None:
            raise KeyError("No Trader Risk Group account for this wallet. Please create a new one first.")
        self.trgKey = PublicKey(trgAddress)
        response = self.connection.get_account_info(self.trgKey)
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