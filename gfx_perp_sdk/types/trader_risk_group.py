# LOCK-BEGIN[imports]: DON'T MODIFY
from .account_tag import AccountTag
from .fractional import Fractional
from .open_orders import OpenOrders
from .trader_position import TraderPosition
from .trade_history import TradeHistory
from .average_position import AveragePosition
from .solana_pubkey import Solana_pubkey
from solders.pubkey import Pubkey as PublicKey

from podite import (
    FixedLenArray,
    I32,
    U128,
    U64,
    U8,
    pod,
)

# LOCK-END


# LOCK-BEGIN[class(TraderRiskGroup)]: DON'T MODIFY
@pod
class TraderRiskGroup:
    tag: AccountTag
    market_product_group: Solana_pubkey
    owner: Solana_pubkey
    active_products: FixedLenArray[U8, 16]
    total_deposited: Fractional
    total_withdrawn: Fractional
    cash_balance: Fractional
    pending_cash_balance: Fractional
    pending_fees: Fractional
    valid_until: U64
    maker_fee_bps: I32
    taker_fee_bps: I32
    trader_positions: FixedLenArray[TraderPosition, 16]
    risk_state_account: Solana_pubkey
    fee_state_account: Solana_pubkey
    client_order_id: U128
    open_orders: OpenOrders
    trade_history: FixedLenArray[TradeHistory, 14]
    funding_balance: Fractional
    referral: Solana_pubkey
    pending_reward_balance: Fractional
    _padding: FixedLenArray[U8, 464]
    avg_position: FixedLenArray[AveragePosition, 16]
    total_traded_volume: Fractional
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)

    def to_json(self):
        return {
            'tag': self.tag.get_name(),
            'market_product_group': str(PublicKey(self.market_product_group.bytes)),  # assuming PublicKey has a str representation
            'owner': str(PublicKey(self.owner.bytes)),  # likewise
            'active_products': [{'index': i, 'value': int(x)} for i, x in enumerate(self.active_products) if int(x) != 255],
            'total_deposited': float(self.total_deposited.value),
            'total_withdrawn': float(self.total_withdrawn.value),
            'cash_balance': float(self.cash_balance.value),
            'pending_cash_balance': float(self.pending_cash_balance.value),
            'pending_fees': float(self.pending_fees.value),
            'valid_until': int(self.valid_until),
            'maker_fee_bps': int(self.maker_fee_bps),
            'taker_fee_bps': int(self.taker_fee_bps),
            'trader_positions': [pos.to_json() for pos in self.trader_positions if pos.tag.get_name() == 'TRADER_POSITION'],
            'risk_state_account': str(PublicKey(self.risk_state_account.bytes)),
            'fee_state_account': str(PublicKey(self.fee_state_account.bytes)),
            'client_order_id': str(self.client_order_id),  # U128 might be too large for JSON int
            'open_orders': self.open_orders.to_json(),
            'trade_history': [history.to_json() for history in self.trade_history],
            'funding_balance': float(self.funding_balance.value),
            'referral': str(PublicKey(self.referral.bytes)),
            'pending_reward_balance': float(self.pending_reward_balance.value),
            'avg_position': [avg.to_json() for avg in self.avg_position],
            'total_traded_volume': float(self.total_traded_volume.value),
        }
