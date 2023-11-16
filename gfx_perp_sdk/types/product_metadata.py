# LOCK-BEGIN[imports]: DON'T MODIFY
from .fractional import Fractional
from .price_ewma import PriceEwma
from .solana_pubkey import Solana_pubkey
from podite import (
    FixedLenArray,
    U64,
    U8,
    pod,
)
from solders.pubkey import Pubkey as PublicKey

# LOCK-END


# LOCK-BEGIN[class(ProductMetadata)]: DON'T MODIFY
@pod
class ProductMetadata:
    bump: U64
    product_key: Solana_pubkey
    name: FixedLenArray[U8, 16]
    orderbook: Solana_pubkey
    tick_size: "Fractional"
    base_decimals: U64
    price_offset: "Fractional"
    contract_volume: "Fractional"
    prices: PriceEwma
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)

    def to_json(self):
        return {
            "bump": str(self.bump),
            "product_key": str(PublicKey(self.product_key.bytes)),
            "name": bytes(self.name).rstrip(b'\x00').decode('utf-8'),
            "orderbook": str(PublicKey(self.orderbook.bytes)),
            "tick_size": float(self.tick_size.value),
            "base_decimals": str(self.base_decimals),
            "price_offset": float(self.price_offset.value),
            "contract_volume": float(self.contract_volume.value),
            "prices": self.prices.to_json(),
        }