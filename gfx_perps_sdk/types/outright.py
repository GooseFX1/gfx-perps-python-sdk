# LOCK-BEGIN[imports]: DON'T MODIFY
from .fractional import Fractional
from .product_metadata import ProductMetadata
from .product_status import ProductStatus
from podite import (
    FixedLenArray,
    U64,
    pod,
)

# LOCK-END


# LOCK-BEGIN[class(Outright)]: DON'T MODIFY
@pod
class Outright:
    metadata: "ProductMetadata"
    num_queue_events: U64
    product_status: "ProductStatus"
    dust: "Fractional"
    cum_funding_per_share: "Fractional"
    cum_social_loss_per_share: "Fractional"
    open_long_interest: "Fractional"
    open_short_interest: "Fractional"
    padding: FixedLenArray[U64, 14]
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
