# LOCK-BEGIN[imports]: DON'T MODIFY
#from types.combo import Combo
from .outright import Outright
from podite import (
    AutoTagType,
    Enum,
    Option,
    Variant,
    named_fields,
    pod,
)

# LOCK-END

import gfx_perp_sdk.types as types


# LOCK-BEGIN[class(Product)]: DON'T MODIFY
@pod
class Product(Enum[AutoTagType]):
    OUTRIGHT = Variant(field=named_fields(outright=Outright))
    # LOCK-END

    def metadata(self) -> "types.ProductMetadata":
        if getattr(self.field, "outright"):
            return self.field.outright.metadata
        else:
            raise ValueError(f"Uknown product type for {self}")

    @classmethod
    def _to_bytes_partial(cls, buffer, obj, **kwargs):
        # to modify packing, change this method
        return super()._to_bytes_partial(buffer, obj, **kwargs)

    @classmethod
    def _from_bytes_partial(cls, buffer, **kwargs):
        # to modify unpacking, change this method
        return super()._from_bytes_partial(buffer, **kwargs)

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
