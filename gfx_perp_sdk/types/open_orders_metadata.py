# LOCK-BEGIN[imports]: DON'T MODIFY
from .fractional import Fractional
from podite import (
    U64,
    pod,
)

# LOCK-END


# LOCK-BEGIN[class(OpenOrdersMetadata)]: DON'T MODIFY
@pod
class OpenOrdersMetadata:
    ask_qty_in_book: "Fractional"
    bid_qty_in_book: "Fractional"
    head_index: U64
    num_open_orders: U64
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)

    def to_json(self):
        return {
            "ask_qty_in_book": float(self.ask_qty_in_book.value),
            "bid_qty_in_book": float(self.bid_qty_in_book.value),
            "head_index": str(self.head_index),
            "num_open_orders": str(self.num_open_orders),
        }