# LOCK-BEGIN[imports]: DON'T MODIFY
from .account_tag import AccountTag
from .fractional import Fractional
from podite import (pod, U64, FixedLenArray)
from .solana_pubkey import Solana_pubkey as PublicKey

# LOCK-END


# LOCK-BEGIN[class(TraderPosition)]: DON'T MODIFY
@pod
class TradeHistory:
    qty: FixedLenArray[Fractional, 8]
    price: FixedLenArray[Fractional, 8]
    latest_idx: U64
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
    
    def to_json(self):
        return {
            "qty": [float(qty.value) for qty in self.qty],
            "price": [float(price.value) for price in self.price],
            "latest_idx": str(self.latest_idx),
        }
