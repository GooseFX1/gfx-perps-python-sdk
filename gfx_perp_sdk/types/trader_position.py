# LOCK-BEGIN[imports]: DON'T MODIFY
from .account_tag import AccountTag
from .fractional import Fractional
from podite import (pod, U64)
from .solana_pubkey import Solana_pubkey
from solders.pubkey import Pubkey as PublicKey

# LOCK-END


# LOCK-BEGIN[class(TraderPosition)]: DON'T MODIFY
@pod
class TraderPosition:
    tag: "AccountTag"
    product_key: Solana_pubkey
    position: "Fractional"
    pending_position: "Fractional"
    product_index: U64
    last_cum_funding_snapshot: "Fractional"
    last_social_loss_snapshot: "Fractional"
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)

    def to_json(self):
        return {
            "tag": self.tag.get_name(),
            "product_key": str(PublicKey(self.product_key.bytes)),
            "position": float(self.position.value),
            "pending_position": float(self.pending_position.value),
            "product_index": int(self.product_index),
            "last_cum_funding_snapshot": float(self.last_cum_funding_snapshot.value),
            "last_social_loss_snapshot": float(self.last_social_loss_snapshot.value),
        }