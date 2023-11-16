# LOCK-BEGIN[imports]: DON'T MODIFY
from .fractional import Fractional
from podite import (
    FixedLenArray,
    U64,
    pod,
)

# LOCK-END


# LOCK-BEGIN[class(PriceEwma)]: DON'T MODIFY
@pod
class PriceEwma:
    ewma_bid: FixedLenArray["Fractional", 4]
    ewma_ask: FixedLenArray["Fractional", 4]
    bid: "Fractional"
    ask: "Fractional"
    slot: U64
    prev_bid: "Fractional"
    prev_ask: "Fractional"
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)

    def to_json(self):
        return {
            "ewma_bid": [float(ewma_bid.value) for ewma_bid in self.ewma_bid],
            "ewma_ask": [float(ewma_ask.value) for ewma_ask in self.ewma_ask],
            "bid": float(self.bid.value),
            "ask": float(self.ask.value),
            "slot": str(self.slot),
            "prev_bid": float(self.prev_bid.value),
            "prev_ask": float(self.prev_ask.value),
        }