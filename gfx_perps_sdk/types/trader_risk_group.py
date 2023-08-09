# LOCK-BEGIN[imports]: DON'T MODIFY
from .account_tag import AccountTag
from .fractional import Fractional
from .open_orders import OpenOrders
from .trader_position import TraderPosition
from .trade_history import TradeHistory
from .average_position import AveragePosition
from .solana_pubkey import Solana_pubkey as PublicKey
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
    market_product_group: PublicKey
    owner: PublicKey
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
    risk_state_account: PublicKey
    fee_state_account: PublicKey
    client_order_id: U128
    open_orders: OpenOrders
    trade_history: FixedLenArray[TradeHistory, 14]
    funding_balance: Fractional
    referral: PublicKey
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
