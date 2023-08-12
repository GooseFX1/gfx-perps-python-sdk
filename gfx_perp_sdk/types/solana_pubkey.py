from podite import (
    FixedLenArray,
    U8,
    pod,
)

@pod
class Solana_pubkey:
    bytes: FixedLenArray[U8, 32]

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
