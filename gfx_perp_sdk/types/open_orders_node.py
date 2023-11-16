# LOCK-BEGIN[imports]: DON'T MODIFY
from podite import (
    U128,
    pod,
    U64
)

# LOCK-END


# LOCK-BEGIN[class(OpenOrdersNode)]: DON'T MODIFY
@pod
class OpenOrdersNode:
    id: U128
    client_id: U128
    prev: U64
    next: U64
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)

    def to_json(self):
        return {
            "id": str(self.id),
            "client_id": str(self.client_id),
            "prev": str(self.prev),
            "next": str(self.next)
        }