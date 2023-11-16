# LOCK-BEGIN[imports]: DON'T MODIFY
from .account_tag import AccountTag
from .fractional import Fractional
from podite import (pod)
from .solana_pubkey import Solana_pubkey as PublicKey



@pod
class AveragePosition:
    qty: "Fractional"
    price: "Fractional"
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)

    def to_json(self):
        return {
            "qty": float(self.qty.value),
            "price": float(self.price.value),
        }