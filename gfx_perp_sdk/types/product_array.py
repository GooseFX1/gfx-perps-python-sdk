# LOCK-BEGIN[imports]: DON'T MODIFY
from gfx_perp_sdk.types.product_status import ProductStatus
from .product import Product
from podite import (
    FixedLenArray,
    pod,
)

# LOCK-END


# LOCK-BEGIN[class(ProductArray)]: DON'T MODIFY
@pod
class ProductArray:
    array: FixedLenArray[Product, 256]
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)

    def to_json(self):
        products_json = []
        for product in self.array:
            if getattr(product.field, "outright"):
                if product.field.outright.product_status == ProductStatus.INITIALIZED:
                    products_json.append(product.field.outright.to_json())
        return products_json